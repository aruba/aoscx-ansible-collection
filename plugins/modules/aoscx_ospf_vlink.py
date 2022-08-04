#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_ospf_vlink
version_added: "4.1.0"
short_description: Create or Delete OSPF configuration on AOS-CX
description: >
  This modules provides configuration management of OSPF Virtual Links on
  AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  state:
    description: Create or update or delete the Interface.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
  vrf:
    description: >
      The VRF the OSPF Area will belong to once created. If the OSPF Area
      is created and the user wants to change its VRF, the user must first
      delete the OSPF Area, and then recreate it in the desired VRF.
    type: str
    required: true
  ospf_id:
    description: The OSPF Router the Area will belong to once created
    type: int
    required: true
  area_id:
    description: >
      OSPF Area Identifier, in X.X.X.X form, or as a number in [0, 4294967295].
    required: true
    type: str
  peer_router_id:
    description: Id of the Peer Router in IPv4 (X.X.X.X) format.
    required: true
    type: str
  ipsec_ah:
    description: >
      IPsec Authentication Header configuration. Specifies Security
      Parameters Index (SPI), authentication type and key to use. IPsec
      AH is preferred over IPsec Encapsulating Security Payload (ESP)
      if both ipsec_ah and ipsec_esp are configured.
    type: dict
    required: false
    suboptions:
      auth_key:
        description: IPsec AH authentication key.
        type: str
        required: true
      auth_type:
        description: IPsec AH authentication algorithm.
        type: str
        choices:
          - md5
          - sha1
        required: true
      spi:
        description: >
          Security Parameters Index for the Security Association (SA).
          AH SPI must be unique on a router because it is carried in
          IPsec protocol packet to enable the receiving system to
          select the SA to process the packet. Must be in
          [256, 4294967295].
        type: int
        required: true
  ipsec_esp:
    description: >
      IPsec Encapsulating Security Payload (ESP) configuration.
      Specifies SPI, encryption/authentication type, and key to use.
      IPsec AH is preferred over IPsec ESP if both ipsec_ah and
      ipsec_esp are configured.
    type: dict
    required: false
    suboptions:
      auth_key:
        description: IPsec ESP authentication key.
        type: str
        required: true
      auth_type:
        description: IPsec ESP authentication algorithm.
        type: str
        choices:
          - md5
          - sha1
        required: true
      encryption_key:
        description: IPsec ESP encryption key.
        type: str
        required: true
      encryption_type:
        description: IPsec ESP encryption algorithm.
        type: str
        choices:
          - des
          - 3des
          - aes
          - none
        required: true
      spi:
        description: >
          Security Parameters Index for the Security Association (SA).
          ESP SPI must be unique on a router because it is carried in
          IPsec protocol packet to enable the receiving system to
          select the SA to process the packet. Must be in
          [256, 4294967295].
        type: int
        required: true
  ospf_auth_md5_keys:
    description: >
      The authentication keys for OSPFv2 authentication type md5
      message-digest.
    required: false
    type: list
    elements: dict
    suboptions:
      id:
        description: Key ID for secure-hash key. In range 1, 255.
        type: int
        required: true
      key:
        description: md5 key to use.
        type: str
        required: true
  ospf_auth_sha_keys:
    description: >
      The authentication keys for OSPFv2 authentication type sha.
    required: false
    type: list
    elements: dict
    suboptions:
      id:
        description: Key ID for secure-hash key. In range 1, 255.
        type: int
        required: true
      key:
        description: md5 key to use.
        type: str
        required: true
  ospf_auth_keychain:
    description: >
      Name of the "Keychain" used for cryptographic authentication. Supports
      MD5, SHA-1, SHA-256, SHA-384, and SHA-512.
    type: str
    required: false
  ospf_auth_text_key:
    description: >
      The authentication key for OSPFv2 authentication type "text".
    type: str
    required: false
  ospf_auth_type:
    description: >
      The type of OSPFv2 authentication. If not set, then the area level
      authentication of the transit area holds for the port.
    type: str
    required: false
    choices:
      - none
      - text
      - md5
      - sha1
      - sha256
      - sha384
      - sha512
      - keychain
  other_config:
    description: Miscellaneous options
    required: false
    type: dict
    suboptions:
      dead_interval:
        description: >
          The time, in seconds, that a neighbor waits for a Hello packet before
          tearing down adjacency with local router.
        type: int
        required: true
      transmit_delay:
        description: >
          The estimated time, in seconds, to transmit an LSA to a neighbor.
        type: int
        required: true
      virtual_ifindex:
        description: >
          The virtual link index assigned to the OSPF virtual interface.
        type: int
        required: true
      retransmit_interval:
        description: The estimated time, in seconds, between successive LSAs
        type: int
        required: true
      hello_interval:
        description: The time, in seconds, between successive Hello packets.
        type: int
        required: true
"""

EXAMPLES = """
---
- name: Create new OSPF Vlink
  aoscx_ospf_vlink:
    state: create
    vrf: default
    ospf_id: 1
    area_id: 0.0.0.1
    peer_router_id: 0.0.0.1
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.ospf_router import OspfRouter
    from pyaoscx.ospf_area import OspfArea
    from pyaoscx.ospf_virtual_link import OspfVlink
    from pyaoscx.vrf import Vrf

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "state": {
            "type": "str",
            "required": False,
            "choices": ["create", "update", "delete"],
            "default": "create",
        },
        "vrf": {
            "type": "str",
            "required": True,
        },
        "ospf_id": {
            "type": "int",
            "required": True,
        },
        "area_id": {
            "type": "str",
            "required": True,
        },
        "peer_router_id": {
            "type": "str",
            "required": True,
        },
        "ipsec_ah": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "auth_key": {
                    "type": "str",
                    "required": True,
                    "no_log": True,
                },
                "auth_type": {
                    "type": "str",
                    "required": True,
                    "choices": ["md5", "sha1"],
                },
                "spi": {
                    "type": "int",
                    "required": True,
                },
            },
        },
        "ipsec_esp": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "auth_key": {
                    "type": "str",
                    "required": True,
                    "no_log": True,
                },
                "auth_type": {
                    "type": "str",
                    "required": True,
                    "choices": ["md5", "sha1"],
                },
                "encryption_key": {
                    "type": "str",
                    "required": True,
                    "no_log": True,
                },
                "encryption_type": {
                    "type": "str",
                    "required": True,
                    "choices": ["des", "3des", "aes", "none"],
                },
                "spi": {
                    "type": "int",
                    "required": True,
                },
            },
        },
        "ospf_auth_md5_keys": {
            "type": "list",
            "elements": "dict",
            "required": False,
            "default": None,
            "no_log": False,
            "options": {
                "id": {
                    "type": "int",
                    "required": True,
                },
                "key": {
                    "type": "str",
                    "required": True,
                    "no_log": True,
                },
            },
        },
        "ospf_auth_sha_keys": {
            "type": "list",
            "elements": "dict",
            "required": False,
            "default": None,
            "no_log": False,
            "options": {
                "id": {
                    "type": "int",
                    "required": True,
                },
                "key": {
                    "type": "str",
                    "required": True,
                    "no_log": True,
                },
            },
        },
        "ospf_auth_keychain": {
            "type": "str",
            "required": False,
            "default": None,
            "no_log": False,
        },
        "ospf_auth_text_key": {
            "type": "str",
            "required": False,
            "default": None,
            "no_log": True,
        },
        "ospf_auth_type": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": [
                "none",
                "text",
                "md5",
                "sha1",
                "sha256",
                "sha384",
                "sha512",
                "keychain",
            ],
        },
        "other_config": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "dead_interval": {"type": "int", "required": True},
                "transmit_delay": {"type": "int", "required": True},
                "virtual_ifindex": {"type": "int", "required": True},
                "retransmit_interval": {"type": "int", "required": True},
                "hello_interval": {"type": "int", "required": True},
            },
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        mutually_exclusive=[
            (
                "ospf_auth_md5_keys",
                "ospf_auth_sha_keys",
                "ospf_auth_text_key",
                "ospf_auth_keychain",
            )
        ],
        required_if=[
            ("ospf_auth_type", "md5", ["ospf_auth_md5_keys"]),
            ("ospf_auth_type", "text", ["ospf_auth_text_key"]),
            ("ospf_auth_type", "sha1", ["ospf_auth_sha_keys"]),
            ("ospf_auth_type", "sha216", ["ospf_auth_sha_keys"]),
            ("ospf_auth_type", "sha384", ["ospf_auth_sha_keys"]),
            ("ospf_auth_type", "sha512", ["ospf_auth_sha_keys"]),
            ("ospf_auth_type", "keychain", ["ospf_auth_keychain"]),
        ],
    )

    result = {"changed": False}

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    # Get playbook's arguments
    params = ansible_module.params.copy()

    # Remove what is not a direct parameter for the interface
    state = params.pop("state")
    vrf = params.pop("vrf")
    ospf_id = params.pop("ospf_id")
    area_id = params.pop("area_id")
    peer_router_id = params.pop("peer_router_id")

    if params["ospf_auth_md5_keys"]:
        for keydict in params["ospf_auth_md5_keys"]:
            _id = keydict["id"]
            if _id < 1 or 255 < _id:
                ansible_module.fail_json(
                    msg="md5 key IDs must be at least 1, and at most 255"
                )

    if params["ospf_auth_sha_keys"]:
        for keydict in params["ospf_auth_sha_keys"]:
            _id = keydict["id"]
            if _id < 1 or 255 < _id:
                ansible_module.fail_json(
                    msg="SHA key IDs must be at least 1, and at most 255"
                )

    if params["ospf_auth_type"]:
        if params["ospf_auth_type"] == "none":
            # NOTE: 'null' needs to be quoted in YAML to get the string rather
            # than None, we use 'none' as the value in YAML, to mean 'null',
            # which is what the REST API expects
            params["ospf_auth_type"] = "null"

    # NOTE: this is converted from a list, which is easier to read/write, to a
    # dictionary, with the id as key, and the security key as the value, which
    # is the format the REST API expects
    if params["ospf_auth_md5_keys"]:
        _ospf_auth_md5_keys = {}
        for keydict in params["ospf_auth_md5_keys"]:
            k, v = keydict["id"], keydict["key"]
            _ospf_auth_md5_keys[k] = v
        params["ospf_auth_md5_keys"] = _ospf_auth_md5_keys
    if params["ospf_auth_sha_keys"]:
        _ospf_auth_sha_keys = {}
        for keydict in params["ospf_auth_sha_keys"]:
            k, v = keydict["id"], keydict["key"]
            _ospf_auth_sha_keys[k] = v
        params["ospf_auth_sha_keys"] = _ospf_auth_sha_keys

    session = get_pyaoscx_session(ansible_module)

    if params["ospf_auth_keychain"]:
        params[
            "ospf_auth_keychain"
        ] = "/rest/v{0}/system/keychains/{1}".format(
            session.api.version, params["ospf_auth_keychain"]
        )

    if params["ipsec_esp"]:
        # NOTE: encryption_type is required, so it cannot be None
        if params["ipsec_esp"]["encryption_type"] == "none":
            # NOTE: 'null' needs to be quoted in YAML to get the string rather
            # than None, we use 'none' as the value in YAML, to mean 'null',
            # which is what the REST API expects
            params["ipsec_esp"]["encryption_type"] = "null"

    # Avoid passing None, as it could delete config
    for key in list(params):
        if params[key] is None:
            del params[key]

    vrf = Vrf(session, vrf)
    try:
        vrf.get()
    except Exception:
        ansible_module.fail_json(msg="Could not find VRF, make sure it exists")

    ospf_router = OspfRouter(session, ospf_id, vrf)
    try:
        ospf_router.get()
    except Exception:
        ansible_module.fail_json(
            msg="Could not find OSPF Router, make sure it exists"
        )

    ospf_area = OspfArea(session, area_id, ospf_router)
    try:
        ospf_area.get()
    except Exception:
        ansible_module.fail_json(
            msg="Could not find OSPF Area, make sure it exists"
        )

    ospf_vlink = OspfVlink(session, peer_router_id, ospf_area, **params)
    try:
        ospf_vlink.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            ospf_vlink.delete()
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        ospf_vlink.create()
        result["changed"] = True
        ansible_module.exit_json(**result)

    for key, value in params.items():
        present = getattr(ospf_vlink, key)
        if present != value:
            result["changed"] = True
        setattr(ospf_vlink, key, value)
    if result["changed"]:
        ospf_vlink.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
