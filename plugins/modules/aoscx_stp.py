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
module: aoscx_stp
version_added: "4.6.0"
short_description: Manage Spanning Tree instance settings
description: >
  This module provides configuration management of Spanning Tree instances
  on AOS-CX devices (system/stp_instances).
author: Aruba Networks (@ArubaNetworks)
options:
  instance:
    description: Spanning Tree instance identifier (for example "mstp,0").
    required: false
    type: str
    default: "mstp,0"
  priority:
    description: Bridge priority multiplier (0-15).
    required: false
    type: int
  hello_time:
    description: Hello time in seconds.
    required: false
    type: int
  forward_delay:
    description: Forward delay in seconds.
    required: false
    type: int
  max_age:
    description: Maximum age in seconds.
    required: false
    type: int
  topology_change_trap_enable:
    description: Enable topology change traps for this instance.
    required: false
    type: bool
  state:
    description: Update or delete the Spanning Tree instance.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Set a low bridge priority on the default instance
  aoscx_stp:
    instance: "mstp,0"
    priority: 4

- name: Tune STP timers
  aoscx_stp:
    instance: "mstp,0"
    hello_time: 2
    forward_delay: 15
    max_age: 20
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.stp import Stp

    HAS_PYAOSCX_STP = True
except ImportError:
    HAS_PYAOSCX_STP = False

if HAS_PYAOSCX_STP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        instance=dict(type="str", required=False, default="mstp,0"),
        priority=dict(type="int", required=False),
        hello_time=dict(type="int", required=False),
        forward_delay=dict(type="int", required=False),
        max_age=dict(type="int", required=False),
        topology_change_trap_enable=dict(type="bool", required=False),
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

    if not HAS_PYAOSCX_STP:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support STP instances. "
            "Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    instance = ansible_module.params["instance"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    stp = Stp(session, instance)
    try:
        stp.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            stp.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    changed = not exists
    for field in (
        "priority",
        "hello_time",
        "forward_delay",
        "max_age",
        "topology_change_trap_enable",
    ):
        value = ansible_module.params[field]
        if value is None:
            continue
        if not exists or getattr(stp, field, None) != value:
            setattr(stp, field, value)
            if field not in stp.config_attrs:
                stp.config_attrs.append(field)
            changed = True

    if changed:
        stp.apply()
    result["changed"] = changed

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
