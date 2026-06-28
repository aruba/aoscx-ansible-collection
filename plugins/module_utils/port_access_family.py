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

CLASS_COLLECTION = "system/classes"


def ok(response):
    return response is not None and response.status_code < 400


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


def _container_exists(session, collection, name):
    response = session.request("GET", "{0}/{1}".format(collection, name))
    return ok(response)


def _resolve_class_uri(session, ansible_module, class_name, class_type):
    index = "{0}{1}{2}".format(
        class_name, session.api.compound_index_separator, class_type
    )
    response = session.request(
        "GET", "{0}/{1}".format(CLASS_COLLECTION, index)
    )
    if not ok(response):
        ansible_module.fail_json(
            msg="Traffic class '{0}' of type '{1}' does not exist".format(
                class_name, class_type
            )
        )
    return "{0}{1}/{2}".format(
        session.resource_prefix, CLASS_COLLECTION, index
    )


def _get_entries(session, collection, name):
    response = session.request(
        "GET",
        "{0}/{1}/cfg_entries".format(collection, name),
        params={"depth": 2, "selector": "configuration"},
    )
    if not ok(response):
        return {}
    result = {}
    for seq, data in response.json().items():
        result[int(seq)] = data
    return result


def _get_action_set(session, base, seq, action_key):
    response = session.request(
        "GET",
        "{0}/{1}/{2}".format(base, seq, action_key),
        params={"selector": "writable"},
    )
    if not ok(response):
        return None
    return response.json()


def run_port_access_family(
    ansible_module, session, collection, action_key, action_fields
):
    """
    Reconcile a port access policy family container and its entries.

    :param session: an established pyaoscx session.
    :param collection: e.g. ``system/port_access_gbps``.
    :param action_key: e.g. ``gbp_action_set``.
    :param action_fields: the same list passed to build_argument_spec.
    """
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    entries_param = params["entries"]
    manage_entries = entries_param is not None
    entries = entries_param or []
    check_mode = ansible_module.check_mode
    bool_names = {f["name"] for f in action_fields if f["type"] == "bool"}

    result = dict(changed=False)
    exists = _container_exists(session, collection, name)

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not check_mode:
            response = session.request(
                "DELETE", "{0}/{1}".format(collection, name)
            )
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, response.text)
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
            response = session.request(
                "POST",
                collection,
                data=ansible_module.jsonify({"name": name}),
            )
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, response.text)
                )
        current = {}
    elif manage_entries:
        current = _get_entries(session, collection, name)
    else:
        current = {}

    if manage_entries:
        changed = _reconcile_entries(
            ansible_module,
            session,
            collection,
            action_key,
            bool_names,
            name,
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
    collection,
    action_key,
    bool_names,
    name,
    desired,
    current,
    check_mode,
    changed,
):
    base = "{0}/{1}/cfg_entries".format(collection, name)

    # Remove entries that are no longer desired (full replace).
    for seq in current:
        if seq not in desired:
            changed = True
            if not check_mode:
                session.request("DELETE", "{0}/{1}".format(base, seq))

    for seq, want in desired.items():
        cur = current.get(seq)
        cur_class_uri = None
        if cur is not None:
            class_ref = cur.get("class")
            if isinstance(class_ref, dict):
                cur_class_uri = next(iter(class_ref.values()), None)

        # Create the entry, or recreate it when the class reference changed
        # (the class of an existing entry is immutable).
        if cur is None or cur_class_uri != want["class_uri"]:
            changed = True
            if not check_mode:
                if cur is not None:
                    session.request("DELETE", "{0}/{1}".format(base, seq))
                body = {
                    "sequence_number": seq,
                    "class": want["class_uri"],
                }
                if want["comment"] is not None:
                    body["comment"] = want["comment"]
                response = session.request(
                    "POST", base, data=ansible_module.jsonify(body)
                )
                if not ok(response):
                    ansible_module.fail_json(
                        msg="Could not create entry {0}: {1}".format(
                            seq, response.text
                        )
                    )
            cur = None
        elif want["comment"] is not None and want["comment"] != cur.get(
            "comment"
        ):
            changed = True
            if not check_mode:
                session.request(
                    "PUT",
                    "{0}/{1}".format(base, seq),
                    data=ansible_module.jsonify({"comment": want["comment"]}),
                )

        if want["action"]:
            changed = _reconcile_action_set(
                ansible_module,
                session,
                base,
                action_key,
                bool_names,
                seq,
                want["action"],
                cur,
                check_mode,
                changed,
            )

    return changed


def _reconcile_action_set(
    ansible_module,
    session,
    base,
    action_key,
    bool_names,
    seq,
    want_action,
    cur,
    check_mode,
    changed,
):
    cur_action = None
    if cur is not None:
        cur_action = _get_action_set(session, base, seq, action_key)
    cur_action = cur_action or {}

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
            verb = "PUT" if cur_action else "POST"
            response = session.request(
                verb,
                "{0}/{1}/{2}".format(base, seq, action_key),
                data=ansible_module.jsonify(merged),
            )
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not set action for entry {0}: {1}".format(
                        seq, response.text
                    )
                )

    return changed
