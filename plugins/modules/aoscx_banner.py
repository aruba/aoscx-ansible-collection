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

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule

def main():
    module_args = dict(banner_type=dict(type='str', required=True,
                                        choices=['banner', 'banner_exec']),
                       banner=dict(type='str', required=False),
                       state=dict(default='create', choices=['create',
                                                             'delete']))

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
        state = ansible_module.params['state']
        banner_type = ansible_module.params['banner_type']
        banner = ansible_module.params['banner']

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
        # Create Device Object
        device = pyaoscx_factory.device()

        if state == 'delete':
            # Delete it
            modified_op = device.delete_banner(banner_type)

        if state == 'create' or state == 'update':
            # Set Banner
            modified_op = device.update_banner(banner, banner_type)

        # Changed
        result['changed'] = modified_op

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
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

            aruba_ansible_module.module.log(
                'Banner is removed from the switch.')

        if state == 'create':

            if banner is None:
                banner = ""

            if 'other_config' not in aruba_ansible_module.running_config['System'].keys():  # NOQA
                aruba_ansible_module.running_config['System']["other_config"] = {
                }

            if banner_type not in aruba_ansible_module.running_config['System']["other_config"].keys():  # NOQA
                aruba_ansible_module.running_config['System']["other_config"][banner_type] = banner  # NOQA

            elif aruba_ansible_module.running_config['System']["other_config"][banner_type] != banner:  # NOQA
                aruba_ansible_module.running_config['System']["other_config"][banner_type] = banner  # NOQA

            aruba_ansible_module.module.log('Banner is added to the switch.')

        aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
