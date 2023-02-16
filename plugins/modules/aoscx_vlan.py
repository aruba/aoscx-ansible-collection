#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2023 Hewlett Packard Enterprise Development LP.
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
module: aoscx_vlan
version_added: "2.8.0"
short_description: Create or Delete VLAN configuration on AOS-CX
description: >
  This modules provides configuration management of VLANs on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  vlan_id:
    description: >
      The ID of this VLAN. Non-internal VLANs must have an 'id' between 1 and
      4094 to be effectively instantiated.
    required: true
    type: int
  name:
    description: VLAN name
    required: false
    type: str
  description:
    description: VLAN description
    required: false
    type: str
  admin_state:
    description: The Admin State of the VLAN, options are 'up' and 'down'.
    required: false
    choices:
      - up
      - down
    type: str
  voice:
    description: Enable Voice VLAN
    required: false
    default: false
    type: bool
  state:
    description: Create or update or delete the VLAN.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create VLAN 200 with description
  aoscx_vlan:
    vlan_id: 200
    description: This is VLAN 200

- name: Create VLAN 300 with description, name and voice
  aoscx_vlan:
    vlan_id: 300
    name: UPLINK_VLAN
    description: This is VLAN 300
    voice: True

- name: Delete VLAN 300
  aoscx_vlan:
    vlan_id: 300
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        vlan_id=dict(type="int", required=True),
        name=dict(type="str", default=None),
        description=dict(type="str", default=None),
        admin_state=dict(type="str", default=None, choices=["up", "down"]),
        voice=dict(type='bool', required=False, default=False),
        vsx_sync=dict(type='bool', required=False, default=False),
        state=dict(
            type="str",
            default="create",
            choices=["create", "delete", "update"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    # Set Variables
    vlan_id = ansible_module.params["vlan_id"]
    vlan_name = ansible_module.params["name"]
    if vlan_name is None:
        vlan_name = "VLAN{0}".format(vlan_id)
    description = ansible_module.params["description"]
    admin_state = ansible_module.params["admin_state"]
    voice = ansible_module.params["voice"]
    vsx_sync = ansible_module.params["vsx_sync"]

    state = ansible_module.params["state"]

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        from pyaoscx.device import Device
    except Exception as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    device = Device(session)

    if state == "delete":
        # Create Vlan Object
        vlan = device.vlan(vlan_id)
        # Delete it
        vlan.delete()
        # Changed
        result["changed"] = True

    elif state == "update" or state == "create":
        # Create Vlan with incoming attributes, in case VLAN does not exist
        # inside device
        vlan = device.vlan(
            vlan_id, vlan_name, description, "static", admin_state
        )
        vlan.voice = voice
        if vsx_sync is True:
            vlan.vsx_sync = ["all_attributes_and_dependents"]
        else:
            vlan.vsx_sync = ""
        vlan.apply()

        if vlan.was_modified():
            # Changed
            result["changed"] = True

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
