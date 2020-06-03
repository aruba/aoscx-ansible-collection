#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


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
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: The name of the VRF
    required: true
    type: str
  state:
    description: Create or delete the VRF.
    required: false
    choices: ['create', 'delete']
    default: create
    type: str
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

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf import VRF
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule


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
