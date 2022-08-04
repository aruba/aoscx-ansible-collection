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
module: aoscx_ospf_area
version_added: "4.1.0"
short_description: Create or Delete OSPF configuration on AOS-CX
description: >
  This modules provides configuration management of OSPF Areas on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  state:
    description: Create or update or delete the OSPF Area.
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
  area_type:
    description: >
      Alphanumeric option defining how the external routing and summary LSAs
      for this area will be handled.
    required: false
    choices:
      - default
      - nssa
      - nssa_no_summary
      - stub
      - stub_no_summary
    default: default
    type: str
  ipsec_ah:
    description: >
      IPsec Authentication Header (AH) configuration. Specifies Security
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
  no_ipsec_ah:
    description: Remove IPsec authentication AH.
    type: bool
    required: false
  other_config:
    description: Extra configuration parameters for the area
    type: dict
    required: false
    suboptions:
      stub_default_cost:
        description: >
          Cost for the default summary route sent to the stub area
        type: int
      stub_metric_type:
        description: Type of metric
        type: str
        choices:
          - metric_standard
          - metric_comparable_cost
          - metric_non_comparable
        default: metric_non_comparable
"""

EXAMPLES = """
---
- name: Create new OSPF Area
  aoscx_ospf_area:
    vrf: default
    ospf_id: 1
    area_id: 1
    other_config:
      stub_metric_cost: 2
      stub_metric_type: metric_non_comparable

- name: Create new OSPF Area
  aoscx_ospf_area:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    area_type: nssa
    state: update
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.ospf_router import OspfRouter
    from pyaoscx.ospf_area import OspfArea
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
        "area_type": {
            "type": "str",
            "required": False,
            "choices": [
                "default",
                "nssa",
                "nssa_no_summary",
                "stub",
                "stub_no_summary",
            ],
            "default": "default",
        },
        "ipsec_ah": {
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
                "auth_key": {"type": "str", "required": True, "no_log": True},
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
        "no_ipsec_ah": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "other_config": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "stub_default_cost": {
                    "type": "int",
                    "required": False,
                },
                "stub_metric_type": {
                    "type": "str",
                    "required": False,
                    "choices": [
                        "metric_standard",
                        "metric_comparable_cost",
                        "metric_non_comparable",
                    ],
                    "default": "metric_non_comparable",
                },
            },
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        mutually_exclusive=[("ipsec_ah", "no_ipsec_ah")],
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

    # Remove what is not a direct parameter for the area
    vrf = params.pop("vrf")
    ospf_id = params.pop("ospf_id")
    area_id = params.pop("area_id")
    state = params.pop("state")
    no_ipsec_ah = params.pop("no_ipsec_ah")

    session = get_pyaoscx_session(ansible_module)

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

    if params["ipsec_esp"]:
        params["ipsec_esp"] = params["ipsec_esp"] or {}
        if params["ipsec_esp"]["encryption_type"] == "none":
            params["ipsec_esp"]["encryption_type"] = "null"

    # Avoid passing None, as it could delete config
    for key in list(params):
        if params[key] is None:
            del params[key]

    # this must be done here, so we don't avoid passing `None`
    if no_ipsec_ah:
        params["ipsec_ah"] = None

    ospf_area = OspfArea(session, area_id, ospf_router, **params)
    try:
        ospf_area.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            ospf_area.delete()
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        ospf_area.create()
        result["changed"] = True
        ansible_module.exit_json(**result)

    for key, value in params.items():
        present = getattr(ospf_area, key)
        if present != value:
            result["changed"] = True
        setattr(ospf_area, key, value)
    if result["changed"]:
        ospf_area.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
