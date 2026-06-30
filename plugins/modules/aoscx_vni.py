#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_vni
version_added: "4.6.0"
short_description: Create, Update or Delete a VXLAN VNI on AOS-CX
description: >
  This module provides configuration management of Virtual Network
  Identifiers (VNIs) on AOS-CX devices. A VNI maps a network segment onto a
  VXLAN tunnel interface. A Layer 2 VNI maps the segment to a VLAN, while a
  Layer 3 VNI maps it to a VRF with routing enabled.
author: Aruba Networks (@ArubaNetworks)
options:
  vni_id:
    description: >
      Numeric identifier of the VNI (VXLAN Network Identifier), in the range
      1 to 16777215.
    required: true
    type: int
  interface:
    description: >
      Name of the VXLAN tunnel interface the VNI is attached to, for example
      C(vxlan1). The interface must already exist and be of type VXLAN.
    required: true
    type: str
  vni_type:
    description: Type of the VNI. Only VXLAN VNIs are supported.
    required: false
    default: vxlan_vni
    choices:
      - vxlan_vni
    type: str
  vlan:
    description: >
      VLAN ID mapped to the VNI for a Layer 2 VNI. Mutually exclusive with
      I(vrf). The VLAN must already exist on the device. When omitted it is
      left unchanged. Ignored when I(state) is C(delete).
    required: false
    type: int
  vrf:
    description: >
      Name of the VRF mapped to the VNI for a Layer 3 VNI. Mutually exclusive
      with I(vlan). The VRF must already exist on the device. When omitted it
      is left unchanged. Ignored when I(state) is C(delete).
    required: false
    type: str
  routing:
    description: >
      Whether routing is enabled for the VNI. Enable it for a Layer 3 (VRF)
      VNI. When omitted it is left unchanged. Ignored when I(state) is
      C(delete).
    required: false
    type: bool
  vtep_peers:
    description: >
      List of static remote VTEP IPv4 addresses (head-end replication) added
      to this VNI's flood list. The supplied list fully replaces the set of
      static peers attached to this VNI. When omitted the peers are left
      unchanged; an empty list removes all static peers for this VNI. Ignored
      when I(state) is C(delete).
    required: false
    type: list
    elements: str
  vtep_peer_vrf:
    description: >
      Transport VRF in which the static VTEP peers are reachable.
    required: false
    default: default
    type: str
  state:
    description: Create, update or delete the VNI.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create a Layer 2 VNI mapping VLAN 4000
  aoscx_vni:
    vni_id: 40000
    interface: vxlan1
    vlan: 4000

- name: Create a Layer 3 VNI mapping a VRF
  aoscx_vni:
    vni_id: 50000
    interface: vxlan1
    vrf: red
    routing: true

- name: Update the VLAN mapped to an existing VNI
  aoscx_vni:
    vni_id: 40000
    interface: vxlan1
    state: update
    vlan: 4001

- name: Create a Layer 2 VNI with static VTEP peers (head-end replication)
  aoscx_vni:
    vni_id: 206
    interface: vxlan1
    vlan: 206
    vtep_peers:
      - 10.0.0.9
      - 10.0.0.10

- name: Remove all static VTEP peers from a VNI
  aoscx_vni:
    vni_id: 206
    interface: vxlan1
    state: update
    vtep_peers: []

- name: Delete a VNI
  aoscx_vni:
    vni_id: 40000
    interface: vxlan1
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the VNI was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

# VXLAN Network Identifiers are 24-bit values, 0 is reserved.
MIN_VNI_ID = 1
MAX_VNI_ID = 16777215


def reconcile_vtep_peers(
    ansible_module, session, interface_obj, vni, desired_peers, peer_vrf
):
    """Reconcile the set of static VTEP peers flooding this VNI.

    Each peer is a static Tunnel Endpoint (head-end replication) keyed by
    (vrf, origin, destination) whose network_id map references the VNIs it
    floods. A single endpoint may flood several VNIs, so this VNI is added to
    or removed from the endpoint's network_id map; an endpoint is only created
    or deleted when it becomes referenced or unreferenced.

    Returns True if any tunnel endpoint was created, modified or deleted.
    """
    try:
        tep_class = session.api.get_module_class(session, "TunnelEndpoint")
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support VTEP peers "
                "(TunnelEndpoint). Upgrade pyaoscx. Details: {0}".format(
                    str(e)
                )
            )
        )

    vni_index = session.api.get_index(vni)
    vni_key = next(iter(vni_index))

    desired = set(desired_peers)
    changed = False

    try:
        # Existing static tunnel endpoints in the target VRF, by peer IP.
        teps = tep_class.get_all(session, interface_obj)
        existing_by_ip = {}
        current_ips = set()
        for tep in teps.values():
            if getattr(tep, "origin", None) != "static":
                continue
            if getattr(tep, "vrf_name", None) != peer_vrf:
                continue
            tep.get()
            existing_by_ip[tep.destination] = tep
            if vni_key in tep.network_id:
                current_ips.add(tep.destination)

        to_add = desired - current_ips
        to_remove = current_ips - desired
        changed = bool(to_add or to_remove)

        if not changed or ansible_module.check_mode:
            return changed

        vrf_obj = session.api.get_module(session, "Vrf", peer_vrf)
        vrf_obj.get()

        for ip in to_add:
            tep = existing_by_ip.get(ip)
            if tep is not None:
                # Endpoint already exists (floods other VNIs): attach this one.
                tep.network_id.update(vni_index)
                tep.update()
            else:
                tep = session.api.get_module(
                    session,
                    "TunnelEndpoint",
                    interface_obj,
                    network_id=vni,
                    destination=ip,
                    vrf=vrf_obj,
                )
                tep.create()

        for ip in to_remove:
            tep = existing_by_ip[ip]
            del tep.network_id[vni_key]
            if tep.network_id:
                tep.update()
            else:
                tep.delete()
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not reconcile VTEP peers: {0}".format(str(e))
        )

    return changed


def main():
    module_args = dict(
        vni_id=dict(type="int", required=True),
        interface=dict(type="str", required=True),
        vni_type=dict(type="str", default="vxlan_vni", choices=["vxlan_vni"]),
        vlan=dict(type="int", default=None),
        vrf=dict(type="str", default=None),
        routing=dict(type="bool", default=None),
        vtep_peers=dict(type="list", elements="str", default=None),
        vtep_peer_vrf=dict(type="str", default="default"),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[["vlan", "vrf"]],
    )

    vni_id = ansible_module.params["vni_id"]
    interface = ansible_module.params["interface"]
    vni_type = ansible_module.params["vni_type"]
    vlan = ansible_module.params["vlan"]
    vrf = ansible_module.params["vrf"]
    routing = ansible_module.params["routing"]
    vtep_peers = ansible_module.params["vtep_peers"]
    vtep_peer_vrf = ansible_module.params["vtep_peer_vrf"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    if not MIN_VNI_ID <= vni_id <= MAX_VNI_ID:
        ansible_module.fail_json(
            msg="vni_id must be between {0} and {1}.".format(
                MIN_VNI_ID, MAX_VNI_ID
            )
        )

    # Defense in depth: interface and vrf names are interpolated into REST
    # URIs, reject values that could escape the resource path.
    if interface in ("", ".", "..") or "," in interface:
        ansible_module.fail_json(
            msg="Invalid interface: {0}".format(interface)
        )
    if vrf is not None and (
        vrf in ("", ".", "..") or "," in vrf or "/" in vrf
    ):
        ansible_module.fail_json(msg="Invalid vrf: {0}".format(vrf))

    if (
        vtep_peer_vrf in ("", ".", "..")
        or "," in vtep_peer_vrf
        or "/" in vtep_peer_vrf
    ):
        ansible_module.fail_json(
            msg="Invalid vtep_peer_vrf: {0}".format(vtep_peer_vrf)
        )
    if vtep_peers is not None:
        for peer in vtep_peers:
            if peer in ("", ".", "..") or "," in peer or "/" in peer:
                ansible_module.fail_json(
                    msg="Invalid VTEP peer: {0}".format(peer)
                )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    # Resolve and materialize the VXLAN tunnel interface. The Vni constructor
    # validates that the interface is of type VXLAN.
    try:
        interface_obj = session.api.get_module(session, "Interface", interface)
        interface_obj.get()
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not find interface {0}: {1}".format(interface, str(e))
        )
    if getattr(interface_obj, "type", None) != "vxlan":
        ansible_module.fail_json(
            msg="Interface {0} is not a VXLAN interface.".format(interface)
        )

    try:
        vni = session.api.get_module(
            session,
            "Vni",
            vni_id,
            interface=interface_obj,
            vni_type=vni_type,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support VNIs. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        vni.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                vni.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete VNI: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # Resolve the mapped VLAN or VRF objects when requested.
    vlan_obj = None
    if vlan is not None:
        try:
            vlan_obj = session.api.get_module(session, "Vlan", vlan)
            vlan_obj.get()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not find VLAN {0}: {1}".format(vlan, str(e))
            )

    vrf_obj = None
    if vrf is not None:
        try:
            vrf_obj = session.api.get_module(session, "Vrf", vrf)
            vrf_obj.get()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not find VRF {0}: {1}".format(vrf, str(e))
            )

    # ------------------------------------------------------- create / update
    changed = False
    if not exists:
        kwargs = {}
        if vlan_obj is not None:
            kwargs["vlan"] = vlan_obj
        if vrf_obj is not None:
            kwargs["vrf"] = vrf_obj
        if routing is not None:
            kwargs["routing"] = routing
        vni = session.api.get_module(
            session,
            "Vni",
            vni_id,
            interface=interface_obj,
            vni_type=vni_type,
            **kwargs
        )
        changed = True
        if not ansible_module.check_mode:
            try:
                vni.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create VNI: {0}".format(str(e))
                )
    else:
        if vlan_obj is not None:
            current_vlan = getattr(vni, "vlan", None)
            current_vlan_id = getattr(current_vlan, "id", None)
            if current_vlan_id != vlan:
                changed = True
                vni.vlan = vlan_obj

        if vrf_obj is not None:
            current_vrf = getattr(vni, "vrf", None)
            current_vrf_name = getattr(current_vrf, "name", None)
            if current_vrf_name != vrf:
                changed = True
                vni.vrf = vrf_obj

        if routing is not None:
            if bool(getattr(vni, "routing", False)) != routing:
                changed = True
                vni.routing = routing

        if changed and not ansible_module.check_mode:
            try:
                vni.update()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not update VNI: {0}".format(str(e))
                )

    if vtep_peers is not None:
        peers_changed = reconcile_vtep_peers(
            ansible_module,
            session,
            interface_obj,
            vni,
            vtep_peers,
            vtep_peer_vrf,
        )
        changed = changed or peers_changed

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
