#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'certified'
}

DOCUMENTATION = '''
---
module: aoscx_banner
version_added: "2.8"
short_description: Create or Delete Banner configuration on AOS-CX
description:
  - This modules provides configuration management of Banner on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  banner_type:
    description: Type of banner being configured on the switch.
    required: True
    choices: ['banner', 'banner_exec']
    type: str

  state:
    description: Create or Delete Banner on the switch.
    default: create
    choices: ['create', 'delete']
    required: False
    type: str

  banner:
    description : String to be configured as the banner.
    required: True
    type: str
'''

EXAMPLES = '''
- name: Adding or Updating Banner
  aoscx_banner:
    banner_type: banner
    banner: "Aruba Rocks!"

- name: Delete Banner
  aoscx_banner:
    banner_type: banner
    state: delete

- name: Delete Exec Banner
  aoscx_banner:
    banner_type: banner_exec
    state: delete
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule  # NOQA


def main():
    module_args = dict(banner_type=dict(type='str', required=True,
                                        choices=['banner', 'banner_exec']),
                       banner=dict(type='str', required=False),
                       state=dict(default='create', choices=['create',
                                                             'delete']))

    aruba_ansible_module = ArubaAnsibleModule(module_args)
    state = aruba_ansible_module.module.params['state']
    banner_type = aruba_ansible_module.module.params['banner_type']
    banner = aruba_ansible_module.module.params['banner']

    if state == 'delete':
        if 'other_config' in aruba_ansible_module.running_config['System'].keys():  # NOQA
            if banner_type in aruba_ansible_module.running_config['System']["other_config"].keys():  # NOQA
                aruba_ansible_module.running_config['System']["other_config"].pop(banner_type)  # NOQA
            else:
                aruba_ansible_module.warnings.append("{x} has already been "
                                                     "removed"
                                                     "".format(x=banner_type))
        else:
            aruba_ansible_module.warnings.append("{x} has already been "
                                                 "removed"
                                                 "".format(x=banner_type))

        aruba_ansible_module.module.log('Banner is removed from the switch.')

    if state == 'create':

        if banner is None:
            banner = ""

        if 'other_config' not in aruba_ansible_module.running_config['System'].keys():  # NOQA
            aruba_ansible_module.running_config['System']["other_config"] = {}

        if banner_type not in aruba_ansible_module.running_config['System']["other_config"].keys():  # NOQA
            aruba_ansible_module.running_config['System']["other_config"][banner_type] = banner  # NOQA

        elif aruba_ansible_module.running_config['System']["other_config"][banner_type] != banner:  # NOQA
            aruba_ansible_module.running_config['System']["other_config"][banner_type] = banner  # NOQA

        aruba_ansible_module.module.log('Banner is added to the switch.')

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
