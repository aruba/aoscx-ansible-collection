#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_port_access_gbp
version_added: "4.6.0"
short_description: Create, update or delete a Port Access Group Based Policy
description: >
  This module provides configuration management of Port Access Group Based
  Policies (GBP) on AOS-CX devices (system/port_access_gbps). A group based
  policy is an ordered list of entries; each entry references an existing
  traffic class (system/classes) and optionally drops or reflects the matching
  traffic. The policy can then be applied to a port access role through its
  in_gbp attribute. This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16). The referenced traffic classes must
  already exist; this module does not create them. The supplied entries fully
  replace the existing entries of the policy.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the group based policy. This is the index of the resource under
      system/port_access_gbps.
    required: true
    type: str
  entries:
    description: >
      Ordered list of policy entries. The supplied list fully replaces the
      existing entries of the policy.
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: Sequence number of the entry within the policy.
        required: true
        type: int
      class_name:
        description: >
          Name of the existing traffic class (system/classes) matched by this
          entry. The class must already exist.
        required: true
        type: str
      class_type:
        description: Type of the referenced traffic class.
        required: true
        type: str
        choices:
          - gbp-ipv4
          - gbp-ipv6
          - gbp-mac
      comment:
        description: Optional comment for the entry.
        required: false
        type: str
      drop:
        description: >
          Drop packets matching the class of this entry. When omitted, the
          action set of the entry is not managed by this module.
        required: false
        type: bool
      reflect:
        description: >
          Reflect packets matching the class of this entry in the reverse
          direction only when the flow is learnt. When omitted, the action set
          of the entry is not managed by this module.
        required: false
        type: bool
  state:
    description: Create, update or delete the group based policy.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a group based policy that drops traffic of a class
  aoscx_port_access_gbp:
    name: employee_r2r_policy
    entries:
      - sequence_number: 10
        class_name: employee_DENY
        class_type: gbp-ipv4
        drop: true
      - sequence_number: 20
        class_name: employee_ALLOW
        class_type: gbp-ipv4

- name: Delete a group based policy
  aoscx_port_access_gbp:
    name: employee_r2r_policy
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

GBP_COLLECTION = "system/port_access_gbps"
CLASS_COLLECTION = "system/classes"


def _ok(response):
    return response is not None and response.status_code < 400


def gbp_exists(session, name):
    response = session.request("GET", "{0}/{1}".format(GBP_COLLECTION, name))
    return _ok(response)


def class_uri(session, ansible_module, class_name, class_type):
    """
    Validate that the referenced traffic class exists and return its URI.
    """
    index = "{0}{1}{2}".format(
        class_name, session.api.compound_index_separator, class_type
    )
    response = session.request(
        "GET", "{0}/{1}".format(CLASS_COLLECTION, index)
    )
    if not _ok(response):
        ansible_module.fail_json(
            msg="Traffic class '{0}' of type '{1}' does not exist".format(
                class_name, class_type
            )
        )
    return "{0}{1}/{2}".format(
        session.resource_prefix, CLASS_COLLECTION, index
    )


def get_entries(session, name):
    """
    Return the current entries of the policy as {sequence_number: data}.
    """
    response = session.request(
        "GET",
        "{0}/{1}/cfg_entries".format(GBP_COLLECTION, name),
        params={"depth": 2, "selector": "configuration"},
    )
    if not _ok(response):
        return {}
    result = {}
    for seq, data in response.json().items():
        result[int(seq)] = data
    return result


def get_action_set(session, name, seq):
    response = session.request(
        "GET",
        "{0}/{1}/cfg_entries/{2}/gbp_action_set".format(
            GBP_COLLECTION, name, seq
        ),
        params={"selector": "writable"},
    )
    if not _ok(response):
        return None
    return response.json()


def main():
    entry_spec = dict(
        sequence_number=dict(type="int", required=True),
        class_name=dict(type="str", required=True),
        class_type=dict(
            type="str",
            required=True,
            choices=["gbp-ipv4", "gbp-ipv6", "gbp-mac"],
        ),
        comment=dict(type="str", required=False, default=None),
        drop=dict(type="bool", required=False, default=None),
        reflect=dict(type="bool", required=False, default=None),
    )
    module_args = dict(
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
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    name = ansible_module.params["name"]
    state = ansible_module.params["state"]
    entries = ansible_module.params["entries"] or []

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    exists = gbp_exists(session, name)

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            response = session.request(
                "DELETE", "{0}/{1}".format(GBP_COLLECTION, name)
            )
            if not _ok(response):
                ansible_module.fail_json(
                    msg="Could not delete group based policy: {0}".format(
                        response.text
                    )
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # Resolve and validate referenced classes; detect duplicate sequences.
    desired = {}
    for entry in entries:
        seq = entry["sequence_number"]
        if seq in desired:
            ansible_module.fail_json(
                msg="Duplicate sequence_number {0}".format(seq)
            )
        uri = class_uri(
            session, ansible_module, entry["class_name"], entry["class_type"]
        )
        manage_action = (
            entry["drop"] is not None or entry["reflect"] is not None
        )
        desired[seq] = {
            "class_uri": uri,
            "comment": entry["comment"],
            "drop": bool(entry["drop"]),
            "reflect": bool(entry["reflect"]),
            "manage_action": manage_action,
        }

    changed = False

    # --------------------------------------------------------------- create
    if not exists:
        changed = True
        if not ansible_module.check_mode:
            response = session.request(
                "POST",
                GBP_COLLECTION,
                data=ansible_module.jsonify({"name": name}),
            )
            if not _ok(response):
                ansible_module.fail_json(
                    msg="Could not create group based policy: {0}".format(
                        response.text
                    )
                )
        current = {}
    else:
        current = get_entries(session, name)

    base = "{0}/{1}/cfg_entries".format(GBP_COLLECTION, name)

    # Remove entries that are no longer desired (full replace).
    for seq in current:
        if seq not in desired:
            changed = True
            if not ansible_module.check_mode:
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
            if not ansible_module.check_mode:
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
                if not _ok(response):
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
            if not ansible_module.check_mode:
                session.request(
                    "PUT",
                    "{0}/{1}".format(base, seq),
                    data=ansible_module.jsonify({"comment": want["comment"]}),
                )

        # Reconcile the action set when drop/reflect were supplied.
        if want["manage_action"]:
            action = None
            if cur is not None:
                action = get_action_set(session, name, seq)
            cur_drop = bool(action.get("drop")) if action else False
            cur_reflect = bool(action.get("reflect")) if action else False
            if (cur_drop, cur_reflect) != (want["drop"], want["reflect"]):
                changed = True
                if not ansible_module.check_mode:
                    verb = "PUT" if action is not None else "POST"
                    session.request(
                        verb,
                        "{0}/{1}/gbp_action_set".format(base, seq),
                        data=ansible_module.jsonify(
                            {
                                "drop": want["drop"],
                                "reflect": want["reflect"],
                            }
                        ),
                    )

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
