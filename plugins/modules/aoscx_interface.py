#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_interface
version_added: "4.0.0"
short_description: Module for configuring Interfaces in AOS-CX switches.
description: >
  This module provides the functionality for configuring Interfaces on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Interface name, should be in the format chassis/slot/port, e.g. 1/2/3,
      1/2/32.
    type: str
    required: true
  enabled:
    description: >
      Administrative state of the interface. Use true to administratively
      enable it.
    type: bool
    required: false
  description:
    description: Description of the interface.
    type: str
    required: false
  duplex:
    description: >
      Enable full duplex or disable for half duplex. If this value is
      specified, speeds must also be specified.
    type: str
    choices:
      - full
      - half
    required: false
  speeds:
    description: >
      Configure the speeds of the interface in megabits per second. If this
      value is specified, duplex must also be specified.
    type: list
    required: false
  vsx_sync:
    description: >
      Controls which attributes should be synchronized between VSX peers.
    type: list
    required: false
    choices:
      - acl
      - irdp
      - qos
      - rate_limits
      - vlan
      - vsx_virtual
      - virtual_gw_l3_src_mac_enable
      - policy
      - threshold_profile
      - macsec_policy
      - mka_policy
      - portfilter
      - client_ip_track_configuration
      - mgmd_acl
      - mgmd_enable
      - mgmd_robustness
      - mgmd_querier_max_response_time
      - mgmd_mld_version
      - mgmd_querier_interval
      - mgmd_last_member_query_interval
      - mgmd_querier_enable
      - mgmd_mld_static_groups
      - mgmd_igmp_static_groups
      - mgmd_igmp_version
  qos:
    description: >
      Name of existing QoS schedule profile to apply to interface. This option
      is mutually exclusive with the no_qos option.
    type: str
    required: false
  no_qos:
    description: >
      Flag to remove the existing QoS schedule profile of the interface. use
      true to remove it. This option is mutually exclusive with the qos option.
    type: bool
    default: false
    required: false
  qos_rate:
    description: >
      The rate limit value configured for broadcast/multicast/unknown unicast
      traffic.
    type: dict
    required: false
    suboptions:
      unknown-unicast:
        description: >
          Ingress unknown unicast rate-limit bandwidth value. The unit type is
          specified by the end of the string, i.e.: 200pps or 100kbps.
        type: str
        required: false
      broadcast:
        description: >
          Ingress broadcast rate-limit bandwidth value. The unit type is
          specified by the end of the string, i.e.: 200pps or 100kpbs.
        type: str
        required: false
      multicast:
        description: >
          Ingress multicast rate-limit bandwidth value. The unit type is
          specified by the end of the string. i.e.: 200pps or 100kpbs.
        type: str
        required: false
  queue_profile:
    description: Name of queue profile to apply to interface.
    type: str
    required: false
  use_global_queue_profile:
    description: >
      Option to use the switch's global Queue Profile. This option is mutually
      exclusive with the queue_profile option.
    type: bool
    required: false
    default: false
  qos_trust_mode:
    description: >
      Specifies the interface QoS Trust Mode. 'global' configures the interface
      to use the global configuration.
    type: str
    choices:
      - cos
      - dscp
      - none
      - global
    required: false
  state:
    description: Create, Update or Delete the Interface.
    type: str
    default: create
    choices:
      - create
      - update
      - delete
    required: false
"""

EXAMPLES = """
- name: Configure Interface 1/1/2 - enable full duplex at 1000 Mbit/s
  aoscx_interface:
    name: 1/1/2
    duplex: full
    speeds: ['1000']
    enabled: true

- name: Administratively disable interface 1/1/2
  aoscx_interface:
    name: 1/1/2
    enabled: false

- name: Set a QoS trust mode for interface 1/1/2
  aoscx_interface:
    name: 1/1/2
    qos_trust_mode: cos

- name: Set interface 1/1/3 to use global trust mode
  aoscx_interface:
    name: 1/1/3
    qos_trust_mode: global

- name: Configure Interface 1/1/3 to use the global QoS trust mode
  aoscx_interface:
    name: 1/1/13
    qos_trust_mode: global

- name: Set a Queue Profile for interface 1/1/2
  aoscx_interface:
    name: 1/1/2
    queue_profile: STRICT-PROFILE

- name: Set interface 1/1/3 to use global Queue Profile
  aoscx_interface:
    name: 1/1/3
    use_global_queue_profile: true

- name: Configure Schedule Profile on an interface
  aoscx_interface:
    name: 1/1/17
    qos: STRICT

- name: Remove a Schedule Profile from an interface
  aoscx_interface:
    name: 1/1/17
    no_qos: true

- name: Set the QoS rate to the 1/1/17 Interface
  aoscx_interface:
    name: 1/1/17
    qos_rate:
      broadcast: 200pps
      unknown-unicast: 100kbps
      multicast: 200pps

- name: Configure Interface 1/1/2 - enable vsx-sync features
  aoscx_interface:
    name: 1/1/2
    duplex: full
    speeds: ['1000']
    vsx_sync:
      - acl
      - irdp
      - qos
      - rate_limits
      - vlan
      - vsx_virtual
"""

RETURN = r""" # """


def get_argument_spec():
    argument_spec = {
        "name": {
            "type": "str",
            "required": True,
        },
        "description": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "enabled": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "description": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "duplex": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["full", "half"],
        },
        "speeds": {
            "type": "list",
            "required": False,
            "default": None,
        },
        "vsx_sync": {
            "type": "list",
            "default": None,
            "choices": [
                "acl",
                "irdp",
                "qos",
                "rate_limits",
                "vlan",
                "vsx_virtual",
                "virtual_gw_l3_src_mac_enable",
                "policy",
                "threshold_profile",
                "macsec_policy",
                "mka_policy",
                "portfilter",
                "client_ip_track_configuration",
                "mgmd_acl",
                "mgmd_enable",
                "mgmd_robustness",
                "mgmd_querier_max_response_time",
                "mgmd_mld_version",
                "mgmd_querier_interval",
                "mgmd_last_member_query_interval",
                "mgmd_querier_enable",
                "mgmd_mld_static_groups",
                "mgmd_igmp_static_groups",
                "mgmd_igmp_version",
            ],
        },
        "qos": {
            "type": "str",
            "default": None,
            "required": False,
        },
        "no_qos": {
            "type": "bool",
            "default": False,
            "required": False,
        },
        "queue_profile": {
            "type": "str",
            "default": None,
            "required": False,
        },
        "use_global_queue_profile": {
            "type": "bool",
            "required": False,
            "default": False,
        },
        "qos_trust_mode": {
            "type": "str",
            "default": None,
            "required": False,
            "choices": ["cos", "dscp", "none", "global"],
        },
        "qos_rate": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "unknown-unicast": {
                    "type": "str",
                    "required": False,
                },
                "broadcast": {
                    "type": "str",
                    "required": False,
                },
                "multicast": {
                    "type": "str",
                    "required": False,
                },
            },
        },
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
    }
    return argument_spec


def vsx_sync_features_mapping(feature):
    mapping = {
        "acl": "^acl.*",
        "irdp": ".irdp.*",
        "qos": "^qos.*",
        "rate_limits": "rate_limits",
        "vlan": "^vlan.*",
        "vsx_virtual": "^vsx_virtual.*",
        "virtual_gw_l3_src_mac_enable": "virtual_gw_l3_src_mac_enable",
        "policy": "^policy.*",
        "threshold_profile": "threshold_profile",
        "macsec_policy": "macsec_policy",
        "mka_policy": "mka_policy",
        "portfilter": "portfilter",
        "client_ip_track_configuration": "client_ip_track_configuration",
        "mgmd_acl": "mgmd_acl",
        "mgmd_enable": "mgmd_enable",
        "mgmd_robustness": "mgmd_robustness",
        "mgmd_querier_max_response_time": "mgmd_querier_max_response_time",
        "mgmd_mld_version": "mgmd_mld_version",
        "mgmd_querier_interval": "mgmd_querier_interval",
        "mgmd_last_member_query_interval": "mgmd_last_member_query_interval",
        "mgmd_querier_enable": "mgmd_querier_enable",
        "mgmd_mld_static_groups": "mgmd_mld_static_groups",
        "mgmd_igmp_static_groups": "mgmd_igmp_static_groups",
        "mgmd_igmp_version": "mgmd_igmp_version",
    }
    return mapping[feature]


def main():
    # Create the Ansible Module
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        required_together=[["duplex", "speeds"]],
        mutually_exclusive=[
            ("qos", "no_qos"),
            ("queue_profile", "use_global_queue_profile"),
        ],
    )

    result = dict(
        changed=False
    )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    # Get playbook's arguments
    name = ansible_module.params["name"]
    enabled = ansible_module.params["enabled"]
    description = ansible_module.params["description"]
    duplex = ansible_module.params["duplex"]
    speeds = ansible_module.params["speeds"]
    vsx_sync = ansible_module.params["vsx_sync"]
    state = ansible_module.params["state"]
    qos = ansible_module.params["qos"]
    no_qos = ansible_module.params["no_qos"]
    queue_profile = ansible_module.params["queue_profile"]
    use_global_queue_profile = ansible_module.params[
        "use_global_queue_profile"
    ]
    qos_trust_mode = ansible_module.params["qos_trust_mode"]
    qos_rate = ansible_module.params["qos_rate"]

    session = get_pyaoscx_session(ansible_module)
    device = Device(session)

    interface = device.interface(name)
    modified = interface.modified

    if state == "delete":
        interface.delete()
        # report only if created before this run
        result["changed"] = not modified
        ansible_module.exit_json(**result)

    if description:
        interface.description = description
    if enabled is not None:
        interface.admin_state = "up" if enabled else "down"
    if vsx_sync:
        if not device.materialized:
            device.get()
        if not device.vsx_capable():
            ansible_module.module.fail_json(msg="Device doesn't support VSX")
        clean_vsx_features = [
            vsx_sync_features_mapping(feature) for feature in vsx_sync
        ]
        interface.vsx_sync = clean_vsx_features

    modified |= interface.apply()
    if duplex and speeds:
        modified |= interface.speed_duplex_configure(
            speeds=speeds, duplex=duplex
        )
    if qos:
        modified |= interface.update_interface_qos(qos)
    if no_qos:
        modified |= interface.update_interface_qos(None)
    if queue_profile:
        modified |= interface.update_interface_queue_profile(queue_profile)
    if use_global_queue_profile:
        modified |= interface.update_interface_queue_profile(None)
    if qos_trust_mode:
        modified |= interface.update_interface_qos_trust_mode(qos_trust_mode)
    if qos_rate:
        modified |= interface.update_interface_qos_rate(qos_rate)

    result["changed"] = modified
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
