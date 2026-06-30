# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Shared helpers for the port access device classification group modules
(aoscx_port_access_cdp_group, aoscx_port_access_lldp_group).

Both families share the same shape:

    container (system/port_access_<cdp|lldp>_groups, indexed by name)
      -> entries/{sequence_number} (match fields only)

Unlike the policy families, the entries hold only match fields; there is no
referenced traffic class and no action set. The supplied entries fully replace
the existing entries of the container, unless ``entries`` is omitted, in which
case the entries are left untouched and only the container existence is
reconciled. Within an entry, the supplied match fields fully replace the
current ones (a field that is not supplied is cleared on the switch).
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def _normalize(value):
    """
    Normalize an unset match field to None so that the empty representations
    returned by the switch (null, empty string, empty dict/list) compare equal
    to a field that was not supplied.
    """
    if value in (None, "", {}, []):
        return None
    return value


def build_argument_spec(match_fields):
    """
    Build the full argument_spec for a port access device group module.

    :param match_fields: list of dicts describing the per-entry match fields,
        each with keys ``name``, ``type`` (str/int/dict) and optionally
        ``choices``.
    """
    entry_spec = dict(
        sequence_number=dict(type="int", required=True),
    )
    for field in match_fields:
        spec = dict(type=field["type"], required=False, default=None)
        if field.get("choices"):
            spec["choices"] = list(field["choices"])
        entry_spec[field["name"]] = spec

    return dict(
        name=dict(type="str", required=True),
        entries=dict(
            type="list",
            elements="dict",
            options=entry_spec,
            required=False,
            default=None,
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )


def _get_entries(session, entry_cls, container, field_names):
    entries = {}
    for entry in entry_cls.get_all(session, container).values():
        entry.get(selector="configuration")
        seq = int(entry.sequence_number)
        entries[seq] = {
            field: _normalize(getattr(entry, field, None))
            for field in field_names
        }
    return entries


def run_port_access_device_group(
    ansible_module, session, container_cls, match_fields
):
    """
    Reconcile a port access device classification group and its entries.

    :param session: an established pyaoscx session.
    :param container_cls: the pyaoscx container class for this family
        (e.g. ``PortAccessCdpGroup``). Its ``entry_class`` drives the entry
        reconciliation.
    :param match_fields: the same list passed to build_argument_spec.
    """
    entry_cls = container_cls.entry_class
    field_names = [field["name"] for field in match_fields]

    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    entries_param = params["entries"]
    manage_entries = entries_param is not None
    entries = entries_param or []
    check_mode = ansible_module.check_mode

    result = dict(changed=False)

    container = container_cls(session, name)
    try:
        container.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not check_mode:
            try:
                container.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # Build the desired entries; detect duplicate sequence numbers.
    desired = {}
    if manage_entries:
        for entry in entries:
            seq = entry["sequence_number"]
            if seq in desired:
                ansible_module.fail_json(
                    msg="Duplicate sequence_number {0}".format(seq)
                )
            desired[seq] = {
                field: _normalize(entry.get(field)) for field in field_names
            }

    changed = False

    # --------------------------------------------------------------- create
    if not exists:
        changed = True
        if not check_mode:
            try:
                container_cls(session, name).create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, str(e))
                )
        current = {}
    elif manage_entries:
        current = _get_entries(session, entry_cls, container, field_names)
    else:
        current = {}

    if manage_entries:
        changed = _reconcile_entries(
            ansible_module,
            session,
            container,
            entry_cls,
            field_names,
            desired,
            current,
            check_mode,
            changed,
        )

    result["changed"] = changed
    ansible_module.exit_json(**result)


def _reconcile_entries(
    ansible_module,
    session,
    container,
    entry_cls,
    field_names,
    desired,
    current,
    check_mode,
    changed,
):
    # Remove entries that are no longer desired (full replace).
    for seq in current:
        if seq not in desired:
            changed = True
            if not check_mode:
                entry_cls(session, seq, container).delete()

    for seq, want in desired.items():
        cur = current.get(seq)
        if cur is not None and cur == want:
            continue

        changed = True
        if check_mode:
            continue

        # Only the supplied (not None) match fields are written.
        attrs = {
            field: value
            for field, value in want.items()
            if value is not None
        }

        if cur is None:
            entry = entry_cls(session, seq, container, **attrs)
            try:
                entry.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create entry {0}: {1}".format(
                        seq, str(e)
                    )
                )
        else:
            entry = entry_cls(session, seq, container)
            for field, value in attrs.items():
                setattr(entry, field, value)
            entry.config_attrs = list(attrs.keys())
            try:
                entry.update()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not update entry {0}: {1}".format(
                        seq, str(e)
                    )
                )

    return changed
