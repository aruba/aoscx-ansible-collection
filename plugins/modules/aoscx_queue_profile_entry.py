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
module: aoscx_queue_profile_entry
version_added: "4.0.0"
short_description: >
  Create, Update or Delete a Queue Profile Entry on AOS-CX devices.
description: >
  This module provides configuration management of Queue Profile Entries on
  AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  queue_profile:
    description: User-defined Queue Profile name.
    required: true
    type: str
  queue_number:
    description: Queue Profile Entry's queue number identifier.
    required: true
    type: int
  description:
    description: User-defined alphanumeric entry description.
    required: false
    type: str
  local_priorities:
    description: One or more priority(ies) assigned to this entry.
    required: false
    type: list
    elements: int
  cos:
    description: One or more cos assigned to this entry.
    required: false
    type: list
    elements: int
  state:
    description: Create, update or delete a Queue Profile.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create queue profile entry for 'Strict-Profile'
  aoscx_queue_profile_entry:
    queue_profile: Strict-Profile
    queue_number: 1
    description: Low-Queue-Prof-entry
    local_priorities:
      - 1
      - 2
      - 3

- name: Delete queue profile entry 2 from 'Strict-Profile'
  aoscx_queue_profile_entry:
    queue_profile: Strict-Profile
    queue_number: 2
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.queue_profile import QueueProfile
    from pyaoscx.queue_profile_entry import QueueProfileEntry

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "queue_profile": {
            "type": "str",
            "required": True,
        },
        "queue_number": {
            "type": "int",
            "required": True,
        },
        "description": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "local_priorities": {
            "type": "list",
            "elements": "int",
            "required": False,
            "default": None,
        },
        "cos": {
            "type": "list",
            "elements": "int",
            "required": False,
            "default": None,
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

    # Get playbook's arguments
    queue_profile = ansible_module.params["queue_profile"]
    queue_number = ansible_module.params["queue_number"]
    description = ansible_module.params["description"]
    local_priorities = ansible_module.params["local_priorities"]
    cos = ansible_module.params["cos"]
    state = ansible_module.params["state"]

    kwargs = {}
    if description:
        kwargs["description"] = description
    if cos:
        kwargs["cos"] = cos
    if local_priorities:
        kwargs["local_priorities"] = local_priorities

    q_profile = QueueProfile(session, queue_profile)
    entry = QueueProfileEntry(session, queue_number, q_profile, **kwargs)
    try:
        entry.get()
        exists = True
    except Exception as exc:
        exists = False

    if state == "delete":
        if exists:
            entry.delete()
        result["changed"] = exists
    else:
        if not exists:
            result["changed"] = True
        for k, v in kwargs.items():
            if hasattr(entry, k):
                result["changed"] |= getattr(entry, k) != v
            else:
                result["changed"] = True
            setattr(entry, k, v)
        if not exists or result["changed"]:
            entry.apply()

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
