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
module: aoscx_route_map
version_added: "4.6.0"
short_description: Create, Update or Delete route maps on AOS-CX
description: >
  This module provides configuration management of route maps and their
  entries on AOS-CX devices. Route maps are used by routing protocols (for
  example BGP) to filter and modify routes through ordered match/set clauses.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the route map.
    required: true
    type: str
  entries:
    description: >
      List of route map entries that make up the route map. When provided this
      represents the full desired set of entries: entries present on the switch
      but not listed here are removed. Ignored when I(state) is C(delete).
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
          Policy applied after the entry is processed. C(goto) jumps to the
          entry given by I(goto_target) while C(next) continues with the next
          entry.
        required: false
        choices:
          - goto
          - next
        type: str
      route_map_continue:
        description: >
          Preference of the entry to continue with after this entry matches.
        required: false
        type: int
      match:
        description: >
          Match conditions for the entry. Only the listed scalar clauses are
          managed; clauses are compared on a per key basis.
        required: false
        type: dict
        suboptions:
          metric:
            description: Match routes with this metric.
            required: false
            type: int
          local_preference:
            description: Match routes with this local preference.
            required: false
            type: int
          origin:
            description: Match routes with this BGP origin.
            required: false
            choices:
              - EGP
              - IBGP
              - incomplete
            type: str
          route_type:
            description: Match routes of this type.
            required: false
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
            required: false
            choices:
              - static
              - connected
              - ospf
              - bgp
            type: str
          ipv4_next_hop_address:
            description: Match routes with this IPv4 next hop address.
            required: false
            type: str
          ipv6_next_hop:
            description: Match routes with this IPv6 next hop address.
            required: false
            type: str
          vni:
            description: Match routes with this VNI.
            required: false
            type: int
          probability:
            description: Match a percentage of routes.
            required: false
            type: int
      set:
        description: >
          Set actions applied to matched routes. Only the listed scalar
          clauses are managed; clauses are compared on a per key basis.
        required: false
        type: dict
        suboptions:
          local_preference:
            description: Set the local preference.
            required: false
            type: int
          metric:
            description: Set the metric.
            required: false
            type: int
          metric_type:
            description: Set the metric type.
            required: false
            choices:
              - internal
              - external_type1
              - external_type2
            type: str
          origin:
            description: Set the BGP origin.
            required: false
            choices:
              - EGP
              - IBGP
              - incomplete
            type: str
          community:
            description: Set the BGP community.
            required: false
            type: str
          as_path_prepend:
            description: Prepend the given AS path.
            required: false
            type: str
          as_path_exclude:
            description: Exclude the given AS numbers from the AS path.
            required: false
            type: str
          weight:
            description: Set the BGP weight.
            required: false
            type: int
          ipv4_next_hop_address:
            description: Set the IPv4 next hop address.
            required: false
            type: str
          ipv6_next_hop_global:
            description: Set the global IPv6 next hop address.
            required: false
            type: str
          aggregator_as:
            description: Set the aggregator AS number.
            required: false
            type: int
          atomic_aggregate:
            description: Set the atomic aggregate attribute.
            required: false
            type: bool
  state:
    description: Create, update or delete the route map.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create a route map that sets local preference on RFC1918 routes
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
      - preference: 20
        action: deny

- name: Delete a route map
  aoscx_route_map:
    name: SET_LOCAL_PREF
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the route map or any of its entries was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

# REST keys that differ from the Ansible suboption names.
_SET_KEY_MAP = {"atomic_aggregate": "atomic-aggregate"}


def _clean(clause, key_map=None):
    """Drop keys whose value is None and remap names for the REST body."""
    if not clause:
        return {}
    key_map = key_map or {}
    cleaned = {}
    for key, value in clause.items():
        if value is None:
            continue
        cleaned[key_map.get(key, key)] = value
    return cleaned


def main():
    match_spec = dict(
        metric=dict(type="int"),
        local_preference=dict(type="int"),
        origin=dict(type="str", choices=["EGP", "IBGP", "incomplete"]),
        route_type=dict(
            type="str",
            choices=[
                "local",
                "internal",
                "external_type1",
                "external_type2",
                "evpn-type-1",
                "evpn-type-2",
                "evpn-type-3",
                "evpn-type-4",
                "evpn-type-5",
            ],
        ),
        source_protocol=dict(
            type="str",
            choices=["static", "connected", "ospf", "bgp"],
        ),
        ipv4_next_hop_address=dict(type="str"),
        ipv6_next_hop=dict(type="str"),
        vni=dict(type="int"),
        probability=dict(type="int"),
    )
    set_spec = dict(
        local_preference=dict(type="int"),
        metric=dict(type="int"),
        metric_type=dict(
            type="str",
            choices=["internal", "external_type1", "external_type2"],
        ),
        origin=dict(type="str", choices=["EGP", "IBGP", "incomplete"]),
        community=dict(type="str"),
        as_path_prepend=dict(type="str"),
        as_path_exclude=dict(type="str"),
        weight=dict(type="int"),
        ipv4_next_hop_address=dict(type="str"),
        ipv6_next_hop_global=dict(type="str"),
        aggregator_as=dict(type="int"),
        atomic_aggregate=dict(type="bool"),
    )
    entry_spec = dict(
        preference=dict(type="int", required=True),
        action=dict(type="str", required=True, choices=["permit", "deny"]),
        description=dict(type="str"),
        exitpolicy=dict(type="str", choices=["goto", "next"]),
        route_map_continue=dict(type="int"),
        match=dict(type="dict", options=match_spec),
        set=dict(type="dict", options=set_spec),
    )
    module_args = dict(
        name=dict(type="str", required=True),
        entries=dict(
            type="list",
            elements="dict",
            options=entry_spec,
            default=None,
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    name = ansible_module.params["name"]
    entries = ansible_module.params["entries"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: the name is interpolated into the REST URI, reject
    # values that could escape the route_maps collection path.
    if "/" in name or name in ("", ".", ".."):
        ansible_module.fail_json(
            msg="Invalid route map name: {0}".format(name)
        )

    if entries:
        _validate_entries(ansible_module, entries)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        route_map = session.api.get_module(session, "RouteMap", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support route maps. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        route_map.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                route_map.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete route map: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        route_map = session.api.get_module(session, "RouteMap", name)
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                route_map.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create route map: {0}".format(str(e))
                )

    # --------------------------------------------------------------- entries
    if entries is not None:
        _reconcile_entries(
            ansible_module, session, route_map, name, entries, result
        )

    ansible_module.exit_json(**result)


def _validate_entries(ansible_module, entries):
    """Validate route map entry consistency before contacting the switch."""
    seen = set()
    for entry in entries:
        preference = entry["preference"]
        if preference in seen:
            ansible_module.fail_json(
                msg="Duplicate entry preference: {0}.".format(preference)
            )
        seen.add(preference)

        if entry.get("exitpolicy") == "goto" and (
            entry.get("route_map_continue") is None
        ):
            ansible_module.fail_json(
                msg=(
                    "Entry {0}: route_map_continue is required when "
                    "exitpolicy is goto.".format(preference)
                )
            )


def _desired_entry_attrs(entry):
    """Build the REST attribute dict for a desired entry."""
    attrs = {"action": entry["action"]}
    if entry.get("description") is not None:
        attrs["description"] = entry["description"]
    if entry.get("exitpolicy") is not None:
        attrs["exitpolicy"] = entry["exitpolicy"]
    if entry.get("route_map_continue") is not None:
        attrs["route_map_continue"] = entry["route_map_continue"]
    match = _clean(entry.get("match"))
    if match:
        attrs["match"] = match
    set_clause = _clean(entry.get("set"), _SET_KEY_MAP)
    if set_clause:
        attrs["set"] = set_clause
    return attrs


def _entry_changed(entry_obj, desired):
    """Return True if the existing entry differs from the desired attrs."""
    for key, value in desired.items():
        current = getattr(entry_obj, key, None)
        if key in ("match", "set"):
            current = current or {}
            for sub_key, sub_value in value.items():
                if current.get(sub_key) != sub_value:
                    return True
        elif current != value:
            return True
    return False


def _reconcile_entries(
    ansible_module, session, route_map, name, entries, result
):
    """Create, update and prune entries to match the desired set."""
    entry_class = session.api.get_module_class(session, "RouteMapEntry")

    try:
        existing = entry_class.get_all(session, name)
    except Exception:
        existing = {}

    desired_prefs = set()
    for entry in entries:
        preference = entry["preference"]
        desired_prefs.add(str(preference))
        desired = _desired_entry_attrs(entry)

        entry_obj = session.api.get_module(
            session,
            "RouteMapEntry",
            preference,
            parent_route_map=route_map,
            **desired
        )

        try:
            entry_obj.get()
            entry_exists = True
        except Exception:
            entry_exists = False

        if not entry_exists:
            result["changed"] = True
            if not ansible_module.check_mode:
                try:
                    entry_obj.create()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not create route map entry {0}: "
                        "{1}".format(preference, str(e))
                    )
        elif _entry_changed(entry_obj, desired):
            result["changed"] = True
            for key, value in desired.items():
                setattr(entry_obj, key, value)
                if key not in entry_obj.config_attrs:
                    entry_obj.config_attrs.append(key)
            if not ansible_module.check_mode:
                try:
                    entry_obj.update()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not update route map entry {0}: "
                        "{1}".format(preference, str(e))
                    )

    # Remove entries that are no longer desired.
    for preference, entry_obj in existing.items():
        if str(preference) not in desired_prefs:
            result["changed"] = True
            if not ansible_module.check_mode:
                try:
                    entry_obj.delete()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not delete route map entry {0}: "
                        "{1}".format(preference, str(e))
                    )


if __name__ == "__main__":
    main()
