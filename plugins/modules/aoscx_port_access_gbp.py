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
module: aoscx_port_access_gbp
version_added: "4.6.0"
short_description: Create, update or delete a Port Access Group Based Policy
description: >
  This module provides configuration management of Port Access Group Based
  Policies (GBP) on AOS-CX devices (system/port_access_gbps). A group based
  policy is an ordered list of entries; each entry references an existing
  traffic class (system/classes) and optionally drops or reflects the matching
  traffic. The policy can then be applied to a port access role through its
  in_gbp attribute. This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16). The referenced traffic classes must
  already exist; this module does not create them. The supplied entries fully
  replace the existing entries of the policy.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the group based policy. This is the index of the resource under
      system/port_access_gbps.
    required: true
    type: str
  entries:
    description: >
      Ordered list of policy entries. The supplied list fully replaces the
      existing entries of the policy.
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
          - gbp-ipv4
          - gbp-ipv6
          - gbp-mac
      comment:
        description: Optional comment for the entry.
        required: false
        type: str
      drop:
        description: >
          Drop packets matching the class of this entry. When omitted, the
          action set of the entry is not managed by this module.
        required: false
        type: bool
      reflect:
        description: >
          Reflect packets matching the class of this entry in the reverse
          direction only when the flow is learnt. When omitted, the action set
          of the entry is not managed by this module.
        required: false
        type: bool
  state:
    description: Create, update or delete the group based policy.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a group based policy that drops traffic of a class
  aoscx_port_access_gbp:
    name: employee_r2r_policy
    entries:
      - sequence_number: 10
        class_name: employee_DENY
        class_type: gbp-ipv4
        drop: true
      - sequence_number: 20
        class_name: employee_ALLOW
        class_type: gbp-ipv4

- name: Delete a group based policy
  aoscx_port_access_gbp:
    name: employee_r2r_policy
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

COLLECTION = "system/port_access_gbps"
ACTION_KEY = "gbp_action_set"
CLASS_TYPES = ["gbp-ipv4", "gbp-ipv6", "gbp-mac"]
ACTION_FIELDS = [
    {"name": "drop", "type": "bool"},
    {"name": "reflect", "type": "bool"},
]


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(CLASS_TYPES, ACTION_FIELDS),
        supports_check_mode=True,
    )
    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    run_port_access_family(
        ansible_module, session, COLLECTION, ACTION_KEY, ACTION_FIELDS
    )


if __name__ == "__main__":
    main()
