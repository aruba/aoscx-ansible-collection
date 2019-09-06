#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
# -*- coding: utf-8 -*-
#
# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'certified'
}

DOCUMENTATION = '''
---
module: aoscx_acl_vlan
version_added: "2.8"
short_description: Apply/Remove ACL configuration on VLANs for AOS-CX.
description:
  - This modules provides application management of Access Classifier Lists
  on VLANs on AOS-CX devices.
author:
  - Aruba Networks
options:
  acl_name:
    description: Name of the ACL being applied or removed from the VLAN.
    required: true

  acl_type:
    description: Type of ACL being applied or removed from the VLAN.
    choices: ['ipv4', 'ipv6', 'mac']
    required: true

  acl_vlan_list:
    description: List of VLANs for which the ACL is to be applied or removed.
    required: true

  acl_direction:
    description: Direction for which the ACL is to be applied or removed.
    required: true
    choices: ['in', 'out']
    default: 'in'

  state:
    description: Create or delete the ACL configuration from the VLANs.
    required: false
    choices: ['create', 'delete']
    default: create
'''

EXAMPLES = '''
- name: Apply ipv4 ACL to VLANs
  aoscx_acl_vlan:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_vlan_list: [2, 4]

- name: Remove ipv4 ACL from VLANs
  aoscx_acl_vlan:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_vlan_list: [2, 4]
    state: delete

- name: Apply ipv6 ACL to VLANs
  aoscx_acl_vlan:
    acl_name: ipv6_acl
    acl_type: ipv6
    acl_vlan_list: [2, 4]
'''

RETURN = r''' # '''

from random import randint
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vlan import VLAN


def main():
    module_args = dict(
        acl_name=dict(type='str', required=True),
        acl_type=dict(type='str', required=True, choices=['ipv4',
                                                          'ipv6', 'mac']),
        acl_vlan_list=dict(type='list', required=True),
        acl_direction=dict(type='str', default='in', choices=['in', 'out']),
        state=dict(type='str', default='create', choices=['create', 'delete'])
    )

    aruba_ansible_module = ArubaAnsibleModule(module_args)

    acl_name = aruba_ansible_module.module.params['acl_name']
    acl_vlan_list = aruba_ansible_module.module.params['acl_vlan_list']
    acl_type = aruba_ansible_module.module.params['acl_type']
    acl_direction = aruba_ansible_module.module.params['acl_direction']
    state = aruba_ansible_module.module.params['state']

    acl_type_prefix = ""
    if acl_type == "ipv4":
        acl_type_prefix = "aclv4"
    elif acl_type == "ipv6":
        acl_type_prefix = "aclv6"
    elif acl_type == "mac":
        acl_type_prefix = "aclmac"

    vlan = VLAN()

    for vlan_id in acl_vlan_list:
        field1 = '{}_{}_cfg'.format(acl_type_prefix, acl_direction)
        value1 = '{}/{}'.format(acl_name, acl_type)
        field2 = '{}_{}_cfg_version'.format(acl_type_prefix, acl_direction)
        value2 = randint(-900719925474099, 900719925474099)

        vlan_fields = {field1: value1, field2: value2}

        if (state == 'create') or (state == 'update'):

            existing_values = vlan.get_vlan_fields_values(aruba_ansible_module,
                                                          vlan_id,
                                                          [field1])

            if field1 in existing_values.keys():
                if existing_values[field1] != vlan_fields[field1]:
                    aruba_ansible_module = vlan.update_vlan_fields(aruba_ansible_module, vlan_id, vlan_fields, update_type='insert')  # NOQA
            else:
                aruba_ansible_module = vlan.update_vlan_fields(aruba_ansible_module, vlan_id, vlan_fields, update_type='insert')  # NOQA

            if state == 'create':
                aruba_ansible_module.module.log(msg=" Inserted ACL {} of type {} to VLAN {}".format(acl_name, acl_type, vlan_id))  # NOQA

            if state == 'update':
                aruba_ansible_module.module.log(msg=" Updated  ACL {} of type {} to VLAN {}".format(acl_name, acl_type, vlan_id))  # NOQA
        elif state == 'delete':
            aruba_ansible_module = vlan.update_vlan_fields(aruba_ansible_module, vlan_id, vlan_fields, update_type='delete')  # NOQA
            aruba_ansible_module.module.log(msg="Deleted ACL {} of type {} from VLAN {}".format(acl_name, acl_type, vlan_id))  # NOQA

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
