#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2023 Hewlett Packard Enterprise Development LP.
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
module: aoscx_poe
version_added: "4.0.0"
short_description: >
  Manages the configuration of an Interface's Power over Ethernet.
description: >
  This module manages the Power over Ethernet configuration onto a selected
  interface.
author: Aruba Networks (@ArubaNetworks)
options:
  state:
    description: Create, update or delete the Interface's PoE configuration.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
  interface:
    description: The name of an interface available inside a switch
    type: str
    required: true
  enable:
    description: >
      Configurable flag to control PoE power delivery on this Interface. A
      value of true would enable PoE power delivery on this Interface. By
      default, the flag is set to false for all PoE capable Interfaces.
    type: bool
    required: false
  priority:
    description: >
      Power priority level for the PoE Interface. The choices are 'low',
      'high', and 'critical'.
    choices:
      - low
      - high
      - critical
    type: str
    required: false
  allocate_by_method:
    description: >
      Configure the power allocation method for the PoE Interface.
      The choices are 'usage' and 'class'.
    choices:
      - usage
      - class
    type: str
    required: false
  assigned_class:
    description: >
      Assigned class (power limit) for the PoE Interface.
      The choices are 3, 4, 6 and 8.
    choices:
      - 3
      - 4
      - 6
      - 8
    type: int
    required: false
  pd_class_override:
    description: Enable PD requested class override by user assigned class.
    type: bool
    required: false
  pre_standard_detect:
    description: Enable detection of pre-standard PoE devices.
    type: bool
    required: false
"""

EXAMPLES = """
- name: Configure Power over Ethernet on Interface 1/1/5
  aoscx_poe:
    interface: 1/1/5
    enable: true
    priority: high

- name: Enable Power Over Ethernet on Interface 1/1/10
  aoscx_poe:
    interface: 1/1/10
    enable: true

- name: Disable Power Over Ethernet on Interface 1/1/10
  aoscx_poe:
    interface: 1/1/10
    enable: false

- name: Set Power Criticality level over Ethernet on Interface 1/1/7
  aoscx_poe:
    interface: 1/1/7
    priority: low

- name: Set class for Power over Ethernet on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    assigned_class: 3

- name: Set allocate method for Power over Ethernet on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    allocate_by_method: class

- name: Enable PD requested class override on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    pd_class_override: true

- name: Enable detection of pre-standard on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    pre_standard_detect: true

- name: Delete parameter selected on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    allocate_by_method: class
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


def get_argument_spec():
    argument_spec = {
        "state": {
            "type": "str",
            "default": "create",
            "choices": ["create", "delete", "update"],
        },
        "interface": {"type": "str", "required": True},
        "enable": {"type": "bool", "required": False, "default": None},
        "priority": {
            "type": "str",
            "required": False,
            "choices": ["low", "high", "critical"],
        },
        "allocate_by_method": {
            "type": "str",
            "required": False,
            "choices": ["usage", "class"],
        },
        "assigned_class": {
            "type": "int",
            "required": False,
            "choices": [3, 4, 6, 8],
        },
        "pd_class_override": {
            "type": "bool",
            "required": False,
        },
        "pre_standard_detect": {
            "type": "bool",
            "required": False,
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
    )

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    # Get Ansible module's parameters
    interface = ansible_module.params["interface"]
    enable = ansible_module.params["enable"]
    priority = ansible_module.params["priority"]
    class_number = ansible_module.params["assigned_class"]
    a_class = "class{0}".format(class_number)
    method = ansible_module.params["allocate_by_method"]
    pd_class_override = ansible_module.params["pd_class_override"]
    pre_standard_detect = ansible_module.params["pre_standard_detect"]
    state = ansible_module.params["state"]

    session = get_pyaoscx_session(ansible_module)
    device = Device(session)
    poe_interface = device.poe_interface(interface)
    firmware = device.get_firmware_version()
    platform = firmware.split(".")[0]

    try:
        poe_interface.get()
    except Exception:
        ansible_module.fail_json(
            msg="PoE not supported by interface {0}".format(interface)
        )

    if pd_class_override and method == "usage":
        ansible_module.fail_json(
            msg="The power allocation method cannot be 'usage' when "
            "pd-class-override is enabled."
        )

    if poe_interface.pd_class_override and method == "usage":
        ansible_module.fail_json(
            msg="The power allocation method cannot be changed when "
            "pd-class-override is enabled."
        )

    if state == "delete":
        if priority and poe_interface.priority != "low":
            result["changed"] = True
            poe_interface.priority = "low"
        if method and poe_interface.allocate_by_method != "usage":
            result["changed"] = True
            poe_interface.allocate_by_method = "usage"
        if class_number:
            if platform == "RL" or platform == "FL":
                warning = (
                    "Currently there are limitations to delete the "
                    "assigned_class on platforms RL and FL. "
                    "The recommendation is to use a workaround explained on "
                    "the documentation of the Config Ansible module. "
                )
                if "warnings" in result:
                    result["warnings"].append(warning)
                else:
                    result["warnings"] = [warning]
            # CR 249060 does not allow deleting platforms RL and FL.
            # After this issue is solved, remove this comment, remove the
            # warning above and uncomment the funcionality below.

            # if platform == "RL" and poe_interface.assigned_class != "class8":
            #     result["changed"] = True
            #     poe_interface.assigned_class = "class8"
            # elif platform == "FL" and poe_interface.assigned_class != "class6":
            #     result["changed"] = True
            #     poe_interface.assigned_class = "class6"
            elif poe_interface.assigned_class != "class4":
                result["changed"] = True
                poe_interface.assigned_class = "class4"
        if pd_class_override is not None and poe_interface.pd_class_override:
            result["changed"] = True
            poe_interface.pd_class_override = False
        if (
            pre_standard_detect is not None
            and poe_interface.pre_standard_detect
        ):
            result["changed"] = True
            poe_interface.pre_standard_detect = False
    else:
        # enable is a boolean, so we need to explicitly check for None
        if enable is not None and poe_interface.power_enabled != enable:
            result["changed"] = True
            poe_interface.power_enabled = enable
        if priority and poe_interface.priority != priority:
            result["changed"] = True
            poe_interface.priority = priority
        if class_number and poe_interface.assigned_class != a_class:
            result["changed"] = True
            poe_interface.assigned_class = a_class
        if method and poe_interface.allocate_by_method != method:
            result["changed"] = True
            poe_interface.allocate_by_method = method
        if (
            pd_class_override is not None
            and poe_interface.pd_class_override != pd_class_override
        ):
            result["changed"] = True
            poe_interface.pd_class_override = pd_class_override
            poe_interface.allocate_by_method = "class"
            warning = (
                "Enabling pd-class-override will also change the allocate-by "
                "setting to class."
            )
            if "warnings" in result:
                result["warnings"].append(warning)
            else:
                result["warnings"] = [warning]
        if (
            pre_standard_detect is not None
            and poe_interface.pre_standard_detect != pre_standard_detect
        ):
            result["changed"] = True
            poe_interface.pre_standard_detect = pre_standard_detect

    if result["changed"]:
        poe_interface.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
