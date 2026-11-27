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
module: aoscx_evpn
version_added: "4.6.0"
short_description: Manage the global EVPN configuration on AOS-CX
description: >
  This module provides configuration management of the global EVPN
  (Ethernet VPN) settings on AOS-CX devices. EVPN is a singleton resource,
  so this module only updates the existing configuration; it never creates
  or deletes the resource. Only the parameters you supply are reconciled;
  any parameter left unset is preserved.
author: Aruba Networks (@ArubaNetworks)
options:
  arp_suppression_enable:
    description: >
      Whether ARP suppression is globally enabled. When omitted it is left
      unchanged.
    required: false
    type: bool
  nd_suppression_enable:
    description: >
      Whether Neighbor Discovery (ND) suppression is globally enabled. When
      omitted it is left unchanged.
    required: false
    type: bool
  arp_suppression_extended_enable:
    description: >
      Whether ARP suppression extended is globally enabled (CLI
      C(arp-suppression-extended)). It suppresses ARP requests on L2 VLANs as
      well as on active gateway SVIs, and cannot be enabled together with
      I(arp_suppression_enable): to migrate, disable the latter in the same
      task. A VLAN can override it, see
      M(arubanetworks.aoscx.aoscx_evpn_vlan). When omitted it is left
      unchanged. Requires a pyaoscx version providing C(Evpn.check_suppression()).
    required: false
    type: bool
  nd_suppression_extended_enable:
    description: >
      Whether ND suppression extended is globally enabled (CLI
      C(nd-suppression-extended)). Same behavior as
      I(arp_suppression_extended_enable), and cannot be enabled together with
      I(nd_suppression_enable). When omitted it is left unchanged.
    required: false
    type: bool
  mac_move_count:
    description: >
      Maximum number of MAC moves allowed within the MAC move interval
      before the MAC address is frozen. When omitted it is left unchanged.
    required: false
    type: int
  mac_move_timer:
    description: >
      Length of the MAC move detection interval, in seconds. When omitted it
      is left unchanged.
    required: false
    type: int
  redistribute:
    description: >
      Dictionary controlling which local address types are redistributed
      into EVPN, for example C({"local-mac": true, "local-svi": false}).
      Only the keys you provide are reconciled; other keys are preserved.
      When omitted it is left unchanged.
    required: false
    type: dict
  dyn_vxlan_tunnel_bridging_mode:
    description: >
      Bridging mode between dynamic (EVPN) VXLAN tunnels. C(ibgp-ebgp)
      (CLI C(dyn-vxlan-tunnel-bridging-mode ibgp-ebgp)) puts the iBGP and
      eBGP tunnels in different broadcast groups and permits bridging
      between them, for example between two fabrics interconnected by
      border leaves. C(no-bridging) (default of the switch, CLI
      C(no dyn-vxlan-tunnel-bridging-mode ibgp-ebgp)) puts all EVPN tunnels
      in the same broadcast group. The module fails if the switch platform
      or firmware does not support it. When omitted it is left unchanged.
    required: false
    type: str
    choices:
      - no-bridging
      - ibgp-ebgp
  state:
    description: >
      Use C(create) or C(update) to apply the configuration. Both behave
      the same because EVPN is a singleton that always exists.
    required: false
    default: update
    choices:
      - create
      - update
    type: str
"""

EXAMPLES = """
- name: Enable ARP and ND suppression globally
  aoscx_evpn:
    arp_suppression_enable: true
    nd_suppression_enable: true

- name: Tune the MAC move detection
  aoscx_evpn:
    mac_move_count: 5
    mac_move_timer: 180

- name: Configure EVPN redistribution
  aoscx_evpn:
    redistribute:
      local-mac: true
      local-svi: true

- name: Permit bridging between iBGP and eBGP EVPN tunnels on a border leaf
  aoscx_evpn:
    dyn_vxlan_tunnel_bridging_mode: ibgp-ebgp

- name: Put back all EVPN tunnels in the same broadcast group (default)
  aoscx_evpn:
    dyn_vxlan_tunnel_bridging_mode: no-bridging

- name: Migrate the global ARP and ND suppression to the extended versions
  aoscx_evpn:
    arp_suppression_enable: false
    arp_suppression_extended_enable: true
    nd_suppression_enable: false
    nd_suppression_extended_enable: true
"""

RETURN = r"""
changed:
  description: Whether the global EVPN configuration was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        arp_suppression_enable=dict(type="bool", default=None),
        nd_suppression_enable=dict(type="bool", default=None),
        arp_suppression_extended_enable=dict(type="bool", default=None),
        nd_suppression_extended_enable=dict(type="bool", default=None),
        mac_move_count=dict(type="int", default=None),
        mac_move_timer=dict(type="int", default=None),
        redistribute=dict(type="dict", default=None),
        dyn_vxlan_tunnel_bridging_mode=dict(
            type="str",
            default=None,
            choices=["no-bridging", "ibgp-ebgp"],
        ),
        state=dict(
            type="str",
            default="update",
            choices=["create", "update"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    arp_suppression_enable = ansible_module.params["arp_suppression_enable"]
    nd_suppression_enable = ansible_module.params["nd_suppression_enable"]
    arp_suppression_extended_enable = ansible_module.params[
        "arp_suppression_extended_enable"
    ]
    nd_suppression_extended_enable = ansible_module.params[
        "nd_suppression_extended_enable"
    ]
    mac_move_count = ansible_module.params["mac_move_count"]
    mac_move_timer = ansible_module.params["mac_move_timer"]
    redistribute = ansible_module.params["redistribute"]
    bridging_mode = ansible_module.params["dyn_vxlan_tunnel_bridging_mode"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        evpn = session.api.get_module(session, "Evpn")
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support EVPN. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        evpn.get(selector="writable")
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not retrieve EVPN configuration: {0}".format(str(e))
        )

    changed = False

    # Simple scalar attributes: reconcile each supplied value.
    scalars = {
        "arp_suppression_enable": arp_suppression_enable,
        "nd_suppression_enable": nd_suppression_enable,
        "arp_suppression_extended_enable": arp_suppression_extended_enable,
        "nd_suppression_extended_enable": nd_suppression_extended_enable,
        "mac_move_count": mac_move_count,
        "mac_move_timer": mac_move_timer,
    }
    for attr, value in scalars.items():
        if value is None:
            continue
        if attr.endswith("_extended_enable") and attr not in evpn.config_attrs:
            ansible_module.fail_json(
                msg="{0} is not supported by the firmware of the "
                "switch.".format(attr)
            )
        if getattr(evpn, attr, None) != value:
            changed = True
            setattr(evpn, attr, value)

    # redistribute is a dictionary; only reconcile the keys provided and
    # preserve any existing keys the user did not mention.
    if redistribute is not None:
        current = dict(getattr(evpn, "redistribute", None) or {})
        merged = dict(current)
        merged.update(redistribute)
        if merged != current:
            changed = True
            evpn.redistribute = merged

    if bridging_mode is not None and (
        getattr(evpn, "dyn_vxlan_tunnel_bridging_mode", None) != bridging_mode
    ):
        if not hasattr(evpn, "set_dyn_vxlan_tunnel_bridging_mode"):
            ansible_module.fail_json(
                msg=(
                    "This pyaoscx version does not support "
                    "dyn_vxlan_tunnel_bridging_mode. Upgrade pyaoscx."
                )
            )
        changed = True
        evpn.set_dyn_vxlan_tunnel_bridging_mode(bridging_mode)

    if changed:
        extended_requested = (
            arp_suppression_extended_enable is not None
            or nd_suppression_extended_enable is not None
        )
        if hasattr(evpn, "check_suppression"):
            # A dry run must refuse what the real run would refuse
            try:
                evpn.check_suppression()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Invalid suppression configuration: {0}".format(str(e))
                )
        elif extended_requested:
            ansible_module.fail_json(
                msg=(
                    "The extended suppression options require a pyaoscx "
                    "version providing Evpn.check_suppression(). Upgrade "
                    "pyaoscx."
                )
            )

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            evpn.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update EVPN configuration: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
