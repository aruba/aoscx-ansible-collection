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
module: aoscx_bgp_neighbor
version_added: "4.6.0"
short_description: Create, Update or Delete BGP neighbors on AOS-CX
description: >
  This module provides configuration management of BGP neighbors or peer
  groups (C(neighbor) commands of the C(router bgp) context) on AOS-CX
  devices, including their per address family settings. The same settings
  are applied to every neighbor given in I(neighbor) or I(neighbors). Other
  neighbors of the BGP router are never modified or deleted. The BGP router
  must exist, see M(arubanetworks.aoscx.aoscx_bgp_router).
author: Aruba Networks (@ArubaNetworks)
notes:
  - Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor and route
    map handling of earlier releases.
  - Tested on a switch with REST API version 10.09 (firmware 10.19).
  - The switch stores I(password) encrypted, so a change of password is only
    applied with I(update_password=always).
  - In check mode, a missing VRF or BGP router is reported as a change
    instead of an error, and referenced route maps are not checked, because
    they may be created by a previous task of the playbook.
options:
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
      name of an unnumbered neighbor. Mutually exclusive with I(neighbors),
      one of them is required.
    required: false
    type: str
  neighbors:
    description: >
      List of neighbors (IPv4/IPv6 addresses or peer group names) that get
      the same settings. Neighbors of the BGP router that are not listed are
      not modified. All the neighbors are checked before the first change is
      applied. Mutually exclusive with I(neighbor).
    required: false
    type: list
    elements: str
  is_peer_group:
    description: >
      Whether the neighbors are peer groups (C(neighbor <name> peer-group)).
      Only used on creation, it cannot be changed on an existing neighbor.
    required: false
    default: false
    type: bool
  peer_group:
    description: >
      Name of the peer group the neighbor belongs to
      (C(neighbor <ip> peer-group <name>)). The peer group must exist. Use an
      empty string to remove the neighbor from its peer group. Not supported
      when I(is_peer_group) is C(true).
    required: false
    type: str
  remote_as:
    description: ASN of the neighbor (C(remote-as)).
    required: false
    type: int
  description:
    description: Description of the neighbor (C(description)).
    required: false
    type: str
  update_source:
    description: >
      Source of the BGP session (C(update-source)): either an IP address, or
      the name of a loopback interface such as C(loopback0) (C(loopback 0)
      is also accepted). Use an empty string to remove it.
    required: false
    type: str
  ebgp_multihop:
    description: >
      Maximum number of hops to an external neighbor (C(ebgp-multihop)),
      between 1 and 255. Required for eBGP sessions between loopbacks. Use
      C(255) for the CLI C(ebgp-multihop) command without value, and C(1) to
      remove it (C(no neighbor ... ebgp-multihop)).
    required: false
    type: int
  shutdown:
    description: Administratively shut down the neighbor (C(shutdown)).
    required: false
    type: bool
  fall_over:
    description: >
      Reset the session as soon as the route to the neighbor is lost
      (C(fall-over)).
    required: false
    type: bool
  fall_over_bfd:
    description: >
      Track the session with BFD (C(fall-over bfd)).
    required: false
    type: bool
  passive:
    description: >
      Do not initiate the session, only accept it (C(passive)).
    required: false
    type: bool
  remove_private_as:
    description: >
      Remove the private AS numbers from the updates sent to the neighbor
      (C(remove-private-as)).
    required: false
    type: bool
  slow_peer:
    description: >
      Place the neighbor in a separate update group for slow peers
      (C(slow-peer)).
    required: false
    type: bool
  weight:
    description: >
      Default weight of the routes received from the neighbor, between 0 and
      65535 (C(weight)).
    required: false
    type: int
  local_as:
    description: >
      Local AS number used with this external neighbor, between 1 and
      4294967295 (C(local-as)). Use C(0) to remove it.
    required: false
    type: int
  local_as_mode:
    description: >
      Options of I(local_as): C(no-prepend), C(no-prepend-replace-as),
      C(no-prepend-replace-as-dual-as), or C(none) for no option.
    required: false
    type: str
    choices:
      - none
      - no-prepend
      - no-prepend-replace-as
      - no-prepend-replace-as-dual-as
  port:
    description: >
      TCP port of the session, between 1 and 65535 (C(port)). Use C(0) to
      remove it.
    required: false
    type: int
  ttl_security_hops:
    description: >
      Maximum number of hops to the neighbor checked with TTL security,
      between 1 and 254 (C(ttl-security-hops)). Takes precedence over
      I(ebgp_multihop). Use C(0) to remove it.
    required: false
    type: int
  password:
    description: >
      Password of the session (C(password)). The switch stores it encrypted,
      so it cannot be compared: see I(update_password). Use an empty string
      to remove it. Mutually exclusive with the TCP-AO keychain of I(ao).
    required: false
    type: str
  update_password:
    description: >
      C(on_create) sets I(password) only when the neighbor has no password,
      so that the module stays idempotent. C(always) sets it on every run,
      and then always reports a change.
    required: false
    default: on_create
    type: str
    choices:
      - on_create
      - always
  timers:
    description: >
      Timers of the session in seconds (C(timers)). Only the given timers are
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
          (C(timers connect-retry)).
        required: false
        type: int
  graceful_shutdown:
    description: >
      Graceful shutdown parameters (C(graceful-shutdown)). Only the given
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
      the session (C(invalid-attribute all accept)). Enabled by default on the
      switch.
    required: false
    type: bool
  ao:
    description: >
      TCP Authentication Option settings (C(ao)). Only the given settings are
      changed.
    required: false
    type: dict
    suboptions:
      keychain:
        description: >
          Keychain used by TCP-AO (C(ao keychain)). The keychain must exist.
          Use an empty string to remove it. Mutually exclusive with
          I(password).
        required: false
        type: str
      accept_ao_mismatch:
        description: >
          Accept the segments whose TCP-AO MAC does not match
          (C(ao accept-ao-mismatch)).
        required: false
        type: bool
      include_tcp_options:
        description: >
          Include the other TCP options in the MAC calculation
          (C(ao include-tcp-options)).
        required: false
        type: bool
  interface:
    description: >
      Interface of an unnumbered neighbor (C(interface)), for example
      C(1/1/3); the neighbor is then usually named after the interface. Only
      used on creation, it cannot be changed on an existing neighbor. The
      interface must exist.
    required: false
    type: str
  address_families:
    description: >
      Per address family settings (C(neighbor) commands of the
      C(address-family) contexts). Only the listed address families, and
      within them only the given settings, are changed. Ignored when
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
      activate:
        description: Activate the neighbor in the address family (C(activate)).
        required: false
        type: bool
      send_community:
        description: >
          Communities sent to the neighbor (C(send-community)). C(none)
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
          (C(route-reflector-client)).
        required: false
        type: bool
      next_hop_self:
        description: >
          Advertise this router as next hop (C(next-hop-self)). Not supported
          for C(l2vpn_evpn).
        required: false
        type: bool
      next_hop_unchanged:
        description: >
          Keep the next hop unchanged (C(next-hop-unchanged)). Only supported
          for C(l2vpn_evpn).
        required: false
        type: bool
      inbound_soft_reconfiguration:
        description: >
          Enable inbound soft reconfiguration
          (C(soft-reconfiguration inbound)). Not supported for C(l2vpn_evpn).
        required: false
        type: bool
      route_map_in:
        description: >
          Route map applied to the routes received from the neighbor
          (C(route-map <name> in)). The route map must exist, see
          M(arubanetworks.aoscx.aoscx_route_map). Use an empty string to
          remove it.
        required: false
        type: str
      route_map_out:
        description: >
          Route map applied to the routes advertised to the neighbor
          (C(route-map <name> out)). The route map must exist. Use an empty
          string to remove it.
        required: false
        type: str
      default_originate:
        description: >
          Advertise a default route to the neighbor (C(default-originate)).
          Not supported for C(l2vpn_evpn).
        required: false
        type: bool
      default_originate_route_map:
        description: >
          Route map that sets the criteria to advertise the default route
          (C(default-originate route-map <name>)). Requires
          I(default_originate). The route map must exist. Use an empty string
          to remove it. Not supported for C(l2vpn_evpn).
        required: false
        type: str
      allowas_in:
        description: >
          Number of times the local AS may appear in the AS path of the
          received routes, between 1 and 10 (C(allowas-in)). Use C(0) to
          remove it.
        required: false
        type: int
      advertisement_interval:
        description: >
          Minimum interval in seconds between two updates, between 0 and 600
          (C(advertisement-interval)). Not supported for C(l2vpn_evpn).
        required: false
        type: int
      add_paths:
        description: >
          Additional paths capability (C(add-paths)). Not supported for
          C(l2vpn_evpn).
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
          (C(add-paths advertise-best)). Not supported for C(l2vpn_evpn).
        required: false
        type: int
      maximum_prefix:
        description: >
          Maximum number of prefixes accepted from the neighbor
          (C(maximum-prefix)). Replaces the settings of this address family.
        required: false
        type: dict
        suboptions:
          limit:
            description: >
              Maximum number of prefixes, between 1 and 4294967295. Use C(0)
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
              closing the session (C(warning-only)). The switch uses
              C(true) when it is not given.
            required: false
            type: bool
      orf_capability:
        description: >
          Outbound Route Filtering capability for prefix lists
          (C(capability orf prefix-list)). C(none) removes it. C(both) is not
          available, because the switch ignores it when set through the REST
          API. Not supported for C(l2vpn_evpn).
        required: false
        type: str
        choices:
          - send
          - receive
          - none
      orf_prefix_list:
        description: >
          Inbound prefix list advertised to the neighbor with ORF
          (C(orf-prefix-list <name> in)). The prefix list must exist. Use an
          empty string to remove it. Not supported for C(l2vpn_evpn).
        required: false
        type: str
      replace_rt_asn:
        description: >
          Replace the AS number of the received route targets by the local AS
          number (C(replace-rt-asn)). Only supported for C(l2vpn_evpn).
        required: false
        type: bool
  state:
    description: >
      Create or update (C(create)) or delete (C(delete)) the given
      neighbors. Other neighbors are never deleted. A peer group cannot be
      deleted while neighbors belong to it.
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
"""

RETURN = r"""
changed:
  description: Whether a neighbor was created, modified or deleted.
  returned: always
  type: bool
"""

import copy
import ipaddress
import json
import re

from ansible.module_utils.six.moves.urllib.parse import quote

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_routing_policy import (  # NOQA
    check_reference,
    reference_name,
    reference_uri,
)

AF_SETTINGS = (
    "activate",
    "send_community",
    "route_reflector_client",
    "next_hop_self",
    "next_hop_unchanged",
    "inbound_soft_reconfiguration",
    "default_originate",
    "replace_rt_asn",
)

# Per address family values whose REST attribute has another name, or that
# are removed with 0: option -> (REST attribute, removable with 0)
AF_VALUES = {
    "allowas_in": ("allow_as_in", True),
    "advertisement_interval": ("advertisement_interval", False),
    "add_paths": ("add_paths", False),
    "add_paths_advertise_best": ("add_paths_adv_best_n", False),
}

AF_RANGES = {
    "allowas_in": (0, 10),
    "advertisement_interval": (0, 600),
    "add_paths_advertise_best": (1, 4),
}

MAXIMUM_PREFIX = {
    "limit": "maximum_prefix_limit",
    "threshold": "threshold",
    "restart": "restart",
}

MAXIMUM_PREFIX_RANGES = {
    "limit": (0, 4294967295),
    "threshold": (1, 100),
    "restart": (30, 65535),
}

# Session options whose REST attribute has another name
SESSION_OPTIONS = {
    "remote_as": "remote_as",
    "description": "description",
    "shutdown": "shutdown",
    "fall_over": "fall_over",
    "fall_over_bfd": "bfd_enable",
    "passive": "passive",
    "remove_private_as": "remove_private_as",
    "slow_peer": "slow_peer",
    "weight": "weight",
    "local_as_mode": "local_as_mode",
}

# Session options removed with 0: option -> REST attribute
REMOVABLE_OPTIONS = {
    "local_as": "local_as",
    "port": "tcp_port_number",
    "ttl_security_hops": "ttl_security_hops",
}

RANGES = {
    ("weight", None): (0, 65535),
    ("local_as", None): (0, 4294967295),
    ("port", None): (0, 65535),
    ("ttl_security_hops", None): (0, 254),
    ("timers", "keepalive"): (0, 65535),
    ("timers", "holdtime"): (0, 65535),
    ("timers", "connect_retry"): (1, 65535),
    ("graceful_shutdown", "timer"): (10, 1200),
    ("graceful_shutdown", "local_preference"): (0, 4294967295),
}

# Unnumbered neighbors are named after their interface, for example 1/1/3
INTERFACE_NAME = re.compile(r"^\d+(/\d+)+$")

# Per address family route map references: option -> (REST attribute, key)
AF_ROUTE_MAPS = {
    "route_map_in": ("route_maps", "in"),
    "route_map_out": ("route_maps", "out"),
    "default_originate_route_map": ("default_originate_route_map", None),
}

# Settings that do not exist in some address families
UNSUPPORTED_AF_SETTINGS = {
    "l2vpn_evpn": (
        "next_hop_self",
        "inbound_soft_reconfiguration",
        "default_originate",
        "default_originate_route_map",
        "advertisement_interval",
        "add_paths",
        "add_paths_advertise_best",
        "orf_capability",
        "orf_prefix_list",
    ),
    "ipv4_unicast": ("next_hop_unchanged", "replace_rt_asn"),
    "ipv6_unicast": ("next_hop_unchanged", "replace_rt_asn"),
}


def get_argument_spec():
    af_options = {
        "address_family": {
            "type": "str",
            "required": True,
            "choices": list(UNSUPPORTED_AF_SETTINGS),
        },
        "send_community": {
            "type": "str",
            "choices": ["both", "extended", "standard", "none"],
        },
    }
    for setting in AF_SETTINGS:
        af_options.setdefault(setting, {"type": "bool"})
    for option in AF_ROUTE_MAPS:
        af_options[option] = {"type": "str"}
    af_options.update(
        {
            "allowas_in": {"type": "int"},
            "advertisement_interval": {"type": "int"},
            "add_paths": {
                "type": "str",
                "choices": ["send", "recv", "both", "disable"],
            },
            "add_paths_advertise_best": {"type": "int"},
            "maximum_prefix": {
                "type": "dict",
                "options": {
                    "limit": {"type": "int", "required": True},
                    "threshold": {"type": "int"},
                    "restart": {"type": "int"},
                    "warning_only": {"type": "bool"},
                },
            },
            "orf_capability": {
                "type": "str",
                "choices": ["send", "receive", "none"],
            },
            "orf_prefix_list": {"type": "str"},
        }
    )
    return {
        "asn": {"type": "int", "required": True},
        "vrf": {"type": "str", "default": "default"},
        "neighbor": {"type": "str"},
        "neighbors": {"type": "list", "elements": "str"},
        "is_peer_group": {"type": "bool", "default": False},
        "peer_group": {"type": "str"},
        "remote_as": {"type": "int"},
        "description": {"type": "str"},
        "update_source": {"type": "str"},
        "ebgp_multihop": {"type": "int"},
        "shutdown": {"type": "bool"},
        "fall_over": {"type": "bool"},
        "fall_over_bfd": {"type": "bool"},
        "passive": {"type": "bool"},
        "remove_private_as": {"type": "bool"},
        "slow_peer": {"type": "bool"},
        "weight": {"type": "int"},
        "local_as": {"type": "int"},
        "local_as_mode": {
            "type": "str",
            "choices": [
                "none",
                "no-prepend",
                "no-prepend-replace-as",
                "no-prepend-replace-as-dual-as",
            ],
        },
        "port": {"type": "int"},
        "ttl_security_hops": {"type": "int"},
        "password": {"type": "str", "no_log": True},
        "update_password": {
            "type": "str",
            "default": "on_create",
            "choices": ["on_create", "always"],
        },
        "timers": {
            "type": "dict",
            "options": {
                "keepalive": {"type": "int"},
                "holdtime": {"type": "int"},
                "connect_retry": {"type": "int"},
            },
        },
        "graceful_shutdown": {
            "type": "dict",
            "options": {
                "timer": {"type": "int"},
                "local_preference": {"type": "int"},
            },
        },
        "accept_invalid_attributes": {"type": "bool"},
        "ao": {
            "type": "dict",
            "options": {
                "keychain": {"type": "str", "no_log": False},
                "accept_ao_mismatch": {"type": "bool"},
                "include_tcp_options": {"type": "bool"},
            },
        },
        "interface": {"type": "str"},
        "address_families": {
            "type": "list",
            "elements": "dict",
            "options": af_options,
        },
        "state": {
            "type": "str",
            "default": "create",
            "choices": ["create", "delete"],
        },
    }


def get_neighbor_names(params):
    if params["neighbor"] is not None:
        return [params["neighbor"]]
    return params["neighbors"]


def validate_params(ansible_module):
    params = ansible_module.params
    names = get_neighbor_names(params)
    if not 1 <= params["asn"] <= 4294967295:
        ansible_module.fail_json(msg="asn must be between 1 and 4294967295")
    if params["remote_as"] is not None and not (
        1 <= params["remote_as"] <= 4294967295
    ):
        ansible_module.fail_json(
            msg="remote_as must be between 1 and 4294967295"
        )
    if params["ebgp_multihop"] is not None and not (
        1 <= params["ebgp_multihop"] <= 255
    ):
        ansible_module.fail_json(msg="ebgp_multihop must be between 1 and 255")
    if not names:
        ansible_module.fail_json(msg="neighbors must not be empty")
    if len(set(names)) != len(names):
        ansible_module.fail_json(msg="Duplicate entries in neighbors")
    for name in names:
        # The name is interpolated into the REST URI
        if name in ("", ".", "..") or (
            "/" in name and not INTERFACE_NAME.match(name)
        ):
            ansible_module.fail_json(msg="Invalid neighbor: {0}".format(name))
    for (option, suboption), (low, high) in RANGES.items():
        value = params[option]
        if suboption is not None:
            value = (value or {}).get(suboption)
        name = option if suboption is None else option + "." + suboption
        check_range(ansible_module, name, value, low, high)
    if params["password"] and (params["ao"] or {}).get("keychain"):
        ansible_module.fail_json(
            msg="password and ao.keychain are mutually exclusive"
        )
    if params["interface"] is not None and (
        params["is_peer_group"] or not params["interface"]
    ):
        ansible_module.fail_json(
            msg=(
                "interface is not supported for a peer group"
                if params["interface"]
                else "interface must not be empty"
            )
        )
    if params["peer_group"] and params["peer_group"] in names:
        ansible_module.fail_json(
            msg="A neighbor cannot belong to itself as peer group"
        )
    if params["is_peer_group"] and params["peer_group"]:
        ansible_module.fail_json(
            msg="peer_group is not supported when is_peer_group is true"
        )
    seen = set()
    for entry in params["address_families"] or []:
        family = entry["address_family"]
        if family in seen:
            ansible_module.fail_json(msg="Duplicate address family: " + family)
        seen.add(family)
        for setting in UNSUPPORTED_AF_SETTINGS[family]:
            if entry[setting] is not None:
                ansible_module.fail_json(
                    msg="{0} is not supported for {1}".format(setting, family)
                )
        if entry["default_originate_route_map"] and (
            entry["default_originate"] is False
        ):
            ansible_module.fail_json(
                msg="default_originate_route_map requires default_originate"
            )
        for option, (low, high) in AF_RANGES.items():
            check_range(ansible_module, option, entry[option], low, high)
        for option, (low, high) in MAXIMUM_PREFIX_RANGES.items():
            value = (entry["maximum_prefix"] or {}).get(option)
            check_range(
                ansible_module, "maximum_prefix." + option, value, low, high
            )


def check_range(ansible_module, name, value, low, high):
    if value is not None and not low <= value <= high:
        ansible_module.fail_json(
            msg="{0} must be between {1} and {2}".format(name, low, high)
        )


def check_references(ansible_module, session):
    """Fail if a referenced route map, prefix list or keychain is missing."""
    params = ansible_module.params
    references = set()
    for entry in params["address_families"] or []:
        for option in AF_ROUTE_MAPS:
            references.add(("route map", entry[option]))
        references.add(("prefix list", entry["orf_prefix_list"]))
    references.add(("keychain", (params["ao"] or {}).get("keychain")))
    for kind, name in sorted(ref for ref in references if ref[1]):
        check_reference(ansible_module, session, kind, name)


def is_ip_address(value):
    try:
        ipaddress.ip_address("{0}".format(value))
    except ValueError:
        return False
    return True


def read_create_only(neighbor):
    """
    is_peer_group and nbr_interface can only be set on creation, so the
    switch does not return them with the writable selector used by pyaoscx:
    read them separately.
    """
    from pyaoscx.exceptions.generic_op_error import GenericOperationError

    uri = "{0}/{1}".format(
        neighbor.base_uri,
        quote(str(neighbor.ip_or_ifname_or_group_name), safe=""),
    )
    response = neighbor.session.request(
        "GET",
        uri,
        params={
            "selector": "configuration",
            "attributes": "is_peer_group,nbr_interface",
        },
    )
    if response.status_code != 200:
        raise GenericOperationError(response.text, response.status_code)
    return json.loads(response.text)


def read_is_peer_group(neighbor):
    return bool(read_create_only(neighbor).get("is_peer_group", False))


class NeighborConfig(object):
    """Compute and apply the changes of a BGP neighbor."""

    def __init__(self, ansible_module, session, bgp_router, neighbor):
        self.module = ansible_module
        self.params = ansible_module.params
        self.session = session
        self.bgp_router = bgp_router
        self.neighbor = neighbor
        self.changes = {}

    def set(self, key, value, current):
        if current != value:
            self.changes[key] = value

    def merge(self, attribute, values):
        """Merge the given values into a dictionary attribute."""
        current = self.changes.get(attribute)
        if current is None:
            current = dict(getattr(self.neighbor, attribute, None) or {})
        merged = dict(current, **values)
        if merged != current or attribute in self.changes:
            self.changes[attribute] = merged

    def compute(self):
        params = self.params
        neighbor = self.neighbor
        for option, attribute in SESSION_OPTIONS.items():
            if params[option] is not None:
                self.set(
                    attribute,
                    params[option],
                    getattr(neighbor, attribute, None),
                )
        for option, attribute in REMOVABLE_OPTIONS.items():
            if params[option] is not None:
                self.set(
                    attribute,
                    params[option] or None,
                    getattr(neighbor, attribute, None),
                )
        if params["accept_invalid_attributes"] is not None:
            accept = "all" if params["accept_invalid_attributes"] else "none"
            self.merge("invalid_attributes", {"accept_route": accept})
        if params["timers"] is not None:
            self.merge(
                "timers",
                {
                    key.replace("_", "-"): value
                    for key, value in params["timers"].items()
                    if value is not None
                },
            )
        if params["graceful_shutdown"] is not None:
            names = {"timer": "timer", "local_preference": "local_pref"}
            self.merge(
                "gshut",
                {
                    names[key]: value
                    for key, value in params["graceful_shutdown"].items()
                    if value is not None
                },
            )
        if params["ao"] is not None:
            self.compute_ao(params["ao"])
        if params["password"] is not None:
            self.compute_password(params["password"])
        if params["interface"] is not None and neighbor.materialized:
            current = reference_name(
                read_create_only(neighbor).get("nbr_interface")
            )
            if current != params["interface"]:
                self.module.fail_json(
                    msg="interface cannot be changed on an existing neighbor, "
                    "delete {0} first".format(
                        neighbor.ip_or_ifname_or_group_name
                    )
                )
        if params["ebgp_multihop"] is not None:
            # The switch reports 1 when ebgp-multihop is not configured
            current = getattr(neighbor, "ebgp_hop_count", None) or 1
            self.set("ebgp_hop_count", params["ebgp_multihop"], current)

        if params["peer_group"] is not None:
            self.compute_peer_group(params["peer_group"])
        if params["update_source"] is not None:
            self.compute_update_source(params["update_source"].strip())

        for entry in params["address_families"] or []:
            family = entry["address_family"].replace("_", "-")
            for setting in AF_SETTINGS:
                if entry[setting] is None:
                    continue
                current = dict(getattr(neighbor, setting, None) or {})
                if current.get(family) != entry[setting]:
                    merged = self.changes.get(setting, current)
                    merged[family] = entry[setting]
                    self.changes[setting] = merged
            for option, (attribute, key) in AF_ROUTE_MAPS.items():
                if entry[option] is not None:
                    self.compute_route_map(
                        attribute, family, key, entry[option]
                    )
            self.compute_family_values(family, entry)

    def compute_family_values(self, family, entry):
        """Per address family values, kept in {family: value} attributes."""
        for option, (attribute, removable) in AF_VALUES.items():
            value = entry[option]
            if value is None:
                continue
            current = self.changes.get(attribute)
            if current is None:
                current = dict(getattr(self.neighbor, attribute, None) or {})
            if removable and not value:
                if family in current:
                    current.pop(family)
                    self.changes[attribute] = current
            elif current.get(family) != value:
                current[family] = value
                self.changes[attribute] = current
        if entry["maximum_prefix"] is not None:
            values = {
                attribute: entry["maximum_prefix"][option]
                for option, attribute in MAXIMUM_PREFIX.items()
                if entry["maximum_prefix"][option] is not None
            }
            warning_only = entry["maximum_prefix"]["warning_only"]
            if warning_only is False:
                # The REST attribute has the opposite meaning, and the switch
                # does not return it when it is false (the default)
                values["warning_disable"] = True
            if not values["maximum_prefix_limit"]:
                values = {}
            self.set_family_value("max_prefix_options", family, values)
        if entry["orf_capability"] is not None:
            mode = entry["orf_capability"]
            value = {} if mode == "none" else {"prefix-list": mode}
            self.set_family_value("ORF_capability", family, value)
        if entry["orf_prefix_list"] is not None:
            name = entry["orf_prefix_list"]
            current = getattr(self.neighbor, "ORF_prefix_list", None) or {}
            if reference_name((current.get(family) or {}).get("in")) != (
                name or None
            ):
                value = (
                    {"in": reference_uri(self.session, "prefix list", name)}
                    if name
                    else {}
                )
                self.set_family_value("ORF_prefix_list", family, value, True)

    def set_family_value(self, attribute, family, value, force=False):
        """Set {family: value} in a dictionary attribute, {} removes it."""
        current = self.changes.get(attribute)
        if current is None:
            current = copy.deepcopy(
                getattr(self.neighbor, attribute, None) or {}
            )
        if not force and (current.get(family) or {}) == value:
            return
        if value:
            current[family] = value
        else:
            current.pop(family, None)
        self.changes[attribute] = current

    def compute_ao(self, ao):
        values = {
            key: ao[key]
            for key in ("accept_ao_mismatch", "include_tcp_options")
            if ao[key] is not None
        }
        if values:
            self.merge("ao_options", values)
        if ao["keychain"] is not None:
            current = reference_name(
                getattr(self.neighbor, "ao_keychain", None)
            )
            if current != (ao["keychain"] or None):
                self.changes["ao_keychain"] = (
                    reference_uri(self.session, "keychain", ao["keychain"])
                    if ao["keychain"]
                    else None
                )

    def compute_password(self, password):
        current = getattr(self.neighbor, "password", None)
        if not password:
            if current:
                self.changes["password"] = None
        elif not current or self.params["update_password"] == "always":
            self.changes["password"] = password

    def compute_route_map(self, attribute, family, direction, name):
        """
        Set a route map reference, kept by address family in a dictionary:
        {family: uri}, or {family: {direction: uri}} when direction is set.
        """
        current = self.changes.get(attribute)
        if current is None:
            current = copy.deepcopy(
                getattr(self.neighbor, attribute, None) or {}
            )
        if direction is None:
            references, key = current, family
        else:
            references, key = current.setdefault(family, {}), direction
        changed = reference_name(references.get(key)) != (name or None)
        if changed:
            if name:
                references[key] = reference_uri(
                    self.session, "route map", name
                )
            else:
                references.pop(key, None)
        if direction is not None and not references:
            current.pop(family)
        if changed:
            self.changes[attribute] = current

    def compute_peer_group(self, name):
        current = reference_name(
            getattr(self.neighbor, "bgp_peer_group", None)
        )
        if name == "":
            if current is not None:
                self.changes["bgp_peer_group"] = None
            return
        if current == name:
            return
        BgpNeighbor = self.session.api.get_module_class(
            self.session, "BgpNeighbor"
        )
        peer_group = BgpNeighbor(
            self.session, name, parent_bgp_router=self.bgp_router
        )
        if not self.module.check_mode:
            # Fails if the peer group does not exist
            self.read(peer_group, "peer group {0}".format(name))
            if not read_is_peer_group(peer_group):
                self.module.fail_json(
                    msg="{0} is not a peer group".format(name)
                )
        self.changes["bgp_peer_group"] = self.session.api.get_index(peer_group)

    def compute_update_source(self, source):
        current_ip = getattr(self.neighbor, "update_source", None) or None
        current_interface = reference_name(
            getattr(self.neighbor, "local_interface", None)
        )
        ip_source = None
        interface = None
        if is_ip_address(source):
            ip_source = source
        elif source:
            interface = source.replace(" ", "")

        if current_ip != ip_source:
            self.changes["update_source"] = ip_source
        if current_interface != interface:
            if interface is None:
                self.changes["local_interface"] = None
                return
            Interface = self.session.api.get_module_class(
                self.session, "Interface"
            )
            port = Interface(self.session, interface)
            if not self.module.check_mode:
                self.read(port, "interface {0}".format(interface))
            self.changes["local_interface"] = port

    def read(self, resource, label):
        from pyaoscx.exceptions.generic_op_error import GenericOperationError

        try:
            resource.get()
        except GenericOperationError as e:
            if e.response_code == 404:
                self.module.fail_json(msg="Could not find " + label)
            raise

    def apply(self):
        neighbor = self.neighbor
        if neighbor.materialized and not self.changes:
            return False
        if self.module.check_mode:
            return True
        if not neighbor.materialized:
            neighbor.is_peer_group = self.params["is_peer_group"]
            self.changes.setdefault("is_peer_group", neighbor.is_peer_group)
            if self.params["interface"]:
                self.changes["nbr_interface"] = "{0}{1}/{2}".format(
                    self.session.resource_prefix,
                    "system/interfaces",
                    quote(self.params["interface"], safe=""),
                )
        for key, value in self.changes.items():
            setattr(neighbor, key, value)
            if key not in neighbor.config_attrs:
                neighbor.config_attrs.append(key)
        neighbor.apply()
        return True


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        mutually_exclusive=[["neighbor", "neighbors"]],
        required_one_of=[["neighbor", "neighbors"]],
        supports_check_mode=True,
    )
    validate_params(ansible_module)

    params = ansible_module.params
    vrf_name = params["vrf"]
    asn = params["asn"]
    names = get_neighbor_names(params)
    state = params["state"]

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

    def get_or_fail(resource, missing_msg):
        try:
            resource.get()
        except GenericOperationError as e:
            if e.response_code != 404 or resource.materialized:
                ansible_module.fail_json(msg=str(e))
            if missing_msg:
                ansible_module.fail_json(msg=missing_msg)
        except PyaoscxError as e:
            ansible_module.fail_json(msg=str(e))

    def require_parent(resource, missing_msg):
        get_or_fail(resource, None)
        if resource.materialized:
            return
        if state == "delete":
            # No parent, so no neighbor to delete
            ansible_module.exit_json(**result)
        if ansible_module.check_mode:
            # The parent may be created by a previous task of the playbook
            result["changed"] = True
            ansible_module.exit_json(**result)
        ansible_module.fail_json(msg=missing_msg)

    Vrf = session.api.get_module_class(session, "Vrf")
    vrf = Vrf(session, vrf_name)
    require_parent(vrf, "VRF {0} does not exist".format(vrf_name))

    BgpRouter = session.api.get_module_class(session, "BgpRouter")
    bgp_router = BgpRouter(session, asn, parent_vrf=vrf)
    require_parent(
        bgp_router,
        "BGP router {0} does not exist in VRF {1}, create it with "
        "aoscx_bgp_router first".format(asn, vrf_name),
    )

    BgpNeighbor = session.api.get_module_class(session, "BgpNeighbor")
    neighbors = []
    for name in names:
        neighbor = BgpNeighbor(session, name, parent_bgp_router=bgp_router)
        get_or_fail(neighbor, None)
        neighbors.append(neighbor)

    try:
        if state == "delete":
            for neighbor in neighbors:
                if neighbor.materialized:
                    if not ansible_module.check_mode:
                        neighbor.delete()
                    result["changed"] = True
        else:
            # Read and validate every neighbor before the first write
            check_references(ansible_module, session)
            if params["interface"] and not ansible_module.check_mode:
                path = "system/interfaces/" + quote(
                    params["interface"], safe=""
                )
                response = session.request(
                    "GET", path, params={"attributes": "name"}
                )
                if response.status_code != 200:
                    ansible_module.fail_json(
                        msg="Could not find interface {0}".format(
                            params["interface"]
                        )
                    )
            configs = []
            for neighbor in neighbors:
                if neighbor.materialized and params[
                    "is_peer_group"
                ] != read_is_peer_group(neighbor):
                    ansible_module.fail_json(
                        msg="is_peer_group cannot be changed on an existing "
                        "neighbor, delete {0} first".format(
                            neighbor.ip_or_ifname_or_group_name
                        )
                    )
                config = NeighborConfig(
                    ansible_module, session, bgp_router, neighbor
                )
                config.compute()
                configs.append(config)
            for config in configs:
                if config.apply():
                    result["changed"] = True
    except PyaoscxError as e:
        ansible_module.fail_json(msg=str(e), **result)

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
