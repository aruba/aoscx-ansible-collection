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
module: aoscx_port_security
version_added: "5.0.0"
short_description: Manage the global port security settings on AOS-CX.
description: >
  This module manages the global port access port security settings on AOS-CX
  devices. Per-port port security is managed with the aoscx_l2_interface
  module.
author: Aruba Networks (@ArubaNetworks)
options:
  enable:
    description: >
      Globally enable port access port security on the device (the
      C(port-access port-security enable) command).
    type: bool
    required: false
  trap_disable:
    description: Disable the port security SNMP traps.
    type: bool
    required: false
"""

EXAMPLES = """
- name: Enable port access port security globally
  aoscx_port_security:
    enable: true

- name: Disable port access port security globally
  aoscx_port_security:
    enable: false
"""

RETURN = r""" # """

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SETTINGS = {
    "enable": "port_security_enable",
    "trap_disable": "port_security_trap_disable",
}


def main():
    module_args = {
        param: dict(type="bool", required=False) for param in SETTINGS
    }

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

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

    response = session.request(
        "GET", "system", params={"selector": "writable", "depth": 2}
    )
    system_doc = json.loads(response.text)

    if any(system_doc.get(k) != v for k, v in supplied.items()):
        system_doc.update(supplied)
        put = session.request("PUT", "system", data=json.dumps(system_doc))
        if not 200 <= put.status_code < 300:
            ansible_module.fail_json(
                msg="Could not update port security settings: {0}".format(
                    put.text
                )
            )
        result["changed"] = True

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
