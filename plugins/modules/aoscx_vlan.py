#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
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
    default: None
    type: bool
  vsx_sync:
    description: Enable vsx_sync (Only for VSX device)
    required: false
    default: None
    type: bool
  ip_igmp_snooping:
    description: Enable IP IGMP Snooping
    required: false
    default: None
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

- name: Create VLAN 300 with description and name
  aoscx_vlan:
    vlan_id: 300
    name: UPLINK_VLAN
    description: This is VLAN 300

- name: Create VLAN 400 with name, voice, vsx_sync and ip igmp snooping
  aoscx_vlan:
    vlan_id: 400
    name: VOICE_VLAN
    voice: True
    vsx_sync: True
    ip_igmp_snooping: True

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


def get_argument_spec():
    argument_spec = {
        "vlan_id": {
            "type": "int",
            "required": True,
        },
        "name": {
            "type": "str",
            "default": None,
        },
        "description": {
            "type": "str",
            "default": None,
        },
        "admin_state": {
            "type": "str",
            "default": None,
            "choices": [
                "up",
                "down",
            ],
        },
        "voice": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "vsx_sync": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "ip_igmp_snooping": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "state": {
            "type": "str",
            "default": "create",
            "choices": [
                "create",
                "delete",
                "update",
            ],
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

    # Get playbook's arguments
    vlan_id = ansible_module.params["vlan_id"]
    vlan_name = ansible_module.params["name"]
    description = ansible_module.params["description"]
    admin_state = ansible_module.params["admin_state"]
    voice = ansible_module.params["voice"]
    vsx_sync = ansible_module.params["vsx_sync"]
    ip_igmp_snooping = ansible_module.params["ip_igmp_snooping"]
    state = ansible_module.params["state"]
    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {}".format(str(e))
        )
    # device = Device(session)
    Vlan = session.api.get_module_class(session, "Vlan")
    vlan = Vlan(session, vlan_id, vlan_name)
    modified = False

    try:
        vlan.get()
        vlan_exists = True
    except Exception:
        vlan_exists = False

    if state == "delete":
        if vlan_exists:
            vlan.delete()
            modified = True

    elif state == "update" or state == "create":
        if not vlan_exists:
            try:
                if vlan_name is None:
                    vlan.name = "VLAN{0}".format(vlan_id)
                vlan.create()
                modified = True
            except Exception as e:
                ansible_module.fail_json(msg=str(e))

        if vlan_name is not None:
            modified |= vlan.name != vlan_name
            vlan.name = vlan_name

        if description is not None:
            modified |= vlan.description != description
            vlan.description = description

        if admin_state is not None:
            modified |= vlan.admin != admin_state
            vlan.admin = admin_state

        if voice is not None:
            modified |= vlan.voice != voice
            vlan.voice = voice

        if vsx_sync is not None:
            vsx_sync_all = ["all_attributes_and_dependents"]
            if vsx_sync:
                modified |= vlan.vsx_sync != vsx_sync_all
                try:
                    vlan.vsx_sync = vsx_sync_all
                except Exception as e:
                    ansible_module.fail_json(msg=str(e))
            else:
                modified |= vlan.vsx_sync != []
                vlan.vsx_sync = []

        if ip_igmp_snooping is not None:
            modified |= (
                "igmp" not in vlan.mgmd_enable
                or vlan.mgmd_enable["igmp"] != ip_igmp_snooping
            )
            vlan.mgmd_enable["igmp"] = ip_igmp_snooping

        try:
            vlan.apply()
        except Exception as e:
            ansible_module.fail_json(msg=str(e))

    result["changed"] = modified

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
