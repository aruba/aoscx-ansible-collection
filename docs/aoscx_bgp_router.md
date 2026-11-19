# module: aoscx_bgp_router

description: This module provides configuration management of the BGP router
instance (`router bgp <asn>`) of a VRF on AOS-CX devices: router ID,
multipath, best path selection options and route redistribution per address
family. BGP neighbors and peer groups are managed with
[aoscx_bgp_neighbor](aoscx_bgp_neighbor.md).

##### NOTES

- Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor and route map handling of earlier releases.
- Tested on a switch with REST API version 10.09 (firmware 10.19).
- The per address family maximum_paths requires REST API version 10.13 or later, which the arubanetworks.aoscx.aoscx connection does not support yet; it is only covered by unit tests.
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
  bestpath_as_path_ignore:
    description: >
      Ignore the AS path length when selecting the best path
      (bgp bestpath as-path ignore).
    required: false
    type: bool
  bestpath_compare_routerid:
    description: >
      Compare the router IDs of identical eBGP paths
      (bgp bestpath compare-routerid).
    required: false
    type: bool
  bestpath_med_confed:
    description: >
      Compare the MED of paths received from different sub-AS of a
      confederation (bgp bestpath med confed). Changing it restarts the BGP
      sessions of the VRF.
    required: false
    type: bool
  bestpath_med_missing_as_worst:
    description: >
      Treat a missing MED as the worst value
      (bgp bestpath med missing-as-worst).
    required: false
    type: bool
  bestpath_bgp_std_selection:
    description: >
      Use the standard BGP best path selection process
      (bgp bestpath bgp-std-selection).
    required: false
    type: bool
  aggregate_split_horizon:
    description: >
      Do not advertise an aggregate route back to the peer that advertises
      the same network. Enabled by default on the switch.
    required: false
    type: bool
  trap_enable:
    description: Enable the BGP SNMP traps (trap-enable).
    required: false
    type: bool
  disable:
    description: >
      Disable the BGP instance of the VRF (disable). Use false to enable
      it again (enable).
    required: false
    type: bool
  cluster_id:
    description: >
      Route reflector cluster ID, as an IPv4 address or an integer between 1
      and 4294967295 (bgp cluster-id). Use an empty string to remove it.
    required: false
    type: str
  default_local_preference:
    description: >
      Default local preference, between 0 and 4294967295
      (bgp default local-preference).
    required: false
    type: int
  maxas_limit:
    description: >
      Maximum number of AS numbers allowed in the AS path of received routes,
      between 1 and 32 (bgp maxas-limit).
    required: false
    type: int
  asnotation:
    description: >
      Notation of the 4-byte AS numbers in show commands (bgp asnotation).
    required: false
    type: str
    choices:
      - plain-text
      - dotted
      - dotted-plus
  timers:
    description: >
      BGP timers in seconds (timers bgp). Only the given timers are changed.
    required: false
    type: dict
    suboptions:
      keepalive:
        description: Keepalive interval, between 0 and 65535.
        required: false
        type: int
      holdtime:
        description: Hold time, between 0 and 65535.
        required: false
        type: int
      connect_retry:
        description: >
          Connect retry interval, between 1 and 65535
          (timers bgp connect-retry).
        required: false
        type: int
  distance:
    description: >
      Administrative distances of the BGP routes (distance bgp). Only the
      given distances are changed.
    required: false
    type: dict
    suboptions:
      ebgp:
        description: Distance of the external routes, between 1 and 255.
        required: false
        type: int
      ibgp:
        description: Distance of the internal routes, between 1 and 255.
        required: false
        type: int
  graceful_restart:
    description: >
      Graceful restart settings (bgp graceful-restart). Only the given
      settings are changed.
    required: false
    type: dict
    suboptions:
      enable:
        description: Enable the graceful restart procedures.
        required: false
        type: bool
      restart_time:
        description: >
          Maximum time in seconds to restart and establish the sessions,
          between 1 and 3600 (bgp graceful-restart restart-time).
        required: false
        type: int
      stalepath_time:
        description: >
          Time in seconds the routes of a restarting peer are kept as stale,
          between 1 and 3600 (bgp graceful-restart stalepath-time).
        required: false
        type: int
  confederation:
    description: >
      BGP confederation settings (bgp confederation). Only the given
      settings are changed.
    required: false
    type: dict
    suboptions:
      identifier:
        description: >
          Confederation identifier, between 1 and 4294967295. Use 0 to
          remove it.
        required: false
        type: int
      peers:
        description: >
          AS numbers of the other sub-AS of the confederation
          (bgp confederation peers). Replaces the configured list, use an
          empty list to remove them.
        required: false
        type: list
        elements: int
  address_families:
    description: >
      Settings of the address-family contexts. Only the listed address
      families, and within them only the given settings, are changed.
      Redistribution is configured with redistribute. Ignored when
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
      maximum_paths:
        description: >
          Maximum number of equal-cost paths for this address family
          (maximum-paths in the address-family context). Requires REST
          API version 10.13 or later; with earlier versions only the global
          maximum_paths is available.
        required: false
        type: int
      networks:
        description: >
          Networks announced by BGP (network). Replaces the networks of this
          address family; use an empty list to remove them. Not supported for
          l2vpn_evpn.
        required: false
        type: list
        elements: dict
        suboptions:
          prefix:
            description: Network prefix, for example 10.1.0.0/16.
            required: true
            type: str
          route_map:
            description: >
              Route map applied to the network (network <prefix> route-map
              <name>). The route map must exist.
            required: false
            type: str
      aggregate_addresses:
        description: >
          Aggregate addresses (aggregate-address). Replaces the aggregate
          addresses of this address family; use an empty list to remove them.
          Not supported for l2vpn_evpn.
        required: false
        type: list
        elements: dict
        suboptions:
          prefix:
            description: Aggregate prefix, for example 10.2.0.0/16.
            required: true
            type: str
          options:
            description: >
              summary-only advertises only the aggregate, as-set keeps
              the AS path information of the aggregated routes,
              summary-as-set combines both.
            required: false
            default: none
            type: str
            choices:
              - none
              - summary-only
              - as-set
              - summary-as-set
          suppress_map:
            description: >
              Route map selecting the routes to suppress (suppress-map).
              The route map must exist.
            required: false
            type: str
          advertise_map:
            description: >
              Route map selecting the routes used to build the aggregate
              (advertise-map). The route map must exist.
            required: false
            type: str
          attribute_map:
            description: >
              Route map setting the attributes of the aggregate
              (attribute-map). The route map must exist.
            required: false
            type: str
      dampening:
        description: >
          Route flap dampening parameters (bgp dampening). Only the given
          parameters are changed; give none of them to disable dampening. Not
          supported for l2vpn_evpn.
        required: false
        type: dict
        suboptions:
          half_life:
            description: Half-life in minutes, between 1 and 45.
            required: false
            type: int
          reuse:
            description: Reuse threshold, between 1 and 20000.
            required: false
            type: int
          suppress:
            description: Suppress threshold, between 1 and 20000.
            required: false
            type: int
          max_suppress_time:
            description: Maximum suppress time in minutes, between 1 and 255.
            required: false
            type: int
      dampening_route_map:
        description: >
          Route map selecting the routes to dampen
          (bgp dampening route-map). The route map must exist. Use an empty
          string to remove it. Not supported for l2vpn_evpn.
        required: false
        type: str
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

# Equivalent CLI configuration:
#   router bgp 65000
#       bgp cluster-id 10.147.253.1
#       timers bgp 20 60
#       distance bgp 30 210
#       bgp graceful-restart restart-time 200
#       address-family ipv4 unicast
#           network 10.1.0.0/16 route-map RM_NETWORKS
#           network 10.3.0.0/16
#           aggregate-address 10.2.0.0/16 summary-only
#           bgp dampening half-life 10 reuse 800 suppress 3000
#               max-suppress-time 40
#       exit-address-family
- name: Configure the global options, networks and aggregate addresses
  aoscx_bgp_router:
    asn: 65000
    cluster_id: 10.147.253.1
    timers:
      keepalive: 20
      holdtime: 60
    distance:
      ebgp: 30
      ibgp: 210
    graceful_restart:
      enable: true
      restart_time: 200
    address_families:
      - address_family: ipv4_unicast
        networks:
          - prefix: 10.1.0.0/16
            route_map: RM_NETWORKS
          - prefix: 10.3.0.0/16
        aggregate_addresses:
          - prefix: 10.2.0.0/16
            options: summary-only
        dampening:
          half_life: 10
          reuse: 800
          suppress: 3000
          max_suppress_time: 40

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
