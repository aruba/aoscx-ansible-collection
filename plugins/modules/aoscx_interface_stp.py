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
module: aoscx_interface_stp
version_added: "4.6.0"
short_description: Configure per-interface spanning-tree settings.
description:
  - This module configures spanning-tree (STP) settings on an AOS-CX
    interface.
author: Aruba Networks (@ArubaNetworks)
options:
  interface:
    description: Name of the interface to configure.
    required: true
    type: str
  admin_edge:
    description: Configure the interface as an administrative edge port.
    required: false
    type: bool
  bpdu_filter:
    description: Enable BPDU filtering on the interface.
    required: false
    type: bool
  bpdu_guard:
    description: Enable BPDU guard on the interface.
    required: false
    type: bool
  root_guard:
    description: Enable root guard on the interface.
    required: false
    type: bool
  loop_guard:
    description: Enable loop guard on the interface.
    required: false
    type: bool
  link_type:
    description: Spanning-tree link type.
    required: false
    type: str
    choices:
      - point_to_point
      - shared
      - auto
  admin_path_cost:
    description: Administrative path cost.
    required: false
    type: int
  port_priority:
    description: Port priority.
    required: false
    type: int
  bpdus_rx_disable:
    description: Disable reception of BPDUs.
    required: false
    type: bool
  bpdus_tx_disable:
    description: Disable transmission of BPDUs.
    required: false
    type: bool
  state:
    description: Configure or reset the spanning-tree settings.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Configure an admin-edge port with BPDU filter
  arubanetworks.aoscx.aoscx_interface_stp:
    interface: 1/1/5
    admin_edge: true
    bpdu_filter: true
    state: create

- name: Reset spanning-tree settings
  arubanetworks.aoscx.aoscx_interface_stp:
    interface: 1/1/5
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )

KEY_MAP = {
    "admin_edge": "admin_edge_port_enable",
    "bpdu_filter": "bpdu_filter_enable",
    "bpdu_guard": "bpdu_guard_enable",
    "root_guard": "root_guard_enable",
    "loop_guard": "loop_guard_enable",
    "link_type": "link_type",
    "admin_path_cost": "admin_path_cost",
    "port_priority": "port_priority",
    "bpdus_rx_disable": "bpdus_rx_disable",
    "bpdus_tx_disable": "bpdus_tx_disable",
}


def main():
    module_args = dict(
        interface=dict(type="str", required=True),
        admin_edge=dict(type="bool", default=None),
        bpdu_filter=dict(type="bool", default=None),
        bpdu_guard=dict(type="bool", default=None),
        root_guard=dict(type="bool", default=None),
        loop_guard=dict(type="bool", default=None),
        link_type=dict(
            type="str", default=None,
            choices=["point_to_point", "shared", "auto"],
        ),
        admin_path_cost=dict(type="int", default=None),
        port_priority=dict(type="int", default=None),
        bpdus_rx_disable=dict(type="bool", default=None),
        bpdus_tx_disable=dict(type="bool", default=None),
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

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    name = ansible_module.params["interface"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    session = get_pyaoscx_session(ansible_module)
    device = Device(session)
    interface = device.interface(name)

    supplied = {
        KEY_MAP[k]: ansible_module.params[k]
        for k in KEY_MAP
        if ansible_module.params[k] is not None
    }

    current = getattr(interface, "stp_config", None)
    if not isinstance(current, dict):
        current = {}

    if state == "delete":
        defaults = {
            "admin_edge_port_enable": False,
            "bpdu_filter_enable": False,
            "bpdu_guard_enable": False,
            "root_guard_enable": False,
            "loop_guard_enable": False,
            "link_type": "auto",
            "port_priority": 128,
            "bpdus_rx_disable": False,
            "bpdus_tx_disable": False,
        }
        new_config = dict(current)
        new_config.update(defaults)
        new_config.pop("admin_path_cost", None)
    else:
        new_config = dict(current)
        new_config.update(supplied)

    changed = new_config != current
    if changed:
        interface.stp_config = new_config
        if "stp_config" not in interface.config_attrs:
            interface.config_attrs.append("stp_config")
        if not ansible_module.check_mode:
            interface.apply()

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
