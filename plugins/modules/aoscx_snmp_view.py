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
module: aoscx_snmp_view
version_added: "4.6.0"
short_description: Create, update or delete an SNMP view
description: >
  This module provides configuration management of SNMP views and their
  entries on AOS-CX devices (system/snmp_views). View entries are immutable,
  so the requested entries fully replace the existing ones. Requires REST API
  v10.16 (set ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the SNMP view.
    required: true
    type: str
  entries:
    description: Full list of OID-tree entries for the view. Existing entries
      not present in this list are removed.
    required: false
    type: list
    elements: dict
    suboptions:
      oid_tree:
        description: OID subtree of the entry.
        required: true
        type: str
      type:
        description: Whether the subtree is included or excluded.
        required: false
        type: str
        choices:
          - included
          - excluded
        default: included
      mask:
        description: Bitmask applied to the OID subtree.
        required: false
        type: str
  state:
    description: Create, update or delete the SNMP view.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an SNMP view with two entries
  aoscx_snmp_view:
    name: my_view
    entries:
      - oid_tree: "1.3.6.1"
        type: included
      - oid_tree: "1.3.6.1.6.3"
        type: excluded

- name: Delete an SNMP view
  aoscx_snmp_view:
    name: my_view
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.snmp_view import SnmpView
    from pyaoscx.snmp_view_entry import SnmpViewEntry

    HAS_PYAOSCX_SNMP = True
except ImportError:
    HAS_PYAOSCX_SNMP = False

if HAS_PYAOSCX_SNMP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    entry_spec = dict(
        oid_tree=dict(type="str", required=True),
        type=dict(
            type="str",
            required=False,
            choices=["included", "excluded"],
            default="included",
        ),
        mask=dict(type="str", required=False),
    )
    module_args = dict(
        name=dict(type="str", required=True),
        entries=dict(type="list", elements="dict", options=entry_spec),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_SNMP:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support SNMP. Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    name = ansible_module.params["name"]
    entries = ansible_module.params["entries"] or []
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    view = SnmpView(session, name)
    try:
        view.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            view.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    if not exists:
        view.create()
        result["changed"] = True

    desired = set()
    for entry in entries:
        desired.add(
            (entry["oid_tree"], entry["type"], entry.get("mask"))
        )

    current = {}
    try:
        existing_entries = SnmpViewEntry.get_all(session, view)
    except Exception:
        existing_entries = {}
    for index, existing in existing_entries.items():
        if not existing.materialized:
            existing.get()
        key = (
            existing.oid_tree,
            getattr(existing, "type", "included"),
            getattr(existing, "mask", None),
        )
        current[key] = existing

    for key, existing in current.items():
        if key not in desired:
            existing.delete()
            result["changed"] = True

    for oid_tree, etype, mask in desired:
        if (oid_tree, etype, mask) in current:
            continue
        kwargs = {"oid_tree": oid_tree, "type": etype}
        if mask is not None:
            kwargs["mask"] = mask
        SnmpViewEntry(session, None, view, **kwargs).create()
        result["changed"] = True

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
