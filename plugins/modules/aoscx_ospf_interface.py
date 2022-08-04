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
module: aoscx_ospf_interface
version_added: "4.1.0"
short_description: Create, update or delete an OSPF interface configuration.
description: >
  This module provides configuration management of OSPF interface on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  state:
    description: >
      Create, update, or delete the OSPF interface_name configuration.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
  vrf:
    description: Alphanumeric name of the VRF the OSPF ID belongs to.
    type: str
    required: true
  version:
    description: >
      OSPF version. 'v2' for OSPFv2 and 'v3' for OSPFv3.
    type: str
    required: true
    choices:
      - v2
      - v3
  ospf_id:
    description: OSPF process ID between numbers 1-63.
    type: int
    required: true
  area_id:
    description: Unique identifier in X.X.X.X format.
    type: str
    required: true
  interface_name:
    description: >
      Name of the Interface in which the OSPF process must be attached.
    type: str
    required: true
  cost:
    description: Output cost configured for the interface.
    type: int
    required: false
  type:
    description: The type of the OSPF network interface.
    type: str
    required: false
    choices:
      - none
      - broadcast
      - nbma
      - point_to_point
      - point_to_multipoint
      - virtual_link
      - loopback
  shutdown:
    description: Shutdown OSPF functionalities on this interface.
    type: bool
    required: false
  priority:
    description: >
      The router with the highest priority will be more eligible to become the
      Designated Router. Setting the value to 0, makes the router ineligible to
      become the Designated Router.
    type: int
    required: false
  bfd:
    description: >
      Specifies whether the router global Bidirectional Forwarding Detection
      (BFD) mode should be overridden for this particular interface.
    type: str
    required: false
    choices:
      - enable
      - disable
      - default
  transmit_delay:
    description: >
      The estimated time in seconds to transmit an LSA to a neighbor.
    type: int
    required: false
  retransmit_interval:
    description: The number of seconds between LSA retransmissions.
    type: int
    required: false
  hello_interval:
    description: >
      The Hello packet will be sent every hello interval timer value seconds.
    type: int
    required: false
  dead_interval:
    description: >
      The time duration, in seconds, that a neighbor should wait for a
      Hello packet before tearing down adjacencies with the local router.
    type: int
    required: false
  ospfv2_auth_type:
    description: >
      The type of OSPFv2 authentication. If not set, then parent area level
      authentication holds for the port.
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
  ospfv2_auth_sha_keys:
    description: >
      The authentication keys for OSPFv2 authentication type "sha".
    type: list
    elements: dict
    required: false
    suboptions:
      id:
        description: Key ID for secure-hash key. In range 1, 255.
        type: int
        required: true
      key:
        description: SHA key to use.
        type: str
        required: true
  ospfv2_auth_md5_keys:
    description: >
      The authentication keys for OSPFv2 authentication type "md5".
    type: list
    elements: dict
    required: false
    suboptions:
      id:
        description: Key ID for secure-hash key. In range 1, 255.
        type: int
        required: true
      key:
        description: MD5 key to use.
        type: str
        required: true
  ospfv2_auth_text_key:
    description: >
      The authentication key for OSPFv2 authentication type "text".
    type: str
    required: false
  ospfv2_auth_keychain:
    description: >
      Name of the "Keychain" used for cryptographic authentication. Supports
      MD5, SHA-1, SHA-256, SHA-384, and SHA-512.
    type: str
    required: false
  ospfv3_ipsec_ah:
    description: >
      IPsec Authentication Header (AH) configuration. 'ospfv3_ipsec_ah'
      will be used if 'ospfv3_ipsec_esp' is also configured.
    type: dict
    required: false
    suboptions:
      auth_key:
        description: >
          Authentication key.
          This parameter is required if auth_type and spi are set.
        type: str
        required: false
      auth_type:
        description: >
          Authentication algorithm.
          This parameter is required if auth_key is set.
        type: str
        required: false
        choices:
          - md5
          - sha1
      spi:
        description: >
          Security Parameters Index (SPI) for the Security Association.
          AH SPI must be unique on a router.
          This parameter is required if auth_key is set.
        type: int
        required: false
      ah_null:
        description: >
          Disable OSPF IPsec AH authentication. This is used to override
          OSPF_Area level IPsec AH authentication. When IPsec AH is
          configured at OSPF_Area, set true to disable OSPF IPsec AH on
          this interface. When IPsec AH is configured at OSPF_Area and OSPF
          Interface, making true will remove OSPF Interface IPsec AH
          configuration and disable OSPF IPsec AH on this interface.
        type: bool
        required: false
  no_ospfv3_ipsec_ah:
    description: >
      Option to delete ospfv3 IPsec AH configuration. This option is mutually
      exclusive with the `ospfv3_ipsec_ah` option.
    type: bool
    required: false
  ospfv3_ipsec_esp:
    description: >
      IPsec Encapsulating Security Payload (ESP) configuration.
      'ospfv3_ipsec_ah' will be used if 'ospfv3_ipsec_esp' is also configured.
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
        required: true
        choices:
          - md5
          - sha1
      encryption_key:
        description: IPsec ESP encryption key.
        type: str
        required: false
      encryption_type:
        description: IPsec ESP encryption algorithm.
        type: str
        required: true
        choices:
          - des
          - 3des
          - aes
          - none
      spi:
        description: >
          Security Parameters Index (SPI) for the Security Association. ESP
          SPI must be unique on a router.
        type: int
        required: true
      esp_null:
        description: >
          Disable OSPF IPsec ESP encryption and authentication. This is used to
          override OSPF Area-level IPsec ESP encryption and authentication.
          When IPsec ESP is configured at OSPF Area-level, true disables OSPF
          IPsec ESP on this interface. When IPsec ESP is configured at OSPF
          Area-level and OSPF Interface, true removes OSPF Interface IPsec ESP
          configuration and disable OSPF IPsec ESP on this interface.
        type: bool
        required: false
"""

EXAMPLES = """
---
- name: Attach an OSPF router and area to interface 1/1/1
  aoscx_ospf_interface:
    vrf: RED
    version: v3
    ospf_id: 5
    area_id: 1.1.1.1
    interface_name: 1/1/1
    state: create

- name: Remove interface 1/1/3 from OSPFv3 Area 1.1.1.1
  aoscx_ospf_interface:
    vrf: RED
    version: v3
    ospf_id: 5
    area_id: 1.1.1.1
    interface_name: 1/1/3
    state: delete

- name: Set the OSPFv3 transmit delay in interface 1/1/13
  aoscx_ospf_interface:
    vrf: default
    version: v3
    ospf_id: 4
    area_id: 1.1.1.2
    interface_name: 1/1/13
    transmit_delay: 20

- name: Enable OSPF authentication
  aoscx_ospf_interface:
    vrf: default
    version: v2
    ospf_id: 5
    area_id: 1.1.1.1
    interface_name: 1/1/4
    ospfv2_auth_type: sha1
    ospfv2_auth_sha_keys:
      - id: 1
        key: sha_key_1
      - id: 2
        key: sha_key_2
"""


RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device
    from pyaoscx.ospf_router import OspfRouter
    from pyaoscx.ospfv3_router import Ospfv3Router
    from pyaoscx.ospf_area import OspfArea
    from pyaoscx.ospf_interface import OspfInterface
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
            "default": "create",
            "choices": ["create", "delete", "update"],
        },
        "version": {
            "type": "str",
            "required": True,
            "choices": ["v2", "v3"],
        },
        "vrf": {"type": "str", "required": True},
        "ospf_id": {"type": "int", "required": True},
        "area_id": {"type": "str", "required": True},
        "interface_name": {"type": "str", "required": True},
        "cost": {"type": "int", "required": False, "default": None},
        "type": {
            "type": "str",
            "required": False,
            "choices": [
                "none",
                "broadcast",
                "nbma",
                "point_to_point",
                "point_to_multipoint",
                "virtual_link",
                "loopback",
            ],
            "default": None,
        },
        "shutdown": {"type": "bool", "required": False, "default": None},
        "priority": {"type": "int", "required": False, "default": None},
        "bfd": {
            "type": "str",
            "required": False,
            "choices": ["enable", "disable", "default"],
            "default": None,
        },
        "transmit_delay": {"type": "int", "required": False, "default": None},
        "retransmit_interval": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "hello_interval": {"type": "int", "required": False, "default": None},
        "dead_interval": {"type": "int", "required": False, "default": None},
        "ospfv2_auth_type": {
            "type": "str",
            "required": False,
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
            "default": None,
        },
        "ospfv2_auth_sha_keys": {
            "type": "list",
            "required": False,
            "elements": "dict",
            "options": {
                "id": {
                    "type": "int",
                    "required": True,
                },
                "key": {"type": "str", "required": True, "no_log": True},
            },
            "no_log": False,
        },
        "ospfv2_auth_text_key": {
            "type": "str",
            "required": False,
            "no_log": True,
        },
        "ospfv2_auth_md5_keys": {
            "type": "list",
            "required": False,
            "elements": "dict",
            "options": {
                "id": {
                    "type": "int",
                    "required": True,
                },
                "key": {"type": "str", "required": True, "no_log": True},
            },
            "no_log": False,
        },
        "ospfv2_auth_keychain": {
            "type": "str",
            "required": False,
            "no_log": False,
        },
        "ospfv3_ipsec_ah": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "auth_key": {"type": "str", "required": False, "no_log": True},
                "auth_type": {
                    "type": "str",
                    "required": False,
                    "choices": ["md5", "sha1"],
                },
                "spi": {"type": "int", "required": False, "no_log": True},
                "ah_null": {
                    "type": "bool",
                    "required": False,
                    "default": None,
                },
            },
            "required_together": [
                ("auth_key", "auth_type", "spi"),
            ],
            "mutually_exclusive": [
                ("ah_null", "auth_key"),
                ("ah_null", "auth_type"),
                ("ah_null", "spi"),
            ],
        },
        "no_ospfv3_ipsec_ah": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "ospfv3_ipsec_esp": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "auth_key": {"type": "str", "required": True, "no_log": True},
                "auth_type": {
                    "type": "str",
                    "required": True,
                    "choices": ["md5", "sha1"],
                },
                "encryption_key": {
                    "type": "str",
                    "required": False,
                    "no_log": True,
                },
                "encryption_type": {
                    "type": "str",
                    "required": True,
                    "choices": ["des", "3des", "aes", "none"],
                },
                "spi": {"type": "int", "required": True, "no_log": True},
                "esp_null": {
                    "type": "bool",
                    "required": False,
                    "default": None,
                },
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
                "ospfv2_auth_md5_keys",
                "ospfv2_auth_sha_keys",
                "ospfv2_auth_text_key",
                "ospfv2_auth_keychain",
            ),
            ("ospfv3_ipsec_ah", "no_ospfv3_ipsec_ah"),
        ],
        required_if=[
            ("ospfv2_auth_type", "md5", ["ospfv2_auth_md5_keys"]),
            ("ospfv2_auth_type", "text", ["ospfv2_auth_text_key"]),
            ("ospfv2_auth_type", "sha1", ["ospfv2_auth_sha_keys"]),
            ("ospfv2_auth_type", "sha216", ["ospfv2_auth_sha_keys"]),
            ("ospfv2_auth_type", "sha384", ["ospfv2_auth_sha_keys"]),
            ("ospfv2_auth_type", "sha512", ["ospfv2_auth_sha_keys"]),
            ("ospfv2_auth_type", "keychain", ["ospfv2_auth_keychain"]),
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
    state = params["state"]

    interface_name = params["interface_name"]
    vrf = params["vrf"]
    version = params["version"]
    ospf_id = params["ospf_id"]
    area_id = params["area_id"]
    cost = params["cost"]
    if_type = params["type"]
    if if_type:
        if_type = params["type"].replace("_", "").replace("tt", "t")
    shutdown = params["shutdown"]
    priority = params["priority"]
    bfd = params["bfd"]
    transmit_delay = params["transmit_delay"]
    retransmit_interval = params["retransmit_interval"]
    hello_interval = params["hello_interval"]
    dead_interval = params["dead_interval"]

    ospfv2_auth_type = params["ospfv2_auth_type"]
    ospfv2_auth_sha_keys = params["ospfv2_auth_sha_keys"]
    ospfv2_auth_md5_keys = params["ospfv2_auth_md5_keys"]
    ospfv2_auth_text_key = params["ospfv2_auth_text_key"]
    ospfv2_auth_keychain = params["ospfv2_auth_keychain"]

    ospfv3_ipsec_ah = params["ospfv3_ipsec_ah"]
    ospfv3_ipsec_esp = params["ospfv3_ipsec_esp"]

    no_ospfv3_ipsec_ah = params["no_ospfv3_ipsec_ah"]

    # Do parameter validation that cannot be done through ansible module's
    # validation
    if ospfv2_auth_type == "none":
        # NOTE: 'null' needs to be quoted in YAML to get the string rather than
        # None, so we use 'none' as the value in YAML, to mean 'null', which is
        # what the REST API expects
        ospfv2_auth_type = "null"

    if ospfv3_ipsec_esp and ospfv3_ipsec_esp["encryption_type"] == "none":
        # NOTE: 'null' needs to be quoted in YAML to get the string rather than
        # None, so we use 'none' as the value in YAML, to mean 'null', which is
        # what the REST API expects
        ospfv3_ipsec_esp["encryption_type"] = "null"

    if version == "v3":
        # NOTE: gotta compare here to virtuallink, not virtual_link
        if if_type == "virtuallink":
            ansible_module.fail_json(
                msg="Invalid interface type 'virtual_link' for OSPFv3"
            )
        ospfv2_parameters = [
            "ospfv2_auth_type",
            "ospfv2_auth_sha_keys",
            "ospfv2_auth_md5_keys",
            "ospfv2_auth_text_key",
            "ospfv2_auth_keychain",
        ]
        for param in ospfv2_parameters:
            if params[param]:
                ansible_module.fail_json(
                    msg="ospfv2_auth configuration only applies for OSPFv2"
                )
    else:
        ospfv3_parameters = [
            "ospfv3_ipsec_ah",
            "ospfv3_ipsec_esp",
        ]
        for param in ospfv3_parameters:
            if params[param]:
                ansible_module.fail_json(
                    msg="ospfv3_ipsec configuration only applies for OSPFv3"
                )

    if 1 > ospf_id or 63 < ospf_id:
        ansible_module.fail_json(
            msg="The OSPF ID must be no lower than 1, and no higher than 63"
        )
    if ospfv2_auth_md5_keys:
        for keydict in ospfv2_auth_md5_keys:
            _id = keydict["id"]
            if _id < 1 or 255 < _id:
                ansible_module.fail_json(
                    msg="md5 key IDs must be at least 1, and at most 255"
                )

    if ospfv2_auth_sha_keys:
        for keydict in ospfv2_auth_sha_keys:
            _id = keydict["id"]
            if _id < 1 or 255 < _id:
                ansible_module.fail_json(
                    msg="SHA key IDs must be at least 1, and at most 255"
                )

    session = get_pyaoscx_session(ansible_module)

    device = Device(session)

    vrf = Vrf(session, vrf)
    try:
        vrf.get()
    except Exception:
        ansible_module.fail_json(msg="Could not find VRF, make sure it exists")

    ospf_router = (
        Ospfv3Router(session, ospf_id, vrf)
        if version == "v3"
        else OspfRouter(session, ospf_id, vrf)
    )
    try:
        ospf_router.get()
    except Exception:
        ansible_module.fail_json(
            msg="Could not find OSPF{0} Router, make sure it exists".format(
                version
            )
        )

    ospf_area = OspfArea(session, area_id, ospf_router)
    try:
        ospf_area.get()
    except Exception:
        ansible_module.fail_json(
            msg="Could not find OSPF{0} Area, make sure it exists".format(
                version
            )
        )

    ospf_interface = OspfInterface(session, interface_name, ospf_area)
    try:
        ospf_interface.get()
        exists = True
    except Exception:
        exists = False

    interface = device.interface(interface_name)

    if state == "delete":
        if exists:
            ospf_interface.delete()
        result["changed"] = exists
        config_attrs = (
            "ospf_auth_keychain",
            "ospf_auth_md5_keys",
            "ospf_auth_sha_keys",
            "ospf_auth_text_key",
            "ospf_auth_type",
            "ospf_bfd",
            "ospf_if_out_cost",
            "ospf_if_shutdown",
            "ospf_if_type",
            "ospf_intervals",
            "ospf_priority",
            "ospfv3_bfd",
            "ospfv3_dead_interval",
            "ospfv3_hello_interval",
            "ospfv3_if_cost",
            "ospfv3_if_priority",
            "ospfv3_if_shutdown",
            "ospfv3_if_type",
            "ospfv3_ipsec_ah",
            "ospfv3_ipsec_esp",
            "ospfv3_retransmit_interval",
            "ospfv3_transmit_delay",
        )
        for a in config_attrs:
            if hasattr(interface, a):
                setattr(interface, a, None)
        interface.apply()
        ansible_module.exit_json(**result)

    # Configure the interface
    if version == "v3":
        if cost:
            result["changed"] |= interface.ospfv3_if_cost != cost
            interface.ospfv3_if_cost = cost
        if if_type:
            result["changed"] |= interface.ospfv3_if_type != if_type
            interface.ospfv3_if_type = if_type
        if shutdown is not None:
            result["changed"] |= interface.ospfv3_if_shutdown != shutdown
            interface.ospfv3_if_shutdown = shutdown
        if priority:
            result["changed"] |= interface.ospfv3_if_priority != priority
            interface.ospfv3_if_priority = priority
        if bfd:
            result["changed"] |= (
                hasattr(interface, "ospfv3_bfd")
                and interface.ospfv3_bfd != bfd
            )
            interface.ospfv3_bfd = bfd
        if transmit_delay:
            result["changed"] |= (
                interface.ospfv3_transmit_delay != transmit_delay
            )
            interface.ospfv3_transmit_delay = transmit_delay
        if retransmit_interval:
            result["changed"] |= (
                interface.ospfv3_retransmit_interval != retransmit_interval
            )
            interface.ospfv3_retransmit_interval = retransmit_interval
        if hello_interval:
            result["changed"] |= (
                interface.ospfv3_hello_interval != hello_interval
            )
            interface.ospfv3_hello_interval = hello_interval
        if dead_interval:
            result["changed"] |= (
                interface.ospfv3_dead_interval != dead_interval
            )
            interface.ospfv3_dead_interval = dead_interval

        ospfv3_authentication_fail = False
        if (
            ospfv3_ipsec_ah is None
            and hasattr(interface, "ospfv3_ipsec_ah")
            and set(interface.ospfv3_ipsec_ah.keys()) != {'ah_null'}
            and not no_ospfv3_ipsec_ah
        ):
            ospfv3_authentication_fail = True
        if (
            ospfv3_ipsec_esp is None
            and hasattr(interface, "ospfv3_ipsec_esp")
            and set(interface.ospfv3_ipsec_esp.keys()) != {'esp_null'}
        ):
            ospfv3_authentication_fail = True

        if ospfv3_authentication_fail:
            ansible_module.fail_json(
                msg="OSPFv3 IPSec configuration active, must be provided"
            )

        if ospfv3_ipsec_ah:
            result["changed"] = True
            ah_null = ospfv3_ipsec_ah.pop("ah_null", None)
            if ah_null is not None:
                interface.ospfv3_ipsec_ah = {"ah_null": ah_null}
            else:
                interface.ospfv3_ipsec_ah = ospfv3_ipsec_ah
        if no_ospfv3_ipsec_ah:
            result["changed"] |= bool(interface.ospfv3_ipsec_ah)
            interface.ospfv3_ipsec_ah = None
        if ospfv3_ipsec_esp:
            result["changed"] = True
            esp_null = ospfv3_ipsec_esp.pop("esp_null", None)
            if esp_null is not None:
                ospfv3_ipsec_esp["esp_null"] = esp_null
            interface.ospfv3_ipsec_esp = ospfv3_ipsec_esp
    else:
        if cost:
            result["changed"] |= interface.ospf_if_out_cost != cost
            interface.ospf_if_out_cost = cost
        if if_type:
            if_type = "ospf_iftype_{0}".format(if_type)
            result["changed"] |= interface.ospf_if_type != if_type
            interface.ospf_if_type = if_type
        if shutdown is not None:
            result["changed"] |= interface.ospf_if_shutdown != shutdown
            interface.ospf_if_shutdown = shutdown
        if priority:
            result["changed"] |= interface.ospf_priority != priority
            interface.ospf_priority = priority
        if bfd:
            result["changed"] |= interface.ospf_bfd != bfd
            interface.ospf_bfd = bfd

        _ospf_intervals = {}
        if transmit_delay:
            _ospf_intervals["transmit_delay"] = transmit_delay
        if retransmit_interval:
            _ospf_intervals["retransmit_interval"] = retransmit_interval
        if hello_interval:
            _ospf_intervals["hello_interval"] = hello_interval
        if dead_interval:
            _ospf_intervals["dead_interval"] = dead_interval
        if _ospf_intervals:
            result["changed"] |= interface.ospf_intervals != _ospf_intervals
            interface.ospf_intervals = _ospf_intervals

        ospfv2_authentication_fail = False
        if (
            ospfv2_auth_type is None
            and hasattr(interface, "ospfv2_auth_type")
            and interface.ospfv2_auth_type != "null"
        ):
            ospfv2_authentication_fail = True
        if (
            ospfv2_auth_sha_keys is None
            and hasattr(interface, "ospf_auth_sha_keys")
            and interface.ospf_auth_sha_keys
        ):
            ospfv2_authentication_fail = True
        if (
            ospfv2_auth_text_key is None
            and hasattr(interface, "ospf_auth_text_key")
            and interface.ospf_auth_text_key
        ):
            ospfv2_authentication_fail = True
        if (
            ospfv2_auth_md5_keys is None
            and hasattr(interface, "ospf_auth_md5_keys")
            and interface.ospf_auth_md5_keys
        ):
            ospfv2_authentication_fail = True
        if (
            ospfv2_auth_keychain is None
            and hasattr(interface, "ospf_auth_keychain")
            and interface.ospf_auth_keychain
        ):
            ospfv2_authentication_fail = True

        if ospfv2_authentication_fail:
            ansible_module.fail_json(
                msg="OSPFv2 IPSec configuration active, must be provided"
            )

        if ospfv2_auth_type:
            result["changed"] |= interface.ospf_auth_type != ospfv2_auth_type
            interface.ospf_auth_type = ospfv2_auth_type

        if ospfv2_auth_type != "null":
            if ospfv2_auth_sha_keys:
                _ospf_auth_sha_keys = {}
                for keydict in ospfv2_auth_sha_keys.items():
                    k, v = keydict["id"], keydict["key"]
                    _ospf_auth_sha_keys[k] = v
                result["changed"] |= (
                    interface.ospf_auth_sha_keys != _ospf_auth_sha_keys
                )
                interface.ospf_auth_sha_keys = _ospf_auth_sha_keys
            if ospfv2_auth_text_key:
                result["changed"] |= (
                    interface.ospf_auth_text_key != ospfv2_auth_text_key
                )
                interface.ospf_auth_text_key = ospfv2_auth_text_key
            if ospfv2_auth_md5_keys:
                _ospf_auth_md5_keys = {}
                for keydict in ospfv2_auth_md5_keys:
                    k, v = keydict["id"], keydict["key"]
                    _ospf_auth_md5_keys[k] = v
                result["changed"] |= (
                    interface.ospf_auth_md5_keys != _ospf_auth_md5_keys
                )
                interface.ospf_auth_md5_keys = _ospf_auth_md5_keys
            if ospfv2_auth_keychain:
                keychain_url = "/rest/v{0}/system/keychains/{1}".format(
                    session.api.version, ospfv2_auth_keychain
                )
                result["changed"] |= (
                    interface.ospf_auth_keychain != keychain_url
                )
                interface.ospf_auth_keychain = keychain_url

    if result["changed"]:
        interface.apply()

    if not exists:
        ospf_interface.create()
        result["changed"] = True

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
