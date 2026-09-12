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
module: aoscx_port_access_policy
version_added: "4.6.0"
short_description: Create, update or delete a Port Access Policy
description: >
  This module provides configuration management of Port Access Policies on
  AOS-CX devices (system/port_access_policies). A port access policy is an
  ordered list of entries; each entry references an existing traffic class
  (system/classes) and applies an action set (drop, reflect, dscp, rate
  limiting, redirect to captive portal, ...) to the matching traffic. The
  policy can then be applied to a port access role through its in_policy
  attribute. This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16). The referenced traffic classes must
  already exist; this module does not create them. When the entries argument is
  supplied it fully replaces the existing entries of the policy; when it is
  omitted the entries are left untouched. An action field is only managed when
  it is supplied.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the port access policy. This is the index of the resource under
      system/port_access_policies.
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
          - ipv4
          - ipv6
          - mac
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
      reflect:
        description: >
          Reflect packets matching the class of this entry. When omitted, this
          part of the action set is not managed by this module.
        required: false
        type: bool
      dscp:
        description: >
          DSCP value to set on packets matching the class of this entry. When
          omitted, this part of the action set is not managed by this module.
        required: false
        type: int
      cir:
        description: >
          Committed information rate in kbps for packets matching the class of
          this entry. When omitted, this part of the action set is not managed
          by this module.
        required: false
        type: int
      cbs:
        description: >
          Committed burst size in bytes for packets matching the class of this
          entry. When omitted, this part of the action set is not managed by
          this module.
        required: false
        type: int
      pcp:
        description: >
          Priority code point to set on packets matching the class of this
          entry. When omitted, this part of the action set is not managed by
          this module.
        required: false
        type: int
      ecn:
        description: >
          ECN value to set on packets matching the class of this entry. When
          omitted, this part of the action set is not managed by this module.
        required: false
        type: int
      ip_precedence:
        description: >
          IP precedence to set on packets matching the class of this entry.
          When omitted, this part of the action set is not managed by this
          module.
        required: false
        type: int
      local_priority:
        description: >
          Local priority to set on packets matching the class of this entry.
          When omitted, this part of the action set is not managed by this
          module.
        required: false
        type: int
      exceed_drop:
        description: >
          Drop packets that exceed the committed rate for the class of this
          entry. When omitted, this part of the action set is not managed by
          this module.
        required: false
        type: bool
      redirect:
        description: >
          Redirect packets matching the class of this entry. When omitted, this
          part of the action set is not managed by this module.
        required: false
        type: str
        choices:
          - captive-portal
  state:
    description: Create, update or delete the port access policy.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a port access policy that redirects a class to captive portal
  aoscx_port_access_policy:
    name: guest_policy
    entries:
      - sequence_number: 10
        class_name: guest_http
        class_type: ipv4
        redirect: captive-portal
      - sequence_number: 20
        class_name: guest_voice
        class_type: ipv4
        dscp: 46
        cir: 1000
        cbs: 5000

- name: Delete a port access policy
  aoscx_port_access_policy:
    name: guest_policy
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
    from pyaoscx.port_access_policy import PortAccessPolicy

    HAS_PYAOSCX_PORT_ACCESS = True
except ImportError:
    HAS_PYAOSCX_PORT_ACCESS = False

CLASS_TYPES = ["ipv4", "ipv6", "mac"]
ACTION_FIELDS = [
    {"name": "drop", "type": "bool"},
    {"name": "reflect", "type": "bool"},
    {"name": "dscp", "type": "int"},
    {"name": "cir", "type": "int"},
    {"name": "cbs", "type": "int"},
    {"name": "pcp", "type": "int"},
    {"name": "ecn", "type": "int"},
    {"name": "ip_precedence", "type": "int"},
    {"name": "local_priority", "type": "int"},
    {"name": "exceed_drop", "type": "bool"},
    {"name": "redirect", "type": "str", "choices": ["captive-portal"]},
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
        ansible_module, session, PortAccessPolicy, ACTION_FIELDS
    )


if __name__ == "__main__":
    main()
