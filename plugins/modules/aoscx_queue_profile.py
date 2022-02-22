#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_queue_profile
version_added: "4.0.0"
short_description: Create, Update or Delete a Queue Profile on AOS-CX devices.
description: >
  This module provides configuration management of Queue Profiles on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: User-defined Queue Profile name.
    required: true
    type: str
  vsx_sync:
    description: Mark for synchronization between VSX peers.
    required: false
    choices:
      - all_attributes_and_dependents
    type: list
    elements: str
  state:
    description: Create, update, or delete a Queue Profile.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a Queue Profile named 'STRICT-PROFILE'
  aoscx_queue_profile:
    state: create
    name: STRICT-PROFILE

- name: Delete a Queue Profile named 'STRICT-PROFILE'
  aoscx_queue_profile:
    state: delete
    name: STRICT-PROFILE

- name: Create Queue Profile 'STRICT-PROFILE'
  aoscx_queue_profile:
    name: STRICT-PROFILE
    state: create

- name: Set Queue Profile 'STRICT-PROFILE' as switch's global Queue Profile
  aoscx_system:
    global_queue_profile: STRICT-PROFILE
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device
    from pyaoscx.queue_profile import QueueProfile

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "name": {
            "type": "str",
            "required": True,
        },
        "vsx_sync": {
            "type": "list",
            "elements": "str",
            "required": False,
            "default": None,
            "choices": ["all_attributes_and_dependents"],
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

    session = get_pyaoscx_session(ansible_module)

    # Get Ansible module's parameters
    name = ansible_module.params["name"]
    vsx_sync = ansible_module.params["vsx_sync"]
    state = ansible_module.params["state"]

    kwargs = {}
    if vsx_sync:
        kwargs["vsx_sync"] = vsx_sync

    q_profile = QueueProfile(session, name, **kwargs)
    try:
        q_profile.get()
        exists = True
    except Exception as exc:
        exists = False

    if state == "delete":
        device = Device(session)
        if not device.materialized:
            device.get()
        if device.q_profile_default == name:
            msg = (
                "Skipping, cannot delete Queue Profile, while it is set "
                "as global."
            )
            result["msg"] = msg
            result["skipped"] = True
        else:
            if exists:
                q_profile.delete()
            result["changed"] = exists
    else:
        if not exists:
            result["changed"] = True
        for k, v in kwargs.items():
            if hasattr(q_profile, k):
                result["changed"] |= getattr(q_profile, k) != v
            else:
                result["changed"] = True
            setattr(q_profile, k, v)
        if not exists or result["changed"]:
            q_profile.apply()

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
