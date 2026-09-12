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
module: aoscx_bgp_aspath_list
version_added: "4.6.0"
short_description: Create, Update or Delete BGP AS-Path filters on AOS-CX
description: >
  This module provides configuration management of BGP AS-Path filters (also
  known as AS-Path lists) and their entries on AOS-CX devices. AS-Path filters
  are used by routing policies to permit or deny routes based on a regular
  expression matched against the BGP AS path.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the BGP AS-Path filter.
    required: true
    type: str
  description:
    description: Description of the BGP AS-Path filter.
    required: false
    type: str
  entries:
    description: >
      List of AS-Path filter entries that make up the filter. When provided
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
        description: Whether the entry permits or denies the matched AS path.
        required: true
        choices:
          - permit
          - deny
        type: str
      regex:
        description: >
          Regular expression matched against the BGP AS path, for example
          C(^65000_) or C(_65001$).
        required: true
        type: str
  state:
    description: Create, update or delete the BGP AS-Path filter.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create a BGP AS-Path filter with two entries
  aoscx_bgp_aspath_list:
    name: FILTER_AS65000
    description: Filter routes from AS 65000
    entries:
      - preference: 10
        action: permit
        regex: '^65000_'
      - preference: 20
        action: deny
        regex: '_65001$'

- name: Add or update a single entry on an existing filter
  aoscx_bgp_aspath_list:
    name: FILTER_AS65000
    state: update
    entries:
      - preference: 10
        action: permit
        regex: '^65000_'
      - preference: 20
        action: deny
        regex: '_65001$'
      - preference: 30
        action: deny
        regex: '.*'

- name: Delete a BGP AS-Path filter
  aoscx_bgp_aspath_list:
    name: FILTER_AS65000
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the AS-Path filter or any of its entries was modified.
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
        regex=dict(type="str", required=True),
    )
    module_args = dict(
        name=dict(type="str", required=True),
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
    description = ansible_module.params["description"]
    entries = ansible_module.params["entries"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: the name is interpolated into the REST URI, reject
    # values that could escape the bgp_aspath_filters collection path.
    if "/" in name or name in ("", ".", ".."):
        ansible_module.fail_json(
            msg="Invalid AS-Path filter name: {0}".format(name)
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
        aspath_filter = session.api.get_module(
            session, "BgpAspathFilter", name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support BGP AS-Path filters. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        aspath_filter.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                aspath_filter.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete AS-Path filter: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        create_kwargs = {}
        if description is not None:
            create_kwargs["description"] = description
        aspath_filter = session.api.get_module(
            session, "BgpAspathFilter", name, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                aspath_filter.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create AS-Path filter: {0}".format(str(e))
                )
    else:
        if description is not None and (
            getattr(aspath_filter, "description", None) != description
        ):
            result["changed"] = True
            setattr(aspath_filter, "description", description)
            if "description" not in aspath_filter.config_attrs:
                aspath_filter.config_attrs.append("description")
            if not ansible_module.check_mode:
                try:
                    aspath_filter.update()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not update AS-Path filter: {0}".format(
                            str(e)
                        )
                    )

    # --------------------------------------------------------------- entries
    if entries is not None:
        _reconcile_entries(
            ansible_module, session, aspath_filter, name, entries, result
        )

    ansible_module.exit_json(**result)


def _validate_entries(ansible_module, entries):
    """Validate AS-Path filter entry consistency before the switch call."""
    seen = set()
    for entry in entries:
        preference = entry["preference"]
        if preference in seen:
            ansible_module.fail_json(
                msg="Duplicate entry preference: {0}.".format(preference)
            )
        seen.add(preference)


def _reconcile_entries(
    ansible_module, session, aspath_filter, name, entries, result
):
    """Create, update and prune entries to match the desired set."""
    entry_class = session.api.get_module_class(session, "BgpAspathFilterEntry")

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
            "regex": entry["regex"],
        }

        entry_obj = session.api.get_module(
            session,
            "BgpAspathFilterEntry",
            preference,
            parent_aspath_filter=aspath_filter,
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
                        msg="Could not create AS-Path filter entry {0}: "
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
                            msg="Could not update AS-Path filter entry {0}: "
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
                        msg="Could not delete AS-Path filter entry {0}: "
                        "{1}".format(preference, str(e))
                    )


if __name__ == "__main__":
    main()
