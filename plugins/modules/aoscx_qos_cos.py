#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified"
}

DOCUMENTATION = """
---
module: aoscx_qos_cos
version_added: "4.0.0"
short_description: Create or Delete QoS COS trust modes on AOS-CX.
description: >
  This module provides configuration management of QoS COS trust mode on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  code_point:
    description: 3-bit integer value that marks packets with one of eight
      priority levels, defined as Class of Service Priority Code Point (PCP) in
      IEEE 802.1Q VLAN tag.
    required: True
    type: int
  color:
    description: String to identify the color which may be used later in the
      pipeline in packet-drop decision points.
    required: false
    choices: ["green, yellow, red"]
    type: str
  description:
    description: String used for customer documentation.
    required: false
    type: str
  local_priority:
    description: Integer to represent an internal meta-data value that will be
      associated with the packet. This value will be used later to select the
      egress queue for the packet.
    required: false
    type: str
"""

EXAMPLES = """
---
- name: Update description of QoS COS trust type map entry with code point 3
  aoscx_qos_cos:
   code_point: 3
   description: QoS COS 3 - Engineering Department

- name: Update color of QoS COS trust type map entry with code point 5
  aoscx_qos_cos:
    code_point: 5
    color: yellow

- name: Update color and local priority of QoS COS trust type map entry with code point 5
  aoscx_qos_cos:
    code_point: 5
    color: yellow
    local_priority: 3
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

def main():
    module_args = dict(
        code_point=dict(
            type="int",
            required=True,
            default=None,
            choices=[0, 1, 2, 3, 4, 5, 6 ,7]
        ),
        color=dict(
            type="str",
            required=False,
            choices=["green", "yellow", "red"]
        ),
        description=dict(type="str", required=False),
        local_priority=dict(type="int", required=False)
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    result = dict(
        changed = False
    )

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    # Get playbook's arguments
    code_point = ansible_module.params["code_point"]
    color = ansible_module.params["color"]
    description = ansible_module.params["description"]
    local_priority = ansible_module.params["local_priority"]

    session = get_pyaoscx_session(ansible_module)

    # Get Pyaoscx device to handle switch configuration
    device = Device(session)

    # Create QosCos object with incoming code_point
    qos_cos = device.qos_cos(code_point)

    _change_needed = False
    if color is not None:
        qos_cos.color = color
        _change_needed = True

    if description is not None:
        qos_cos.description = description
        _change_needed = True

    if local_priority is not None:
        qos_cos.local_priority = local_priority
        _change_needed = True

    if _change_needed:
        result["changed"] = qos_cos.apply()

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
