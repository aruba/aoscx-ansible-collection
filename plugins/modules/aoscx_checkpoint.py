#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2023 Hewlett Packard Enterprise Development LP.
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
module: aoscx_checkpoint
version_added: "2.8.0"
short_description: >
  Creates a new checkpoint or copies an existing checkpoint to AOS-CX switch
  config.
description: >
  This module creates a new checkpoint or copies existing checkpoint to the
  running or startup config of an AOS-CX switch.
author: Aruba Networks (@ArubaNetworks)
options:
  source_config:
    description: >
      Name of the source configuration from which checkpoint needs to be
      created or copied.
    type: str
    required: false
    default: running-config
  destination_config:
    description: Name of the destination configuration or name of checkpoint.
    type: str
    required: false
    default: startup-config
  auto:
    description: >
      Manage the auto-checkpoint (confirmed commit) timer instead of copying a
      configuration. C(start) arms the timer and takes an automatic rollback
      checkpoint (the C(checkpoint auto <minutes>) command); if it is not
      confirmed before the timer expires the switch automatically restores the
      configuration. C(confirm) ends the timer and keeps the running
      configuration (the C(checkpoint auto confirm) command). When set, the
      C(source_config) and C(destination_config) options are ignored.
    type: str
    required: false
    choices:
      - start
      - confirm
  auto_timeout:
    description: >
      Auto-checkpoint timer interval in minutes (1-60). Required when C(auto)
      is C(start).
    type: int
    required: false
"""

EXAMPLES = """
- name: Copy running-config to startup-config
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'startup-config'

- name: Copy startup-config to running-config
  aoscx_checkpoint:
    source_config: 'startup-config'
    destination_config: 'running-config'

- name: Copy running-config to backup checkpoint
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'checkpoint_20200128'

- name: Arm the auto-checkpoint timer for 2 minutes before a risky change
  aoscx_checkpoint:
    auto: start
    auto_timeout: 2

- name: Confirm the configuration and stop the auto-checkpoint timer
  aoscx_checkpoint:
    auto: confirm
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        source_config=dict(type="str", default="running-config"),
        destination_config=dict(type="str", default="startup-config"),
        auto=dict(type="str", required=False, choices=["start", "confirm"]),
        auto_timeout=dict(type="int", required=False),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[("auto", "start", ["auto_timeout"])],
    )

    # Get playbook's arguments
    source_config = ansible_module.params["source_config"]
    destination_config = ansible_module.params["destination_config"]
    auto = ansible_module.params["auto"]
    auto_timeout = ansible_module.params["auto_timeout"]

    result = dict(changed=False)

    if auto == "start" and auto_timeout not in range(1, 61):
        ansible_module.fail_json(
            msg="auto_timeout must be between 1 and 60 minutes"
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        from pyaoscx.device import Device
    except Exception as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    device = Device(session)

    # Create a Configuration Object
    config = device.configuration()

    # Auto-checkpoint (confirmed commit) timer management.
    if auto is not None:
        if auto == "start":
            success = config.set_auto_checkpoint(auto_timeout)
        else:
            success = config.confirm_auto_checkpoint()
        result["changed"] = success
        ansible_module.exit_json(**result)

    success = config.create_checkpoint(source_config, destination_config)

    # Changed
    result["changed"] = success

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
