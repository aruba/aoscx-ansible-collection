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
module: aoscx_user
version_added: "4.6.0"
short_description: Create, update or delete a local user
description: >
  This module provides configuration management of local users on AOS-CX
  devices (system/users).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the local user. Index under system/users.
    required: true
    type: str
  password:
    description: Cleartext password for the user. The switch stores it
      encrypted, so this module cannot detect changes and always applies it
      when supplied.
    required: false
    type: str
  user_group:
    description: Name of the user group (role) the user belongs to.
    required: false
    type: str
  state:
    description: Create, update or delete the local user.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a local operator user
  aoscx_user:
    name: netops
    password: MySecret123!
    user_group: operators

- name: Delete a local user
  aoscx_user:
    name: netops
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.user import User

    HAS_PYAOSCX_USER = True
except ImportError:
    HAS_PYAOSCX_USER = False

if HAS_PYAOSCX_USER:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        password=dict(type="str", required=False, no_log=True),
        user_group=dict(type="str", required=False),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_USER:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support local users. "
            "Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    name = ansible_module.params["name"]
    password = ansible_module.params["password"]
    user_group = ansible_module.params["user_group"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    user = User(session, name)
    try:
        user.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            user.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    changed = not exists

    if user_group is not None:
        current = getattr(user, "user_group", None) if exists else None
        same = isinstance(current, dict) and user_group in current
        if not same:
            group_uri = "{0}system/user_groups/{1}".format(
                session.resource_prefix, user_group
            )
            user.user_group = group_uri
            if "user_group" not in user.config_attrs:
                user.config_attrs.append("user_group")
            changed = True

    if password is not None:
        user.password = password
        if "password" not in user.config_attrs:
            user.config_attrs.append("password")
        changed = True

    if changed:
        user.apply()
    result["changed"] = changed

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
