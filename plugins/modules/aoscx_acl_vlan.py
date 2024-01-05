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
module: aoscx_acl_vlan
version_added: "2.8.0"
short_description: Apply/Remove ACL configuration on VLANs for AOS-CX.
description: >
  This modules provides application management of Access Classifier Lists on
  VLANs on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  acl_name:
    description: Name of the ACL being applied or removed from the VLAN.
    required: true
    type: str
  acl_type:
    description: Type of ACL being applied or removed from the VLAN.
    choices:
      - ipv4
      - ipv6
      - mac
    required: true
    type: str
  acl_vlan_list:
    description: List of VLANs for which the ACL is to be applied or removed.
    required: true
    type: list
    elements: int
  acl_direction:
    description: Direction for which the ACL is to be applied or removed.
    choices:
      - in
      - out
    default: in
    type: str
  state:
    description: Create or delete the ACL configuration from the VLANs.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Apply ipv4 ACL to VLANs
  aoscx_acl_vlan:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_vlan_list:
      - 2
      - 4

- name: Remove ipv4 ACL from VLANs
  aoscx_acl_vlan:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_vlan_list:
      - 2
      - 4
    state: delete

- name: Apply ipv6 ACL to VLANs
  aoscx_acl_vlan:
    acl_name: ipv6_acl
    acl_type: ipv6
    acl_vlan_list:
      - 2
      - 4
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        acl_name=dict(type="str", required=True),
        acl_type=dict(
            type="str", required=True, choices=["ipv4", "ipv6", "mac"]
        ),
        acl_vlan_list=dict(type="list", elements="int", required=True),
        acl_direction=dict(type="str", default="in", choices=["in", "out"]),
        state=dict(type="str", default="create", choices=["create", "delete"]),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    # Set Variables
    acl_name = ansible_module.params["acl_name"]
    acl_vlan_list = ansible_module.params["acl_vlan_list"]
    acl_type = ansible_module.params["acl_type"]
    acl_direction = ansible_module.params["acl_direction"]
    state = ansible_module.params["state"]
    result = dict(changed=False)
    warnings = []
    warnings.append(
       "This module is deprecated, use aoscx_vlan instead"
    )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    for vlan_name in acl_vlan_list:
        # Create VLAN Object
        vlan = session.api.get_module(session, "Vlan", vlan_name)
        try:
            vlan.get()
        except Exception as e:
            ansible_module.fail_json(
                msg="VLAN {0}: {1}".format(vlan_name, str(e))
            )
        modified = False
        if state == "delete":
            # Delete acl
            modified |= vlan.clear_acl(acl_type, acl_direction)
            # Changed
            result["changed"] = modified

        if state == "create" or state == "update":
            modified |= vlan.set_acl(acl_name, acl_type, acl_direction)
            result["changed"] = modified

    # Exit
    ansible_module.exit_json(**result, warnings=warnings)


if __name__ == "__main__":
    main()
