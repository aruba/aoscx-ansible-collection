# module: aoscx_bgp_neighbor

description: This module provides configuration management of BGP neighbors or
peer groups (`neighbor` commands of the `router bgp` context) on AOS-CX
devices, including their per address family settings. The same settings are
applied to every neighbor given in `neighbor` or `neighbors`. Other neighbors
of the BGP router are never modified or deleted. The BGP router must exist,
see [aoscx_bgp_router](aoscx_bgp_router.md).

##### NOTES

- Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor handling of earlier releases.
- Tested on a switch with REST API version 10.09 (firmware 10.19).
- In check mode, a missing VRF or BGP router is reported as a change instead of an error, because it may be created by a previous task of the playbook.

##### ARGUMENTS

```YAML
  asn:
    description: Autonomous System Number of the BGP router.
    required: true
    type: int
  vrf:
    description: Name of the VRF of the BGP router.
    required: false
    default: default
    type: str
  neighbor:
    description: >
      IPv4/IPv6 address of the neighbor, or name of the peer group. Mutually
      exclusive with neighbors, one of them is required.
    required: false
    type: str
  neighbors:
    description: >
      List of neighbors (IPv4/IPv6 addresses or peer group names) that get
      the same settings. Neighbors of the BGP router that are not listed are
      not modified. All the neighbors are checked before the first change is
      applied. Mutually exclusive with neighbor.
    required: false
    type: list
    elements: str
  is_peer_group:
    description: >
      Whether the neighbors are peer groups (neighbor <name> peer-group).
      Only used on creation, it cannot be changed on an existing neighbor.
    required: false
    default: false
    type: bool
  peer_group:
    description: >
      Name of the peer group the neighbor belongs to
      (neighbor <ip> peer-group <name>). The peer group must exist. Use an
      empty string to remove the neighbor from its peer group. Not supported
      when is_peer_group is true.
    required: false
    type: str
  remote_as:
    description: ASN of the neighbor (remote-as).
    required: false
    type: int
  description:
    description: Description of the neighbor (description).
    required: false
    type: str
  update_source:
    description: >
      Source of the BGP session (update-source): either an IP address, or
      the name of a loopback interface such as loopback0 (loopback 0
      is also accepted). Use an empty string to remove it.
    required: false
    type: str
  ebgp_multihop:
    description: >
      Maximum number of hops to an external neighbor (ebgp-multihop),
      between 1 and 255. Required for eBGP sessions between loopbacks. Use
      255 for the CLI ebgp-multihop command without value, and 1 to
      remove it (no neighbor ... ebgp-multihop).
    required: false
    type: int
  shutdown:
    description: Administratively shut down the neighbor (shutdown).
    required: false
    type: bool
  address_families:
    description: >
      Per address family settings (neighbor commands of the
      address-family contexts). Only the listed address families, and
      within them only the given settings, are changed. Ignored when
      state is delete.
    required: false
    type: list
    elements: dict
    suboptions:
      address_family:
        description: Address family of the settings.
        required: true
        type: str
        choices:
          - ipv4_unicast
          - ipv6_unicast
          - l2vpn_evpn
      activate:
        description: Activate the neighbor in the address family (activate).
        required: false
        type: bool
      send_community:
        description: >
          Communities sent to the neighbor (send-community). none
          disables it.
        required: false
        type: str
        choices:
          - both
          - extended
          - standard
          - none
      route_reflector_client:
        description: >
          Configure the neighbor as route reflector client
          (route-reflector-client).
        required: false
        type: bool
      next_hop_self:
        description: >
          Advertise this router as next hop (next-hop-self). Not supported
          for l2vpn_evpn.
        required: false
        type: bool
      next_hop_unchanged:
        description: >
          Keep the next hop unchanged (next-hop-unchanged). Only supported
          for l2vpn_evpn.
        required: false
        type: bool
      inbound_soft_reconfiguration:
        description: >
          Enable inbound soft reconfiguration
          (soft-reconfiguration inbound). Not supported for l2vpn_evpn.
        required: false
        type: bool
  state:
    description: >
      Create or update (create) or delete (delete) the given
      neighbors. Other neighbors are never deleted. A peer group cannot be
      deleted while neighbors belong to it.
    required: false
    default: create
    choices:
      - create
      - delete
    type: str
```

##### EXAMPLES

```YAML
# Equivalent CLI configuration:
#   router bgp 65000
#       neighbor spine-RR peer-group
#       neighbor spine-RR remote-as 65000
#       neighbor spine-RR description Spine and RR peer-group
#       neighbor spine-RR update-source loopback 0
#       neighbor spine-RR ebgp-multihop 255
#       neighbor 10.147.253.132 peer-group spine-RR
#       neighbor 10.147.253.165 peer-group spine-RR
#       address-family l2vpn evpn
#           neighbor spine-RR send-community both
#           neighbor 10.147.253.132 activate
#           neighbor 10.147.253.165 activate
#       exit-address-family
- name: Configure the spine-RR peer group
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: spine-RR
    is_peer_group: true
    remote_as: 65000
    description: Spine and RR peer-group
    update_source: loopback0
    ebgp_multihop: 255
    address_families:
      - address_family: l2vpn_evpn
        send_community: both

- name: Configure the spine neighbors
  aoscx_bgp_neighbor:
    asn: 65000
    neighbors:
      - 10.147.253.132
      - 10.147.253.165
    peer_group: spine-RR
    address_families:
      - address_family: l2vpn_evpn
        activate: true

# Equivalent CLI configuration:
#   router bgp 65000
#       address-family l2vpn evpn
#           neighbor leaf route-reflector-client
#           neighbor leaf send-community both
#       exit-address-family
- name: Configure the leaf peer group as route reflector clients
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: leaf
    is_peer_group: true
    remote_as: 65000
    address_families:
      - address_family: l2vpn_evpn
        route_reflector_client: true
        send_community: both

- name: Add the leafs to the leaf peer group
  aoscx_bgp_neighbor:
    asn: 65000
    neighbors:
      - 10.147.253.170
      - 10.147.253.171
    peer_group: leaf
    address_families:
      - address_family: l2vpn_evpn
        activate: true

- name: Delete a neighbor
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: 10.147.253.165
    state: delete
```
