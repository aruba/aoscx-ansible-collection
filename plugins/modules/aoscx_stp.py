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
  This module provides configuration management of Spanning Tree on AOS-CX
  devices: the global settings (system/stp_config, e.g. enable, mode, bridge
  priority, MSTP region name and revision) and the per-instance settings
  (system/stp_instances, e.g. timers and topology change traps).
author: Aruba Networks (@ArubaNetworks)
options:
  instance:
    description: Spanning Tree instance identifier (for example "mstp,0").
    required: false
    type: str
    default: "mstp,0"
  enable:
    description: >
      Global knob to enable or disable Spanning Tree on the device
      (the C(spanning-tree) global command).
    required: false
    type: bool
  mode:
    description: Global spanning tree mode.
    required: false
    type: str
    choices:
      - mstp
      - rpvst
  config_name:
    description: >
      MSTP region configuration name (the C(spanning-tree config-name)
      command). Global setting.
    required: false
    type: str
  config_revision:
    description: >
      MSTP region configuration revision number (the
      C(spanning-tree config-revision) command). Global setting.
    required: false
    type: int
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

import json

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
        enable=dict(type="bool", required=False),
        mode=dict(
            type="str", required=False, choices=["mstp", "rpvst"]
        ),
        config_name=dict(type="str", required=False),
        config_revision=dict(type="int", required=False),
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

    # Global Spanning Tree settings live in system/stp_config.
    global_map = {
        "enable": "stp_enable",
        "mode": "stp_mode",
        "config_name": "mstp_config_name",
        "config_revision": "mstp_config_revision",
    }
    global_supplied = {
        attr: ansible_module.params[param]
        for param, attr in global_map.items()
        if ansible_module.params[param] is not None
    }
    if global_supplied:
        response = session.request(
            "GET", "system", params={"selector": "writable", "depth": 1}
        )
        system_doc = json.loads(response.text)
        stp_cfg = dict(system_doc.get("stp_config") or {})
        if any(stp_cfg.get(k) != v for k, v in global_supplied.items()):
            stp_cfg.update(global_supplied)
            system_doc["stp_config"] = stp_cfg
            put = session.request(
                "PUT", "system", data=json.dumps(system_doc)
            )
            if not 200 <= put.status_code < 300:
                ansible_module.fail_json(
                    msg="Could not update global STP config: {0}".format(
                        put.text
                    )
                )
            changed = True

    result["changed"] = changed

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
