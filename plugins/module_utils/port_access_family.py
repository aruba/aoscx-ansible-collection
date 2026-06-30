# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Shared helpers for the port access policy family modules
(aoscx_port_access_gbp, aoscx_port_access_abp, aoscx_port_access_policy).

The three families share the same shape:

    container (system/port_access_<family>s, indexed by name)
      -> cfg_entries/{sequence_number} (class reference + comment)
           -> <family>_action_set (drop, ... family specific fields)

The referenced traffic classes (system/classes, compound index name,type) are
not managed here; they must already exist. The supplied entries fully replace
the existing entries of the container, unless ``entries`` is omitted, in which
case the entries are left untouched and only the container existence is
reconciled.

An action field is only reconciled when it is supplied (not None). Supplied
action fields are merged onto the current action set so that fields that are
not supplied are preserved.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


def build_argument_spec(class_type_choices, action_fields):
    """
    Build the full argument_spec for a port access policy family module.

    :param class_type_choices: list of valid class types for this family.
    :param action_fields: list of dicts describing the per-entry action fields,
        each with keys ``name``, ``type`` (bool/int/str) and optionally
        ``choices``.
    """
    entry_spec = dict(
        sequence_number=dict(type="int", required=True),
        class_name=dict(type="str", required=True),
        class_type=dict(
            type="str", required=True, choices=list(class_type_choices)
        ),
        comment=dict(type="str", required=False, default=None),
    )
    for field in action_fields:
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


def _resolve_class_uri(session, ansible_module, class_name, class_type):
    traffic_class = session.api.get_module(
        session, "Class", class_name, type=class_type
    )
    try:
        traffic_class.get()
    except Exception:
        ansible_module.fail_json(
            msg="Traffic class '{0}' of type '{1}' does not exist".format(
                class_name, class_type
            )
        )
    return traffic_class.get_uri()


def _get_entries(session, entry_cls, container):
    entries = {}
    for entry in entry_cls.get_all(session, container).values():
        entry.get(selector="configuration")
        seq = int(entry.sequence_number)
        class_ref = getattr(entry, "class", None)
        class_uri = None
        if isinstance(class_ref, dict):
            class_uri = next(iter(class_ref.values()), None)
        entries[seq] = {
            "class_uri": class_uri,
            "comment": getattr(entry, "comment", None),
        }
    return entries


def run_port_access_family(
    ansible_module, session, container_cls, action_fields
):
    """
    Reconcile a port access policy family container and its entries.

    :param session: an established pyaoscx session.
    :param container_cls: the pyaoscx container class for this family
        (e.g. ``PortAccessGbp``). Its ``entry_class`` and the entry's
        ``action_set_class`` drive the entry and action set reconciliation.
    :param action_fields: the same list passed to build_argument_spec.
    """
    entry_cls = container_cls.entry_class
    action_set_cls = entry_cls.action_set_class

    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    entries_param = params["entries"]
    manage_entries = entries_param is not None
    entries = entries_param or []
    check_mode = ansible_module.check_mode
    bool_names = {f["name"] for f in action_fields if f["type"] == "bool"}

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

    # Resolve and validate referenced classes; detect duplicate sequences.
    desired = {}
    if manage_entries:
        for entry in entries:
            seq = entry["sequence_number"]
            if seq in desired:
                ansible_module.fail_json(
                    msg="Duplicate sequence_number {0}".format(seq)
                )
            uri = _resolve_class_uri(
                session,
                ansible_module,
                entry["class_name"],
                entry["class_type"],
            )
            action = {}
            for field in action_fields:
                value = entry.get(field["name"])
                if value is not None:
                    action[field["name"]] = value
            desired[seq] = {
                "class_uri": uri,
                "comment": entry["comment"],
                "action": action,
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
        current = _get_entries(session, entry_cls, container)
    else:
        current = {}

    if manage_entries:
        changed = _reconcile_entries(
            ansible_module,
            session,
            container,
            entry_cls,
            action_set_cls,
            bool_names,
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
    action_set_cls,
    bool_names,
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
        cur_class_uri = cur["class_uri"] if cur is not None else None
        entry_existed = cur is not None

        # Create the entry, or recreate it when the class reference changed
        # (the class of an existing entry is immutable).
        if cur is None or cur_class_uri != want["class_uri"]:
            changed = True
            entry_existed = False
            if not check_mode:
                if cur is not None:
                    entry_cls(session, seq, container).delete()
                attrs = {"class": want["class_uri"]}
                if want["comment"] is not None:
                    attrs["comment"] = want["comment"]
                entry = entry_cls(session, seq, container, **attrs)
                try:
                    entry.create()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not create entry {0}: {1}".format(
                            seq, str(e)
                        )
                    )
        elif want["comment"] is not None and want["comment"] != cur.get(
            "comment"
        ):
            changed = True
            if not check_mode:
                entry = entry_cls(session, seq, container)
                entry.comment = want["comment"]
                entry.config_attrs = ["comment"]
                try:
                    entry.update()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not update entry {0}: {1}".format(
                            seq, str(e)
                        )
                    )

        if want["action"]:
            changed = _reconcile_action_set(
                ansible_module,
                session,
                container,
                entry_cls,
                action_set_cls,
                bool_names,
                seq,
                want["action"],
                entry_existed,
                check_mode,
                changed,
            )

    return changed


def _reconcile_action_set(
    ansible_module,
    session,
    container,
    entry_cls,
    action_set_cls,
    bool_names,
    seq,
    want_action,
    entry_existed,
    check_mode,
    changed,
):
    entry = entry_cls(session, seq, container)
    cur_action = {}
    present = False
    if entry_existed:
        probe = action_set_cls(session, entry)
        try:
            probe.get(selector="writable")
            cur_action = dict(probe._original_attributes)
            present = True
        except Exception:
            present = False

    need = False
    for field, value in want_action.items():
        cur_value = cur_action.get(field)
        if field in bool_names and cur_value is None:
            cur_value = False
        if value != cur_value:
            need = True
            break

    if need:
        changed = True
        if not check_mode:
            merged = dict(cur_action)
            merged.update(want_action)
            action = action_set_cls(session, entry)
            for key, value in merged.items():
                setattr(action, key, value)
            action.config_attrs = list(merged.keys())
            try:
                if present:
                    action.update()
                else:
                    action.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not set action for entry {0}: {1}".format(
                        seq, str(e)
                    )
                )

    return changed
