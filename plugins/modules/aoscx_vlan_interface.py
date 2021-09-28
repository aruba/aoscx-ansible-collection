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
module: aoscx_vlan_interface
version_added: "2.8"
short_description: Create or Delete VLAN Interface configuration on AOS-CX
description:
  - This modules provides configuration management of VLAN Interfacess on
    AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  vlan_id:
    description: The ID of this VLAN interface. Non-internal VLANs must have
                 an 'id' between 1 and 4094 to be effectively instantiated.
    required: true
    type: str
  admin_state:
    description: Admin State status of vlan interface.
    choices: ['up', 'down']
    required: false
    type: str
  ipv4:
    description: "The IPv4 address and subnet mask in the address/mask format.
      The first entry in the list is the primary IPv4, the remainings are
      secondary IPv4. i.e. ['10.1.1.1/24', '10.2.1.3/255.255.254.0']. To remove
      an IP address pass in '' and set state: update."
    type: list
    required: False
  ipv6:
    description: "The IPv6 address and subnet mask in the address/mask format.
      It takes multiple IPv6 with comma separated in the list.
      i.e. ['2000:cc92::2/64', '3000:820a::43/64']  . To remove an IP address
      pass in '' and set state: update."
    type: list
    required: False
  vrf:
    description: "The VRF the vlan interface will belong to once created. If
      none provided, the interface will be in the Default VRF. If the VLAN
      interface is created and the user wants to change the interface vlan's
      VRF, the user must delete the VLAN interface then recreate the VLAN
      interface in the desired VRF."
    type: str
    required: False
  ip_helper_address:
    description: "Configure a remote DHCP server/relay IP address on the vlan
      interface. Here the helper address is same as the DHCP server address or
      another intermediate DHCP relay."
    type: list
    required: False
  description:
    description: VLAN description
    required: false
    type: str
  active_gateway_ip:
    description: Configure IPv4 active-gateway for vlan interface.
    type: str
    required: False
  active_gateway_mac_v4:
    description: "Configure virtual MAC address for IPv4 active-gateway for
      vlan interface. Must be used in conjunction of active_gateway_ip"
    type: str
    required: False
  state:
    description: Create or update or delete the VLAN.
    required: false
    choices: ['create', 'update', 'delete']
    default: create
    type: str
'''  # NOQA

EXAMPLES = '''
  - name: Create VLAN Interface 100
    aoscx_vlan_interface:
      vlan_id: 100
      description: UPLINK_VLAN
      ipv4: ['10.10.20.1/24']
      ipv6: ['2000:db8::1234/64']

  - name: Create VLAN Interface 200
    aoscx_vlan_interface:
      vlan_id: 200
      description: UPLINK_VLAN
      ipv4: ['10.20.20.1/24']
      ipv6: ['3000:db8::1234/64']
      vrf: red
      ip_helper_address: ['10.40.20.1']

  - name: Delete VLAN Interface 100
    aoscx_vlan_interface:
      vlan_id: 100
      state: delete
'''  # NOQA

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_interface import Interface, L3_Interface
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_port import Port
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vlan import VLAN
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule


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

    # Version management
    try:
        from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import Session
        from pyaoscx.session import Session as Pyaoscx_Session
        from pyaoscx.device import Device

        USE_PYAOSCX_SDK = True

    except ImportError:

        USE_PYAOSCX_SDK = False

    if USE_PYAOSCX_SDK:
        from ansible.module_utils.basic import AnsibleModule

        # ArubaModule
        ansible_module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True)

        vlan_id = ansible_module.params['vlan_id']
        admin_state = ansible_module.params['admin_state']
        ipv4 = ansible_module.params['ipv4']
        ipv6 = ansible_module.params['ipv6']
        vrf = ansible_module.params['vrf']
        description = ansible_module.params['description']
        ip_helper_address = ansible_module.params['ip_helper_address']  # NOQA
        active_gateway_ip = ansible_module.params['active_gateway_ip']
        active_gateway_mac_v4 = ansible_module.params['active_gateway_mac_v4']
        state = ansible_module.params['state']

        # Set IP variable as empty arrays
        if ipv4 ==['']:
            ipv4 = []
        if ipv6 == ['']:
            ipv6 = []

        # Session
        session = Session(ansible_module)

        # Set variables
        vlan_interface_id = "vlan" + vlan_id
        if admin_state is None:
            admin_state = 'up'
        if vrf is not None:
            vrf_name = vrf
        else:
            vrf_name = "default"

        # Set result var
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
            # Create Interface Object
            vlan_interface = device.interface(vlan_interface_id)
            # Delete it
            vlan_interface.delete()
            # Changed
            result['changed'] = True

        if state == 'create' or state == 'update':
            # Create Interface with incoming attributes
            vlan_interface = device.interface(vlan_interface_id)
            # Verify if interface was create
            if vlan_interface.was_modified():
                # Changed
                result['changed'] = True

            # Configure SVI
            # Verify if object was changed
            modified_op = vlan_interface.configure_svi(
                vlan=int(vlan_id),
                ipv4=ipv4,
                ipv6=ipv6,
                vrf=vrf,
                description=description,
                user_config=admin_state)

            if active_gateway_ip is not None and active_gateway_mac_v4 is not None:
                modified_op2 = vlan_interface.set_active_gateaway(
                    active_gateway_ip, active_gateway_mac_v4)
                modified_op = modified_op2 or modified_op

            if ip_helper_address is not None:
                # Create DHCP_Relay object
                dhcp_relay = device.dhcp_relay(
                    vrf=vrf, port=vlan_interface_id)
                # Add helper addresses
                modified_dhcp_relay = dhcp_relay.add_ipv4_addresses(
                    ip_helper_address)
                modified_op = modified_op or modified_dhcp_relay

            if modified_op:
                # Changed
                result['changed'] = True

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
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
            aruba_ansible_module.module.fail_json(
                msg="VLAN {id} does not exist. "
                "VLAN needs to be created "
                "before adding or deleting "
                "interfaces"
                "".format(
                    id=vlan_id))

        if state == 'create':
            aruba_ansible_module = port.create_port(aruba_ansible_module,
                                                    vlan_interface_id)
            aruba_ansible_module = interface.create_interface(
                aruba_ansible_module, vlan_interface_id, type='vlan')

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
            aruba_ansible_module = port.update_port_fields(
                aruba_ansible_module, vlan_interface_id, port_fields)

        if (state == 'create') or (state == 'update'):

            if not port.check_port_exists(
                    aruba_ansible_module, vlan_interface_id):
                aruba_ansible_module.module.fail_json(
                    msg="VLAN interface does not" " exist")

            if admin_state is not None:
                port_fields = {"admin": admin_state}
                user_config = {"admin": admin_state}
                interface_fields = {"user_config": user_config}

            aruba_ansible_module = port.update_port_fields(
                aruba_ansible_module, vlan_interface_id, port_fields)
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

            if (active_gateway_ip is not None) and (
                    active_gateway_mac_v4 is None):
                aruba_ansible_module.module.fail_json(msg=" Both active_gateway_ip and active_gateway_mac_v4 are required for configure active gateway.")  # NOQA
            elif (active_gateway_ip is None) and (active_gateway_mac_v4 is not None):  # NOQA
                aruba_ansible_module.module.fail_json(msg=" Both active_gateway_ip and active_gateway_mac_v4 are required for configure active gateway.")  # NOQA
            elif (active_gateway_ip is not None) and (active_gateway_mac_v4 is not None):  # NOQA
                port_fields = {"vsx_virtual_ip4": active_gateway_ip,
                               "vsx_virtual_gw_mac_v4": active_gateway_mac_v4
                               }
                aruba_ansible_module = port.update_port_fields(aruba_ansible_module, vlan_interface_id, port_fields)  # NOQA

        if state == 'delete':
            aruba_ansible_module = port.delete_port(aruba_ansible_module,
                                                    vlan_interface_id)
            aruba_ansible_module = interface.delete_interface(
                aruba_ansible_module, vlan_interface_id, type='vlan')

        aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
