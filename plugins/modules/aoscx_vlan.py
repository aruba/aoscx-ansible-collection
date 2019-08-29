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
module: aoscx_vlan
version_added: "2.8"
short_description: Create or Delete VLAN configuration on AOS-CX
description:
  - This modules provides configuration management of VLANs on AOS-CX devices.
author:
  - Aruba Networks
options:
  vlan_id:
    description: The ID of this VLAN. Non-internal VLANs must have an 'id'
                 between 1 and 4094 to be effectively instantiated.
    required: true
  name:
    description: VLAN name
    required: false
  description:
    description: VLAN description
    required: false
  admin_state:
    description: The Admin State of the VLAN, options are 'up' and 'down'.
    required: false
    choices: ['up', 'down']
    default: None
  state:
    description: Create or update or delete the VLAN.
    required: false
    choices: ['create', 'update', 'delete']
    default: create
'''

EXAMPLES = '''
- name: Create VLAN 200 with description
  aoscx_vlan:
    vlan_id: 200
    description: This is VLAN 200

- name: Create VLAN 300 with description and name
  aoscx_vlan:
    vlan_id: 300
    name: UPLINK_VLAN
    description: This is VLAN 300

- name: Delete VLAN 300
  aoscx_vlan:
    vlan_id: 300
    state: delete
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vlan import VLAN


def main():
    module_args = dict(
        vlan_id=dict(type='int', required=True),
        name=dict(type='str', default=None),
        description=dict(type='str', default=None),
        admin_state=dict(type='str', default=None, choices=[None,
                                                            'up', 'down']),
        state=dict(type='str', default='create', choices=['create', 'delete',
                                                          'update'])
    )

    aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)

    vlan_id = aruba_ansible_module.module.params['vlan_id']
    vlan_name = aruba_ansible_module.module.params['name']
    description = aruba_ansible_module.module.params['description']
    admin_state = aruba_ansible_module.module.params['admin_state']
    state = aruba_ansible_module.module.params['state']

    vlan = VLAN()

    if state == 'delete':
        aruba_ansible_module = vlan.delete_vlan(aruba_ansible_module, vlan_id)

    if state == 'create':
        aruba_ansible_module = vlan.create_vlan(aruba_ansible_module, vlan_id)

        if vlan_name is not None:
            name = vlan_name
        else:
            name = "VLAN " + str(vlan_id)

        if admin_state is None:
            admin_state = 'up'

        vlan_fields = {
            "name": name,
            "admin": admin_state,
            "type": "static"
        }
        if description is not None:
            vlan_fields["description"] = description
        aruba_ansible_module = vlan.update_vlan_fields(aruba_ansible_module,
                                                       vlan_id, vlan_fields,
                                                       update_type='insert')

    if state == 'update':
        vlan_fields = {}
        if admin_state is not None:
            vlan_fields['admin'] = admin_state

        if description is not None:
            vlan_fields['description'] = description

        if state is not None:
            vlan_fields['state'] = state

        aruba_ansible_module = vlan.update_vlan_fields(aruba_ansible_module,
                                                       vlan_id, vlan_fields,
                                                       update_type='update')

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
