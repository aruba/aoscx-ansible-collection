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
module: aoscx_keychain
version_added: "4.6.0"
short_description: Create, update or delete a keychain
description: >
  This module provides configuration management of keychains on AOS-CX devices
  (system/keychains). A keychain is a named container of authentication keys
  used by MKA policies and routing protocol authentication. This module
  requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16).
  The supplied keys fully replace the existing keys of the keychain. The
  fields of a key cannot be modified in place; when they change the key is
  recreated. The auth_key value is write-only on the switch and cannot be read
  back, so a change to auth_key alone (without any other key field change) is
  not detected.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the keychain (index under system/keychains).
    required: true
    type: str
  keys:
    description: >
      List of keys of the keychain. The supplied list fully replaces the
      existing keys. When omitted, the keys are left untouched and only the
      existence of the keychain is reconciled.
    required: false
    type: list
    elements: dict
    suboptions:
      key_id:
        description: Identifier of the key within the keychain.
        required: true
        type: int
      auth_type:
        description: Authentication algorithm of the key.
        required: false
        type: str
        choices:
          - md5
          - sha1
          - sha256
          - sha384
          - sha512
          - aes_cmac128
      auth_key:
        description: >
          Authentication key value. This value is write-only on the switch and
          cannot be read back; a change to auth_key alone is not detected.
        required: false
        type: str
      name:
        description: Optional name of the key.
        required: false
        type: str
      accept_start:
        description: >
          Start of the period during which the key is accepted, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      accept_end:
        description: >
          End of the period during which the key is accepted, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      send_start:
        description: >
          Start of the period during which the key is used to send, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      send_end:
        description: >
          End of the period during which the key is used to send, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      recv_id:
        description: Receive identifier of the key.
        required: false
        type: int
      send_id:
        description: Send identifier of the key.
        required: false
        type: int
  state:
    description: Create, update or delete the keychain.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a keychain with one SHA-256 key
  aoscx_keychain:
    name: mka_keys
    keys:
      - key_id: 1
        auth_type: sha256
        auth_key: "S3cretKey123"
        accept_start: 1577836800
        accept_end: 2556143999
        send_start: 1577836800
        send_end: 2556143999
        recv_id: 1
        send_id: 1

- name: Remove all keys but keep the keychain
  aoscx_keychain:
    name: mka_keys
    keys: []

- name: Delete a keychain
  aoscx_keychain:
    name: mka_keys
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

COLLECTION = "system/keychains"

# Comparable (immutable) key fields used to decide whether an existing key
# must be recreated. auth_key is excluded because it is write-only and cannot
# be read back for comparison.
COMPARABLE_KEY_FIELDS = [
    "auth_type",
    "name",
    "accept_start",
    "accept_end",
    "send_start",
    "send_end",
    "recv_id",
    "send_id",
]

KEY_FIELDS = [
    {
        "name": "auth_type",
        "type": "str",
        "choices": [
            "md5",
            "sha1",
            "sha256",
            "sha384",
            "sha512",
            "aes_cmac128",
        ],
    },
    {"name": "auth_key", "type": "str", "no_log": True},
    {"name": "name", "type": "str"},
    {"name": "accept_start", "type": "int"},
    {"name": "accept_end", "type": "int"},
    {"name": "send_start", "type": "int"},
    {"name": "send_end", "type": "int"},
    {"name": "recv_id", "type": "int"},
    {"name": "send_id", "type": "int"},
]


def ok(response):
    return response is not None and response.status_code < 400


def build_argument_spec():
    key_spec = dict(key_id=dict(type="int", required=True))
    for field in KEY_FIELDS:
        opt = dict(type=field["type"], required=False, default=None)
        if field.get("choices"):
            opt["choices"] = list(field["choices"])
        if field.get("no_log"):
            opt["no_log"] = True
        key_spec[field["name"]] = opt

    return dict(
        name=dict(type="str", required=True),
        keys=dict(
            type="list",
            elements="dict",
            options=key_spec,
            required=False,
            default=None,
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )


def _build_desired(ansible_module, keys):
    desired = {}
    for key in keys:
        key_id = key["key_id"]
        if key_id in desired:
            ansible_module.fail_json(msg="Duplicate key_id {0}".format(key_id))
        body = {"key_id": key_id}
        for field in KEY_FIELDS:
            value = key.get(field["name"])
            if value is not None:
                body[field["name"]] = value
        desired[key_id] = body
    return desired


def _key_differs(want, current):
    for field in COMPARABLE_KEY_FIELDS:
        if field in want and want[field] != current.get(field):
            return True
    return False


def _get_keys(session, container_path):
    response = session.request(
        "GET",
        "{0}/keys".format(container_path),
        params={"depth": 2, "selector": "configuration"},
    )
    if not ok(response):
        return {}
    return {int(kid): data for kid, data in response.json().items()}


def _reconcile_keys(
    ansible_module, session, container_path, desired, current, check_mode
):
    base = "{0}/keys".format(container_path)
    changed = False

    for key_id in current:
        if key_id not in desired:
            changed = True
            if not check_mode:
                session.request("DELETE", "{0}/{1}".format(base, key_id))

    for key_id, want in desired.items():
        cur = current.get(key_id)
        if cur is None or _key_differs(want, cur):
            changed = True
            if not check_mode:
                if cur is not None:
                    session.request("DELETE", "{0}/{1}".format(base, key_id))
                response = session.request(
                    "POST", base, data=ansible_module.jsonify(want)
                )
                if not ok(response):
                    ansible_module.fail_json(
                        msg="Could not create key {0}: {1}".format(
                            key_id, response.text
                        )
                    )

    return changed


def run_module(ansible_module, session):
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    keys_param = params["keys"]
    manage_keys = keys_param is not None
    keys = keys_param or []
    check_mode = ansible_module.check_mode
    container_path = "{0}/{1}".format(COLLECTION, name)

    result = dict(changed=False)
    exists = ok(session.request("GET", container_path))

    if state == "delete":
        if exists and not check_mode:
            response = session.request("DELETE", container_path)
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, response.text)
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    desired = {}
    if manage_keys:
        desired = _build_desired(ansible_module, keys)

    changed = False
    if not exists:
        changed = True
        if not check_mode:
            response = session.request(
                "POST",
                COLLECTION,
                data=ansible_module.jsonify({"name": name}),
            )
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, response.text)
                )
        current = {}
    elif manage_keys:
        current = _get_keys(session, container_path)
    else:
        current = {}

    if manage_keys:
        changed = (
            _reconcile_keys(
                ansible_module,
                session,
                container_path,
                desired,
                current,
                check_mode,
            )
            or changed
        )

    result["changed"] = changed
    ansible_module.exit_json(**result)


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(),
        supports_check_mode=True,
    )
    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    run_module(ansible_module, session)


if __name__ == "__main__":
    main()
