#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_bgp_router
version_added: "4.6.0"
short_description: Create, Update or Delete a BGP router instance on AOS-CX
description: >
  This module provides configuration management of the BGP router instance
  (C(router bgp <asn>)) of a VRF on AOS-CX devices: router ID, multipath,
  best path selection options and route redistribution per address family.
  BGP neighbors and peer groups are managed with
  M(arubanetworks.aoscx.aoscx_bgp_neighbor).
author: Aruba Networks (@ArubaNetworks)
notes:
  - Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor and route
    map handling of earlier releases.
  - Tested on a switch with REST API version 10.09 (firmware 10.19).
  - The per address family I(maximum_paths) requires REST API version 10.13
    or later, which the C(arubanetworks.aoscx.aoscx) connection does not
    support yet; it is only covered by unit tests.
  - In check mode, a missing VRF is reported as a change
    instead of an error, and referenced route maps are not checked, because
    they may be created by a previous task of the playbook.
options:
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
      BGP router ID, as an IPv4 address (C(bgp router-id)).
    required: false
    type: str
  maximum_paths:
    description: >
      Maximum number of equal-cost paths BGP may install in the routing table
      for all address families (C(maximum-paths)).
    required: false
    type: int
  log_neighbor_changes:
    description: >
      Log neighbor status changes (C(bgp log-neighbor-changes)).
    required: false
    type: bool
  deterministic_med:
    description: >
      Compare the MED of paths received from the same neighboring AS
      regardless of their arrival order (C(bgp deterministic-med)).
    required: false
    type: bool
  always_compare_med:
    description: >
      Compare the MED of paths received from different neighboring AS
      (C(bgp always-compare-med)).
    required: false
    type: bool
  bestpath_as_path_multipath_relax:
    description: >
      Consider paths with the same AS path length but different AS paths as
      equal-cost paths (C(bgp bestpath as-path multipath-relax)).
    required: false
    type: bool
  fast_external_fallover:
    description: >
      Immediately reset the session of a directly connected external peer
      when the link goes down (C(bgp fast-external-fallover)).
    required: false
    type: bool
  bestpath_as_path_ignore:
    description: >
      Ignore the AS path length when selecting the best path
      (C(bgp bestpath as-path ignore)).
    required: false
    type: bool
  bestpath_compare_routerid:
    description: >
      Compare the router IDs of identical eBGP paths
      (C(bgp bestpath compare-routerid)).
    required: false
    type: bool
  bestpath_med_confed:
    description: >
      Compare the MED of paths received from different sub-AS of a
      confederation (C(bgp bestpath med confed)). Changing it restarts the BGP
      sessions of the VRF.
    required: false
    type: bool
  bestpath_med_missing_as_worst:
    description: >
      Treat a missing MED as the worst value
      (C(bgp bestpath med missing-as-worst)).
    required: false
    type: bool
  bestpath_bgp_std_selection:
    description: >
      Use the standard BGP best path selection process
      (C(bgp bestpath bgp-std-selection)).
    required: false
    type: bool
  aggregate_split_horizon:
    description: >
      Do not advertise an aggregate route back to the peer that advertises
      the same network. Enabled by default on the switch.
    required: false
    type: bool
  trap_enable:
    description: Enable the BGP SNMP traps (C(trap-enable)).
    required: false
    type: bool
  disable:
    description: >
      Disable the BGP instance of the VRF (C(disable)). Use C(false) to enable
      it again (C(enable)).
    required: false
    type: bool
  cluster_id:
    description: >
      Route reflector cluster ID, as an IPv4 address or an integer between 1
      and 4294967295 (C(bgp cluster-id)). Use an empty string to remove it.
    required: false
    type: str
  default_local_preference:
    description: >
      Default local preference, between 0 and 4294967295
      (C(bgp default local-preference)).
    required: false
    type: int
  maxas_limit:
    description: >
      Maximum number of AS numbers allowed in the AS path of received routes,
      between 1 and 32 (C(bgp maxas-limit)).
    required: false
    type: int
  asnotation:
    description: >
      Notation of the 4-byte AS numbers in show commands (C(bgp asnotation)).
    required: false
    type: str
    choices:
      - plain-text
      - dotted
      - dotted-plus
  timers:
    description: >
      BGP timers in seconds (C(timers bgp)). Only the given timers are changed.
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
          (C(timers bgp connect-retry)).
        required: false
        type: int
  distance:
    description: >
      Administrative distances of the BGP routes (C(distance bgp)). Only the
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
      Graceful restart settings (C(bgp graceful-restart)). Only the given
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
          between 1 and 3600 (C(bgp graceful-restart restart-time)).
        required: false
        type: int
      stalepath_time:
        description: >
          Time in seconds the routes of a restarting peer are kept as stale,
          between 1 and 3600 (C(bgp graceful-restart stalepath-time)).
        required: false
        type: int
  confederation:
    description: >
      BGP confederation settings (C(bgp confederation)). Only the given
      settings are changed.
    required: false
    type: dict
    suboptions:
      identifier:
        description: >
          Confederation identifier, between 1 and 4294967295. Use C(0) to
          remove it.
        required: false
        type: int
      peers:
        description: >
          AS numbers of the other sub-AS of the confederation
          (C(bgp confederation peers)). Replaces the configured list, use an
          empty list to remove them.
        required: false
        type: list
        elements: int
  address_families:
    description: >
      Settings of the C(address-family) contexts. Only the listed address
      families, and within them only the given settings, are changed.
      Redistribution is configured with I(redistribute). Ignored when
      I(state) is C(delete).
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
          (C(maximum-paths) in the C(address-family) context). Requires REST
          API version 10.13 or later; with earlier versions only the global
          I(maximum_paths) is available.
        required: false
        type: int
      networks:
        description: >
          Networks announced by BGP (C(network)). Replaces the networks of this
          address family; use an empty list to remove them. Not supported for
          C(l2vpn_evpn).
        required: false
        type: list
        elements: dict
        suboptions:
          prefix:
            description: Network prefix, for example C(10.1.0.0/16).
            required: true
            type: str
          route_map:
            description: >
              Route map applied to the network (C(network <prefix> route-map
              <name>)). The route map must exist.
            required: false
            type: str
      aggregate_addresses:
        description: >
          Aggregate addresses (C(aggregate-address)). Replaces the aggregate
          addresses of this address family; use an empty list to remove them.
          Not supported for C(l2vpn_evpn).
        required: false
        type: list
        elements: dict
        suboptions:
          prefix:
            description: Aggregate prefix, for example C(10.2.0.0/16).
            required: true
            type: str
          options:
            description: >
              C(summary-only) advertises only the aggregate, C(as-set) keeps
              the AS path information of the aggregated routes,
              C(summary-as-set) combines both.
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
              Route map selecting the routes to suppress (C(suppress-map)).
              The route map must exist.
            required: false
            type: str
          advertise_map:
            description: >
              Route map selecting the routes used to build the aggregate
              (C(advertise-map)). The route map must exist.
            required: false
            type: str
          attribute_map:
            description: >
              Route map setting the attributes of the aggregate
              (C(attribute-map)). The route map must exist.
            required: false
            type: str
      dampening:
        description: >
          Route flap dampening parameters (C(bgp dampening)). Only the given
          parameters are changed; give none of them to disable dampening. Not
          supported for C(l2vpn_evpn).
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
          (C(bgp dampening route-map)). The route map must exist. Use an empty
          string to remove it. Not supported for C(l2vpn_evpn).
        required: false
        type: str
  redistribute:
    description: >
      Route redistribution per address family (C(redistribute) commands of
      the C(address-family) context). Only the listed address families are
      changed. Ignored when I(state) is C(delete).
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
          (C(redistribute <type> route-map <name>)), as a dictionary whose
          keys are route types of I(route_types) and values are route map
          names. Route types of I(route_types) that are not listed are
          redistributed without route map. The route maps must exist, see
          M(arubanetworks.aoscx.aoscx_route_map).
        required: false
        type: dict
  state:
    description: >
      Create or update (C(create)) or delete (C(delete)) the BGP router.
      Deleting the BGP router also removes its neighbors.
    required: false
    default: create
    choices:
      - create
      - delete
    type: str
"""

EXAMPLES = """
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
"""

RETURN = r"""
changed:
  description: Whether the BGP router was created, modified or deleted.
  returned: always
  type: bool
"""

import ipaddress

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_routing_policy import (  # NOQA
    check_reference,
    reference_name,
    reference_uri,
)

BOOLEAN_OPTIONS = (
    "log_neighbor_changes",
    "deterministic_med",
    "always_compare_med",
    "bestpath_as_path_multipath_relax",
    "fast_external_fallover",
    "bestpath_as_path_ignore",
    "bestpath_compare_routerid",
    "bestpath_med_confed",
    "bestpath_med_missing_as_worst",
    "bestpath_bgp_std_selection",
    "trap_enable",
)

# Options whose REST attribute has another name: option -> attribute
RENAMED_OPTIONS = {
    "aggregate_split_horizon": "agg_split_horizon",
    "disable": "protocol_disable",
    "default_local_preference": "local_pref",
    "maxas_limit": "maxas_limit",
    "asnotation": "asnotation",
}

# Dictionary options set on separate REST attributes:
# option -> {suboption: attribute}
GROUPED_OPTIONS = {
    "distance": {"ebgp": "ebgp_distance", "ibgp": "ibgp_distance"},
    "graceful_restart": {
        "enable": "gr_enable",
        "restart_time": "gr_restart_timer",
        "stalepath_time": "gr_stale_timer",
    },
    "confederation": {
        "identifier": "confederation_id",
        "peers": "confederation_peers",
    },
}

# Valid ranges of the integer options: (option, suboption) -> (min, max)
RANGES = {
    ("default_local_preference", None): (0, 4294967295),
    ("maxas_limit", None): (1, 32),
    ("timers", "keepalive"): (0, 65535),
    ("timers", "holdtime"): (0, 65535),
    ("timers", "connect_retry"): (1, 65535),
    ("distance", "ebgp"): (1, 255),
    ("distance", "ibgp"): (1, 255),
    ("graceful_restart", "restart_time"): (1, 3600),
    ("graceful_restart", "stalepath_time"): (1, 3600),
    ("confederation", "identifier"): (0, 4294967295),
}

DAMPENING_RANGES = {
    "half_life": (1, 45),
    "reuse": (1, 20000),
    "suppress": (1, 20000),
    "max_suppress_time": (1, 255),
}

AGGREGATE_MAPS = {
    "suppress_map": "suppress",
    "advertise_map": "advertise",
    "attribute_map": "attribute",
}

# Settings that do not exist for the l2vpn_evpn address family
UNICAST_ONLY = (
    "networks",
    "aggregate_addresses",
    "dampening",
    "dampening_route_map",
)

ROUTE_TYPES = ["connected", "local-loopback", "static", "ospf", "isis"]


def get_argument_spec():
    argument_spec = {
        "asn": {"type": "int", "required": True},
        "vrf": {"type": "str", "default": "default"},
        "router_id": {"type": "str"},
        "maximum_paths": {"type": "int"},
        "redistribute": {
            "type": "list",
            "elements": "dict",
            "options": {
                "address_family": {
                    "type": "str",
                    "required": True,
                    "choices": ["ipv4_unicast", "ipv6_unicast"],
                },
                "route_types": {
                    "type": "list",
                    "elements": "str",
                    "required": True,
                    "choices": ROUTE_TYPES,
                },
                "route_maps": {"type": "dict"},
            },
        },
        "cluster_id": {"type": "str"},
        "default_local_preference": {"type": "int"},
        "maxas_limit": {"type": "int"},
        "asnotation": {
            "type": "str",
            "choices": ["plain-text", "dotted", "dotted-plus"],
        },
        "aggregate_split_horizon": {"type": "bool"},
        "disable": {"type": "bool"},
        "timers": {
            "type": "dict",
            "options": {
                "keepalive": {"type": "int"},
                "holdtime": {"type": "int"},
                "connect_retry": {"type": "int"},
            },
        },
        "distance": {
            "type": "dict",
            "options": {"ebgp": {"type": "int"}, "ibgp": {"type": "int"}},
        },
        "graceful_restart": {
            "type": "dict",
            "options": {
                "enable": {"type": "bool"},
                "restart_time": {"type": "int"},
                "stalepath_time": {"type": "int"},
            },
        },
        "confederation": {
            "type": "dict",
            "options": {
                "identifier": {"type": "int"},
                "peers": {"type": "list", "elements": "int"},
            },
        },
        "address_families": {
            "type": "list",
            "elements": "dict",
            "options": {
                "address_family": {
                    "type": "str",
                    "required": True,
                    "choices": ["ipv4_unicast", "ipv6_unicast", "l2vpn_evpn"],
                },
                "maximum_paths": {"type": "int"},
                "networks": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "prefix": {"type": "str", "required": True},
                        "route_map": {"type": "str"},
                    },
                },
                "aggregate_addresses": {
                    "type": "list",
                    "elements": "dict",
                    "options": {
                        "prefix": {"type": "str", "required": True},
                        "options": {
                            "type": "str",
                            "default": "none",
                            "choices": [
                                "none",
                                "summary-only",
                                "as-set",
                                "summary-as-set",
                            ],
                        },
                        "suppress_map": {"type": "str"},
                        "advertise_map": {"type": "str"},
                        "attribute_map": {"type": "str"},
                    },
                },
                "dampening": {
                    "type": "dict",
                    "options": {
                        key: {"type": "int"} for key in DAMPENING_RANGES
                    },
                },
                "dampening_route_map": {"type": "str"},
            },
        },
        "state": {
            "type": "str",
            "default": "create",
            "choices": ["create", "delete"],
        },
    }
    for option in BOOLEAN_OPTIONS:
        argument_spec[option] = {"type": "bool"}
    return argument_spec


def validate_params(ansible_module):
    params = ansible_module.params
    if not 1 <= params["asn"] <= 4294967295:
        ansible_module.fail_json(msg="asn must be between 1 and 4294967295")
    if params["maximum_paths"] is not None and params["maximum_paths"] < 1:
        ansible_module.fail_json(msg="maximum_paths must be greater than 0")
    seen = set()
    for entry in params["redistribute"] or []:
        family = entry["address_family"]
        if family in seen:
            ansible_module.fail_json(
                msg="Duplicate redistribute address family: " + family
            )
        seen.add(family)
        for route_type, route_map in (entry["route_maps"] or {}).items():
            if route_type not in entry["route_types"]:
                ansible_module.fail_json(
                    msg="route_maps: {0} is not in the route_types of "
                    "{1}".format(route_type, family)
                )
            if not isinstance(route_map, str) or not route_map:
                ansible_module.fail_json(
                    msg="route_maps: invalid route map for {0}".format(
                        route_type
                    )
                )

    for (option, suboption), (low, high) in RANGES.items():
        value = params[option]
        if suboption is not None:
            value = (value or {}).get(suboption)
        name = option if suboption is None else option + "." + suboption
        check_range(ansible_module, name, value, low, high)
    peers = (params["confederation"] or {}).get("peers") or []
    for peer in peers:
        check_range(ansible_module, "confederation.peers", peer, 1, 4294967295)
    validate_address_families(ansible_module)


def check_range(ansible_module, name, value, low, high):
    if value is not None and not low <= value <= high:
        ansible_module.fail_json(
            msg="{0} must be between {1} and {2}".format(name, low, high)
        )


def normalize_prefix(ansible_module, prefix):
    try:
        return str(ipaddress.ip_network("{0}".format(prefix), strict=False))
    except ValueError:
        ansible_module.fail_json(msg="Invalid prefix: {0}".format(prefix))


def validate_address_families(ansible_module):
    seen = set()
    for entry in ansible_module.params["address_families"] or []:
        family = entry["address_family"]
        if family in seen:
            ansible_module.fail_json(msg="Duplicate address family: " + family)
        seen.add(family)
        if family == "l2vpn_evpn":
            for setting in UNICAST_ONLY:
                if entry[setting] is not None:
                    ansible_module.fail_json(
                        msg="{0} is not supported for {1}".format(
                            setting, family
                        )
                    )
        if entry["maximum_paths"] is not None and entry["maximum_paths"] < 1:
            ansible_module.fail_json(
                msg="maximum_paths must be greater than 0"
            )
        for key, (low, high) in DAMPENING_RANGES.items():
            value = (entry["dampening"] or {}).get(key)
            check_range(ansible_module, "dampening." + key, value, low, high)
        version = 6 if family == "ipv6_unicast" else 4
        for setting in ("networks", "aggregate_addresses"):
            prefixes = set()
            for item in entry[setting] or []:
                prefix = normalize_prefix(ansible_module, item["prefix"])
                if ipaddress.ip_network(prefix).version != version:
                    ansible_module.fail_json(
                        msg="{0}: {1} is not an {2} prefix".format(
                            setting, item["prefix"], family
                        )
                    )
                if prefix in prefixes:
                    ansible_module.fail_json(
                        msg="{0}: duplicate prefix {1}".format(setting, prefix)
                    )
                prefixes.add(prefix)
                item["prefix"] = prefix


def referenced_route_maps(params):
    names = set()
    for entry in params["redistribute"] or []:
        names.update((entry["route_maps"] or {}).values())
    for entry in params["address_families"] or []:
        names.add(entry["dampening_route_map"])
        for network in entry["networks"] or []:
            names.add(network["route_map"])
        for aggregate in entry["aggregate_addresses"] or []:
            names.update(aggregate[option] for option in AGGREGATE_MAPS)
    return sorted(name for name in names if name)


def check_route_maps(ansible_module, session):
    for route_map in referenced_route_maps(ansible_module.params):
        check_reference(ansible_module, session, "route map", route_map)


def get_desired(params, bgp_router):
    """
    Build the desired REST attributes. Per address family attributes are
    merged with the current ones, so that only the given families change.
    """
    desired = {}
    if params["router_id"] is not None:
        desired["router_id"] = params["router_id"]
    for option in BOOLEAN_OPTIONS:
        if params[option] is not None:
            desired[option] = params[option]

    if params["maximum_paths"] is not None:
        current = getattr(bgp_router, "maximum_paths", None)
        if isinstance(current, dict) or (
            current is None and not legacy_maximum_paths(bgp_router)
        ):
            maximum_paths = dict(current or {})
            maximum_paths["all-afs"] = params["maximum_paths"]
            desired["maximum_paths"] = maximum_paths
        else:
            desired["maximum_paths"] = params["maximum_paths"]

    if params["redistribute"] is not None:
        session = bgp_router.session
        redistribute = normalize_redistribute(
            getattr(bgp_router, "redistribute", None)
        )
        route_maps = normalize_route_maps(
            getattr(bgp_router, "redistribute_route_map", None)
        )
        for entry in params["redistribute"]:
            family = entry["address_family"].replace("_", "-")
            family_maps = entry["route_maps"] or {}
            # A route type redistributed through a route map is only listed
            # in redistribute_route_map
            route_types = sorted(set(entry["route_types"]) - set(family_maps))
            if route_types:
                redistribute[family] = route_types
            else:
                redistribute.pop(family, None)
            if family_maps:
                route_maps[family] = dict(family_maps)
            else:
                route_maps.pop(family, None)
        desired["redistribute"] = redistribute
        desired["redistribute_route_map"] = route_map_uris(session, route_maps)

    for option, attribute in RENAMED_OPTIONS.items():
        if params[option] is not None:
            desired[attribute] = params[option]
    if params["cluster_id"] is not None:
        desired["cluster_id"] = params["cluster_id"] or None
    if params["timers"] is not None:
        timers = dict(getattr(bgp_router, "timers", None) or {})
        for key, value in params["timers"].items():
            if value is not None:
                timers[key.replace("_", "-")] = value
        desired["timers"] = timers
    for option, attributes in GROUPED_OPTIONS.items():
        for suboption, attribute in attributes.items():
            value = (params[option] or {}).get(suboption)
            if value is None:
                continue
            if attribute == "confederation_id":
                value = value or None
            elif attribute == "confederation_peers":
                value = sorted(set(value))
            desired[attribute] = value

    if params["address_families"]:
        desired.update(get_desired_families(params, bgp_router, desired))
    return desired


def route_map_uris(session, route_maps):
    """{family: {key: name}} -> {family: {key: uri}}"""
    return {
        family: {
            key: reference_uri(session, "route map", name)
            for key, name in maps.items()
        }
        for family, maps in route_maps.items()
    }


def get_desired_families(params, bgp_router, desired):
    """Desired REST attributes of the address_families option."""
    session = bgp_router.session
    families = {}
    # Only a dictionary (REST API 10.13 and later) when maximum_paths is
    # given per address family, which is checked before
    maximum_paths = desired.get("maximum_paths")
    if maximum_paths is None:
        maximum_paths = getattr(bgp_router, "maximum_paths", None)
    if not isinstance(maximum_paths, dict):
        maximum_paths = {}
    maximum_paths = dict(maximum_paths)
    networks = normalize_networks(getattr(bgp_router, "networks", None))
    network_maps = normalize_route_maps(
        getattr(bgp_router, "networks_route_maps", None)
    )
    dampening = dict(getattr(bgp_router, "dampening", None) or {})
    dampening_maps = normalize_references(
        getattr(bgp_router, "dampening_route_map", None)
    )
    for entry in params["address_families"]:
        family = entry["address_family"].replace("_", "-")
        if entry["maximum_paths"] is not None:
            maximum_paths[family] = entry["maximum_paths"]
            families["maximum_paths"] = maximum_paths
        if entry["networks"] is not None:
            # A network announced through a route map is only listed in
            # networks_route_maps
            plain = sorted(
                item["prefix"]
                for item in entry["networks"]
                if not item["route_map"]
            )
            maps = {
                item["prefix"]: item["route_map"]
                for item in entry["networks"]
                if item["route_map"]
            }
            set_or_remove(networks, family, plain)
            set_or_remove(network_maps, family, maps)
            families["networks"] = networks
            families["networks_route_maps"] = route_map_uris(
                session, network_maps
            )
        if entry["dampening"] is not None:
            given = {
                key: value
                for key, value in entry["dampening"].items()
                if value is not None
            }
            current = dict(dampening.get(family) or {}) if given else {}
            current.update(given)
            set_or_remove(dampening, family, current)
            families["dampening"] = dampening
        if entry["dampening_route_map"] is not None:
            set_or_remove(dampening_maps, family, entry["dampening_route_map"])
            families["dampening_route_map"] = {
                key: reference_uri(session, "route map", name)
                for key, name in dampening_maps.items()
            }
    return families


def set_or_remove(container, key, value):
    if value:
        container[key] = value
    else:
        container.pop(key, None)


def normalize_networks(networks):
    return {
        family: sorted(set(prefixes))
        for family, prefixes in (networks or {}).items()
        if prefixes
    }


def normalize_references(references):
    """{key: uri or {name: uri}} -> {key: name}"""
    return {
        key: reference_name(reference)
        for key, reference in (references or {}).items()
        if reference
    }


def legacy_maximum_paths(bgp_router):
    """
    REST API versions up to 10.09 use an integer for maximum_paths, later
    versions use a dictionary keyed by address family.
    """
    version = str(getattr(bgp_router.session.api, "version", ""))
    try:
        major, minor = (int(part) for part in version.split(".")[:2])
    except ValueError:
        return False
    return (major, minor) < (10, 13)


def normalize_redistribute(redistribute):
    return {
        family: sorted(set(route_types))
        for family, route_types in (redistribute or {}).items()
        if route_types
    }


def normalize_route_maps(route_maps):
    """Route maps by address family and route type, as names."""
    return {
        family: {
            route_type: reference_name(route_map)
            for route_type, route_map in maps.items()
        }
        for family, maps in (route_maps or {}).items()
        if maps
    }


NORMALIZERS = {
    "redistribute": normalize_redistribute,
    "redistribute_route_map": normalize_route_maps,
    "networks": normalize_networks,
    "networks_route_maps": normalize_route_maps,
    "dampening_route_map": normalize_references,
    "confederation_peers": lambda peers: sorted(peers or []),
}


def apply_configuration(bgp_router, desired, check_mode):
    changes = {}
    for key, value in desired.items():
        current = getattr(bgp_router, key, None)
        normalize = NORMALIZERS.get(key)
        if normalize:
            changed = normalize(current) != normalize(value)
        else:
            changed = current != value
        if changed:
            changes[key] = value

    if bgp_router.materialized and not changes:
        return False
    if check_mode:
        return True

    for key, value in changes.items():
        setattr(bgp_router, key, value)
        if key not in bgp_router.config_attrs:
            bgp_router.config_attrs.append(key)
    bgp_router.apply()
    return True


class AggregateAddresses(object):
    """Create, update and remove the aggregate addresses of a BGP router."""

    def __init__(self, ansible_module, bgp_router):
        self.module = ansible_module
        self.bgp_router = bgp_router
        self.session = bgp_router.session
        self.cls = self.session.api.get_module_class(
            self.session, "AggregateAddress"
        )
        self.existing = None

    def read_existing(self):
        if not self.bgp_router.materialized:
            return {}
        existing = {}
        for aggregate in self.cls.get_all(
            self.session, self.bgp_router
        ).values():
            aggregate.get()
            existing[(aggregate.address_family, aggregate.ip_prefix)] = (
                aggregate
            )
        return existing

    def desired(self, family, item):
        maps = {
            key: reference_uri(self.session, "route map", item[option])
            for option, key in AGGREGATE_MAPS.items()
            if item[option]
        }
        return {"options": item["options"], "aggregate_route_map": maps}

    @staticmethod
    def differs(aggregate, desired):
        if getattr(aggregate, "options", None) != desired["options"]:
            return True
        current = normalize_references(
            getattr(aggregate, "aggregate_route_map", None)
        )
        return current != normalize_references(desired["aggregate_route_map"])

    def apply(self, families):
        """
        :param families: {family: [aggregate items]} for the address
            families whose aggregate addresses are managed.
        :return: True if an aggregate address was changed.
        """
        check_mode = self.module.check_mode
        existing = self.read_existing()
        changed = False
        for family, items in families.items():
            wanted = set()
            for item in items:
                key = (family, item["prefix"])
                wanted.add(key)
                desired = self.desired(family, item)
                aggregate = existing.get(key)
                if aggregate is None:
                    changed = True
                    if not check_mode:
                        self.cls(
                            self.session,
                            family,
                            item["prefix"],
                            self.bgp_router,
                            **desired
                        ).create()
                elif self.differs(aggregate, desired):
                    changed = True
                    if not check_mode:
                        for attribute, value in desired.items():
                            setattr(aggregate, attribute, value)
                            if attribute not in aggregate.config_attrs:
                                aggregate.config_attrs.append(attribute)
                        aggregate.update()
            for key, aggregate in existing.items():
                if key[0] == family and key not in wanted:
                    changed = True
                    if not check_mode:
                        aggregate.delete()
        return changed


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
    )
    validate_params(ansible_module)

    params = ansible_module.params
    asn = params["asn"]
    vrf_name = params["vrf"]
    state = params["state"]
    check_mode = ansible_module.check_mode

    result = dict(changed=False)

    try:
        from pyaoscx.exceptions.generic_op_error import GenericOperationError
        from pyaoscx.exceptions.pyaoscx_error import PyaoscxError
    except ImportError as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    Vrf = session.api.get_module_class(session, "Vrf")
    vrf = Vrf(session, vrf_name)
    try:
        vrf.get()
    except GenericOperationError as e:
        if e.response_code != 404:
            ansible_module.fail_json(msg=str(e))
        if state == "delete":
            ansible_module.exit_json(**result)
        if check_mode:
            # The VRF may be created by a previous task of the playbook
            result["changed"] = True
            ansible_module.exit_json(**result)
        ansible_module.fail_json(
            msg="VRF {0} does not exist, create it first".format(vrf_name)
        )
    except PyaoscxError as e:
        ansible_module.fail_json(msg=str(e))

    BgpRouter = session.api.get_module_class(session, "BgpRouter")
    bgp_router = BgpRouter(session, asn, parent_vrf=vrf)
    try:
        bgp_router.get()
    except GenericOperationError as e:
        if e.response_code != 404 or bgp_router.materialized:
            ansible_module.fail_json(msg=str(e))
    except PyaoscxError as e:
        ansible_module.fail_json(msg=str(e))

    try:
        if state == "delete":
            if bgp_router.materialized:
                if not check_mode:
                    bgp_router.delete()
                result["changed"] = True
        else:
            check_route_maps(ansible_module, session)
            if legacy_maximum_paths(bgp_router) and any(
                entry["maximum_paths"] is not None
                for entry in params["address_families"] or []
            ):
                ansible_module.fail_json(
                    msg="maximum_paths per address family requires REST API "
                    "version 10.13 or later"
                )
            desired = get_desired(params, bgp_router)
            result["changed"] = apply_configuration(
                bgp_router, desired, check_mode
            )
            aggregates = {
                entry["address_family"].replace("_", "-"): entry[
                    "aggregate_addresses"
                ]
                for entry in params["address_families"] or []
                if entry["aggregate_addresses"] is not None
            }
            if aggregates and AggregateAddresses(
                ansible_module, bgp_router
            ).apply(aggregates):
                result["changed"] = True
    except PyaoscxError as e:
        ansible_module.fail_json(msg=str(e), **result)

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
