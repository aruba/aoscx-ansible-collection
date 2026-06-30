#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_mirror
version_added: "4.6.0"
short_description: Create, update or delete a mirror session on AOS-CX
description: >
  This module provides configuration management of traffic mirror (port
  monitoring) sessions on AOS-CX devices. A mirror session copies traffic
  from one or more source ports or VLANs to a destination (output) port.
author: Aruba Networks (@ArubaNetworks)
options:
  mirror_id:
    description: >
      Numeric identifier of the mirror session. This is the index of the
      resource under system/mirrors.
    required: true
    type: int
  session_type:
    description: >
      Type of the mirror session.
    required: false
    choices:
      - none
      - port
      - cpu
      - tunnel
    type: str
  active:
    description: >
      Whether the mirror session is active. An inactive session is configured
      but does not mirror any traffic.
    required: false
    type: bool
  comment:
    description: A descriptive comment for the mirror session.
    required: false
    type: str
  output_port:
    description: >
      List of destination port names that receive the mirrored traffic. The
      ports must already exist on the device.
    required: false
    type: list
    elements: str
  select_src_port:
    description: >
      List of port names whose ingress (received) traffic is mirrored. The
      ports must already exist on the device.
    required: false
    type: list
    elements: str
  select_dst_port:
    description: >
      List of port names whose egress (transmitted) traffic is mirrored. The
      ports must already exist on the device.
    required: false
    type: list
    elements: str
  select_rx_vlan:
    description: >
      List of VLAN ids whose ingress (received) traffic is mirrored. The
      VLANs must already exist on the device.
    required: false
    type: list
    elements: int
  select_tx_vlan:
    description: >
      List of VLAN ids whose egress (transmitted) traffic is mirrored. The
      VLANs must already exist on the device.
    required: false
    type: list
    elements: int
  tunnel_vrf:
    description: >
      Name of the VRF used to reach the tunnel destination IP address. Only
      considered when I(session_type=tunnel). The VRF must already exist. If
      not specified, the 'default' VRF is used.
    required: false
    type: str
  tunnel:
    description: >
      Tunnel parameters for an ERSPAN (encapsulated remote) mirror session.
      Only considered when I(session_type=tunnel).
    required: false
    type: dict
    suboptions:
      src_ip_address:
        description: Source IPv4 address of the tunnel.
        required: false
        type: str
      dest_ip_address:
        description: Destination IPv4 address of the tunnel.
        required: false
        type: str
      dscp:
        description: DSCP value to mark on the tunneled packets (0-63).
        required: false
        type: int
  state:
    description: Create, update or delete the mirror session.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a port mirror session, source 1/1/1 RX, destination 1/1/10
  aoscx_mirror:
    mirror_id: 5
    session_type: port
    active: true
    comment: span-to-analyzer
    select_src_port:
      - 1/1/1
    output_port:
      - 1/1/10

- name: Add a VLAN to the mirrored receive set
  aoscx_mirror:
    mirror_id: 5
    state: update
    select_rx_vlan:
      - 10
      - 20

- name: Deactivate a mirror session
  aoscx_mirror:
    mirror_id: 5
    state: update
    active: false

- name: Delete a mirror session
  aoscx_mirror:
    mirror_id: 5
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        mirror_id=dict(type="int", required=True),
        session_type=dict(
            type="str",
            required=False,
            choices=["none", "port", "cpu", "tunnel"],
        ),
        active=dict(type="bool", required=False, default=None),
        comment=dict(type="str", required=False, default=None),
        output_port=dict(
            type="list", elements="str", required=False, default=None
        ),
        select_src_port=dict(
            type="list", elements="str", required=False, default=None
        ),
        select_dst_port=dict(
            type="list", elements="str", required=False, default=None
        ),
        select_rx_vlan=dict(
            type="list", elements="int", required=False, default=None
        ),
        select_tx_vlan=dict(
            type="list", elements="int", required=False, default=None
        ),
        tunnel_vrf=dict(type="str", required=False, default=None),
        tunnel=dict(
            type="dict",
            required=False,
            default=None,
            options=dict(
                src_ip_address=dict(
                    type="str", required=False, default=None
                ),
                dest_ip_address=dict(
                    type="str", required=False, default=None
                ),
                dscp=dict(type="int", required=False, default=None),
            ),
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    mirror_id = ansible_module.params["mirror_id"]
    session_type = ansible_module.params["session_type"]
    active = ansible_module.params["active"]
    comment = ansible_module.params["comment"]
    output_port = ansible_module.params["output_port"]
    select_src_port = ansible_module.params["select_src_port"]
    select_dst_port = ansible_module.params["select_dst_port"]
    select_rx_vlan = ansible_module.params["select_rx_vlan"]
    select_tx_vlan = ansible_module.params["select_tx_vlan"]
    tunnel_vrf = ansible_module.params["tunnel_vrf"]
    tunnel = ansible_module.params["tunnel"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    if mirror_id < 1:
        ansible_module.fail_json(msg="mirror_id must be a positive integer.")

    port_params = {
        "output_port": output_port,
        "select_src_port": select_src_port,
        "select_dst_port": select_dst_port,
    }
    vlan_params = {
        "select_rx_vlan": select_rx_vlan,
        "select_tx_vlan": select_tx_vlan,
    }

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        mirror = session.api.get_module(session, "Mirror", mirror_id)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support mirroring. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        mirror.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                mirror.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete mirror session: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    def materialize_ports(names):
        return [session.api.get_module(session, "Interface", n) for n in names]

    def materialize_vlans(ids):
        return [session.api.get_module(session, "Vlan", v) for v in ids]

    def materialize_vrf(vrf_name):
        return session.api.get_module(session, "Vrf", vrf_name)

    def vrf_name_of(ref):
        if not ref:
            return None
        if isinstance(ref, str):
            return ref.rstrip("/").split("/")[-1]
        if isinstance(ref, dict):
            return next(iter(ref), None)
        return getattr(ref, "name", None)

    def clean_tunnel(value):
        return {k: v for k, v in value.items() if v is not None}

    # ------------------------------------------------------- create / update
    if not exists:
        kwargs = {}
        if session_type is not None:
            kwargs["session_type"] = session_type
        if active is not None:
            kwargs["active"] = active
        if comment is not None:
            kwargs["comment"] = comment
        for attr, names in port_params.items():
            if names is not None:
                kwargs[attr] = materialize_ports(names)
        for attr, ids in vlan_params.items():
            if ids is not None:
                kwargs[attr] = materialize_vlans(ids)
        if tunnel is not None:
            kwargs["tunnel"] = clean_tunnel(tunnel)
        if tunnel_vrf is not None:
            kwargs["tunnel_vrf"] = materialize_vrf(tunnel_vrf).get_uri()
        mirror = session.api.get_module(session, "Mirror", mirror_id, **kwargs)
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                mirror.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create mirror session: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False

    if session_type is not None and (
        getattr(mirror, "session_type", None) != session_type
    ):
        changed = True
        mirror.session_type = session_type

    if active is not None and getattr(mirror, "active", None) != active:
        changed = True
        mirror.active = active

    if comment is not None and getattr(mirror, "comment", None) != comment:
        changed = True
        mirror.comment = comment

    # Port references are unordered; compare them by name regardless of order.
    for attr, names in port_params.items():
        if names is None:
            continue
        current = sorted(p.name for p in (getattr(mirror, attr, None) or []))
        if current != sorted(names):
            changed = True
            setattr(mirror, attr, materialize_ports(names))

    # VLAN references are unordered; compare them by id regardless of order.
    for attr, ids in vlan_params.items():
        if ids is None:
            continue
        current = sorted(
            int(v.id) for v in (getattr(mirror, attr, None) or [])
        )
        if current != sorted(int(i) for i in ids):
            changed = True
            setattr(mirror, attr, materialize_vlans(ids))

    if tunnel is not None:
        want = clean_tunnel(tunnel)
        current_tunnel = getattr(mirror, "tunnel", None) or {}
        if any(current_tunnel.get(k) != v for k, v in want.items()):
            changed = True
            merged = dict(current_tunnel)
            merged.update(want)
            mirror.tunnel = merged

    if tunnel_vrf is not None:
        if vrf_name_of(getattr(mirror, "tunnel_vrf", None)) != tunnel_vrf:
            changed = True
            mirror.tunnel_vrf = materialize_vrf(tunnel_vrf).get_uri()

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            mirror.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update mirror session: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
