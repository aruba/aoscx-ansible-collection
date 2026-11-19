# module: aoscx_bgp_router

description: This module provides configuration management of the BGP router
instance (`router bgp <asn>`) of a VRF on AOS-CX devices: router ID,
multipath, best path selection options and route redistribution per address
family. BGP neighbors and peer groups are managed with
[aoscx_bgp_neighbor](aoscx_bgp_neighbor.md).

##### NOTES

- Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor and route map handling of earlier releases.
- Tested on a switch with REST API version 10.09 (firmware 10.19).
- In check mode, a missing VRF is reported as a change instead of an error, and referenced route maps are not checked, because they may be created by a previous task of the playbook.

##### ARGUMENTS

```YAML
  asn:
    description: >
      Autonomous System Number of the BGP router. All the VRFs of a switch
      use the same ASN.
    required: true
    type: int
  vrf:
    description: Name of the VRF of the BGP router. The VRF must exist.
    required: false
    default: default
    type: str
  router_id:
    description: >
      BGP router ID, as an IPv4 address (bgp router-id).
    required: false
    type: str
  maximum_paths:
    description: >
      Maximum number of equal-cost paths BGP may install in the routing table
      for all address families (maximum-paths).
    required: false
    type: int
  log_neighbor_changes:
    description: >
      Log neighbor status changes (bgp log-neighbor-changes).
    required: false
    type: bool
  deterministic_med:
    description: >
      Compare the MED of paths received from the same neighboring AS
      regardless of their arrival order (bgp deterministic-med).
    required: false
    type: bool
  always_compare_med:
    description: >
      Compare the MED of paths received from different neighboring AS
      (bgp always-compare-med).
    required: false
    type: bool
  bestpath_as_path_multipath_relax:
    description: >
      Consider paths with the same AS path length but different AS paths as
      equal-cost paths (bgp bestpath as-path multipath-relax).
    required: false
    type: bool
  fast_external_fallover:
    description: >
      Immediately reset the session of a directly connected external peer
      when the link goes down (bgp fast-external-fallover).
    required: false
    type: bool
  redistribute:
    description: >
      Route redistribution per address family (redistribute commands of
      the address-family context). Only the listed address families are
      changed. Ignored when state is delete.
    required: false
    type: list
    elements: dict
    suboptions:
      address_family:
        description: Address family in which routes are redistributed.
        required: true
        type: str
        choices:
          - ipv4_unicast
          - ipv6_unicast
      route_types:
        description: >
          Types of routes to redistribute. Replaces the redistribution
          configured for this address family, route maps included. Use an
          empty list to remove the redistribution.
        required: true
        type: list
        elements: str
        choices:
          - connected
          - local-loopback
          - static
          - ospf
          - isis
      route_maps:
        description: >
          Route map applied to a redistributed route type
          (redistribute <type> route-map <name>), as a dictionary whose
          keys are route types of route_types and values are route map
          names. Route types of route_types that are not listed are
          redistributed without route map. The route maps must exist, see
          arubanetworks.aoscx.aoscx_route_map.
        required: false
        type: dict
  state:
    description: >
      Create or update (create) or delete (delete) the BGP router.
      Deleting the BGP router also removes its neighbors.
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
#       bgp router-id 10.147.253.160
#       maximum-paths 8
#       bgp log-neighbor-changes
#       bgp deterministic-med
#       bgp always-compare-med
#       bgp bestpath as-path multipath-relax
#       address-family ipv4 unicast
#           redistribute connected
#       exit-address-family
- name: Configure the BGP router of the default VRF
  aoscx_bgp_router:
    asn: 65000
    router_id: 10.147.253.160
    maximum_paths: 8
    log_neighbor_changes: true
    deterministic_med: true
    always_compare_med: true
    bestpath_as_path_multipath_relax: true
    redistribute:
      - address_family: ipv4_unicast
        route_types: [connected]

- name: Configure the BGP router of the VRF sense
  aoscx_bgp_router:
    asn: 65000
    vrf: sense
    router_id: 10.147.253.160
    maximum_paths: 8
    redistribute:
      - address_family: ipv4_unicast
        route_types: [connected]

# Equivalent CLI configuration:
#   router bgp 65000
#       address-family ipv4 unicast
#           redistribute connected route-map RM_CONNECTED
#           redistribute static
#       exit-address-family
- name: Redistribute connected routes through a route map
  aoscx_bgp_router:
    asn: 65000
    redistribute:
      - address_family: ipv4_unicast
        route_types: [connected, static]
        route_maps:
          connected: RM_CONNECTED

- name: Stop redistributing IPv4 routes in the VRF sense
  aoscx_bgp_router:
    asn: 65000
    vrf: sense
    redistribute:
      - address_family: ipv4_unicast
        route_types: []

- name: Delete the BGP router of the VRF sense
  aoscx_bgp_router:
    asn: 65000
    vrf: sense
    state: delete
```
