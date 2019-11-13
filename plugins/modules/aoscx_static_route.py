#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


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

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule  # NOQA
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vrf import VRF  # NOQA


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

    aruba_ansible_module = ArubaAnsibleModule(module_args)

    vrf_name = aruba_ansible_module.module.params['vrf_name']
    prefix = aruba_ansible_module.module.params['destination_address_prefix']
    route_type = aruba_ansible_module.module.params['type']
    distance = aruba_ansible_module.module.params['distance']
    next_hop_interface = aruba_ansible_module.module.params['next_hop_interface']  # NOQA
    next_hop_ip_address = aruba_ansible_module.module.params['next_hop_ip_address']  # NOQA
    state = aruba_ansible_module.module.params['state']

    vrf = VRF()

    if vrf_name is None:
        vrf_name = 'default'

    if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):

        if vrf_name == 'default' and state == 'create':
            aruba_ansible_module = vrf.create_vrf(aruba_ansible_module,
                                                  vrf_name)
        else:
            aruba_ansible_module.module.fail_json(msg="VRF {vrf} is not "
                                                      "configured"
                                                      "".format(vrf=vrf_name))

    encoded_prefix = prefix.replace("/", "%2F")
    index = vrf_name + '/' + encoded_prefix

    if (state == 'create') or (state == 'update'):

        address_family = 'ipv6' if ':' in prefix else 'ipv4'

        if not aruba_ansible_module.running_config['System']['vrfs'][vrf_name].has_key('Static_Route'):  # NOQA
            aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'] = {}  # NOQA

        if not aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'].has_key(index):  # NOQA
            aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index] = {}  # NOQA

        if address_family is not None:
            aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index]["address_family"] = address_family  # NOQA

        if prefix is not None:
            aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index]["prefix"] = prefix  # NOQA

        if route_type is not None:
            aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index]["type"] = route_type  # NOQA

            if route_type == 'forward':
                if not aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index].has_key('static_nexthops'):  # NOQA
                    aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index]['static_nexthops'] = {"0": {"bfd_enable": False, "distance": distance}}  # NOQA

                if next_hop_interface is not None:
                    encoded_interface = next_hop_interface.replace('/', '%2F')
                    aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index]['static_nexthops']["0"]["port"] = encoded_interface  # NOQA

                if next_hop_ip_address is not None:
                    aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'][index]['static_nexthops']["0"]["ip_address"] = next_hop_ip_address  # NOQA

    if state == 'delete':

        if not aruba_ansible_module.running_config['System']['vrfs'][vrf_name].has_key('Static_Route'):  # NOQA
            aruba_ansible_module.warnings.append("Static route for destination {dest} and does not exist in VRF{vrf}".format(dest=prefix, vrf=vrf_name))  # NOQA

        elif not aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'].has_key(index):  # NOQA
            aruba_ansible_module.warnings.append("Static route for destination {dest} and does not exist in VRF{vrf}".format(dest=prefix, vrf=vrf_name))  # NOQA

        else:
            aruba_ansible_module.running_config['System']['vrfs'][vrf_name]['Static_Route'].pop(index)  # NOQA

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
