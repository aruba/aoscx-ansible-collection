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
module: aoscx_ipv6_destination_guard
version_added: "4.6.0"
short_description: Create, update or delete an IPv6 destination guard policy.
description:
  - This module manages IPv6 destination guard policies on AOS-CX switches.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the IPv6 destination guard policy.
    required: true
    type: str
  enforcement:
    description: Enforcement mode applied by the policy.
    required: false
    type: str
  nd_cache_threshold:
    description: >
      Neighbor discovery cache utilization threshold, expressed as a
      percentage, above which destination guard recovery is triggered.
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
- name: Create an IPv6 destination guard policy
  arubanetworks.aoscx.aoscx_ipv6_destination_guard:
    name: dst-guard-1
    nd_cache_threshold: 80
    state: create

- name: Delete an IPv6 destination guard policy
  arubanetworks.aoscx.aoscx_ipv6_destination_guard:
    name: dst-guard-1
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
        enforcement=dict(type="str", required=False, default=None),
        nd_cache_threshold=dict(type="int", required=False, default=None),
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
    state = ansible_module.params["state"]

    scalar_attrs = ["enforcement", "nd_cache_threshold"]
    supplied = {
        attr: ansible_module.params[attr]
        for attr in scalar_attrs
        if ansible_module.params[attr] is not None
    }

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        policy = session.api.get_module(
            session, "Ipv6DestinationGuardPolicy", name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support IPv6 destination "
                "guard policies. Upgrade pyaoscx. Details: {0}".format(str(e))
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
        policy = session.api.get_module(
            session, "Ipv6DestinationGuardPolicy", name, **supplied
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
        if getattr(policy, attr, None) != value:
            setattr(policy, attr, value)
            if attr not in policy.config_attrs:
                policy.config_attrs.append(attr)
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
