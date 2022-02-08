#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified"
}

DOCUMENTATION = """
---
module: aoscx_system
version_added: "4.0.0"
short_description: Set global configuration in AOS-CX devices
description: This module provides configuration management of AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  global_qos_trust_mode:
    description: >
      Trust mode to be set as global for an AOS-CX device. Use "default" to set
      the factory-default global trust mode.
    type: str
    required: false
    choices:
      - cos
      - dscp
      - none
      - default
  global_queue_profile:
    description: >
      Queue Profile to set as the global one for an AOS-CX device. This option
      is mutually exclusive with the use_default_global_queue_profile option.
    type: str
    required: false
  use_default_global_queue_profile:
    description: >
      Set the global queue profile for an AOS-CX device to its factory
      default global queue profile, this option is mutually exclusive with the
      global_queue_profile option.
    type: bool
    required: false
    default: false
  global_schedule_profile:
    description: >
      Schedule Profile to set as the global one for an AOS-CX device. This
      option is mutually exclusive with the use_default_global_schedule_profile
      option.
    type: str
    required: false
  use_default_global_schedule_profile:
    description: >
      Set the global schedule profile for an AOS-CX device to its factory
      default global schedule profile, this option is mutually exclusive with
      the global_queue_profile option.
    type: bool
    required: false
    default: false
"""

EXAMPLES = """
- name: Set the global qos trust mode to dscp
  aoscx_system:
    global_qos_trust_mode: dscp

- name: Set the global qos trust mode to the switch's factory default
  aoscx_system:
    global_qos_trust_mode: default

- name: >
    Set the switch's global Queue Profile to a Queue Profile named
    STRICT-PROFILE
  aoscx_system:
    global_queue_profile: STRICT-PROFILE

- name: Set the global Queue Profile to the switch's factory default
  aoscx_system:
    use_default_global_queue_profile: true

- name: >
    Set the switch's global Schedule Profile to a Schedule Profile named
    STRICT-PROFILE
  aoscx_system:
    global_schedule_profile: STRICT-PROFILE

- name: Set the global Schedule Profile to the switch's factory default
  aoscx_system:
    use_default_global_schedule_profile: true
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.qos import Qos
    from pyaoscx.queue_profile import QueueProfile

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "global_qos_trust_mode": {
            "type": "str",
            "required": False,
            "choices": ["cos", "dscp", "none", "default"],
        },
        "global_queue_profile": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "use_default_global_queue_profile": {
            "type": "bool",
            "required": False,
            "default": False,
        },
        "global_schedule_profile": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "use_default_global_schedule_profile": {
            "type": "bool",
            "required": False,
            "default": False,
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        mutually_exclusive=[
            ("global_queue_profile", "use_default_global_queue_profile"),
            ("global_schedule_profile", "use_default_global_schedule_profile"),
        ],
    )

    result = dict(
        changed=False
    )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    session = get_pyaoscx_session(ansible_module)

    # Get playbook's parameters
    global_qos_trust_mode = ansible_module.params["global_qos_trust_mode"]
    global_queue_profile = ansible_module.params["global_queue_profile"]
    use_default_global_queue_profile = ansible_module.params[
        "use_default_global_queue_profile"
    ]
    global_schedule_profile = ansible_module.params["global_schedule_profile"]
    use_default_global_schedule_profile = ansible_module.params[
        "use_default_global_schedule_profile"
    ]

    if global_qos_trust_mode:
        result["changed"] |= Qos.set_global_trust_mode(
            session, global_qos_trust_mode
        )

    if global_schedule_profile:
        result["changed"] |= Qos.set_global_schedule_profile(
            session,
            global_schedule_profile,
        )

    if use_default_global_schedule_profile:
        result["changed"] |= Qos.set_global_schedule_profile(session, None)

    if global_queue_profile:
        result["changed"] |= QueueProfile.set_global_queue_profile(
            session, global_queue_profile
        )

    if use_default_global_queue_profile:
        result["changed"] |= QueueProfile.set_global_queue_profile(
            session, None
        )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
