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
notes:
  - When C(cak) or C(ckn) are supplied the module reports changed on every
    run because the secret cannot be read back from the switch for comparison.
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


def build_argument_spec():
    spec = dict(
        name=dict(type="str", required=True),
        keychain=dict(type="str", required=False, default=None, no_log=False),
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


def _current_keychain_uri(value):
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
        kc_name = params["keychain"]
        keychain = session.api.get_module(session, "Keychain", kc_name)
        try:
            keychain.get()
        except Exception:
            ansible_module.fail_json(
                msg="Referenced keychain {0} does not exist".format(kc_name)
            )
        keychain_uri = keychain.get_uri()

    return scalars, secrets, keychain_uri


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(),
        supports_check_mode=True,
    )
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        policy = session.api.get_module(session, "MkaPolicy", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support MKA policies. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        policy.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                policy.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    scalars, secrets, keychain_uri = _build_desired(ansible_module, session)

    if not exists:
        create_kwargs = dict(scalars)
        create_kwargs.update(secrets)
        if keychain_uri is not None:
            create_kwargs["keychain"] = keychain_uri
        policy = session.api.get_module(
            session, "MkaPolicy", name, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                policy.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for field, value in scalars.items():
        if getattr(policy, field, None) != value:
            changed = True
            setattr(policy, field, value)
            if field not in policy.config_attrs:
                policy.config_attrs.append(field)
    if keychain_uri is not None:
        current_uri = _current_keychain_uri(getattr(policy, "keychain", None))
        if current_uri != keychain_uri:
            changed = True
            setattr(policy, "keychain", keychain_uri)
            if "keychain" not in policy.config_attrs:
                policy.config_attrs.append("keychain")

    if changed:
        for secret, value in secrets.items():
            setattr(policy, secret, value)
            if secret not in policy.config_attrs:
                policy.config_attrs.append(secret)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            policy.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update {0}: {1}".format(name, str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
