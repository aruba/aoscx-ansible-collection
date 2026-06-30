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
module: aoscx_dhcpv6_snooping_guard
version_added: "4.6.0"
short_description: Create, update or delete a DHCPv6 snooping guard policy.
description:
  - This module manages DHCPv6 snooping guard policies on AOS-CX switches.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the DHCPv6 snooping guard policy.
    required: true
    type: str
  server_access_list:
    description: >
      Name of the existing IPv6 ACL used to filter packets from trusted DHCP
      servers. When omitted server filtering is left unchanged.
    required: false
    type: str
  client_prefix_list:
    description: >
      Name of the existing prefix list of IPv6 prefixes that a client is
      allowed to use. The prefix list must already exist. When omitted the
      client prefix filtering is left unchanged.
    required: false
    type: str
  server_preference_range:
    description: >
      Allowed DHCPv6 server preference value range. The supplied dictionary
      fully replaces the current settings.
    required: false
    type: dict
    suboptions:
      preference_min:
        description: Minimum allowed preference value (0-255).
        required: false
        type: int
      preference_max:
        description: Maximum allowed preference value (0-255).
        required: false
        type: int
  state:
    description: Create, update or delete the policy.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a DHCPv6 snooping guard policy
  arubanetworks.aoscx.aoscx_dhcpv6_snooping_guard:
    name: v6-guard-1
    server_access_list: trusted-servers-v6
    state: create

- name: Delete a DHCPv6 snooping guard policy
  arubanetworks.aoscx.aoscx_dhcpv6_snooping_guard:
    name: v6-guard-1
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        server_access_list=dict(type="str", required=False, default=None),
        client_prefix_list=dict(type="str", required=False, default=None),
        server_preference_range=dict(
            type="dict",
            required=False,
            default=None,
            options=dict(
                preference_min=dict(
                    type="int", required=False, default=None
                ),
                preference_max=dict(
                    type="int", required=False, default=None
                ),
            ),
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

    name = ansible_module.params["name"]
    server_access_list = ansible_module.params["server_access_list"]
    client_prefix_list = ansible_module.params["client_prefix_list"]
    server_preference_range = ansible_module.params["server_preference_range"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    supplied = {}
    if server_access_list is not None:
        acl = session.api.get_module(
            session, "ACL", server_access_list, list_type="ipv6"
        )
        supplied["match_server_access_list"] = acl.get_uri()
    if client_prefix_list is not None:
        prefix_list = session.api.get_module(
            session, "PrefixList", client_prefix_list
        )
        supplied["match_client_prefix_list"] = "{0}{1}".format(
            session.resource_prefix, prefix_list.path
        )

    try:
        policy = session.api.get_module(
            session, "Dhcpv6SnoopingGuardPolicy", name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support DHCPv6 snooping guard "
                "policies. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        policy.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                policy.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete policy: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        create_kwargs = dict(supplied)
        if server_preference_range is not None:
            create_kwargs["server_preference_range"] = {
                k: v
                for k, v in server_preference_range.items()
                if v is not None
            }
        policy = session.api.get_module(
            session, "Dhcpv6SnoopingGuardPolicy", name, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                policy.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create policy: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        current = getattr(policy, attr, None)
        if isinstance(current, dict):
            current = next(iter(current.values()), "")
        if str(current).rstrip("/").rsplit("/", 1)[-1] != value.rstrip("/").rsplit("/", 1)[-1]:
            setattr(policy, attr, value)
            if attr not in policy.config_attrs:
                policy.config_attrs.append(attr)
            changed = True

    if server_preference_range is not None:
        want = {
            k: v for k, v in server_preference_range.items() if v is not None
        }
        current_range = getattr(policy, "server_preference_range", None) or {}
        if any(current_range.get(k) != v for k, v in want.items()):
            merged = dict(current_range)
            merged.update(want)
            policy.server_preference_range = merged
            if "server_preference_range" not in policy.config_attrs:
                policy.config_attrs.append("server_preference_range")
            changed = True

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            policy.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update policy: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
