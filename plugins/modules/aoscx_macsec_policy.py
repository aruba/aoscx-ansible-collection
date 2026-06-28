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
module: aoscx_macsec_policy
version_added: "4.6.0"
short_description: Create, update or delete a MACsec policy
description: >
  This module provides configuration management of MACsec policies on AOS-CX
  devices (system/macsec_policies). A MACsec policy defines the
  confidentiality, replay protection and cipher suite behaviour applied to a
  MACsec protected channel; it is referenced by MKA policies and port access
  roles. This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the MACsec policy, index under system/macsec_policies.
    required: true
    type: str
  clear_tag_mode:
    description: >
      Ethernet data that must precede the MACsec SecTAG in clear text. With
      dot1q the 802.1q tag is sent in clear and untagged traffic is not allowed
      on the MACsec channel.
    required: false
    type: str
    choices:
      - none
      - dot1q
  confidentiality_disable:
    description: Disable encryption on the MACsec interface.
    required: false
    type: bool
  confidentiality_offset:
    description: >
      Number of leading octets of an Ethernet frame that are left unencrypted.
      Only applicable when confidentiality is enabled.
    required: false
    type: str
    choices:
      - byte_0
      - byte_30
      - byte_50
  data_delay_protection_enable:
    description: >
      Enable data delay protection so that MACsec frames delayed by more than
      two seconds are dropped.
    required: false
    type: bool
  include_sci_disable:
    description: >
      Disable inclusion of the Secure Channel Identifier (SCI) in MACsec
      frames.
    required: false
    type: bool
  replay_protect_disable:
    description: Disable replay protection on the MACsec interface.
    required: false
    type: bool
  replay_window:
    description: >
      Replay protection window. A received packet is processed only if its
      packet number is within this window. Only applicable when replay
      protection is enabled.
    required: false
    type: int
  secure_mode:
    description: >
      Forwarding behaviour of the interface when the MKA session is not
      established. should-secure opens the data plane without MACsec
      protection; must-secure blocks the interface.
    required: false
    type: str
    choices:
      - should-secure
      - must-secure
  bypass:
    description: Features that bypass MACsec processing on the channel.
    required: false
    type: dict
    suboptions:
      ieee_bpdu_enabled:
        description: >
          Bypass MACsec protection for IEEE BPDU frames (destination MAC in
          01:80:c2:00:00:0*) in both directions.
        required: false
        type: bool
  cipher_suites:
    description: >
      MACsec cipher suites used to protect the frames. When more than one is
      enabled the most secure one is used to generate the SAK when the switch
      is the key server.
    required: false
    type: dict
    suboptions:
      gcm_aes_128_enabled:
        description: Enable GCM with the AES-128 cipher.
        required: false
        type: bool
      gcm_aes_256_enabled:
        description: Enable GCM with the AES-256 cipher.
        required: false
        type: bool
      gcm_aes_xpn_128_enabled:
        description: >
          Enable GCM with the AES-128 cipher and extended packet numbering.
        required: false
        type: bool
      gcm_aes_xpn_256_enabled:
        description: >
          Enable GCM with the AES-256 cipher and extended packet numbering.
        required: false
        type: bool
  state:
    description: Create, update or delete the MACsec policy.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a MACsec policy that must secure with AES-256
  aoscx_macsec_policy:
    name: secure_uplinks
    secure_mode: must-secure
    confidentiality_offset: byte_0
    cipher_suites:
      gcm_aes_256_enabled: true

- name: Relax a MACsec policy to should-secure and bypass BPDUs
  aoscx_macsec_policy:
    name: secure_uplinks
    state: update
    secure_mode: should-secure
    bypass:
      ieee_bpdu_enabled: true

- name: Delete a MACsec policy
  aoscx_macsec_policy:
    name: secure_uplinks
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

COLLECTION = "system/macsec_policies"

SCALAR_FIELDS = [
    {"name": "clear_tag_mode", "type": "str", "choices": ["none", "dot1q"]},
    {"name": "confidentiality_disable", "type": "bool"},
    {
        "name": "confidentiality_offset",
        "type": "str",
        "choices": ["byte_0", "byte_30", "byte_50"],
    },
    {"name": "data_delay_protection_enable", "type": "bool"},
    {"name": "include_sci_disable", "type": "bool"},
    {"name": "replay_protect_disable", "type": "bool"},
    {"name": "replay_window", "type": "int"},
    {
        "name": "secure_mode",
        "type": "str",
        "choices": ["should-secure", "must-secure"],
    },
]

NESTED_FIELDS = {
    "bypass": ["ieee_bpdu_enabled"],
    "cipher_suites": [
        "gcm_aes_128_enabled",
        "gcm_aes_256_enabled",
        "gcm_aes_xpn_128_enabled",
        "gcm_aes_xpn_256_enabled",
    ],
}


def ok(response):
    return response is not None and response.status_code < 400


def build_argument_spec():
    spec = dict(
        name=dict(type="str", required=True),
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
    for obj, keys in NESTED_FIELDS.items():
        spec[obj] = dict(
            type="dict",
            required=False,
            default=None,
            options={
                k: dict(type="bool", required=False, default=None)
                for k in keys
            },
        )
    return spec


def _build_desired(params):
    scalars = {}
    for field in SCALAR_FIELDS:
        value = params.get(field["name"])
        if value is not None:
            scalars[field["name"]] = value
    nested = {}
    for obj, keys in NESTED_FIELDS.items():
        sub = params.get(obj)
        if sub:
            picked = {k: sub[k] for k in keys if sub.get(k) is not None}
            if picked:
                nested[obj] = picked
    return scalars, nested


def _differs(current, scalars, nested):
    for field, value in scalars.items():
        if current.get(field) != value:
            return True
    for obj, picked in nested.items():
        current_obj = current.get(obj) or {}
        for key, value in picked.items():
            if current_obj.get(key) != value:
                return True
    return False


def run_module(ansible_module, session):
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    check_mode = ansible_module.check_mode
    path = "{0}/{1}".format(COLLECTION, name)

    current_response = session.request(
        "GET", path, params={"selector": "writable"}
    )
    exists = ok(current_response)

    result = dict(changed=False)

    if state == "delete":
        if exists and not check_mode:
            response = session.request("DELETE", path)
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, response.text)
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    scalars, nested = _build_desired(params)

    if not exists:
        if not check_mode:
            body = {"name": name}
            body.update(scalars)
            for obj, picked in nested.items():
                body[obj] = picked
            response = session.request(
                "POST", COLLECTION, data=ansible_module.jsonify(body)
            )
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, response.text)
                )
        result["changed"] = True
        ansible_module.exit_json(**result)

    current = current_response.json()
    if _differs(current, scalars, nested):
        result["changed"] = True
        if not check_mode:
            body = dict(current)
            body.update(scalars)
            for obj, picked in nested.items():
                merged = dict(current.get(obj) or {})
                merged.update(picked)
                body[obj] = merged
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
