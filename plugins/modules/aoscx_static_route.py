#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2023 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_static_route
version_added: "2.8.0"
short_description: Create or Delete static route configuration on AOS-CX
description: >
  This modules provides configuration management of static routes on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  vrf_name:
    description: >
      Name of the VRF on which the static route is to be configured. The VRF
      should have already been configured before using this module to configure
      the static route on the switch. If nothing is provided, the static route
      will be on the Default VRF.
    required: false
    default: default
    type: str
  destination_address_prefix:
    description: >
      The IPv4 or IPv6 destination prefix and mask in the address/mask format
      i.e 1.1.1.0/24.
    required: true
    type: str
  type:
    description: >
      Specifies whether the static route is a forward, blackhole or reject
      route.
      - forward: The packets that match the route for the desination will
        be forwarded.
      - reject: The packets that match the route for the destination will
        be discarded and an ICMP unreachable message is sent to the sender
        of the packet.
      - blackhole: The packets that match the route for the destination will
        be silently discarded without sending any ICMP message to the sender
        of the packet.
    required: false
    choices:
      - forward
      - blackhole
      - reject
    default: forward
    type: str
  distance:
    description: >
      Administrative distance to be used for the next hop in the static route
      instead of default value.
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
    choices:
      - create
      - delete
    default: create
    type: str
"""

EXAMPLES = """
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
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        vrf_name=dict(type="str", required=False, default="default"),
        destination_address_prefix=dict(type="str", required=True),
        type=dict(
            type="str",
            default="forward",
            choices=["forward", "blackhole", "reject"],
        ),
        distance=dict(type="int", default=1),
        next_hop_interface=dict(type="str", default=None),
        next_hop_ip_address=dict(type="str", default=None),
        state=dict(default="create", choices=["create", "delete"]),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    vrf_name = ansible_module.params["vrf_name"]
    prefix = ansible_module.params["destination_address_prefix"]
    route_type = ansible_module.params["type"]
    distance = ansible_module.params["distance"]
    next_hop_interface = ansible_module.params["next_hop_interface"]
    next_hop_ip_address = ansible_module.params["next_hop_ip_address"]
    state = ansible_module.params["state"]

    # Set result var
    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        from pyaoscx.device import Device
    except Exception as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    device = Device(session)

    if state == "delete":
        static_route = device.static_route(vrf_name, prefix)
        static_route.delete()
        result["changed"] = True

    if state in ("create", "update"):
        # Create Static Route object
        static_route = device.static_route(vrf_name, prefix)

        # Add Static Nexthop
        static_route.add_static_nexthop(
            next_hop_ip_address=next_hop_ip_address,
            nexthop_type=route_type,
            distance=distance,
            next_hop_interface=next_hop_interface,
        )

        # Verify if Static Route was created
        if static_route.was_modified():
            result["changed"] = True

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
