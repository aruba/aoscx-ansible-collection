#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
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
    default: false
    required: false
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
    default: false
    required: false
  virtual_mac:
    description: >
      Global virtual MAC address (C(virtual-mac) command), in the
      xx:xx:xx:xx:xx:xx format. EVPN advertises it as the router MAC of the
      symmetric IRB routes. This option is mutually exclusive with the
      use_default_virtual_mac option.
    type: str
    required: false
  use_default_virtual_mac:
    description: >
      Remove the global virtual MAC address (C(no virtual-mac)), this option
      is mutually exclusive with the virtual_mac option.
    type: bool
    default: false
    required: false
  gbp_enable:
    description: >
      Enable (C(gbp enable)) or disable (C(no gbp enable)) Group Based Policy
      enforcement. Requires a pyaoscx release that ships
      Device.set_gbp_enable().
    type: bool
    required: false
  internal_vlan_range:
    description: >
      VLAN range reserved for internal use (C(system internal-vlan-range start
      <start> end <end>)). Platforms such as the 6200 reserve no internal VLAN
      by default and refuse to enable routing on a port until a range is
      configured. The task fails on platforms where the range is not
      configurable (6300, 6400, 8360, ...). Requires a pyaoscx release that
      ships Device.set_internal_vlan_range().
    type: dict
    required: false
    suboptions:
      start:
        description: First VLAN ID of the range (2-4094).
        type: int
        required: true
      end:
        description: Last VLAN ID of the range (2-4094).
        type: int
        required: true
  interface_groups:
    description: >
      Permitted transceiver speed of interface groups (C(system
      interface-group <group> [line-module <line_module>] speed <speed>)).
      Changing the speed of a group resets all its ports. The groups and
      speeds supported by the switch are listed by C(show system
      interface-group) and C(system interface-group <group> speed ?).
      Requires a pyaoscx release that ships Device.set_interface_group_speed().
    type: list
    elements: dict
    required: false
    suboptions:
      group:
        description: Interface group number.
        type: int
        required: true
      speed:
        description: >
          Permitted speed of the group, for example C(10g), C(25g) or C(50g),
          or C(default) to restore the default speed of the group.
        type: str
        required: true
      line_module:
        description: >
          Line module of the group, for example C(1/3). Required on modular
          switches where several line modules have the group.
        type: str
        required: false
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

- name: Set the global virtual MAC address used by EVPN symmetric IRB
  aoscx_system:
    virtual_mac: "02:00:00:00:00:01"

- name: Remove the global virtual MAC address
  aoscx_system:
    use_default_virtual_mac: true

- name: Enable Group Based Policy enforcement
  aoscx_system:
    gbp_enable: true

- name: Reserve VLANs 3000-3999 for internal use (required on a 6200)
  aoscx_system:
    internal_vlan_range:
      start: 3000
      end: 3999

- name: Allow 10G transceivers in interface group 1 of an 8360
  aoscx_system:
    interface_groups:
      - group: 1
        speed: 10g

- name: Restore the default speed of interface group 2 of line module 1/3
  aoscx_system:
    interface_groups:
      - group: 2
        line_module: "1/3"
        speed: default
"""

RETURN = r""" # """

import re

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device
    from pyaoscx.exceptions.pyaoscx_error import PyaoscxError
    from pyaoscx.qos import Qos
    from pyaoscx.queue_profile import QueueProfile

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
        pyaoscx_error_message,
    )


MAC_REGEX = re.compile(r"^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$")


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
        "virtual_mac": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "use_default_virtual_mac": {
            "type": "bool",
            "required": False,
            "default": False,
        },
        "gbp_enable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "internal_vlan_range": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "start": {"type": "int", "required": True},
                "end": {"type": "int", "required": True},
            },
        },
        "interface_groups": {
            "type": "list",
            "elements": "dict",
            "required": False,
            "default": None,
            "options": {
                "group": {"type": "int", "required": True},
                "speed": {"type": "str", "required": True},
                "line_module": {"type": "str", "required": False},
            },
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
            ("virtual_mac", "use_default_virtual_mac"),
        ],
    )

    result = dict(changed=False)

    virtual_mac = ansible_module.params["virtual_mac"]
    if virtual_mac and not MAC_REGEX.match(virtual_mac):
        ansible_module.fail_json(
            msg="virtual_mac must be in the xx:xx:xx:xx:xx:xx format."
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

    if virtual_mac:
        result["changed"] |= Device(session).set_virtual_mac(virtual_mac)

    if ansible_module.params["use_default_virtual_mac"]:
        result["changed"] |= Device(session).set_virtual_mac(None)

    gbp_enable = ansible_module.params["gbp_enable"]
    if gbp_enable is not None:
        device = Device(session)
        if not hasattr(device, "set_gbp_enable"):
            ansible_module.fail_json(
                msg=(
                    "This pyaoscx version does not support gbp_enable. "
                    "Upgrade pyaoscx."
                )
            )
        result["changed"] |= device.set_gbp_enable(gbp_enable)

    internal_vlan_range = ansible_module.params["internal_vlan_range"]
    if internal_vlan_range is not None:
        device = Device(session)
        if not hasattr(device, "set_internal_vlan_range"):
            ansible_module.fail_json(
                msg=(
                    "This pyaoscx version does not support "
                    "internal_vlan_range. Upgrade pyaoscx."
                )
            )
        try:
            result["changed"] |= device.set_internal_vlan_range(
                internal_vlan_range["start"], internal_vlan_range["end"]
            )
        except PyaoscxError as e:
            ansible_module.fail_json(
                msg=pyaoscx_error_message(
                    session, "Could not set the internal VLAN range", e
                ),
                **result
            )

    interface_groups = ansible_module.params["interface_groups"]
    if interface_groups:
        device = Device(session)
        if not hasattr(device, "set_interface_group_speed"):
            ansible_module.fail_json(
                msg=(
                    "This pyaoscx version does not support interface_groups. "
                    "Upgrade pyaoscx."
                )
            )
        for item in interface_groups:
            speed = item["speed"]
            try:
                result["changed"] |= device.set_interface_group_speed(
                    item["group"],
                    None if speed == "default" else speed,
                    line_module=item["line_module"],
                )
            except PyaoscxError as e:
                ansible_module.fail_json(
                    msg=pyaoscx_error_message(
                        session,
                        "Could not set the speed of interface group "
                        "{0}".format(item["group"]),
                        e,
                    ),
                    **result
                )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
