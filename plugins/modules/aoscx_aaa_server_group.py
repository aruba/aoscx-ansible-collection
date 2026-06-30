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
module: aoscx_aaa_server_group
version_added: "4.6.0"
short_description: Create, update or delete an AAA server group
description: >
  This module provides configuration management of AAA server groups on AOS-CX
  devices (system/aaa_server_groups). A server group bundles RADIUS or TACACS+
  servers so they can be referenced together by AAA methods. This module
  requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16).
  The built-in groups (local, none, radius, tacacs) cannot be modified or
  deleted.
author: Aruba Networks (@ArubaNetworks)
options:
  group_name:
    description: >
      Name of the AAA server group. This is the index of the resource under
      system/aaa_server_groups (up to 32 characters).
    required: true
    type: str
  group_type:
    description: >
      Type of the servers grouped together. Set when the group is created.
    required: false
    type: str
    choices:
      - none
      - local
      - radius
      - tacacs
  state:
    description: Create, update or delete the AAA server group.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a RADIUS server group
  aoscx_aaa_server_group:
    group_name: my-radius
    group_type: radius

- name: Create a TACACS+ server group
  aoscx_aaa_server_group:
    group_name: my-tacacs
    group_type: tacacs

- name: Delete a server group
  aoscx_aaa_server_group:
    group_name: my-radius
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

BUILTIN_GROUPS = ["local", "none", "radius", "tacacs"]


def main():
    module_args = dict(
        group_name=dict(type="str", required=True),
        group_type=dict(
            type="str",
            required=False,
            default=None,
            choices=["none", "local", "radius", "tacacs"],
        ),
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

    group_name = ansible_module.params["group_name"]
    group_type = ansible_module.params["group_type"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    if group_name in BUILTIN_GROUPS:
        ansible_module.fail_json(
            msg=(
                "The built-in AAA server group '{0}' cannot be modified or "
                "deleted".format(group_name)
            )
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        group = session.api.get_module(session, "AaaServerGroup", group_name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support AAA server groups. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        group.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                group.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete AAA server group: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- create
    if not exists:
        if group_type is None:
            ansible_module.fail_json(
                msg="group_type is required to create an AAA server group"
            )
        group = session.api.get_module(
            session, "AaaServerGroup", group_name, group_type=group_type
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                group.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create AAA server group: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- update
    changed = False
    if group_type is not None:
        if getattr(group, "group_type", None) != group_type:
            changed = True
            group.group_type = group_type
            if "group_type" not in group.config_attrs:
                group.config_attrs.append("group_type")

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            group.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update AAA server group: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
