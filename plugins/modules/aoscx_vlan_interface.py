#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
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
module: aoscx_vlan_interface
version_added: "2.8"
short_description: Create or Delete VLAN Interface configuration on AOS-CX
description:
  - This modules provides configuration management of VLAN Interfacess on
    AOS-CX devices.
author:
  - Aruba Networks
options:
  vlan_id:
    description: The ID of this VLAN interface. Non-internal VLANs must have
                 an 'id' between 1 and 4094 to be effectively instantiated.
    required: true
  admin_state:
    description: Admin State status of vlan interface.
    default: 'up'
    choices: ['up', 'down']
    required: false
  ipv4:
    description: The IPv4 address and subnet mask in the address/mask format.
      The first entry in the list is the primary IPv4, the remainings are
      secondary IPv4. i.e. ['10.1.1.1/24', '10.2.1.3/255.255.254.0']. To remove
      an IP address pass in "" and set state: update.
    type: list
    required: False
  ipv6:
    description: The IPv6 address and subnet mask in the address/mask format.
      It takes multiple IPv6 with comma separated in the list.
      i.e. ['2000:cc92::2/64', '3000:820a::43/64']  . To remove an IP address
      pass in "" and set state: update.
    type: list
    required: False
  vrf:
    description: The VRF the vlan interface will belong to once created. If
      none provided, the interface will be in the Default VRF. If the VLAN
      interface is created and the user wants to change the interface vlan's
      VRF, the user must delete the VLAN interface then recreate the VLAN
      interface in the desired VRF.
    type: str
    required: False
  ip_helper_address:
    description: Configure a remote DHCP server/relay IP address on the vlan
      interface. Here the helper address is same as the DHCP server address or
      another intermediate DHCP relay.
    type: list
    required: False
  description:
    description: VLAN description
    required: false
  active_gateway_ip:
    description: Configure IPv4 active-gateway for vlan interface.
    type: string
    required: False
  active_gateway_mac_v4:
    description: Configure virtual MAC address for IPv4 active-gateway for
      vlan interface. Must be used in conjunction of active_gateway_ip
    type: string
    required: False
  state:
    description: Create or update or delete the VLAN.
    required: false
    choices: ['create', 'update', 'delete']
    default: create

'''  # NOQA

EXAMPLES = '''
     - name: Adding VLAN interface
       aoscx_vlan_interface:
         interface: "{{ item.interface }}"
         description: "{{ item.description }}"
       with_items:
         - { interface: 1/1/2, vlan_details: {"vlan_tag" 2, "vlan_mode":"access" }}
         - { interface: 1/1/3, vlan_details: {"vlan_tag" 2, "vlan_mode":"access" }}

     - name: Deleting interface
       aoscx_vlan_interface:
         interface: "{{ item.interface }}"
         state: "{{ item.state }}"
       with_items:
           - { interface: vlan2, state: absent }
           - { interface: vlan3, state: absent }
'''  # NOQA

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vlan import VLAN
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_port import Port
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_interface import Interface, L3_Interface


def main():
    module_args = dict(
        vlan_id=dict(type='str', required=True),
        admin_state=dict(type='str', required=False, choices=['up', 'down']),
        state=dict(default='create', choices=['create', 'delete', 'update']),
        ipv4=dict(type='list', default=None),
        description=dict(type='str', default=None),
        ipv6=dict(type='list', default=None),
        vrf=dict(type='str', default=None),
        ip_helper_address=dict(type='list', default=None),
        active_gateway_ip=dict(type='str', default=None),
        active_gateway_mac_v4=dict(type='str', default=None),
    )

    aruba_ansible_module = ArubaAnsibleModule(module_args)

    vlan_id = aruba_ansible_module.module.params['vlan_id']
    admin_state = aruba_ansible_module.module.params['admin_state']
    ipv4 = aruba_ansible_module.module.params['ipv4']
    ipv6 = aruba_ansible_module.module.params['ipv6']
    vrf = aruba_ansible_module.module.params['vrf']
    description = aruba_ansible_module.module.params['description']
    ip_helper_address = aruba_ansible_module.module.params['ip_helper_address']
    active_gateway_ip = aruba_ansible_module.module.params['active_gateway_ip']
    active_gateway_mac_v4 = aruba_ansible_module.module.params['active_gateway_mac_v4']  # NOQA
    state = aruba_ansible_module.module.params['state']

    vlan = VLAN()
    port = Port()
    interface = Interface()
    vlan_interface_id = "vlan" + vlan_id
    if not vlan.check_vlan_exist(aruba_ansible_module, vlan_id):
        aruba_ansible_module.module.fail_json(msg="VLAN {} does not exist. "
                                                  "VLAN needs to be created "
                                                  "before adding or deleting "
                                                  "interfaces".format(vlan_id))

    if state == 'create':
        aruba_ansible_module = port.create_port(aruba_ansible_module,
                                                vlan_interface_id)
        aruba_ansible_module = interface.create_interface(aruba_ansible_module,
                                                          vlan_interface_id)

        if admin_state is None:
            admin_state = 'up'

        user_config = {
            "admin": admin_state,
        }

        interface_fields = {
            "name": vlan_interface_id,
            "type": "vlan",
            "user_config": user_config
        }
        aruba_ansible_module = interface.update_interface_fields(aruba_ansible_module, vlan_interface_id, interface_fields)  # NOQA

        if vrf is not None:
            vrf_name = vrf
        else:
            vrf_name = "default"

        port_fields = {
            "interfaces": [vlan_interface_id],
            "vlan_tag": vlan_id,
            "vrf": vrf_name,
            "admin": admin_state
        }
        aruba_ansible_module = port.update_port_fields(aruba_ansible_module,
                                                       vlan_interface_id,
                                                       port_fields)

    if (state == 'create') or (state == 'update'):

        if not port.check_port_exists(aruba_ansible_module, vlan_interface_id):
            aruba_ansible_module.module.fail_json(msg="VLAN interface does not"
                                                      " exist")

        if admin_state is not None:
            port_fields = {"admin": admin_state}
            user_config = {"admin": admin_state}
            interface_fields = {"user_config": user_config}

        aruba_ansible_module = port.update_port_fields(aruba_ansible_module,
                                                       vlan_interface_id,
                                                       port_fields)
        aruba_ansible_module = interface.update_interface_fields(aruba_ansible_module, vlan_interface_id, interface_fields)  # NOQA

        if description is not None:
            port_fields = {"description": description}

            aruba_ansible_module = port.update_port_fields(aruba_ansible_module, vlan_interface_id, port_fields)  # NOQA

        if ipv4 is not None:
            l3_interface = L3_Interface()
            aruba_ansible_module = l3_interface.update_interface_ipv4_address(aruba_ansible_module, vlan_interface_id, ipv4)  # NOQA

        if ipv6 is not None:
            l3_interface = L3_Interface()
            aruba_ansible_module = l3_interface.update_interface_ipv6_address(aruba_ansible_module, vlan_interface_id, ipv6)  # NOQA

        if ip_helper_address is not None:
            l3_interface = L3_Interface()
            if vrf is None:
                vrf = "default"
            aruba_ansible_module = l3_interface.update_interface_ip_helper_address(aruba_ansible_module, vrf, vlan_interface_id, ip_helper_address)  # NOQA

        if vrf is not None:
            l3_interface = L3_Interface()
            aruba_ansible_module = l3_interface.update_interface_vrf_details_from_l3(aruba_ansible_module, vrf, vlan_interface_id, update_type="insert")  # NOQA

        if (active_gateway_ip is not None) and (active_gateway_mac_v4 is None):
            aruba_ansible_module.module.fail_json(msg=" Both active_gateway_ip and active_gateway_mac_v4 are required for configure active gateway.")  # NOQA
        elif (active_gateway_ip is  None) and (active_gateway_mac_v4 is not None):  # NOQA
            aruba_ansible_module.module.fail_json(msg=" Both active_gateway_ip and active_gateway_mac_v4 are required for configure active gateway.")  # NOQA
        elif (active_gateway_ip is not None) and (active_gateway_mac_v4 is not None):  # NOQA
            port_fields = {"vsx_virtual_ip4": active_gateway_ip,
                           "vsx_virtual_gw_mac_v4": active_gateway_mac_v4
                           }
            aruba_ansible_module = port.update_port_fields(aruba_ansible_module, vlan_interface_id, port_fields)  # NOQA

    if state == 'delete':
        aruba_ansible_module = port.delete_port(aruba_ansible_module,
                                                vlan_interface_id)
        aruba_ansible_module = interface.delete_interface(aruba_ansible_module,
                                                          vlan_interface_id)

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
