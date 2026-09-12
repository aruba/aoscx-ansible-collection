# module: aoscx_udp_bcast_forwarder

description: This module provides configuration management of UDP broadcast
forwarder servers on AOS-CX devices. A forwarder duplicates UDP broadcast
packets received on a routed port to a list of unicast server destinations,
for a given destination UDP port and VRF. A forwarder is identified by the
compound index (dest_vrf, src_port, udp_dport).

##### ARGUMENTS

```YAML
  src_port:
    description: >
      Name of the routed port on which UDP broadcast packets are received,
      for example 1/1/1.
    required: true
    type: str
  udp_dport:
    description: >
      Destination UDP port used to match and forward the broadcast packets.
    required: true
    type: int
  dest_vrf:
    description: VRF through which the configured servers are reachable.
    required: false
    default: default
    type: str
  ipv4_ucast_server:
    description: >
      List of IPv4 unicast server destinations (up to 8) to which the UDP
      broadcast packets are forwarded. Represents the full desired set: a
      server present on the switch but not listed here is removed. Ignored
      when state is delete.
    required: false
    type: list
    elements: str
  state:
    description: Create, update or delete the UDP broadcast forwarder.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
```

##### EXAMPLES

```YAML
- name: Create a UDP broadcast forwarder for DNS (port 53)
  aoscx_udp_bcast_forwarder:
    src_port: 1/1/1
    udp_dport: 53
    dest_vrf: default
    ipv4_ucast_server:
      - 10.0.0.1
      - 10.0.0.2

- name: Update the server list of an existing forwarder
  aoscx_udp_bcast_forwarder:
    src_port: 1/1/1
    udp_dport: 53
    state: update
    ipv4_ucast_server:
      - 10.0.0.1

- name: Delete a UDP broadcast forwarder
  aoscx_udp_bcast_forwarder:
    src_port: 1/1/1
    udp_dport: 53
    state: delete
```
