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
  - Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor handling
    of earlier releases.
  - Tested on a switch with REST API version 10.09 (firmware 10.19).
  - In check mode, a missing VRF is reported as a change instead of an
    error, because it may be created by a previous task of the playbook.
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
          Types of routes to redistribute. Replaces the list configured for
          this address family. Use an empty list to remove the
          redistribution.
        required: true
        type: list
        elements: str
        choices:
          - connected
          - local-loopback
          - static
          - ospf
          - isis
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

BOOLEAN_OPTIONS = (
    "log_neighbor_changes",
    "deterministic_med",
    "always_compare_med",
    "bestpath_as_path_multipath_relax",
    "fast_external_fallover",
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
        redistribute = normalize_redistribute(
            getattr(bgp_router, "redistribute", None)
        )
        for entry in params["redistribute"]:
            family = entry["address_family"].replace("_", "-")
            route_types = sorted(set(entry["route_types"]))
            if route_types:
                redistribute[family] = route_types
            else:
                redistribute.pop(family, None)
        desired["redistribute"] = redistribute
    return desired


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


def apply_configuration(bgp_router, desired, check_mode):
    changes = {}
    for key, value in desired.items():
        current = getattr(bgp_router, key, None)
        if key == "redistribute":
            current = normalize_redistribute(current)
        if current != value:
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
            desired = get_desired(params, bgp_router)
            result["changed"] = apply_configuration(
                bgp_router, desired, check_mode
            )
    except PyaoscxError as e:
        ansible_module.fail_json(msg=str(e), **result)

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
