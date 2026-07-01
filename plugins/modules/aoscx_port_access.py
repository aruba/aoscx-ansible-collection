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
module: aoscx_port_access
version_added: "5.0.0"
short_description: Manage the global port access settings on AOS-CX.
description: >
  This module manages the global (system level) port access settings on
  AOS-CX devices, including port security. Per-port and per-role port access
  configuration is managed with other modules (aoscx_l2_interface,
  aoscx_port_access_role, and so on).
author: Aruba Networks (@ArubaNetworks)
options:
  port_security_enable:
    description: >
      Globally enable port access port security (the
      C(port-access port-security enable) command).
    type: bool
    required: false
  port_security_trap_disable:
    description: Disable the port security SNMP traps.
    type: bool
    required: false
  client_move_secure:
    description: Enable secure client move for port access.
    type: bool
    required: false
  client_moves_disable:
    description: Disable client moves for port access.
    type: bool
    required: false
  event_log_client:
    description: Enable the port access client event log.
    type: bool
    required: false
  gbp_reflexive:
    description: Enable the port access group-based policy reflexive rules.
    type: bool
    required: false
  policy_reflexive:
    description: Enable the port access policy reflexive rules.
    type: bool
    required: false
"""

EXAMPLES = """
- name: Enable port access port security globally
  aoscx_port_access:
    port_security_enable: true

- name: Enable the client event log and secure client move
  aoscx_port_access:
    event_log_client: true
    client_move_secure: true
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

try:
    from pyaoscx.device import Device

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

SETTINGS = {
    "port_security_enable": "port_security_enable",
    "port_security_trap_disable": "port_security_trap_disable",
    "client_move_secure": "port_access_client_move_secure_enable",
    "client_moves_disable": "port_access_client_moves_disable",
    "event_log_client": "port_access_event_log_client_enable",
    "gbp_reflexive": "port_access_gbp_reflexive_enable",
    "policy_reflexive": "port_access_policy_reflexive_enable",
}


def main():
    module_args = {
        param: dict(type="bool", required=False) for param in SETTINGS
    }

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    supplied = {
        attr: ansible_module.params[param]
        for param, attr in SETTINGS.items()
        if ansible_module.params[param] is not None
    }
    if not supplied:
        ansible_module.exit_json(**result)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    device = Device(session)
    device.get(selector="writable")

    for attr, value in supplied.items():
        setattr(device, attr, value)

    result["changed"] = device.update()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
