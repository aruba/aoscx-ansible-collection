# module: aoscx_static_route

description: This modules provides configuration management of static routes on
AOS-CX devices.

##### ARGUMENTS

```YAML
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
```

##### EXAMPLES

```YAML
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
```
