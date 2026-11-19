# module: aoscx_route_map

description: This module provides configuration management of route maps and
their entries on AOS-CX devices. Route maps are used by routing protocols (for
example BGP) to filter and modify routes through ordered match/set clauses.

##### ARGUMENTS

```YAML
  name:
    description: Name of the route map.
    required: true
    type: str
  entries:
    description: >
      List of route map entries that make up the route map. When provided this
      represents the full desired set of entries: entries present on the switch
      but not listed here are removed. Ignored when state is delete.
    required: false
    type: list
    elements: dict
    suboptions:
      preference:
        description: >
          Sequence number of the entry. Entries are evaluated in ascending
          order of preference.
        required: true
        type: int
      action:
        description: Whether the entry permits or denies the matched route.
        required: true
        choices:
          - permit
          - deny
        type: str
      description:
        description: Description of the route map entry.
        required: false
        type: str
      exitpolicy:
        description: >
          Policy applied after the entry is processed. goto jumps to the entry
          given by route_map_continue while next continues with the next entry.
        required: false
        choices:
          - goto
          - next
        type: str
      route_map_continue:
        description: >
          Preference of the entry to continue with after this entry matches.
          Required when exitpolicy is goto.
        required: false
        type: int
      match:
        description: >
          Match conditions for the entry. An existing entry is updated only
          if a given clause differs from the switch; it is then replaced by
          the given entry, so match and set clauses that are not given are
          removed. Always describe each entry entirely.
        required: false
        type: dict
        suboptions:
          metric:
            description: Match routes with this metric.
            type: int
          local_preference:
            description: Match routes with this local preference.
            type: int
          origin:
            description: Match routes with this BGP origin.
            choices: [EGP, IBGP, incomplete]
            type: str
          route_type:
            description: Match routes of this type.
            choices:
              - local
              - internal
              - external_type1
              - external_type2
              - evpn-type-1
              - evpn-type-2
              - evpn-type-3
              - evpn-type-4
              - evpn-type-5
            type: str
          source_protocol:
            description: Match routes redistributed from this protocol.
            choices: [static, connected, ospf, bgp]
            type: str
          ipv4_next_hop_address:
            description: Match routes with this IPv4 next hop address.
            type: str
          ipv6_next_hop:
            description: Match routes with this IPv6 next hop address.
            type: str
          vni:
            description: Match routes with this VNI.
            type: int
          probability:
            description: Match a percentage of routes.
            type: int
          ipv4_prefix_list:
            description: >
              Match routes permitted by this IPv4 prefix list
              (match ip address prefix-list). The prefix list must exist,
              see arubanetworks.aoscx.aoscx_prefix_list. Use an empty
              string to remove the clause.
            type: str
          ipv6_prefix_list:
            description: >
              Match routes permitted by this IPv6 prefix list
              (match ipv6 address prefix-list). The prefix list must
              exist. Use an empty string to remove the clause.
            type: str
          community_list:
            description: >
              Match routes whose communities are permitted by this community
              list (match community). The list must exist, see
              arubanetworks.aoscx.aoscx_bgp_community_list. Use an empty
              string to remove the clause.
            type: str
          community_list_exact_match:
            description: >
              Match only routes whose communities exactly match
              community_list (exact-match).
            type: bool
          extcommunity_list:
            description: >
              Match routes whose extended communities are permitted by this
              extended community list (match extcommunity). The list must
              exist. Use an empty string to remove the clause.
            type: str
          as_path:
            description: >
              Match routes whose AS path is permitted by this AS-path list
              (match aspath-list). The list must exist, see
              arubanetworks.aoscx.aoscx_bgp_aspath_list. Use an empty
              string to remove the clause.
            type: str
          tag:
            description: >
              Match routes with one of these tags (match tag). Use an
              empty list to remove the clause.
            type: list
            elements: int
      set:
        description: >
          Set actions applied to matched routes. Compared and replaced like
          match.
        required: false
        type: dict
        suboptions:
          local_preference:
            description: Set the local preference.
            type: int
          metric:
            description: Set the metric.
            type: int
          metric_type:
            description: Set the metric type.
            choices: [internal, external_type1, external_type2]
            type: str
          origin:
            description: Set the BGP origin.
            choices: [EGP, IBGP, incomplete]
            type: str
          community:
            description: Set the BGP community.
            type: str
          as_path_prepend:
            description: Prepend the given AS path.
            type: str
          as_path_exclude:
            description: Exclude the given AS numbers from the AS path.
            type: str
          weight:
            description: Set the BGP weight.
            type: int
          ipv4_next_hop_address:
            description: Set the IPv4 next hop address.
            type: str
          ipv6_next_hop_global:
            description: Set the global IPv6 next hop address.
            type: str
          aggregator_as:
            description: Set the aggregator AS number.
            type: int
          atomic_aggregate:
            description: Set the atomic aggregate attribute.
            type: bool
          tag:
            description: >
              Set the route tag (set tag). Use an empty list to remove the
              clause.
            type: list
            elements: int
  state:
    description: Create, update or delete the route map.
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
- name: Create a route map that sets local preference on BGP routes
  aoscx_route_map:
    name: SET_LOCAL_PREF
    entries:
      - preference: 10
        action: permit
        description: Prefer internal routes
        match:
          source_protocol: bgp
        set:
          local_preference: 200
          community: "65000:100"
      - preference: 20
        action: deny

- name: Add or update a single entry on an existing route map
  aoscx_route_map:
    name: SET_LOCAL_PREF
    state: update
    entries:
      - preference: 10
        action: permit
        match:
          source_protocol: bgp
        set:
          local_preference: 300

# Equivalent CLI configuration:
#   route-map RM_FROM_SPINES permit seq 10
#       match ip address prefix-list PL_LOOPBACKS
#       match community CL_FABRIC exact-match
#       match aspath-list AS_SPINES
#       set tag 100
#   route-map RM_FROM_SPINES deny seq 20
- name: Create a route map that references other routing policies
  aoscx_route_map:
    name: RM_FROM_SPINES
    entries:
      - preference: 10
        action: permit
        match:
          ipv4_prefix_list: PL_LOOPBACKS
          community_list: CL_FABRIC
          community_list_exact_match: true
          as_path: AS_SPINES
        set:
          tag: [100]
      - preference: 20
        action: deny

- name: Delete a route map
  aoscx_route_map:
    name: SET_LOCAL_PREF
    state: delete
```

##### NOTES

- Match clauses can reference prefix lists, community lists and AS-path
  lists, which must exist. They are not checked in check mode, because they
  may be created by a previous task of the playbook.
- Dampening, EVPN specific fields and `set comm-list delete` are not handled.
- An existing entry is updated only if a given clause differs from the
  switch; it is then replaced by the given entry, so match and set clauses
  that are not given are removed. Always describe each entry entirely.
- When entries is provided with state create or update, it represents the full
  desired set of entries; entries present on the switch but not listed are
  removed.
