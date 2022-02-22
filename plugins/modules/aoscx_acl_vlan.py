#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
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

from random import randint

try:
    from pyaoscx.device import Device

    USE_PYAOSCX_SDK = True
except ImportError:
    USE_PYAOSCX_SDK = False

if USE_PYAOSCX_SDK:
    from ansible.module_utils.basic import AnsibleModule
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )
else:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import (  # NOQA
        ArubaAnsibleModule,
    )
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vlan import (  # NOQA
        VLAN,
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
    if USE_PYAOSCX_SDK:
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

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)

        session = get_pyaoscx_session(ansible_module)

        # Create a Pyaoscx Device Object
        device = Device(session)

        for vlan_name in acl_vlan_list:
            if state == "delete":
                # Create VLAN Object
                vlan = device.vlan(vlan_name)
                # Delete acl
                if acl_direction == "in":
                    vlan.detach_acl_in(acl_name, acl_type)
                if acl_direction == "out":
                    vlan.detach_acl_out(acl_name, acl_type)
                # Changed
                result["changed"] = True

            if state == "create" or state == "update":
                # Create VLAN Object
                vlan = device.vlan(vlan_name)
                # Verify if interface was create
                if vlan.was_modified():
                    # Changed
                    result["changed"] = True
                # Set variables
                modified_op1 = False
                modified_op2 = False
                # Update ACL inside VLAN
                if acl_direction == "in":
                    modified_op1 = vlan.attach_acl_in(acl_name, acl_type)
                if acl_direction == "out":
                    modified_op2 = vlan.attach_acl_out(acl_name, acl_type)
                if modified_op1 or modified_op2:
                    # Changed
                    result["changed"] = True

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args)

        acl_name = aruba_ansible_module.module.params["acl_name"]
        acl_vlan_list = aruba_ansible_module.module.params["acl_vlan_list"]
        acl_type = aruba_ansible_module.module.params["acl_type"]
        acl_direction = aruba_ansible_module.module.params["acl_direction"]
        state = aruba_ansible_module.module.params["state"]

        acl_type_prefix = ""
        if acl_type == "ipv4":
            acl_type_prefix = "aclv4"
        elif acl_type == "ipv6":
            acl_type_prefix = "aclv6"
        elif acl_type == "mac":
            acl_type_prefix = "aclmac"

        vlan = VLAN()

        for vlan_id in acl_vlan_list:
            field1 = "{0}_{1}_cfg".format(acl_type_prefix, acl_direction)
            value1 = "{0}/{1}".format(acl_name, acl_type)
            field2 = "{0}_{1}_cfg_version".format(
                acl_type_prefix, acl_direction
            )
            value2 = randint(-900719925474099, 900719925474099)

            vlan_fields = {field1: value1, field2: value2}

            if state in ("create", "update"):
                existing_values = vlan.get_vlan_fields_values(
                    aruba_ansible_module, vlan_id, [field1]
                )

                if field1 in existing_values.keys():
                    if existing_values[field1] != vlan_fields[field1]:
                        aruba_ansible_module = vlan.update_vlan_fields(
                            aruba_ansible_module,
                            vlan_id,
                            vlan_fields,
                            update_type="insert",
                        )
                else:
                    aruba_ansible_module = vlan.update_vlan_fields(
                        aruba_ansible_module,
                        vlan_id,
                        vlan_fields,
                        update_type="insert",
                    )

                if state == "create":
                    aruba_ansible_module.module.log(
                        msg="Inserted ACL {0} of type {1} from VLAN "
                        "{2}".format(acl_name, acl_type, vlan_id)
                    )

                if state == "update":
                    aruba_ansible_module.module.log(
                        msg="Updated ACL {0} of type {1} from VLAN {2}".format(
                            acl_name, acl_type, vlan_id
                        )
                    )
            elif state == "delete":
                aruba_ansible_module = vlan.update_vlan_fields(
                    aruba_ansible_module,
                    vlan_id,
                    vlan_fields,
                    update_type="delete",
                )
                aruba_ansible_module.module.log(
                    msg="Deleted ACL {0} of type {1} from VLAN {2}".format(
                        acl_name, acl_type, vlan_id
                    )
                )

        aruba_ansible_module.update_switch_config()


if __name__ == "__main__":
    main()
