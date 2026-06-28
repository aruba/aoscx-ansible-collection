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
module: aoscx_mka_policy
version_added: "4.6.0"
short_description: Create, update or delete an MKA policy
description: >
  This module provides configuration management of MKA (MACsec Key Agreement)
  policies on AOS-CX devices (system/mka_policies). An MKA policy references a
  keychain and defines the pre-shared CAK/CKN and EAPOL parameters used to
  establish MACsec sessions. This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16). The cak and ckn values are write-only
  on the switch and cannot be read back, so a change to cak or ckn alone
  (without any other field change) is not detected.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the MKA policy (index under system/mka_policies).
    required: true
    type: str
  mode:
    description: Key agreement mode of the policy.
    required: false
    type: str
    choices:
      - psk
      - eap-tls
  keychain:
    description: >
      Name of the keychain referenced by the policy. The keychain must already
      exist on the device.
    required: false
    type: str
  cak:
    description: >
      Connectivity Association Key. This value is write-only on the switch and
      cannot be read back; a change to cak alone is not detected.
    required: false
    type: str
  ckn:
    description: >
      Connectivity Association Key Name. This value is write-only on the switch
      and cannot be read back; a change to ckn alone is not detected.
    required: false
    type: str
  key_server_priority:
    description: Priority of the key server.
    required: false
    type: int
  transmit_interval:
    description: MKA hello transmit interval in seconds.
    required: false
    type: int
  eapol_destination_mac:
    description: Destination MAC address used for EAPOL frames.
    required: false
    type: str
  eapol_dot1q_tagged:
    description: Whether EAPOL frames are 802.1Q tagged.
    required: false
    type: bool
  eapol_eth_type:
    description: Ethertype used for EAPOL frames.
    required: false
    type: str
  state:
    description: Create, update or delete the MKA policy.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an MKA policy referencing a keychain
  aoscx_mka_policy:
    name: mka1
    mode: psk
    keychain: mka_keys
    cak: "00112233445566778899aabbccddeeff"
    ckn: "11"
    key_server_priority: 5
    transmit_interval: 2

- name: Update the transmit interval of an MKA policy
  aoscx_mka_policy:
    name: mka1
    transmit_interval: 6

- name: Delete an MKA policy
  aoscx_mka_policy:
    name: mka1
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

COLLECTION = "system/mka_policies"
KEYCHAIN_COLLECTION = "system/keychains"

# Comparable scalar fields used to decide whether an update is needed. cak and
# ckn are excluded because they are write-only and cannot be read back.
SCALAR_FIELDS = [
    {
        "name": "mode",
        "type": "str",
        "choices": ["psk", "eap-tls"],
    },
    {"name": "key_server_priority", "type": "int"},
    {"name": "transmit_interval", "type": "int"},
    {"name": "eapol_destination_mac", "type": "str"},
    {"name": "eapol_dot1q_tagged", "type": "bool"},
    {"name": "eapol_eth_type", "type": "str"},
]

SECRET_FIELDS = ["cak", "ckn"]


def ok(response):
    return response is not None and response.status_code < 400


def build_argument_spec():
    spec = dict(
        name=dict(type="str", required=True),
        keychain=dict(type="str", required=False, default=None),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    for field in SCALAR_FIELDS:
        opt = dict(type=field["type"], required=False, default=None)
        if field.get("choices"):
            opt["choices"] = list(field["choices"])
        spec[field["name"]] = opt
    for secret in SECRET_FIELDS:
        spec[secret] = dict(
            type="str", required=False, default=None, no_log=True
        )
    return spec


def _keychain_uri(session, name):
    return "{0}{1}/{2}".format(
        session.resource_prefix, KEYCHAIN_COLLECTION, name
    )


def _current_keychain_uri(current):
    value = current.get("keychain")
    if isinstance(value, dict):
        return next(iter(value.values()), None)
    return value


def _build_desired(ansible_module, session):
    params = ansible_module.params
    scalars = {}
    for field in SCALAR_FIELDS:
        value = params.get(field["name"])
        if value is not None:
            scalars[field["name"]] = value

    secrets = {}
    for secret in SECRET_FIELDS:
        if params.get(secret) is not None:
            secrets[secret] = params[secret]

    keychain_uri = None
    if params.get("keychain") is not None:
        name = params["keychain"]
        if not ok(
            session.request("GET", "{0}/{1}".format(KEYCHAIN_COLLECTION, name))
        ):
            ansible_module.fail_json(
                msg="Referenced keychain {0} does not exist".format(name)
            )
        keychain_uri = _keychain_uri(session, name)

    return scalars, secrets, keychain_uri


def _differs(current, scalars, keychain_uri):
    for field, value in scalars.items():
        if current.get(field) != value:
            return True
    if keychain_uri is not None:
        if _current_keychain_uri(current) != keychain_uri:
            return True
    return False


def run_module(ansible_module, session):
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    check_mode = ansible_module.check_mode
    path = "{0}/{1}".format(COLLECTION, name)

    result = dict(changed=False)
    get_response = session.request(
        "GET", path, params={"selector": "writable"}
    )
    exists = ok(get_response)

    if state == "delete":
        if exists and not check_mode:
            response = session.request("DELETE", path)
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, response.text)
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    scalars, secrets, keychain_uri = _build_desired(ansible_module, session)

    if not exists:
        body = {"name": name}
        body.update(scalars)
        body.update(secrets)
        if keychain_uri is not None:
            body["keychain"] = keychain_uri
        result["changed"] = True
        if not check_mode:
            response = session.request(
                "POST", COLLECTION, data=ansible_module.jsonify(body)
            )
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, response.text)
                )
        ansible_module.exit_json(**result)

    current = get_response.json()
    if not _differs(current, scalars, keychain_uri):
        ansible_module.exit_json(**result)

    body = dict(current)
    body.pop("origin", None)
    body["keychain"] = (
        keychain_uri
        if keychain_uri is not None
        else _current_keychain_uri(current)
    )
    if body.get("keychain") is None:
        body.pop("keychain", None)
    body.update(scalars)
    body.update(secrets)
    result["changed"] = True
    if not check_mode:
        response = session.request(
            "PUT", path, data=ansible_module.jsonify(body)
        )
        if not ok(response):
            ansible_module.fail_json(
                msg="Could not update {0}: {1}".format(name, response.text)
            )
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
