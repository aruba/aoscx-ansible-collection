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
module: aoscx_snmp_trap
version_added: "4.6.0"
short_description: Create or delete an SNMP trap receiver
description: >
  This module provides configuration management of SNMP trap receivers on
  AOS-CX devices (system/snmp_traps). Trap receivers are identified by a
  compound index and are create/delete only. Requires REST API v10.16
  (set ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
options:
  vrf:
    description: Name of the VRF used to reach the receiver.
    required: false
    type: str
    default: default
  receiver_address:
    description: IP address of the trap receiver.
    required: true
    type: str
  receiver_udp_port:
    description: UDP port of the trap receiver.
    required: false
    type: int
    default: 162
  type:
    description: Notification delivery type.
    required: false
    type: str
    choices:
      - trap
      - inform
    default: trap
  version:
    description: SNMP version used for the receiver.
    required: false
    type: str
    choices:
      - v1
      - v2c
      - v3
    default: v2c
  community_name:
    description: SNMP community name for v1/v2c receivers.
    required: false
    type: str
  state:
    description: Create or delete the SNMP trap receiver.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an SNMP v2c trap receiver
  aoscx_snmp_trap:
    receiver_address: 198.51.100.5
    receiver_udp_port: 162
    type: trap
    version: v2c
    community_name: public

- name: Delete an SNMP trap receiver
  aoscx_snmp_trap:
    receiver_address: 198.51.100.5
    type: trap
    version: v2c
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.snmp_trap import SnmpTrap
    from pyaoscx.vrf import Vrf

    HAS_PYAOSCX_SNMP = True
except ImportError:
    HAS_PYAOSCX_SNMP = False

if HAS_PYAOSCX_SNMP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        vrf=dict(type="str", required=False, default="default"),
        receiver_address=dict(type="str", required=True),
        receiver_udp_port=dict(type="int", required=False, default=162),
        type=dict(
            type="str",
            required=False,
            choices=["trap", "inform"],
            default="trap",
        ),
        version=dict(
            type="str",
            required=False,
            choices=["v1", "v2c", "v3"],
            default="v2c",
        ),
        community_name=dict(type="str", required=False),
        state=dict(
            type="str",
            default="create",
            choices=["create", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_SNMP:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support SNMP. Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    params = ansible_module.params
    state = params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    vrf = Vrf(session, params["vrf"])
    try:
        vrf.get()
    except Exception:
        ansible_module.fail_json(
            msg="VRF {0} doesn't exist.".format(params["vrf"])
        )

    kwargs = {}
    if params["community_name"] is not None:
        kwargs["community_name"] = params["community_name"]

    trap = SnmpTrap(
        session,
        vrf,
        params["receiver_address"],
        params["receiver_udp_port"],
        params["type"],
        params["version"],
        **kwargs
    )

    try:
        trap.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            trap.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    if not exists:
        trap.create()
        result["changed"] = True

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
