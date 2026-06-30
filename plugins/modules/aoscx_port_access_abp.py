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
module: aoscx_port_access_abp
version_added: "4.6.0"
short_description: Create, update or delete a Port Access Application Based
  Policy
description: >
  This module provides configuration management of Port Access Application
  Based Policies (ABP) on AOS-CX devices (system/port_access_abps). An
  application based policy is an ordered list of entries; each entry references
  an existing traffic class (system/classes) and applies an action set (drop,
  dscp, local_priority or mirror) to the matching traffic. The policy can then
  be applied to a port access role through its in_abp attribute. This module
  requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16).
  The referenced traffic classes must already exist; this module does not
  create them. When the entries argument is supplied it fully replaces the
  existing entries of the policy; when it is omitted the entries are left
  untouched. An action field is only managed when it is supplied.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the application based policy. This is the index of the resource
      under system/port_access_abps.
    required: true
    type: str
  entries:
    description: >
      Ordered list of policy entries. When supplied the list fully replaces the
      existing entries of the policy. When omitted the entries are left
      untouched.
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: Sequence number of the entry within the policy.
        required: true
        type: int
      class_name:
        description: >
          Name of the existing traffic class (system/classes) matched by this
          entry. The class must already exist.
        required: true
        type: str
      class_type:
        description: Type of the referenced traffic class.
        required: true
        type: str
        choices:
          - abp-ipv4
          - abp-ipv6
      comment:
        description: Optional comment for the entry.
        required: false
        type: str
      drop:
        description: >
          Drop packets matching the class of this entry. When omitted, this
          part of the action set is not managed by this module.
        required: false
        type: bool
      dscp:
        description: >
          DSCP value to set on packets matching the class of this entry. When
          omitted, this part of the action set is not managed by this module.
        required: false
        type: int
      local_priority:
        description: >
          Local priority to set on packets matching the class of this entry.
          When omitted, this part of the action set is not managed by this
          module.
        required: false
        type: int
      mirror:
        description: >
          Mirror session identifier to which packets matching the class of this
          entry are mirrored. When omitted, this part of the action set is not
          managed by this module.
        required: false
        type: int
  state:
    description: Create, update or delete the application based policy.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an application based policy that drops and mirrors a class
  aoscx_port_access_abp:
    name: app_policy
    entries:
      - sequence_number: 10
        class_name: streaming
        class_type: abp-ipv4
        drop: true
      - sequence_number: 20
        class_name: voice
        class_type: abp-ipv4
        dscp: 46
        local_priority: 7

- name: Delete an application based policy
  aoscx_port_access_abp:
    name: app_policy
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.port_access_family import (  # NOQA
    build_argument_spec,
    run_port_access_family,
)

try:
    from pyaoscx.port_access_abp import PortAccessAbp

    HAS_PYAOSCX_PORT_ACCESS = True
except ImportError:
    HAS_PYAOSCX_PORT_ACCESS = False

CLASS_TYPES = ["abp-ipv4", "abp-ipv6"]
ACTION_FIELDS = [
    {"name": "drop", "type": "bool"},
    {"name": "dscp", "type": "int"},
    {"name": "local_priority", "type": "int"},
    {"name": "mirror", "type": "int"},
]


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(CLASS_TYPES, ACTION_FIELDS),
        supports_check_mode=True,
    )
    if not HAS_PYAOSCX_PORT_ACCESS:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support port access policies. "
                "Upgrade pyaoscx."
            )
        )
    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    run_port_access_family(
        ansible_module, session, PortAccessAbp, ACTION_FIELDS
    )


if __name__ == "__main__":
    main()
