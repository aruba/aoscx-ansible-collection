# module: aoscx_dhcp_relay

description: This module provides configuration management of DHCP relays on
AOS-CX devices. A DHCP relay duplicates DHCP broadcast packets received on a
routed port and forwards them as unicast to a list of DHCP server
destinations, for a given VRF. A relay is identified by the compound index
(vrf, port).

##### ARGUMENTS

```YAML
  port:
    description: >
      Name of the routed port on which DHCP broadcast packets are received,
      for example 1/1/3.
    required: true
    type: str
  vrf:
    description: VRF through which the configured DHCP servers are reachable.
    required: false
    default: default
    type: str
  ipv4_ucast_server:
    description: >
      List of IPv4 unicast server destinations (up to 8) to which DHCP packets
      are forwarded. Represents the full desired set: a server present on the
      switch but not listed here is removed. When omitted the IPv4 server list
      is left unchanged. Ignored when state is delete.
    required: false
    type: list
    elements: str
  ipv6_ucast_server:
    description: >
      List of IPv6 unicast server destinations (up to 8) to which DHCP packets
      are forwarded. Represents the full desired set: a server present on the
      switch but not listed here is removed. When omitted the IPv6 server list
      is left unchanged. Ignored when state is delete.
    required: false
    type: list
    elements: str
  bootp_gateway:
    description: >
      Gateway IPv4 address the DHCP relay agent uses as the source for relayed
      packets. When omitted it is left unchanged. Ignored when state is delete.
    required: false
    type: str
  state:
    description: Create, update or delete the DHCP relay.
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
- name: Create a DHCP relay with two IPv4 servers
  aoscx_dhcp_relay:
    port: 1/1/3
    vrf: default
    ipv4_ucast_server:
      - 10.1.1.1
      - 10.1.1.2

- name: Configure a relay with a BOOTP gateway
  aoscx_dhcp_relay:
    port: 1/1/3
    vrf: default
    ipv4_ucast_server:
      - 10.1.1.1
    bootp_gateway: 10.1.1.254

- name: Update the IPv4 server list of an existing relay
  aoscx_dhcp_relay:
    port: 1/1/3
    state: update
    ipv4_ucast_server:
      - 10.1.1.1

- name: Delete a DHCP relay
  aoscx_dhcp_relay:
    port: 1/1/3
    state: delete
```
