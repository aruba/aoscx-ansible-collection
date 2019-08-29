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
module: aoscx_vrf
version_added: "2.8"
short_description: Create or Delete VRF configuration on AOS-CX
description:
  - This modules provides configuration management of VRFs on AOS-CX devices.
author:
  - Aruba Networks
options:
  name:
    description: The name of the VRF
    required: true
  state:
    description: Create or delete the VRF.
    required: false
    choices: ['create', 'delete']
    default: create
'''

EXAMPLES = '''
- name: Create a VRF
  aoscx_vrf:
    name: red
    state: create

- name: Delete a VRF
  aoscx_vrf:
    name: red
    state: delete
'''  # NOQA

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vrf import VRF


def main():
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(default='create', choices=['create', 'delete'])
    )

    aruba_ansible_module = ArubaAnsibleModule(module_args)

    vrf_name = aruba_ansible_module.module.params['name']
    state = aruba_ansible_module.module.params['state']

    vrf = VRF()

    if state == 'create':
        aruba_ansible_module = vrf.create_vrf(aruba_ansible_module, vrf_name)

    if state == 'delete':
        aruba_ansible_module = vrf.delete_vrf(aruba_ansible_module, vrf_name)

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
