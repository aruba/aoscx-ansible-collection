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
module: aoscx_pbr_action_list
version_added: "4.6.0"
short_description: Create, Update or Delete PBR action lists on AOS-CX
description: >
  This module provides configuration management of Policy Based Routing (PBR)
  action lists and their entries on AOS-CX devices. A PBR action list groups
  ordered entries that decide how matched traffic is forwarded (to a next-hop,
  out of an interface, or dropped).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the PBR action list.
    required: true
    type: str
  vsx_sync:
    description: >
      Attributes to synchronize between VSX peers for this action list. When
      omitted the value already on the switch is left untouched.
    required: false
    type: list
    elements: str
  entries:
    description: >
      List of action list entries. When provided this represents the full
      desired set of entries: entries present on the switch but not listed
      here are removed. Because the switch does not support modifying an entry
      in place, a changed entry is deleted and recreated. Ignored when
      I(state) is C(delete).
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: >
          Sequence number of the entry. Entries are evaluated in ascending
          order.
        required: true
        type: int
      type:
        description: >
          Action taken by the entry. C(nexthop) and C(default_nexthop) require
          I(ip); C(interface) requires I(interface); C(blackhole) drops the
          traffic and takes no further argument.
        required: true
        choices:
          - nexthop
          - default_nexthop
          - interface
          - blackhole
        type: str
      ip:
        description: >
          Routing gateway address used by C(nexthop) and C(default_nexthop)
          entries, in IPv4 (A.B.C.D) or IPv6 (A:B::C:D) format.
        required: false
        type: str
      interface:
        description: >
          Name of the next-hop interface used by C(interface) entries, for
          example C(1/1/1).
        required: false
        type: str
  state:
    description: Create, update or delete the PBR action list.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create a PBR action list with a next-hop and a blackhole entry
  aoscx_pbr_action_list:
    name: PBR_WEB
    entries:
      - sequence_number: 10
        type: nexthop
        ip: 10.0.0.1
      - sequence_number: 20
        type: blackhole

- name: Forward matched traffic out of an interface
  aoscx_pbr_action_list:
    name: PBR_WEB
    state: update
    entries:
      - sequence_number: 10
        type: interface
        interface: 1/1/1

- name: Delete a PBR action list
  aoscx_pbr_action_list:
    name: PBR_WEB
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the action list or any of its entries was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import quote
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

# Entry types that require an IP gateway.
IP_TYPES = ("nexthop", "default_nexthop")


def main():
    entry_spec = dict(
        sequence_number=dict(type="int", required=True),
        type=dict(
            type="str",
            required=True,
            choices=[
                "nexthop",
                "default_nexthop",
                "interface",
                "blackhole",
            ],
        ),
        ip=dict(type="str", default=None),
        interface=dict(type="str", default=None),
    )
    module_args = dict(
        name=dict(type="str", required=True),
        vsx_sync=dict(type="list", elements="str", default=None),
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
    vsx_sync = ansible_module.params["vsx_sync"]
    entries = ansible_module.params["entries"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: the name is interpolated into the REST URI, reject
    # values that could escape the pbr_action_lists collection path.
    if "/" in name or name in ("", ".", ".."):
        ansible_module.fail_json(
            msg="Invalid PBR action list name: {0}".format(name)
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
        action_list = session.api.get_module(session, "PbrActionList", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support PBR action lists. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        action_list.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                action_list.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete PBR action list: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        create_kwargs = {}
        if vsx_sync is not None:
            create_kwargs["vsx_sync"] = vsx_sync
        action_list = session.api.get_module(
            session, "PbrActionList", name, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                action_list.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create PBR action list: {0}".format(str(e))
                )
    elif vsx_sync is not None and (
        getattr(action_list, "vsx_sync", None) != vsx_sync
    ):
        result["changed"] = True
        setattr(action_list, "vsx_sync", vsx_sync)
        if "vsx_sync" not in action_list.config_attrs:
            action_list.config_attrs.append("vsx_sync")
        if not ansible_module.check_mode:
            try:
                action_list.update()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not update PBR action list: {0}".format(str(e))
                )

    # --------------------------------------------------------------- entries
    if entries is not None:
        _reconcile_entries(
            ansible_module, session, action_list, name, entries, result
        )

    ansible_module.exit_json(**result)


def _validate_entries(ansible_module, entries):
    """Validate action list entry consistency before the switch call."""
    seen = set()
    for entry in entries:
        sequence_number = entry["sequence_number"]
        if sequence_number in seen:
            ansible_module.fail_json(
                msg="Duplicate entry sequence_number: {0}.".format(
                    sequence_number
                )
            )
        seen.add(sequence_number)

        entry_type = entry["type"]
        ip = entry.get("ip")
        interface = entry.get("interface")

        if entry_type in IP_TYPES:
            if ip is None:
                ansible_module.fail_json(
                    msg="Entry {0} of type '{1}' requires 'ip'.".format(
                        sequence_number, entry_type
                    )
                )
            if interface is not None:
                ansible_module.fail_json(
                    msg="Entry {0} of type '{1}' must not set "
                    "'interface'.".format(sequence_number, entry_type)
                )
        elif entry_type == "interface":
            if interface is None:
                ansible_module.fail_json(
                    msg="Entry {0} of type 'interface' requires "
                    "'interface'.".format(sequence_number)
                )
            if ip is not None:
                ansible_module.fail_json(
                    msg="Entry {0} of type 'interface' must not set "
                    "'ip'.".format(sequence_number)
                )
        else:  # blackhole
            if ip is not None or interface is not None:
                ansible_module.fail_json(
                    msg="Entry {0} of type 'blackhole' must not set 'ip' or "
                    "'interface'.".format(sequence_number)
                )


def _interface_uri(session, interface_name):
    """Build the REST URI that references an interface by name."""
    return "{0}system/interfaces/{1}".format(
        session.resource_prefix, quote(interface_name, safe="")
    )


def _entry_post_kwargs(session, entry):
    """Translate a desired entry into pyaoscx creation keyword arguments."""
    kwargs = {"type": entry["type"]}
    if entry["type"] in IP_TYPES:
        kwargs["ip"] = entry["ip"]
    elif entry["type"] == "interface":
        kwargs["interface"] = _interface_uri(session, entry["interface"])
    return kwargs


def _existing_interface_name(entry_obj):
    """Return the interface name referenced by a materialized entry."""
    interface = getattr(entry_obj, "interface", None)
    if isinstance(interface, dict) and interface:
        return next(iter(interface))
    return None


def _entry_matches(entry_obj, entry):
    """Return True if a materialized entry already matches the desired one."""
    if getattr(entry_obj, "type", None) != entry["type"]:
        return False
    if entry["type"] in IP_TYPES:
        return getattr(entry_obj, "ip", None) == entry["ip"]
    if entry["type"] == "interface":
        return _existing_interface_name(entry_obj) == entry["interface"]
    return True  # blackhole


def _reconcile_entries(
    ansible_module, session, action_list, name, entries, result
):
    """Create, recreate and prune entries to match the desired set.

    PBR entries cannot be modified in place, so a changed entry is deleted and
    created again.
    """
    entry_class = session.api.get_module_class(session, "PbrActionListEntry")

    try:
        existing = entry_class.get_all(session, name)
    except Exception:
        # The list may not exist yet (e.g. check mode on a new list).
        existing = {}

    desired_seqs = set()
    for entry in entries:
        sequence_number = entry["sequence_number"]
        desired_seqs.add(str(sequence_number))
        existing_obj = existing.get(str(sequence_number))

        needs_create = True
        if existing_obj is not None:
            try:
                existing_obj.get(selector="configuration")
                needs_create = not _entry_matches(existing_obj, entry)
            except Exception:
                needs_create = True
            if needs_create:
                # The entry differs and cannot be updated in place.
                result["changed"] = True
                if not ansible_module.check_mode:
                    try:
                        existing_obj.delete()
                    except Exception as e:
                        ansible_module.fail_json(
                            msg="Could not replace PBR entry {0}: {1}".format(
                                sequence_number, str(e)
                            )
                        )

        if needs_create:
            result["changed"] = True
            if not ansible_module.check_mode:
                entry_obj = session.api.get_module(
                    session,
                    "PbrActionListEntry",
                    sequence_number,
                    parent_action_list=action_list,
                    **_entry_post_kwargs(session, entry)
                )
                try:
                    entry_obj.create()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not create PBR entry {0}: {1}".format(
                            sequence_number, str(e)
                        )
                    )

    # Remove entries that are no longer desired.
    for sequence_number, entry_obj in existing.items():
        if str(sequence_number) not in desired_seqs:
            result["changed"] = True
            if not ansible_module.check_mode:
                try:
                    entry_obj.delete()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not delete PBR entry {0}: {1}".format(
                            sequence_number, str(e)
                        )
                    )


if __name__ == "__main__":
    main()
