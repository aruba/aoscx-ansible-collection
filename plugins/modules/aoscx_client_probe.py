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
module: aoscx_client_probe
version_added: "5.0.0"
short_description: Manage Client Probe Profiles on AOS-CX switches.
description: >
  This module provides configuration management of Client Probe Profiles and
  their entries on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the Client Probe Profile.
    type: str
    required: true
  entries:
    description: >
      List of probe entries in the profile. Supplied entries are created or
      updated; entries already present on the device but not listed here are
      left untouched.
    type: list
    elements: dict
    required: false
    suboptions:
      entry_id:
        description: Identifier of the entry within the profile.
        type: int
        required: true
      vlan:
        description: VLAN on which the client is probed.
        type: int
        required: false
      source_ipv4:
        description: Source IPv4 address used in the probe packets.
        type: str
        required: false
      broadcast_ipv4:
        description: >
          Broadcast IPv4 address used in the probe packets when the client
          probe type ping-broadcast is enabled.
        type: str
        required: false
      source_mac:
        description: Source MAC address used in the probe packets.
        type: str
        required: false
      directed_ipv4_list:
        description: >
          List of unicast IPv4 addresses being probed when the client probe
          type ping-unicast or GARP is enabled.
        type: list
        elements: str
        required: false
      directed_ipv4_range:
        description: >
          Range of IPv4 addresses being probed when the client probe type
          ping-sweep or GARP is enabled. Provide a dictionary with the keys
          C(start_ip_addr) and C(end_ip_addr).
        type: dict
        required: false
  state:
    description: Create, update or delete the Client Probe Profile.
    type: str
    required: false
    default: create
    choices:
      - create
      - update
      - delete
"""

EXAMPLES = """
- name: Create a Client Probe Profile with two entries
  aoscx_client_probe:
    name: WakeUp-Clients
    entries:
      - entry_id: 1
        vlan: 99
        source_ipv4: 9.9.9.1
        broadcast_ipv4: 9.9.9.255
      - entry_id: 2
        vlan: 100
        source_ipv4: 10.0.0.1
        directed_ipv4_list:
          - 10.0.0.5
          - 10.0.0.6
    state: create

- name: Probe a range of addresses
  aoscx_client_probe:
    name: Sweep
    entries:
      - entry_id: 1
        vlan: 100
        source_ipv4: 10.0.0.1
        directed_ipv4_range:
          start_ip_addr: 10.0.0.10
          end_ip_addr: 10.0.0.20
    state: create

- name: Delete a Client Probe Profile
  aoscx_client_probe:
    name: WakeUp-Clients
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

try:
    from pyaoscx.client_probe_profile import ClientProbeProfile
    from pyaoscx.client_probe_profile_entry import ClientProbeProfileEntry

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

ENTRY_FIELDS = (
    "vlan",
    "source_ipv4",
    "broadcast_ipv4",
    "source_mac",
    "directed_ipv4_list",
    "directed_ipv4_range",
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        entries=dict(
            type="list",
            elements="dict",
            required=False,
            options=dict(
                entry_id=dict(type="int", required=True),
                vlan=dict(type="int", required=False),
                source_ipv4=dict(type="str", required=False),
                broadcast_ipv4=dict(type="str", required=False),
                source_mac=dict(type="str", required=False),
                directed_ipv4_list=dict(
                    type="list", elements="str", required=False
                ),
                directed_ipv4_range=dict(type="dict", required=False),
            ),
        ),
        state=dict(
            type="str",
            required=False,
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="This module requires a pyaoscx version that provides the "
            "ClientProbeProfile class. Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    name = ansible_module.params["name"]
    entries = ansible_module.params["entries"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    profile = ClientProbeProfile(session, name)
    try:
        profile.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            profile.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    changed = False
    if not exists:
        profile.apply()
        changed = True

    if entries:
        current = ClientProbeProfileEntry.get_all(session, profile)
        for entry in entries:
            entry_id = entry["entry_id"]
            supplied = {
                field: entry[field]
                for field in ENTRY_FIELDS
                if entry.get(field) is not None
            }
            key = str(entry_id)
            if key in current:
                obj = current[key]
                obj.get()
                for field, value in supplied.items():
                    setattr(obj, field, value)
                    if field not in obj.config_attrs:
                        obj.config_attrs.append(field)
                changed |= obj.apply()
            else:
                obj = ClientProbeProfileEntry(
                    session, entry_id, profile, **supplied
                )
                obj.apply()
                changed = True

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
