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
module: aoscx_vlan
version_added: "2.8.0"
short_description: Create or Delete VLAN configuration on AOS-CX
description:
  - This modules provides configuration management of VLANs on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  vlan_id:
    description: The ID of this VLAN. Non-internal VLANs must have an 'id'
                 between 1 and 4094 to be effectively instantiated.
    required: true
    type: int
  name:
    description: VLAN name
    required: false
    type: str
  description:
    description: VLAN description
    required: false
    type: str
  admin_state:
    description: The Admin State of the VLAN, options are 'up' and 'down'.
    required: false
    choices: ['up', 'down']
    type: str
  state:
    description: Create or update or delete the VLAN.
    required: false
    choices: ['create', 'update', 'delete']
    default: create
    type: str
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

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vlan import VLAN
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule


def main():
    module_args = dict(
        vlan_id=dict(type='int', required=True),
        name=dict(type='str', default=None),
        description=dict(type='str', default=None),
        admin_state=dict(type='str', default=None, choices=['up', 'down']),
        state=dict(type='str', default='create', choices=['create', 'delete',
                                                          'update'])
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
        vlan_id = ansible_module.params['vlan_id']
        vlan_name = ansible_module.params['name']
        if vlan_name is None:
            vlan_name = "VLAN{vlan_id}".format(vlan_id=vlan_id)
        description = ansible_module.params['description']
        admin_state = ansible_module.params['admin_state']
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
            # Create Vlan Object
            vlan = device.vlan(vlan_id)
            # Delete it
            vlan.delete()
            # Changed
            result['changed'] = True

        elif state == 'update' or state == 'create':
            # Create Vlan with incoming attributes, in case VLAN does not exist
            # inside device
            vlan = device.vlan(
                vlan_id, vlan_name, description, "static", admin_state)

            if vlan.was_modified():
                # Changed
                result['changed'] = True

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:

        aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)

        vlan_id = aruba_ansible_module.module.params['vlan_id']
        vlan_name = aruba_ansible_module.module.params['name']
        description = aruba_ansible_module.module.params['description']
        admin_state = aruba_ansible_module.module.params['admin_state']
        state = aruba_ansible_module.module.params['state']

        vlan = VLAN()

        if state == 'delete':
            aruba_ansible_module = vlan.delete_vlan(
                aruba_ansible_module, vlan_id)

        if state == 'create':
            aruba_ansible_module = vlan.create_vlan(
                aruba_ansible_module, vlan_id)

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
            aruba_ansible_module = vlan.update_vlan_fields(
                aruba_ansible_module, vlan_id, vlan_fields, update_type='insert')

        if state == 'update':
            vlan_fields = {}
            if admin_state is not None:
                vlan_fields['admin'] = admin_state

            if description is not None:
                vlan_fields['description'] = description

            if state is not None:
                vlan_fields['state'] = state

            aruba_ansible_module = vlan.update_vlan_fields(
                aruba_ansible_module, vlan_id, vlan_fields, update_type='update')

        aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
