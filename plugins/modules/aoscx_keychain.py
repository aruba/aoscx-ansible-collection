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
notes:
  - When a key C(auth_key) is supplied the module reports changed on every
    run because the secret cannot be read back from the switch for comparison.
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

try:
    from pyaoscx.keychain import Keychain
    from pyaoscx.keychain_key import KeychainKey

    HAS_PYAOSCX_KEYCHAIN = True
except ImportError:
    HAS_PYAOSCX_KEYCHAIN = False

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
            no_log=False,
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


def _get_keys(session, keychain):
    keys = {}
    for key in KeychainKey.get_all(session, keychain).values():
        key.get()
        key_id = int(key.key_id)
        keys[key_id] = {
            field: getattr(key, field, None) for field in COMPARABLE_KEY_FIELDS
        }
    return keys


def _reconcile_keys(
    ansible_module, session, keychain, desired, current, check_mode
):
    changed = False

    for key_id in current:
        if key_id not in desired:
            changed = True
            if not check_mode:
                KeychainKey(session, key_id, parent_keychain=keychain).delete()

    for key_id, want in desired.items():
        cur = current.get(key_id)
        if cur is None or _key_differs(want, cur):
            changed = True
            if not check_mode:
                if cur is not None:
                    KeychainKey(
                        session, key_id, parent_keychain=keychain
                    ).delete()
                attrs = {k: v for k, v in want.items() if k != "key_id"}
                key = KeychainKey(
                    session, key_id, parent_keychain=keychain, **attrs
                )
                try:
                    key.create()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not create key {0}: {1}".format(
                            key_id, str(e)
                        )
                    )

    return changed


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(),
        supports_check_mode=True,
    )
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    keys_param = params["keys"]
    manage_keys = keys_param is not None
    keys = keys_param or []
    check_mode = ansible_module.check_mode

    result = dict(changed=False)

    if not HAS_PYAOSCX_KEYCHAIN:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support keychains. "
                "Upgrade pyaoscx."
            )
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    keychain = Keychain(session, name)
    try:
        keychain.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists and not check_mode:
            try:
                keychain.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, str(e))
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
            try:
                keychain.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, str(e))
                )
        current = {}
    elif manage_keys:
        current = _get_keys(session, keychain)
    else:
        current = {}

    if manage_keys:
        changed = (
            _reconcile_keys(
                ansible_module,
                session,
                keychain,
                desired,
                current,
                check_mode,
            )
            or changed
        )

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
