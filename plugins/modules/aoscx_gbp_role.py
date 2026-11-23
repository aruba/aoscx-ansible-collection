#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_gbp_role
version_added: "4.6.0"
short_description: Create, update or delete a Group Based Policy role
description: >
  This module provides configuration management of Group Based Policy (GBP)
  roles on AOS-CX devices (C(gbp role <name> <id>) command, stored in
  system/gbp_role_name_id_maps). A GBP role maps a role name to the role ID
  carried in the traffic, and is referenced by the source and destination
  roles of the gbp-ipv4, gbp-ipv6 and gbp-mac classes. GBP enforcement itself
  is enabled with the gbp_enable option of the aoscx_system module. The
  built-in roles (default, infra, internet, intranet) cannot be modified or
  deleted. Requires a pyaoscx release that ships the GbpRole class.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the GBP role. This is the index of the resource under
      system/gbp_role_name_id_maps (up to 128 characters).
    required: true
    type: str
  role_id:
    description: >
      GBP role ID associated with the role (0 to 8191). Required to create
      the role.
    required: false
    type: int
  state:
    description: Create, update or delete the GBP role.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create the GBP role fabric_user1 with the role ID 1010
  aoscx_gbp_role:
    name: fabric_user1
    role_id: 1010

- name: Change the role ID of an existing GBP role
  aoscx_gbp_role:
    name: fabric_user1
    role_id: 1011
    state: update

- name: Delete a GBP role
  aoscx_gbp_role:
    name: fabric_user1
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

BUILTIN_ROLES = ["default", "infra", "internet", "intranet"]
ROLE_ID_MIN = 0
ROLE_ID_MAX = 8191


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        role_id=dict(type="int", required=False, default=None),
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

    name = ansible_module.params["name"]
    role_id = ansible_module.params["role_id"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    if name in BUILTIN_ROLES:
        ansible_module.fail_json(
            msg=(
                "The built-in GBP role '{0}' cannot be modified or "
                "deleted".format(name)
            )
        )

    if role_id is not None and not ROLE_ID_MIN <= role_id <= ROLE_ID_MAX:
        ansible_module.fail_json(
            msg="role_id must be between {0} and {1}".format(
                ROLE_ID_MIN, ROLE_ID_MAX
            )
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        role = session.api.get_module(session, "GbpRole", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support GBP roles. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        role.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                role.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete GBP role: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- create
    if not exists:
        if role_id is None:
            ansible_module.fail_json(
                msg="role_id is required to create a GBP role"
            )
        role = session.api.get_module(
            session, "GbpRole", name, gbp_role_id=role_id
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                role.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create GBP role: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- update
    changed = False
    if role_id is not None:
        if getattr(role, "gbp_role_id", None) != role_id:
            changed = True
            role.gbp_role_id = role_id
            if "gbp_role_id" not in role.config_attrs:
                role.config_attrs.append("gbp_role_id")

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            role.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update GBP role: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
