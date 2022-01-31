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
module: aoscx_checkpoint
version_added: "2.8.0"
short_description: Creates a new checkpoint or copies an existing checkpoint to AOS-CX switch config.
description:
  - This module creates a new checkpoint or copies existing checkpoint
    to the running or startup config of an AOS-CX switch.
author: Aruba Networks (@ArubaNetworks)
options:
  source_config:
    description: Name of the source configuration from which checkpoint needs
      to be created or copied.
    type: str
    required: False
    default: 'running-config'

  destination_config:
    description: Name of the destination configuration or name of checkpoint.
    type: str
    required: False
    default: 'startup-config'
'''

EXAMPLES = '''
- name: Copy running-config to startup-config
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'startup-config'

- name: Copy startup-config to running-config
  aoscx_checkpoint:
    source_config: 'startup-config'
    destination_config: 'running-config'

- name: Copy running-config to backup checkpoint
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'checkpoint_20200128'
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule, put


def main():
    module_args = dict(
        source_config=dict(type='str', default='running-config'),
        destination_config=dict(type='str', default='startup-config')
    )

    # Version management
    try:

        from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import Session
        from pyaoscx.session import Session as Pyaoscx_Session
        from pyaoscx.device import Device

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
        source_config = ansible_module.params['source_config']
        destination_config = ansible_module.params['destination_config']

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

        # Create a Pyaoscx Device Object
        device = Device(s)

        # Create a Configuration Object
        config = device.configuration()
        success = config.create_checkpoint(source_config, destination_config)

        # Changed
        result['changed'] = success

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)

        source_config = aruba_ansible_module.module.params['source_config']
        destination_config = \
            aruba_ansible_module.module.params['destination_config']

        url = '/rest/v1/fullconfigs/{dest}?from=/rest/v1/fullconfigs/{src}'.format(
            dest=destination_config, src=source_config)
        put(aruba_ansible_module.module, url)
        result = dict(changed=aruba_ansible_module.changed,
                      warnings=aruba_ansible_module.warnings)
        result["changed"] = True
        aruba_ansible_module.module.exit_json(**result)


if __name__ == '__main__':
    main()
