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
module: aoscx_vsx
version_added: "2.8"
short_description: Create or Delete VSX configuration on AOS-CX
description:
  - This modules provides configuration management of VSX on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  role:
    description: Role for the device to take, either primary or secondary.
    required: true
    choices: ['primary', 'secondary']
    default: 'primary'
    type: str
  isl_port:
    description: Inter switch link port, interface to use on the device for ISL.
    required: true
    type: str
  keepalive_interface:
    description: Interface to use for keepalive connection on the device.
    required: false
    type: str
  keepalive_peer:
    description: IP address of the keepalive peer device. Must be set if keepalive_src is also set.
    required: false
    type: str
  keepalive_src:
    description: IP address to use as the keep alive source on the device. Must be set if keepalive_peer is also set.
    required: false
    type: str
  keepalive_vrf:
    description: VRF for keep alive function.
    required: false
    default: 'default'
    type: str
  vsx_mac:
    description: MAC address to assign to the VSX.
    required: false
    type: str
  state:
    description: Create or delete VSX configuration.
    required: true
    choices: ['create', 'delete']
    default: 'create'
    type: str
'''

EXAMPLES = '''
- name: Create VSX configuration
  aoscx_vsx:
    role: primary
    isl_port: 1/1/1
    state: create
- name: Delete VSX configuration
  aoscx_vsx:
    state: delete
- name: Create VSX configuration with lag
  aoscx_vsx:
    role: primary
    isl_port: lag1
    keepalive_vrf: red
    state: create
'''

RETURN = r''' # '''

import ansible.module_utils.aoscx_vsx as vsx
from ansible.module_utils.aoscx_pyaoscx import Session
from ansible.module_utils.basic import AnsibleModule
import os


def run_module():
    module_args = dict(
        role=dict(type='str', default='primary', choices=[
            'primary', 'secondary']),
        isl_port=dict(type='str', default=None),
        keepalive_interface=dict(type='str', default=None),
        keepalive_peer=dict(type='str', default=None),
        keepalive_src=dict(type='str', default=None),
        keepalive_vrf=dict(type='str', default='default'),
        vsx_mac=dict(type='str', default=None),
        state=dict(type='str', default='create', choices=['create', 'delete']))

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

        # ArubaModule
        ansible_module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True)

        # Session
        session = Session(ansible_module)

        # Set Variables
        role = ansible_module.params['role']
        isl_port = ansible_module.params['isl_port']
        keepalive_interface = ansible_module.params['keepalive_interface']
        keepalive_peer = ansible_module.params['keepalive_peer']
        keepalive_src = ansible_module.params['keepalive_src']
        keepalive_vrf = ansible_module.params['keepalive_vrf']
        vsx_mac = ansible_module.params['vsx_mac']
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
            # Create VSX Object
            vsx = device.vsx()
            # Delete it
            vsx.delete()

        if state == 'create':
            # Create VSX with incoming attributes
            vsx = device.vsx(role, isl_port, keepalive_vrf,
                                      keepalive_peer, keepalive_src, vsx_mac)

        # Exit
        ansible_module.exit_json(**result)

    else:
        raise Exception("pyoascx not installed")


def main():
    run_module()


if __name__ == '__main__':
    main()
