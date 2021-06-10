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
module: aoscx_static_route
version_added: "2.8"
short_description: Create or Delete static route configuration on AOS-CX
description:
  - This modules provides configuration management of static routes on
    AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  vrf_name:
    description: Name of the VRF on which the static route is to be configured.
      The VRF should have already been configured before using this module to
      configure the static route on the switch. If nothing is provided, the
      static route will be on the Default VRF.
    required: false
    default: "default"
    type: str

  destination_address_prefix:
    description: The IPv4 or IPv6 destination prefix and mask in the
      address/mask format i.e 1.1.1.0/24.
    required: true
    type: str

  type:
    description: Specifies whether the static route is a forward, blackhole or
      reject route.
        - forward - The packets that match the route for the desination will
          be forwarded.
        - reject - The packets that match the route for the destination will
          be discarded and an ICMP unreachable message is sent to the sender
          of the packet.
        - blackhole - The packets that match the route for the destination will
          be silently discarded without sending any ICMP message to the sender
          of the packet.
    required: false
    choices: ['forward', 'blackhole', 'reject']
    default: forward
    type: str

  distance:
    description: Administrative distance to be used for the next hop in the
      static route instaed of default value.
    required: false
    default: 1
    type: int

  next_hop_interface:
    description: The interface through which the next hop can be reached.
    required: false
    type: str

  next_hop_ip_address:
    description: The IPv4 address or the IPv6 address of next hop.
    required: false
    type: str

  state:
    description: Create or delete the static route.
    required: false
    choices: ['create', 'delete']
    default: create
    type: str
'''  # NOQA

EXAMPLES = '''
- name: Create IPv4 Static Route with VRF - Forwarding
  aoscx_static_route:
    vrf_name: vrf2
    destination_address_prefix: '1.1.1.0/24'
    type: forward
    distance: 1
    next_hop_interface: '1/1/2'
    next_hop_ip_address: '2.2.2.2'

- name: Create IPv6 Static Route with VRF default - Forwarding
  aoscx_static_route:
    destination_address_prefix: 3000:300::2/64
    type: forward
    next_hop_ip_address: 1000:100::2

- name: Create Static Route with VRF - Blackhole
  aoscx_static_route:
    vrf_name: vrf3
    destination_address_prefix: '2.1.1.0/24'
    type: blackhole

- name: Create Static Route with VRF - Reject
  aoscx_static_route:
    vrf_name: vrf4
    destination_address_prefix: '3.1.1.0/24'
    type: reject

- name: Delete Static Route with VRF - Forwarding
  aoscx_static_route:
    destination_address_prefix: '1.1.1.0/24'
    state: 'delete'

- name: Delete Static Route with VRF - Blackhole
  aoscx_static_route:
    destination_address_prefix: '2.1.1.0/24'
    state: 'delete'

- name: Delete Static Route with VRF - Reject
  aoscx_static_route:
    destination_address_prefix: '3.1.1.0/24'
    state: 'delete'
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf import VRF


def main():
    module_args = dict(vrf_name=dict(type='str', required=False,
                                     default='default'),
                       destination_address_prefix=dict(type='str',
                                                       required=True),
                       type=dict(type='str', default='forward',
                                 choices=['forward', 'blackhole', 'reject']),
                       distance=dict(type='int', default=1),
                       next_hop_interface=dict(type='str', default=None),
                       next_hop_ip_address=dict(type='str', default=None),
                       state=dict(default='create',
                                  choices=['create', 'delete']))

    # Version management
    try:
        from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import Session
        from pyaoscx.session import Session as Pyaoscx_Session
        from pyaoscx.pyaoscx_factory import PyaoscxFactory

        USE_PYAOSCX_SDK = True

    except ImportError:

        USE_PYAOSCX_SDK = False

    if USE_PYAOSCX_SDK:

        from ansible.module_utils.basic import AnsibleModule
        # ArubaModule
        ansible_module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True)

        vrf_name = ansible_module.params['vrf_name']
        prefix = ansible_module.params['destination_address_prefix']
        route_type = ansible_module.params['type']
        distance = ansible_module.params['distance']
        next_hop_interface = ansible_module.params['next_hop_interface']
        next_hop_ip_address = ansible_module.params['next_hop_ip_address']
        state = ansible_module.params['state']

        # Session
        session = Session(ansible_module)

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

        # Create a Pyaoscx Factory Object
        pyaoscx_factory = PyaoscxFactory(s)

        if state == 'delete':
            # Create Static Route Object
            static_route = pyaoscx_factory.static_route(
                vrf_name, prefix)
            # Delete it
            static_route.delete()
            # Changed
            result['changed'] = True

        if state == 'create' or state == 'update':
            # Create Static Route object
            static_route = pyaoscx_factory.static_route(
                vrf_name,
                prefix
            )

            # Add Static Nexthop
            static_route.add_static_nexthop(
                next_hop_ip_address=next_hop_ip_address,
                nexthop_type=route_type,
                distance=distance,
                next_hop_interface=next_hop_interface
            )

            # Verify if Static Route was created
            if static_route.was_modified():
                # Changed
                result['changed'] = True

        # Exit
        ansible_module.exit_json(**result)
    else:

        aruba_ansible_module = ArubaAnsibleModule(module_args)

        vrf_name = aruba_ansible_module.module.params['vrf_name']
        prefix = aruba_ansible_module.module.params['destination_address_prefix']
        route_type = aruba_ansible_module.module.params['type']
        distance = aruba_ansible_module.module.params['distance']
        next_hop_interface = aruba_ansible_module.module.params['next_hop_interface']
        next_hop_ip_address = aruba_ansible_module.module.params['next_hop_ip_address']
        state = aruba_ansible_module.module.params['state']

        vrf = VRF()

        if vrf_name is None:
            vrf_name = 'default'

        if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):

            if vrf_name == 'default' and state == 'create':
                aruba_ansible_module = vrf.create_vrf(aruba_ansible_module,
                                                      vrf_name)
            else:
                aruba_ansible_module.module.fail_json(
                    msg="VRF {vrf} is not " "configured" "".format(vrf=vrf_name))

        encoded_prefix = prefix.replace("/", "%2F")
        encoded_prefix = encoded_prefix.replace(":", "%3A")
        index = vrf_name + '/' + encoded_prefix
        if (state == 'create') or (state == 'update'):
            address_family = 'ipv6' if ':' in prefix else 'ipv4'
            static_route = {}
            static_route[index] = {}
            if address_family is not None:
                static_route[index]["address_family"] = address_family
            if prefix is not None:
                static_route[index]["prefix"] = prefix
            if route_type is not None:
                static_route[index]['static_nexthops']["0"]["type"] = route_type
                if route_type == 'forward':
                    static_route[index]['static_nexthops'] = {
                        "0": {
                            "bfd_enable": False,
                            "distance": distance
                        }
                    }
                if next_hop_interface is not None:
                    encoded_interface = next_hop_interface.replace(
                        '/', '%2F')
                    static_route[index]['static_nexthops']["0"]["port"] = encoded_interface
                if next_hop_ip_address is not None:
                    static_route[index]['static_nexthops']["0"]["ip_address"] = next_hop_ip_address

                aruba_ansible_module = vrf.update_vrf_fields(
                    aruba_ansible_module, vrf_name, 'Static_Route', static_route)

        if (state == 'delete'):
            if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):
                aruba_ansible_module.module.fail_json(
                    msg="VRF {vrf_name} does not exist".format(
                        vrf_name=vrf_name))
            static_route = vrf.get_vrf_field_value(
                aruba_ansible_module, vrf_name, 'Static_Route')
            if not static_route:
                aruba_ansible_module.warnings.append(
                    "Static route for destination {dest} does not exist in VRF {vrf}".format(
                        dest=prefix, vrf=vrf_name))
            elif index not in static_route.keys():
                aruba_ansible_module.warnings.append(
                    "Static route for destination {dest} does not exist in VRF {vrf}".format(
                        dest=prefix, vrf=vrf_name))
            else:
                static_route.pop(index)
                aruba_ansible_module = vrf.update_vrf_fields(
                    aruba_ansible_module, vrf_name, 'Static_Route', static_route)

        aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
