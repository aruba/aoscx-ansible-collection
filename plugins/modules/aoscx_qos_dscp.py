#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_qos_dscp
version_added: "4.0.0"
short_description: Create or Delete QoS DSCP trust modes on AOS-CX.
description: >
  This module provides configuration management of QoS DSCP trust type on
  AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  code_point:
    description: >
      6-bit integer value used to mark packets for different per-hop behavior
      as defined by IETF RFC2474. It is carried within the Differentiated
      Services (DS) field of the IPv4 or IPv6 header. Used as an identifier.
    required: True
    type: int
  color:
    description: >
      String to identify the color which may be used later in the pipeline in
      packet-drop decision points.
    required: false
    type: str
    choices:
      - green
      - yellow
      - red
  cos:
    description: >
      Priority Code Point (PCP) that will be assigned to any IP packet with the
      specified DSCP codepoint, if that packet's ingress port has an effective
      trust mode of DSCP. The new PCP is used when the packet is transmitted
      out of a port or trunk with a VLAN tag. If the key is not specified,
      then no remark will occur.
    required: false
    type: int
  description:
    description: String used for customer documentation.
    required: false
    type: str
  local_priority:
    description: >
      Integer to represent an internal meta-data value that will be associated
      with the packet. This value will be used later to select the egress queue
      for the packet.
    required: false
    type: str
"""

EXAMPLES = """
---
- name: Update description of QoS DSCP trust type map entry with code point 3
  aoscx_qos_dscp:
   code_point: 3
   description: QoS DSCP 3 - Engineering Department

- name: Update color of QoS DSCP trust type map entry with code point 5
  aoscx_qos_dscp:
    code_point: 5
    color: yellow

- name: >
    Update color and local priority of QoS DSCP trust type map entry with code
    point 5
  aoscx_qos_dscp:
    code_point: 5
    color: yellow
    local_priority: 3

- name: Update description of a QoS DSCP entry in an access platform switch
  aoscx_qos_dscp:
    code_point: 1
    description: New description
    cos: 2
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device
    from pyaoscx.qos_dscp import QosDscp

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "code_point": {
            "type": "int",
            "default": None,
            "required": False,
        },
        "color": {
            "type": "str",
            "required": False,
            "choices": ["green", "yellow", "red"],
            "default": None,
        },
        "cos": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "local_priority": {
            "type": "int",
            "default": None,
            "required": False,
        },
        "description": {
            "type": "str",
            "default": None,
            "required": False,
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
    )

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    # Get playbook's arguments
    params = ansible_module.params.copy()

    code_point = params.pop("code_point")

    if code_point not in range(0, 64):
        ansible_module.fail_json(
            msg="code_point must be an integer in the [0, 63] interval, "
            "that is, an integer no lower than 0, and no higher than 63"
        )

    session = get_pyaoscx_session(ansible_module)

    device = Device(session)

    supports_cos = device.is_capable("qos_cos_based_queueing")
    supports_dscp_cos = device.is_capable("qos_dscp_map_cos_override")

    if not supports_cos and supports_dscp_cos:
        # Unlike CLI the REST API uses 'priority_code_point' instead of 'cos',
        # so this value must be renamed
        params["priority_code_point"] = params.pop("cos", None)

    # Avoid passing None, as it could delete config
    for key in list(params):
        if params[key] is None:
            del params[key]

    qos_dscp = QosDscp(session, code_point, **params)
    qos_dscp.get()

    for key, value in params.items():
        present = getattr(qos_dscp, key)
        if present != value:
            result["changed"] = True
        setattr(qos_dscp, key, value)
    qos_dscp.apply()

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
