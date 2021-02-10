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
module: aoscx_backup_config
version_added: "2.8"
short_description: Download an existing configuration from AOS-CX switch.
description:
  - This module downloads an existing configuration from AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  config_name:
    description: "Config file or checkpoint to be downloaded. When using TFTP
      only running-config or startup-config can be used"
    type: str
    default: 'running-config'
    required: false
  output_file:
    description: "File name and path for locally downloading configuration,
      only JSON version of configuration will be downloaded"
    type: str
    required: false
  remote_output_file_tftp_path:
    description: "TFTP server address and path for copying off configuration,
      must be reachable through provided vrf
      ex) tftp://192.168.1.2/config.txt"
    type: str
    required: false
  config_type:
    description: Configuration type to be downloaded, JSON or CLI version of the config.
    type: str
    choices: ['json', 'cli']
    default: 'json'
    required: false
  vrf:
    description: VRF to be used to contact TFTP server, required if remote_output_file_tftp_path is provided
    type: str
    required: false
  sort_json:
    description: flag whether or not to sort JSON config
    type: bool
    default: True
    required: false
'''  # NOQA

EXAMPLES = '''
 - name: Copy Running Config to local as JSON
   aoscx_backup_config:
     config_name: 'running-config'
     output_file: '/home/admin/running-config.json'

 - name: Copy Startup Config to local as JSON
   aoscx_backup_config:
     config_name: 'startup-config'
     output_file: '/home/admin/startup-config.json'

 - name: Copy Checkpoint Config to local as JSON
   aoscx_backup_config:
     config_name: 'checkpoint1'
     output_file: '/home/admin/checkpoint1.json'

 - name: Copy Running Config to TFTP server as JSON
   aoscx_backup_config:
     config_name: 'running-config'
     remote_output_file_tftp_path: 'tftp://192.168.1.2/running.json'
     config_type: 'json'
     vrf: 'mgmt'

 - name: Copy Running Config to TFTP server as CLI
   aoscx_backup_config:
     config_name: 'running-config'
     remote_output_file_tftp_path: 'tftp://192.168.1.2/running.cli'
     config_type: 'cli'
     vrf: 'mgmt'

 - name: Copy Startup Config to TFTP server as CLI
   aoscx_backup_config:
     config_name: 'startup-config'
     remote_output_file_tftp_path: 'tftp://192.168.1.2/startup.cli'
     config_type: 'cli'
     vrf: 'mgmt'
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule, comp_sort  # NOQA
import json


def main():
    module_args = dict(
        config_name=dict(type='str', default='running-config'),
        output_file=dict(type='str', default=None),
        remote_output_file_tftp_path=dict(type='str', default=None),
        config_type=dict(type='str', default='json', choices=['json', 'cli']),
        vrf=dict(type='str'),
        sort_json=dict(type='bool', default=True)
    )

    aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)

    tftp_path = \
        aruba_ansible_module.module.params['remote_output_file_tftp_path']
    vrf = aruba_ansible_module.module.params['vrf']
    config_name = aruba_ansible_module.module.params['config_name']
    config_type = aruba_ansible_module.module.params['config_type']
    config_file = aruba_ansible_module.module.params['output_file']
    sort_json = aruba_ansible_module.module.params['sort_json']

    if tftp_path is not None:
        if vrf is None:
            aruba_ansible_module.module.fail_json(
                msg="VRF needs to be provided in order to TFTP "
                    "the configuration from the switch")
        tftp_path_replace = tftp_path.replace("/", "%2F")
        tftp_path_encoded = tftp_path_replace.replace(":", "%3A")
        if config_name != 'running-config' and config_name != 'startup-config':
            aruba_ansible_module.module.fail_json(
                msg="Only running-config or "
                    "startup-config can be backed-up using TFTP")
        aruba_ansible_module.copy_switch_config_to_remote_location(
            config_name, config_type, tftp_path_encoded, vrf)
    else:

        config_json = aruba_ansible_module.get_switch_config(
            store_config=False)
        if sort_json:
            config_json = comp_sort(config_json)
        with open(config_file, 'w') as to_file:
            formatted_file = json.dumps(config_json, indent=4)
            to_file.write(formatted_file)

    result = dict(changed=aruba_ansible_module.changed,
                  warnings=aruba_ansible_module.warnings)
    result["changed"] = True
    aruba_ansible_module.module.exit_json(**result)


if __name__ == '__main__':
    main()
