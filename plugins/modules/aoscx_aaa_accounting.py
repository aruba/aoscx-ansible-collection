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
module: aoscx_aaa_accounting
version_added: "4.6.0"
short_description: Configure AAA accounting attributes.
description:
  - This module configures AAA accounting attributes for a session type on
    AOS-CX switches.
author: Aruba Networks (@ArubaNetworks)
options:
  session_type:
    description: Session type the accounting attributes apply to.
    required: false
    default: port-access
    choices:
      - port-access
    type: str
  accounting_mode:
    description: Accounting mode used for the session type.
    required: false
    choices:
      - start-stop
      - stop-only
    type: str
  interim_update_enable:
    description: Enable interim accounting updates.
    required: false
    type: bool
  interim_update_interval:
    description: Interval, in minutes, between interim accounting updates.
    required: false
    type: int
  interim_update_onreauth_enable:
    description: Send an interim accounting update on reauthentication.
    required: false
    type: bool
  state:
    description: Create, update or delete the accounting attributes.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Configure port-access accounting (start-stop, interim every minute)
  arubanetworks.aoscx.aoscx_aaa_accounting:
    session_type: port-access
    accounting_mode: start-stop
    interim_update_enable: true
    interim_update_interval: 1
    interim_update_onreauth_enable: true
    state: create

- name: Reset port-access accounting attributes
  arubanetworks.aoscx.aoscx_aaa_accounting:
    session_type: port-access
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SCALARS = [
    "accounting_mode",
    "interim_update_enable",
    "interim_update_interval",
    "interim_update_onreauth_enable",
]


def main():
    module_args = dict(
        session_type=dict(
            type="str", default="port-access", choices=["port-access"]
        ),
        accounting_mode=dict(
            type="str", default=None, choices=["start-stop", "stop-only"]
        ),
        interim_update_enable=dict(type="bool", default=None),
        interim_update_interval=dict(type="int", default=None),
        interim_update_onreauth_enable=dict(type="bool", default=None),
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

    session_type = ansible_module.params["session_type"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        entry = session.api.get_module(
            session, "AaaAccountingAttributes", session_type
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support AAA accounting "
                "attributes. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        entry.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    supplied = {
        attr: ansible_module.params[attr]
        for attr in SCALARS
        if ansible_module.params[attr] is not None
    }

    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                entry.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete entry: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        entry = session.api.get_module(
            session, "AaaAccountingAttributes", session_type, **supplied
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                entry.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create entry: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(entry, attr, None) != value:
            setattr(entry, attr, value)
            if attr not in entry.config_attrs:
                entry.config_attrs.append(attr)
            changed = True

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            entry.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update entry: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
