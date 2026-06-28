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
module: aoscx_prefix_list
version_added: "4.6.0"
short_description: Create, Update or Delete prefix lists on AOS-CX
description: >
  This module provides configuration management of IP prefix lists and their
  entries on AOS-CX devices. Prefix lists are used by routing policies (for
  example route maps and BGP filters) to permit or deny IPv4/IPv6 prefixes.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the prefix list.
    required: true
    type: str
  address_family:
    description: >
      Address family of the prefix list. It is only used when the prefix list
      is created and cannot be modified afterwards. Defaults to C(ipv4) on
      creation.
    required: false
    choices:
      - ipv4
      - ipv6
    type: str
  description:
    description: Description of the prefix list.
    required: false
    type: str
  entries:
    description: >
      List of prefix list entries that make up the prefix list. When provided
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
        description: Whether the entry permits or denies the matched prefix.
        required: true
        choices:
          - permit
          - deny
        type: str
      prefix:
        description: >
          The IPv4 or IPv6 prefix and mask in the address/mask format, for
          example C(10.0.0.0/8) or C(2001:db8::/32).
        required: true
        type: str
      ge:
        description: >
          Minimum prefix length to be matched (greater than or equal to). Must
          be in the range 0-128.
        required: false
        type: int
      le:
        description: >
          Maximum prefix length to be matched (less than or equal to). Must be
          in the range 0-128.
        required: false
        type: int
  state:
    description: Create, update or delete the prefix list.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create an IPv4 prefix list with two entries
  aoscx_prefix_list:
    name: PERMIT_RFC1918
    address_family: ipv4
    description: Permit RFC1918 networks
    entries:
      - preference: 10
        action: permit
        prefix: 10.0.0.0/8
        le: 32
      - preference: 20
        action: permit
        prefix: 192.168.0.0/16
        le: 32

- name: Create an IPv6 prefix list
  aoscx_prefix_list:
    name: PERMIT_V6_DOC
    address_family: ipv6
    entries:
      - preference: 10
        action: permit
        prefix: '2001:db8::/32'

- name: Add or update a single entry on an existing prefix list
  aoscx_prefix_list:
    name: PERMIT_RFC1918
    state: update
    entries:
      - preference: 10
        action: permit
        prefix: 10.0.0.0/8
        le: 32
      - preference: 20
        action: permit
        prefix: 192.168.0.0/16
        le: 32
      - preference: 30
        action: deny
        prefix: 0.0.0.0/0

- name: Delete a prefix list
  aoscx_prefix_list:
    name: PERMIT_RFC1918
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the prefix list or any of its entries was modified.
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
        prefix=dict(type="str", required=True),
        ge=dict(type="int"),
        le=dict(type="int"),
    )
    module_args = dict(
        name=dict(type="str", required=True),
        address_family=dict(type="str", choices=["ipv4", "ipv6"]),
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
    address_family = ansible_module.params["address_family"]
    description = ansible_module.params["description"]
    entries = ansible_module.params["entries"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: the name is interpolated into the REST URI, reject
    # values that could escape the prefix_lists collection path.
    if "/" in name or name in ("", ".", ".."):
        ansible_module.fail_json(
            msg="Invalid prefix list name: {0}".format(name)
        )

    # Validate entry bounds at the boundary so the user gets a clear error
    # instead of an opaque switch-side rejection. Runs even in check mode.
    if entries:
        _validate_entries(ansible_module, entries)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        prefix_list = session.api.get_module(session, "PrefixList", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support prefix lists. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        # Use the "configuration" selector so create-only attributes such as
        # address_family are returned and the immutability check can work
        # (the default "writable" selector only exposes the description).
        prefix_list.get(selector="configuration")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                prefix_list.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete prefix list: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        create_kwargs = {"address_family": address_family or "ipv4"}
        if description is not None:
            create_kwargs["description"] = description
        prefix_list = session.api.get_module(
            session, "PrefixList", name, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                prefix_list.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create prefix list: {0}".format(str(e))
                )
    else:
        # The address family is immutable; fail clearly instead of silently
        # ignoring the request.
        current_af = getattr(prefix_list, "address_family", None)
        if address_family is not None and current_af not in (
            None,
            address_family,
        ):
            ansible_module.fail_json(
                msg=(
                    "address_family cannot be changed on an existing prefix "
                    "list (current: {0}). Delete and recreate it.".format(
                        current_af
                    )
                )
            )
        if description is not None and (
            getattr(prefix_list, "description", None) != description
        ):
            result["changed"] = True
            setattr(prefix_list, "description", description)
            if "description" not in prefix_list.config_attrs:
                prefix_list.config_attrs.append("description")
            if not ansible_module.check_mode:
                try:
                    prefix_list.update()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not update prefix list: {0}".format(str(e))
                    )

    # --------------------------------------------------------------- entries
    if entries is not None:
        _reconcile_entries(
            ansible_module, session, prefix_list, name, entries, result
        )

    ansible_module.exit_json(**result)


def _validate_entries(ansible_module, entries):
    """Validate prefix list entry bounds before contacting the switch."""
    seen = set()
    for entry in entries:
        preference = entry["preference"]
        if preference in seen:
            ansible_module.fail_json(
                msg="Duplicate entry preference: {0}.".format(preference)
            )
        seen.add(preference)

        ge = entry.get("ge")
        le = entry.get("le")
        for name, value in (("ge", ge), ("le", le)):
            if value is not None and not 0 <= value <= 128:
                ansible_module.fail_json(
                    msg=(
                        "Invalid {0} value {1} for entry {2}: must be "
                        "between 0 and 128.".format(name, value, preference)
                    )
                )
        if ge is not None and le is not None and ge > le:
            ansible_module.fail_json(
                msg=(
                    "Invalid entry {0}: ge ({1}) cannot be greater than "
                    "le ({2}).".format(preference, ge, le)
                )
            )


def _reconcile_entries(
    ansible_module, session, prefix_list, name, entries, result
):
    """Create, update and prune entries to match the desired set."""
    entry_class = session.api.get_module_class(session, "PrefixListEntry")

    try:
        existing = entry_class.get_all(session, name)
    except Exception:
        # The prefix list may not exist yet (e.g. check mode on a new list).
        existing = {}

    desired_prefs = set()
    for entry in entries:
        preference = entry["preference"]
        desired_prefs.add(str(preference))

        entry_kwargs = {
            "action": entry["action"],
            "prefix": entry["prefix"],
        }
        if entry.get("ge") is not None:
            entry_kwargs["ge"] = entry["ge"]
        if entry.get("le") is not None:
            entry_kwargs["le"] = entry["le"]

        entry_obj = session.api.get_module(
            session,
            "PrefixListEntry",
            preference,
            parent_prefix_list=prefix_list,
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
                        msg="Could not create prefix list entry {0}: "
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
                            msg="Could not update prefix list entry {0}: "
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
                        msg="Could not delete prefix list entry {0}: "
                        "{1}".format(preference, str(e))
                    )


if __name__ == "__main__":
    main()
