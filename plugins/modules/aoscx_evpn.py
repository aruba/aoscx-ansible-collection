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
        mac_move_count=dict(type="int", default=None),
        mac_move_timer=dict(type="int", default=None),
        redistribute=dict(type="dict", default=None),
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
    mac_move_count = ansible_module.params["mac_move_count"]
    mac_move_timer = ansible_module.params["mac_move_timer"]
    redistribute = ansible_module.params["redistribute"]

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
        "mac_move_count": mac_move_count,
        "mac_move_timer": mac_move_timer,
    }
    for attr, value in scalars.items():
        if value is None:
            continue
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
