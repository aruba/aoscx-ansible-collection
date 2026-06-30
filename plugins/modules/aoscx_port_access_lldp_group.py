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
module: aoscx_port_access_lldp_group
version_added: "4.6.0"
short_description: Create, update or delete a Port Access LLDP device group
description: >
  This module provides configuration management of Port Access LLDP device
  classification groups on AOS-CX devices (system/port_access_lldp_groups). An
  LLDP group is an ordered list of entries; each entry matches a connected
  device against the attributes advertised through LLDP (system description,
  system name, vendor OUI and vendor OUI subtype). The group can then be
  referenced by a device profile to classify devices. This module requires
  REST API version 10.13 or higher. The supplied entries fully replace the
  existing entries of the group; within an entry, the supplied match fields
  fully replace the current ones.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the LLDP group. This is the index of the resource under
      system/port_access_lldp_groups.
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
      system_description:
        description: System description TLV of the vendor to match.
        required: false
        type: str
      system_name:
        description: System name TLV of the device vendor to match.
        required: false
        type: str
      vendor_oui:
        description: >
          The organization unique identifier (OUI) of the device vendor to
          match.
        required: false
        type: str
      vendor_oui_subtype:
        description: The OUI subtype of the device vendor to match.
        required: false
        type: dict
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
- name: Create an LLDP device group with two match entries
  arubanetworks.aoscx.aoscx_port_access_lldp_group:
    name: ip_phones
    entries:
      - sequence_number: 10
        system_name: "SEP-phone"
      - sequence_number: 20
        system_description: "IP Phone"
        vendor_oui: "00:1b:0c"
    state: create

- name: Delete an LLDP device group
  arubanetworks.aoscx.aoscx_port_access_lldp_group:
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
    from pyaoscx.port_access_device_group import PortAccessLldpGroup

    HAS_PYAOSCX_PORT_ACCESS = True
except ImportError:
    HAS_PYAOSCX_PORT_ACCESS = False

MATCH_FIELDS = [
    {"name": "system_description", "type": "str"},
    {"name": "system_name", "type": "str"},
    {"name": "vendor_oui", "type": "str"},
    {"name": "vendor_oui_subtype", "type": "dict"},
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
        ansible_module, session, PortAccessLldpGroup, MATCH_FIELDS
    )


if __name__ == "__main__":
    main()
