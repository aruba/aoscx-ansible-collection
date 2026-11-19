# module: aoscx_bgp_neighbor

description: This module provides configuration management of BGP neighbors or
peer groups (`neighbor` commands of the `router bgp` context) on AOS-CX
devices, including their per address family settings. The same settings are
applied to every neighbor given in `neighbor` or `neighbors`. Other neighbors
of the BGP router are never modified or deleted. The BGP router must exist,
see [aoscx_bgp_router](aoscx_bgp_router.md).

##### NOTES

- Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor and route map handling of earlier releases.
- Tested on a switch with REST API version 10.09 (firmware 10.19).
- The switch stores password encrypted, so a change of password is only applied with update_password=always.
- In check mode, a missing VRF or BGP router is reported as a change instead of an error, and referenced route maps are not checked, because they may be created by a previous task of the playbook.

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
      IPv4/IPv6 address of the neighbor, name of the peer group, or interface
      name of an unnumbered neighbor. Mutually exclusive with neighbors,
      one of them is required.
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
  fall_over:
    description: >
      Reset the session as soon as the route to the neighbor is lost
      (fall-over).
    required: false
    type: bool
  fall_over_bfd:
    description: >
      Track the session with BFD (fall-over bfd).
    required: false
    type: bool
  passive:
    description: >
      Do not initiate the session, only accept it (passive).
    required: false
    type: bool
  remove_private_as:
    description: >
      Remove the private AS numbers from the updates sent to the neighbor
      (remove-private-as).
    required: false
    type: bool
  slow_peer:
    description: >
      Place the neighbor in a separate update group for slow peers
      (slow-peer).
    required: false
    type: bool
  weight:
    description: >
      Default weight of the routes received from the neighbor, between 0 and
      65535 (weight).
    required: false
    type: int
  local_as:
    description: >
      Local AS number used with this external neighbor, between 1 and
      4294967295 (local-as). Use 0 to remove it.
    required: false
    type: int
  local_as_mode:
    description: >
      Options of local_as: no-prepend, no-prepend-replace-as,
      no-prepend-replace-as-dual-as, or none for no option.
    required: false
    type: str
    choices:
      - none
      - no-prepend
      - no-prepend-replace-as
      - no-prepend-replace-as-dual-as
  port:
    description: >
      TCP port of the session, between 1 and 65535 (port). Use 0 to
      remove it.
    required: false
    type: int
  ttl_security_hops:
    description: >
      Maximum number of hops to the neighbor checked with TTL security,
      between 1 and 254 (ttl-security-hops). Takes precedence over
      ebgp_multihop. Use 0 to remove it.
    required: false
    type: int
  password:
    description: >
      Password of the session (password). The switch stores it encrypted,
      so it cannot be compared: see update_password. Use an empty string
      to remove it. Mutually exclusive with the TCP-AO keychain of ao.
    required: false
    type: str
  update_password:
    description: >
      on_create sets password only when the neighbor has no password,
      so that the module stays idempotent. always sets it on every run,
      and then always reports a change.
    required: false
    default: on_create
    type: str
    choices:
      - on_create
      - always
  timers:
    description: >
      Timers of the session in seconds (timers). Only the given timers are
      changed.
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
          (timers connect-retry).
        required: false
        type: int
  graceful_shutdown:
    description: >
      Graceful shutdown parameters (graceful-shutdown). Only the given
      parameters are changed.
    required: false
    type: dict
    suboptions:
      timer:
        description: >
          Maximum time in seconds to wait for the convergence, between 10 and
          1200.
        required: false
        type: int
      local_preference:
        description: >
          Local preference of the routes advertised with the graceful
          shutdown community, between 0 and 4294967295.
        required: false
        type: int
  accept_invalid_attributes:
    description: >
      Accept the routes received with invalid attributes instead of resetting
      the session (invalid-attribute all accept). Enabled by default on the
      switch.
    required: false
    type: bool
  ao:
    description: >
      TCP Authentication Option settings (ao). Only the given settings are
      changed.
    required: false
    type: dict
    suboptions:
      keychain:
        description: >
          Keychain used by TCP-AO (ao keychain). The keychain must exist.
          Use an empty string to remove it. Mutually exclusive with
          password.
        required: false
        type: str
      accept_ao_mismatch:
        description: >
          Accept the segments whose TCP-AO MAC does not match
          (ao accept-ao-mismatch).
        required: false
        type: bool
      include_tcp_options:
        description: >
          Include the other TCP options in the MAC calculation
          (ao include-tcp-options).
        required: false
        type: bool
  interface:
    description: >
      Interface of an unnumbered neighbor (interface), for example
      1/1/3; the neighbor is then usually named after the interface. Only
      used on creation, it cannot be changed on an existing neighbor. The
      interface must exist.
    required: false
    type: str
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
      route_map_in:
        description: >
          Route map applied to the routes received from the neighbor
          (route-map <name> in). The route map must exist, see
          arubanetworks.aoscx.aoscx_route_map. Use an empty string to
          remove it.
        required: false
        type: str
      route_map_out:
        description: >
          Route map applied to the routes advertised to the neighbor
          (route-map <name> out). The route map must exist. Use an empty
          string to remove it.
        required: false
        type: str
      default_originate:
        description: >
          Advertise a default route to the neighbor (default-originate).
          Not supported for l2vpn_evpn.
        required: false
        type: bool
      default_originate_route_map:
        description: >
          Route map that sets the criteria to advertise the default route
          (default-originate route-map <name>). Requires
          default_originate. The route map must exist. Use an empty string
          to remove it. Not supported for l2vpn_evpn.
        required: false
        type: str
      allowas_in:
        description: >
          Number of times the local AS may appear in the AS path of the
          received routes, between 1 and 10 (allowas-in). Use 0 to
          remove it.
        required: false
        type: int
      advertisement_interval:
        description: >
          Minimum interval in seconds between two updates, between 0 and 600
          (advertisement-interval). Not supported for l2vpn_evpn.
        required: false
        type: int
      add_paths:
        description: >
          Additional paths capability (add-paths). Not supported for
          l2vpn_evpn.
        required: false
        type: str
        choices:
          - send
          - recv
          - both
          - disable
      add_paths_advertise_best:
        description: >
          Number of paths advertised to the neighbor, between 1 and 4
          (add-paths advertise-best). Not supported for l2vpn_evpn.
        required: false
        type: int
      maximum_prefix:
        description: >
          Maximum number of prefixes accepted from the neighbor
          (maximum-prefix). Replaces the settings of this address family.
        required: false
        type: dict
        suboptions:
          limit:
            description: >
              Maximum number of prefixes, between 1 and 4294967295. Use 0
              to remove the limit.
            required: true
            type: int
          threshold:
            description: >
              Percentage of the limit that triggers a warning, between 1 and
              100.
            required: false
            type: int
          restart:
            description: >
              Seconds before the session is restarted once the limit is
              reached, between 30 and 65535.
            required: false
            type: int
          warning_only:
            description: >
              Only log a warning when the limit is reached, instead of
              closing the session (warning-only). The switch uses
              true when it is not given.
            required: false
            type: bool
      orf_capability:
        description: >
          Outbound Route Filtering capability for prefix lists
          (capability orf prefix-list). none removes it. both is not
          available, because the switch ignores it when set through the REST
          API. Not supported for l2vpn_evpn.
        required: false
        type: str
        choices:
          - send
          - receive
          - none
      orf_prefix_list:
        description: >
          Inbound prefix list advertised to the neighbor with ORF
          (orf-prefix-list <name> in). The prefix list must exist. Use an
          empty string to remove it. Not supported for l2vpn_evpn.
        required: false
        type: str
      replace_rt_asn:
        description: >
          Replace the AS number of the received route targets by the local AS
          number (replace-rt-asn). Only supported for l2vpn_evpn.
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

# Equivalent CLI configuration:
#   router bgp 65000
#       address-family ipv4 unicast
#           neighbor 192.0.2.1 route-map RM_IN in
#           neighbor 192.0.2.1 route-map RM_OUT out
#           neighbor 192.0.2.1 default-originate route-map RM_DEFAULT
#       exit-address-family
- name: Apply route maps to a neighbor
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: 192.0.2.1
    address_families:
      - address_family: ipv4_unicast
        route_map_in: RM_IN
        route_map_out: RM_OUT
        default_originate: true
        default_originate_route_map: RM_DEFAULT

- name: Remove the outbound route map
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: 192.0.2.1
    address_families:
      - address_family: ipv4_unicast
        route_map_out: ""

# Equivalent CLI configuration:
#   router bgp 65000
#       neighbor 192.0.2.1 remote-as 65001
#       neighbor 192.0.2.1 password ciphertext ...
#       neighbor 192.0.2.1 timers 20 60
#       neighbor 192.0.2.1 fall-over bfd
#       neighbor 192.0.2.1 local-as 65100 no-prepend
#       address-family ipv4 unicast
#           neighbor 192.0.2.1 allowas-in 2
#           neighbor 192.0.2.1 maximum-prefix 1000 threshold 80 restart 60
#       exit-address-family
- name: Configure session and per address family options of an external peer
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: 192.0.2.1
    remote_as: 65001
    password: "{{ bgp_password }}"
    timers:
      keepalive: 20
      holdtime: 60
    fall_over_bfd: true
    local_as: 65100
    local_as_mode: no-prepend
    address_families:
      - address_family: ipv4_unicast
        activate: true
        allowas_in: 2
        maximum_prefix:
          limit: 1000
          threshold: 80
          restart: 60
          warning_only: false

# Equivalent CLI configuration:
#   router bgp 65000
#       neighbor 1/1/3 remote-as 65002
#       neighbor 1/1/3 interface 1/1/3
- name: Configure an unnumbered neighbor
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: 1/1/3
    interface: 1/1/3
    remote_as: 65002

- name: Delete a neighbor
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: 10.147.253.165
    state: delete
```
