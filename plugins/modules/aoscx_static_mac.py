#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_static_mac
version_added: "4.1.0"
short_description: Create, Update, or Delete Static MACs on AOS-CX devices.
description: >
  This module provides configuration management of Static MACs on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  vlan:
    description: Vlan to which the Static MAC belongs.
    type: int
    required: true
  mac_addr:
    description: Hexadecimal address of the Static MAC.
    type: str
    required: true
  port:
    description: Port or Interface to which the Static MAC is attached to.
    type: str
    required: true
  state:
    description: Create, update, or delete the Static MAC.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
---
- name: Create Static MAC
  aoscx_static_mac:
    vlan: 23
    mac_addr: aa:bb:cc:dd:ee:ff
    port: 1/1/12

- name: Update Port in Static MAC
  aoscx_static_mac:
    vlan: 23
    mac_addr: aa:bb:cc:dd:ee:ff
    port: 1/1/2
    state: update

- name: Delete Static MAC
  aoscx_static_mac:
    vlan: 23
    mac_addr: aa:bb:cc:dd:ee:ff
    port: 1/1/2
    state: delete
"""

RETURN = r""" # """


from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.static_mac import StaticMac
    from pyaoscx.vlan import Vlan

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "vlan": {
            "type": "int",
            "required": True,
        },
        "mac_addr": {
            "type": "str",
            "required": True,
        },
        "port": {
            "type": "str",
            "required": True,
        },
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
    }

    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(), supports_check_mode=True
    )

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    result = {"changed": False}

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    # Get playbook's arguments
    vlan = ansible_module.params["vlan"]
    interface = ansible_module.params["port"]
    mac_addr = ansible_module.params["mac_addr"]
    state = ansible_module.params["state"]

    session = get_pyaoscx_session(ansible_module)

    vlan = Vlan(session, vlan)

    try:
        vlan.get()
    except Exception:
        ansible_module.fail_json(msg="VLAN {0} doesn't exist.".format(vlan))

    static_mac = StaticMac(session, mac_addr, vlan, port=interface)

    try:
        static_mac.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            static_mac.delete()
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        static_mac.create()
        result["changed"] = True
        ansible_module.exit_json(**result)

    present_port = None
    if hasattr(static_mac, "port"):
        present_port = static_mac.port
    if present_port != interface:
        result["changed"] = True
        static_mac.port = interface
    if result["changed"]:
        static_mac.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
