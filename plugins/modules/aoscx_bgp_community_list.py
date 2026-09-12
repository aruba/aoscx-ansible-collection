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
module: aoscx_bgp_community_list
version_added: "4.6.0"
short_description: Create, Update or Delete BGP community filters on AOS-CX
description: >
  This module provides configuration management of BGP community filters (also
  known as community lists) and their entries on AOS-CX devices. Community
  filters are used by routing policies to permit or deny routes based on a
  string matched against the BGP communities carried by a route.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the BGP community filter.
    required: true
    type: str
  type:
    description: >
      Kind of community filter. Required when creating the filter. C(*-list)
      types match standard community values, while C(*-expanded-list) types
      match a regular expression.
    required: false
    choices:
      - community-list
      - community-expanded-list
      - extcommunity-list
      - extcommunity-expanded-list
    type: str
  description:
    description: Description of the BGP community filter.
    required: false
    type: str
  entries:
    description: >
      List of community filter entries that make up the filter. When provided
      this represents the full desired set of entries: entries present on the
      switch but not listed here are removed. Ignored when I(state) is
      C(delete).
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
      match_string:
        description: >
          Community value or regular expression matched against the BGP
          communities of a route, for example C(65000:1) or C(_65001:).
        required: true
        type: str
  state:
    description: Create, update or delete the BGP community filter.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create a BGP community filter with two entries
  aoscx_bgp_community_list:
    name: COMM_AS65000
    type: community-list
    description: Match communities from AS 65000
    entries:
      - preference: 10
        action: permit
        match_string: '65000:1'
      - preference: 20
        action: deny
        match_string: '65000:666'

- name: Add or update a single entry on an existing filter
  aoscx_bgp_community_list:
    name: COMM_AS65000
    state: update
    entries:
      - preference: 10
        action: permit
        match_string: '65000:1'
      - preference: 20
        action: deny
        match_string: '65000:666'
      - preference: 30
        action: permit
        match_string: '65000:2'

- name: Create an expanded community filter matching a regular expression
  aoscx_bgp_community_list:
    name: COMM_REGEX
    type: community-expanded-list
    entries:
      - preference: 10
        action: permit
        match_string: '_65001:'

- name: Delete a BGP community filter
  aoscx_bgp_community_list:
    name: COMM_AS65000
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the community filter or any of its entries was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    entry_spec = dict(
        preference=dict(type="int", required=True),
        action=dict(type="str", required=True, choices=["permit", "deny"]),
        match_string=dict(type="str", required=True),
    )
    module_args = dict(
        name=dict(type="str", required=True),
        type=dict(
            type="str",
            default=None,
            choices=[
                "community-list",
                "community-expanded-list",
                "extcommunity-list",
                "extcommunity-expanded-list",
            ],
        ),
        description=dict(type="str", default=None),
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
    community_type = ansible_module.params["type"]
    description = ansible_module.params["description"]
    entries = ansible_module.params["entries"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: the name is interpolated into the REST URI, reject
    # values that could escape the bgp_community_filters collection path.
    if "/" in name or name in ("", ".", ".."):
        ansible_module.fail_json(
            msg="Invalid community filter name: {0}".format(name)
        )

    # Validate entry consistency at the boundary so the user gets a clear
    # error instead of an opaque switch-side rejection. Runs in check mode.
    if entries:
        _validate_entries(ansible_module, entries)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        community_filter = session.api.get_module(
            session, "BgpCommunityFilter", name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support BGP community filters. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        community_filter.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                community_filter.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete community filter: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        # The type is mandatory on the REST POST body; fail early with a
        # clear message instead of an opaque switch-side rejection.
        if community_type is None:
            ansible_module.fail_json(
                msg="The 'type' parameter is required to create a community "
                "filter."
            )
        create_kwargs = {"type": community_type}
        if description is not None:
            create_kwargs["description"] = description
        community_filter = session.api.get_module(
            session, "BgpCommunityFilter", name, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                community_filter.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create community filter: {0}".format(str(e))
                )
    else:
        desired = {}
        if community_type is not None:
            desired["type"] = community_type
        if description is not None:
            desired["description"] = description
        changed_filter = False
        for key, value in desired.items():
            if getattr(community_filter, key, None) != value:
                changed_filter = True
            setattr(community_filter, key, value)
            if key not in community_filter.config_attrs:
                community_filter.config_attrs.append(key)
        if changed_filter:
            result["changed"] = True
            if not ansible_module.check_mode:
                try:
                    community_filter.update()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not update community filter: {0}".format(
                            str(e)
                        )
                    )

    # --------------------------------------------------------------- entries
    if entries is not None:
        _reconcile_entries(
            ansible_module, session, community_filter, name, entries, result
        )

    ansible_module.exit_json(**result)


def _validate_entries(ansible_module, entries):
    """Validate community filter entry consistency before the switch call."""
    seen = set()
    for entry in entries:
        preference = entry["preference"]
        if preference in seen:
            ansible_module.fail_json(
                msg="Duplicate entry preference: {0}.".format(preference)
            )
        seen.add(preference)


def _reconcile_entries(
    ansible_module, session, community_filter, name, entries, result
):
    """Create, update and prune entries to match the desired set."""
    entry_class = session.api.get_module_class(
        session, "BgpCommunityFilterEntry"
    )

    try:
        existing = entry_class.get_all(session, name)
    except Exception:
        # The filter may not exist yet (e.g. check mode on a new filter).
        existing = {}

    desired_prefs = set()
    for entry in entries:
        preference = entry["preference"]
        desired_prefs.add(str(preference))

        entry_kwargs = {
            "action": entry["action"],
            "match_string": entry["match_string"],
        }

        entry_obj = session.api.get_module(
            session,
            "BgpCommunityFilterEntry",
            preference,
            parent_community_filter=community_filter,
            **entry_kwargs
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
                        msg="Could not create community filter entry {0}: "
                        "{1}".format(preference, str(e))
                    )
        else:
            changed_entry = False
            for key, value in entry_kwargs.items():
                if getattr(entry_obj, key, None) != value:
                    changed_entry = True
                setattr(entry_obj, key, value)
                if key not in entry_obj.config_attrs:
                    entry_obj.config_attrs.append(key)
            if changed_entry:
                result["changed"] = True
                if not ansible_module.check_mode:
                    try:
                        entry_obj.update()
                    except Exception as e:
                        ansible_module.fail_json(
                            msg="Could not update community filter entry {0}: "
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
                        msg="Could not delete community filter entry {0}: "
                        "{1}".format(preference, str(e))
                    )


if __name__ == "__main__":
    main()
