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
module: aoscx_port_access_cdp_group
version_added: "4.6.0"
short_description: Create, update or delete a Port Access CDP device group
description: >
  This module provides configuration management of Port Access CDP device
  classification groups on AOS-CX devices (system/port_access_cdp_groups). A
  CDP group is an ordered list of entries; each entry matches a connected
  device against the attributes advertised through CDP (platform, software
  version and voice VLAN query value). The group can then be referenced by a
  device profile to classify devices. This module requires REST API version
  10.13 or higher. The supplied entries fully replace the existing entries of
  the group; within an entry, the supplied match fields fully replace the
  current ones.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the CDP group. This is the index of the resource under
      system/port_access_cdp_groups.
    required: true
    type: str
  entries:
    description: >
      Ordered list of group entries. The supplied list fully replaces the
      existing entries of the group. Omit to leave the entries untouched and
      only reconcile the group existence.
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: Sequence number of the entry within the group.
        required: true
        type: int
      platform:
        description: Hardware or model details of the neighbor to match.
        required: false
        type: str
      software_version:
        description: Software version of the neighbor to match.
        required: false
        type: str
      voice_vlan_query_value:
        description: Voice VLAN query value of the neighbor to match.
        required: false
        type: int
  state:
    description: The action to be taken with the current group.
    required: false
    type: str
    default: create
    choices:
      - create
      - update
      - delete
"""

EXAMPLES = """
- name: Create a CDP device group with two match entries
  arubanetworks.aoscx.aoscx_port_access_cdp_group:
    name: ip_phones
    entries:
      - sequence_number: 10
        platform: "Cisco IP Phone 7961"
      - sequence_number: 20
        software_version: "SCCP 9.4"
        voice_vlan_query_value: 200
    state: create

- name: Delete a CDP device group
  arubanetworks.aoscx.aoscx_port_access_cdp_group:
    name: ip_phones
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.port_access_device_group import (  # NOQA
    build_argument_spec,
    run_port_access_device_group,
)

try:
    from pyaoscx.port_access_device_group import PortAccessCdpGroup

    HAS_PYAOSCX_PORT_ACCESS = True
except ImportError:
    HAS_PYAOSCX_PORT_ACCESS = False

MATCH_FIELDS = [
    {"name": "platform", "type": "str"},
    {"name": "software_version", "type": "str"},
    {"name": "voice_vlan_query_value", "type": "int"},
]


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(MATCH_FIELDS),
        supports_check_mode=True,
    )
    if not HAS_PYAOSCX_PORT_ACCESS:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support port access device "
                "groups. Upgrade pyaoscx."
            )
        )
    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    run_port_access_device_group(
        ansible_module, session, PortAccessCdpGroup, MATCH_FIELDS
    )


if __name__ == "__main__":
    main()
