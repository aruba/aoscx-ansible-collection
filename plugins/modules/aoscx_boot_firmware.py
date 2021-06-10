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
module: aoscx_boot_firmware
version_added: "2.8"
short_description:  Boots the AOS-CX switch with image present to the specified partition
description:
  - This module boots the AOS-CX switch with the image present to the specified partition.
author: Aruba Networks (@ArubaNetworks)
options:
  partition_name:
    description: Name of the partition for device to boot to.
    type: str
    default: 'primary'
    choices: ['primary', 'secondary']
    required: false
'''

EXAMPLES = '''
- name: Boot to primary
  aoscx_boot_firmware:
    partition_name: 'primary'

- name: Boot to secondary
  aoscx_boot_firmware:
    partition_name: 'secondary'
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule, post

def main():
    module_args = dict(
        partition_name=dict(type='str', default='primary',
                            choices=['primary', 'secondary']),
    )

    # Version management
    try:

        from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import Session
        from pyaoscx.session import Session as Pyaoscx_Session
        from pyaoscx.pyaoscx_factory import PyaoscxFactory

        USE_PYAOSCX_SDK = True

    except ImportError:
        USE_PYAOSCX_SDK = False

    # Use PYAOSCX SDK
    if USE_PYAOSCX_SDK:
        from ansible.module_utils.basic import AnsibleModule

        # ArubaModule
        ansible_module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True)

        # Session
        session = Session(ansible_module)

        # Set Variables
        partition_name = ansible_module.params['partition_name']

        result = dict(
            changed=False
        )

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)

        # Get session serialized information
        session_info = session.get_session()
        # Create pyaoscx.session object
        s = Pyaoscx_Session.from_session(
            session_info['s'], session_info['url'])

        # Create a Pyaoscx Factory Object
        pyaoscx_factory = PyaoscxFactory(s)

        # Create a Device Object
        device = pyaoscx_factory.device()
        success = device.boot_firmware(partition_name)

        # Changed
        result['changed'] = success

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(
            module_args=module_args, store_config=False)
        partition_name = aruba_ansible_module.module.params['partition_name']

        url = '/rest/v1/boot?image={part}'.format(part=partition_name)
        post(aruba_ansible_module.module, url)

        result = dict(changed=aruba_ansible_module.changed,
                      warnings=aruba_ansible_module.warnings)
        result["changed"] = True
        aruba_ansible_module.module.exit_json(**result)


if __name__ == '__main__':
    main()
