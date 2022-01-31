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
version_added: "2.8.0"
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

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf import VRF


def main():
    module_args = dict(
        name=dict(type='str', required=True),
        state=dict(default='create', choices=['create', 'delete'])
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
        vrf_name = ansible_module.params['name']
        state = ansible_module.params['state']

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

        if state == 'delete':
            # Create VRF Object
            vrf = device.vrf(vrf_name)
            # Delete it
            vrf.delete()
            # Changed
            result['changed'] = vrf.was_modified()

        if state == 'create':
            # Create VRF with incoming attributes
            vrf = device.vrf(vrf_name)
            # Changed
            result['changed'] = vrf.was_modified()

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:

        aruba_ansible_module = ArubaAnsibleModule(module_args)

        vrf_name = aruba_ansible_module.module.params['name']
        state = aruba_ansible_module.module.params['state']

        vrf = VRF()

        if state == 'create':
            aruba_ansible_module = vrf.create_vrf(
                aruba_ansible_module, vrf_name)

        if state == 'delete':
            aruba_ansible_module = vrf.delete_vrf(
                aruba_ansible_module, vrf_name)

        aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
