#!/usr/bin/python
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
module: aoscx_acl_interface
version_added: "2.8"
short_description: Apply/Remove ACL configuration on interfaces for AOS-CX.
description:
  - This modules provides application management of Access Classifier Lists
  on Interfaces on AOS-CX devices.
author:
  - Aruba Networks
options:
  acl_name:
    description: Name of the ACL being applied or removed from the interface.
    required: true

  acl_type:
    description: Type of ACL being applied or removed from the interfaces.
    choices: ['ipv4', 'ipv6', 'mac']
    required: true

  acl_interface_list:
    description: List of interfaces for which the ACL is to be applied or
      removed.
    required: true

  acl_direction:
    description: Direction for which the ACL is to be applied or removed.
    required: true
    choices: ['in', 'out']
    default: 'in'

  state:
    description: Create or delete the ACL configuration from the interfaces.
    required: false
    choices: ['create', 'delete']
    default: create
'''

EXAMPLES = '''
- name: Apply ipv4 ACL to interfaces
  aoscx_acl_interface:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_interface_list: ["1/1/2", "1/2/23"]

- name: Remove ipv4 ACL from interfaces
  aoscx_acl_interface:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_interface_list: ["1/1/2", "1/2/23"]
    state: delete

- name: Apply ipv6 ACL to Interfaces
  aoscx_acl_interface:
    acl_name: ipv6_acl
    acl_type: ipv6
    acl_interface_list: ["1/1/2", "1/2/23"]
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_interface import Interface


def main():
    module_args = dict(
        acl_name=dict(type='str', required=True),
        acl_type=dict(type='str', required=True, choices=['ipv4',
                                                          'ipv6', 'mac']),
        acl_interface_list=dict(type='list', required=True),
        acl_direction=dict(type='str', default='in', choices=['in', 'out']),
        state=dict(type='str', default='create', choices=['create', 'delete'])
    )

    aruba_ansible_module = ArubaAnsibleModule(module_args)

    acl_name = aruba_ansible_module.module.params['acl_name']
    acl_interface_list = aruba_ansible_module.module.params['acl_interface_list']  # NOQA
    acl_type = aruba_ansible_module.module.params['acl_type']
    acl_direction = aruba_ansible_module.module.params['acl_direction']
    state = aruba_ansible_module.module.params['state']

    interface = Interface()

    for interface_name in acl_interface_list:
        if not interface.check_interface_exists(aruba_ansible_module,
                                                interface_name):
            aruba_ansible_module.module.fail_json(msg="Interface {} is not "
                                                      "configured"
                                                      "".format(interface_name)
                                                  )

        if (state == 'create') or (state == 'update'):
            update_type = 'insert'
        elif (state == 'delete'):
            update_type = 'delete'
        aruba_ansible_module = interface.update_interface_acl_details(
            aruba_ansible_module, interface_name, acl_name, acl_type,
            acl_direction, update_type)

        if update_type == 'insert':
            aruba_ansible_module.module.log(msg="Attached ACL {} of type "
                                                "{} to interface {}"
                                                "".format(acl_name,
                                                          acl_type,
                                                          interface_name))

        if update_type == 'update':
            aruba_ansible_module.module.log(msg="Updated ACL {} of type {} attached to interface {}".format(acl_name, acl_type, interface_name))  # NOQA

        if (update_type == 'absent') or (update_type == 'delete'):
            aruba_ansible_module.module.log(
                msg="Removed ACL {} of type {} from interface {}".format(
                    acl_name, acl_type, interface_name))

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
