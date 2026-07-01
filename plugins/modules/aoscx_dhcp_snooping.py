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
module: aoscx_dhcp_snooping
version_added: "5.0.0"
short_description: Manage the global DHCPv4 snooping settings on AOS-CX.
description: >
  This module manages the global DHCPv4 snooping configuration
  (system/dhcpv4_snooping_general_configuration) on AOS-CX devices. Per-VLAN
  snooping is managed with the aoscx_vlan module and per-port trust with the
  aoscx_interface module.
author: Aruba Networks (@ArubaNetworks)
options:
  enable:
    description: >
      Globally enable DHCPv4 snooping on the device (the C(dhcpv4-snooping)
      command).
    type: bool
    required: false
  allow_overwrite_binding:
    description: Allow a binding to be overwritten by a new one.
    type: bool
    required: false
  disable_mac_verification:
    description: >
      Disable the verification of the source MAC address against the DHCP
      client hardware address.
    type: bool
    required: false
  enable_client_attribute_caching:
    description: Enable caching of the DHCP client attributes.
    type: bool
    required: false
  enable_client_event_log:
    description: >
      Enable the DHCPv4 snooping client event log (the
      C(dhcpv4-snooping event-log client) command).
    type: bool
    required: false
  vxlan_trusted:
    description: Treat VXLAN tunnels as trusted for DHCPv4 snooping.
    type: bool
    required: false
"""

EXAMPLES = """
- name: Enable DHCPv4 snooping globally with the client event log
  aoscx_dhcp_snooping:
    enable: true
    enable_client_event_log: true

- name: Disable DHCPv4 snooping globally
  aoscx_dhcp_snooping:
    enable: false
"""

RETURN = r""" # """

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

GENERAL_CONFIG_KEY = "dhcpv4_snooping_general_configuration"

SETTINGS = (
    "enable",
    "allow_overwrite_binding",
    "disable_mac_verification",
    "enable_client_attribute_caching",
    "enable_client_event_log",
    "vxlan_trusted",
)


def main():
    module_args = {
        setting: dict(type="bool", required=False) for setting in SETTINGS
    }

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    supplied = {
        setting: ansible_module.params[setting]
        for setting in SETTINGS
        if ansible_module.params[setting] is not None
    }
    if not supplied:
        ansible_module.exit_json(**result)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    response = session.request(
        "GET", "system", params={"selector": "writable", "depth": 2}
    )
    system_doc = json.loads(response.text)
    general_config = dict(system_doc.get(GENERAL_CONFIG_KEY) or {})

    if any(general_config.get(k) != v for k, v in supplied.items()):
        general_config.update(supplied)
        system_doc[GENERAL_CONFIG_KEY] = general_config
        put = session.request("PUT", "system", data=json.dumps(system_doc))
        if not 200 <= put.status_code < 300:
            ansible_module.fail_json(
                msg="Could not update DHCPv4 snooping settings: {0}".format(
                    put.text
                )
            )
        result["changed"] = True

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
