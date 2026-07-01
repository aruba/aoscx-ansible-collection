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
  configure_speed:
    description: >
      Option to configure speed/duplex in the interface. It `true`, `autoneg`
      is required.
    type: bool
    required: false
    default: false
  mtu:
    description: Configure MTU value of the interface
    type: int
    required: false
  autoneg:
    description: >
      Configure the auto-negotiation state of the interface. If `off` both
      `speeds`, and `duplex` are required.
    type: bool
    required: false
  duplex:
    description: >
      Configure the interface for full duplex or half duplex. If `autoneg`is
      `on` this must be omitted.
    type: str
    choices:
      - full
      - half
    required: false
  speeds:
    description: >
      Configure the speeds of the interface in megabits per second. If `duplex`
      is defined only one speed may be specified.
    type: list
    elements: int
    required: false
  acl_name:
    description: Name of the ACL being applied or removed from the VLAN.
    required: false
    type: str
  acl_type:
    description: Type of ACL being applied or removed from the VLAN.
    choices:
      - ipv4
      - ipv6
      - mac
    required: false
    type: str
  acl_direction:
    description: Direction for which the ACL is to be applied or removed.
    choices:
      - in
      - out
      - routed-in
      - routed-out
    required: false
    type: str
  vsx_sync:
    description: >
      Controls which attributes should be synchronized between VSX peers.
    type: list
    elements: str
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
      unknown_unicast:
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
  pause:
    description: Flow control (pause) mode applied to the interface.
    type: str
    required: false
  eee:
    description: Enable or disable Energy Efficient Ethernet on the interface.
    type: bool
    required: false
  error_control:
    description: Forward error correction (FEC) mode of the interface.
    type: str
    choices:
      - auto
      - none
      - base-r-fec
      - rs-fec
    required: false
  speed_downshift:
    description: Enable or disable speed downshift on the interface.
    type: bool
    required: false
  udld_enable:
    description: Enable or disable UDLD on the interface.
    type: bool
    required: false
  udld_interval:
    description: UDLD probe interval in milliseconds.
    type: int
    required: false
  udld_retries:
    description: Number of UDLD retries before a port is marked down.
    type: int
    required: false
  loop_protect_enable:
    description: Enable or disable loop protection on the interface.
    type: bool
    required: false
  loop_protect_action:
    description: Action taken when a loop is detected.
    type: str
    choices:
      - do-not-disable
      - tx-disable
      - tx-rx-disable
    required: false
  urpf_check:
    description: Unicast Reverse Path Forwarding mode on the interface.
    type: str
    choices:
      - disable
      - loose
      - strict
    required: false
  ip_mtu:
    description: IP MTU of the interface.
    type: int
    required: false
  sflow_enabled:
    description: >
      Enable or disable sFlow sampling on the interface. Set to false to apply
      C(no sflow) on the port (overriding the global sFlow setting).
    type: bool
    required: false
  arp_inspection_trust:
    description: >
      Mark the interface as trusted for Dynamic ARP Inspection. When true,
      ARP packets received on the port are not inspected.
    type: bool
    required: false
  dhcpv4_snooping_trust:
    description: Mark the interface as trusted for DHCPv4 snooping.
    type: bool
    required: false
  dhcpv4_snooping_max_bindings:
    description: >
      Maximum number of DHCPv4 snooping bindings allowed on the port (1-8192).
    type: int
    required: false
  dhcpv6_snooping_trust:
    description: Mark the interface as trusted for DHCPv6 snooping.
    type: bool
    required: false
  dhcpv6_snooping_max_bindings:
    description: >
      Maximum number of DHCPv6 snooping bindings allowed on the port (1-8192).
    type: int
    required: false
  pvlan_port_type:
    description: >
      Private VLAN port type. C(promiscuous) for a port in the primary VLAN,
      C(secondary) for a port in a secondary VLAN. Set to an empty string to
      clear the port type (back to a regular port).
    type: str
    required: false
    choices:
      - promiscuous
      - secondary
      - ""
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
- name: >
    Configure Interface 1/1/2 - full duplex, speed of 1000 Mbps and no
    auto-negotiation.
  aoscx_interface:
    name: 1/1/2
    configure_speed: true
    autoneg: off
    duplex: full
    speeds:
      - 1000

- name: >
    Configure Interface 1/1/2 - half duplex, speed 10 Mbps and no
    auto-negotiation.
  aoscx_interface:
    name: 1/1/2
    configure_speed: true
    autoneg: off
    duplex: half
    speeds:
      - 10

- name: >
    Configure Interface 1/1/2 - advertise only 100 Mbps and 1000 Mbps speeds
    and duplex auto-negotiation.
  aoscx_interface:
    name: 1/1/2
    configure_speed: true
    autoneg: on
    speeds:
      - 100
      - 1000

- name: Configure Interface 1/1/2 - speeds and duplex auto-negotiation.
  aoscx_interface:
    name: 1/1/2
    configure_speed: true
    autoneg: on

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
    name: 1/1/3
    qos_trust_mode: global

- name: Set a Queue Profile for interface 1/1/2
  aoscx_interface:
    name: 1/1/2
    queue_profile: STRICT-PROFILE

- name: Set interface 1/1/3 to use global Queue Profile
  aoscx_interface:
    name: 1/1/3
    use_global_queue_profile: true

- name: Configure Schedule Profile on an interface 1/1/17
  aoscx_interface:
    name: 1/1/17
    qos: STRICT

- name: Remove a Schedule Profile from an interface 1/1/17
  aoscx_interface:
    name: 1/1/17
    no_qos: true

- name: Set the QoS rate to the 1/1/17 Interface
  aoscx_interface:
    name: 1/1/17
    qos_rate:
      broadcast: 200pps
      unknown_unicast: 100kbps
      multicast: 200pps

- name: Configure Interface 1/1/2 - enable vsx-sync features
  aoscx_interface:
    name: 1/1/2
    vsx_sync:
      - acl
      - irdp
      - qos
      - rate_limits
      - vlan
      - vsx_virtual

- name: Set the MTU to the 1/1/17 Interface
  aoscx_interface:
    name: 1/1/17
    mtu: 1300
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device
    from pyaoscx.interface import Interface
    from pyaoscx.utils import util as utils

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "name": {
            "type": "str",
            "required": True,
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
        "configure_speed": {
            "type": "bool",
            "required": False,
            "default": False,
        },
        "autoneg": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "mtu": {
            "type": "int",
            "required": False,
        },
        "duplex": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["full", "half"],
        },
        "speeds": {
            "type": "list",
            "elements": "int",
            "required": False,
            "default": None,
        },
        "acl_name": {"type": "str", "required": False},
        "acl_type": {
            "type": "str",
            "required": False,
            "choices": ["ipv4", "ipv6", "mac"],
        },
        "acl_direction": {
            "type": "str",
            "choices": ["in", "out", "routed-in", "routed-out"],
        },
        "vsx_sync": {
            "type": "list",
            "elements": "str",
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
        "pause": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "eee": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "error_control": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["auto", "none", "base-r-fec", "rs-fec"],
        },
        "speed_downshift": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "udld_enable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "udld_interval": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "udld_retries": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "loop_protect_enable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "loop_protect_action": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["do-not-disable", "tx-disable", "tx-rx-disable"],
        },
        "urpf_check": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["disable", "loose", "strict"],
        },
        "ip_mtu": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "sflow_enabled": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "arp_inspection_trust": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "dhcpv4_snooping_trust": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "dhcpv4_snooping_max_bindings": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "dhcpv6_snooping_trust": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "dhcpv6_snooping_max_bindings": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "pvlan_port_type": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["promiscuous", "secondary", ""],
        },
        "qos_rate": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "unknown_unicast": {
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
        mutually_exclusive=[
            ("qos", "no_qos"),
            ("queue_profile", "use_global_queue_profile"),
        ],
        required_if=[
            ("configure_speed", True, ("autoneg",), False),
            ("autoneg", "off", ("duplex", "speeds"), False),
        ],
        required_together=[["acl_name", "acl_type", "acl_direction"]],
    )

    result = dict(changed=False)

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
    vsx_sync = ansible_module.params["vsx_sync"]
    state = ansible_module.params["state"]
    mtu = ansible_module.params["mtu"]
    acl_name = ansible_module.params["acl_name"]
    acl_type = ansible_module.params["acl_type"]
    acl_direction = ansible_module.params["acl_direction"]
    qos = ansible_module.params["qos"]
    no_qos = ansible_module.params["no_qos"]
    queue_profile = ansible_module.params["queue_profile"]
    use_global_queue_profile = ansible_module.params["use_global_queue_profile"]
    qos_trust_mode = ansible_module.params["qos_trust_mode"]
    qos_rate = ansible_module.params["qos_rate"]

    pause = ansible_module.params["pause"]
    eee = ansible_module.params["eee"]
    error_control = ansible_module.params["error_control"]
    speed_downshift = ansible_module.params["speed_downshift"]
    udld_enable = ansible_module.params["udld_enable"]
    udld_interval = ansible_module.params["udld_interval"]
    udld_retries = ansible_module.params["udld_retries"]
    loop_protect_enable = ansible_module.params["loop_protect_enable"]
    loop_protect_action = ansible_module.params["loop_protect_action"]
    urpf_check = ansible_module.params["urpf_check"]
    ip_mtu = ansible_module.params["ip_mtu"]
    sflow_enabled = ansible_module.params["sflow_enabled"]
    arp_inspection_trust = ansible_module.params["arp_inspection_trust"]
    dhcpv4_snooping_trust = ansible_module.params["dhcpv4_snooping_trust"]
    dhcpv4_snooping_max_bindings = ansible_module.params[
        "dhcpv4_snooping_max_bindings"
    ]
    dhcpv6_snooping_trust = ansible_module.params["dhcpv6_snooping_trust"]
    dhcpv6_snooping_max_bindings = ansible_module.params[
        "dhcpv6_snooping_max_bindings"
    ]
    pvlan_port_type = ansible_module.params["pvlan_port_type"]

    configure_speed = ansible_module.params["configure_speed"]
    autoneg = ansible_module.params["autoneg"]
    duplex = ansible_module.params["duplex"]
    speeds = ansible_module.params["speeds"]

    session = get_pyaoscx_session(ansible_module)
    device = Device(session)

    interface = device.interface(name)
    modified = interface.modified

    if state == "delete" and not configure_speed and not acl_type:
        is_special_type = interface.type in [
            "lag",
            "loopback",
            "tunnel",
            "vlan",
            "vxlan",
        ]
        if is_special_type:
            # report only if created before this run
            interface.delete()
            result["changed"] = not modified
        else:
            # physical interfaces cannot be deleted, in this case default
            # values are loaded
            prev_intf_attrs = utils.get_attrs(interface, interface.config_attrs)
            interface.delete()
            interface = Interface(session, name)
            interface.get()
            curr_intf_attrs = utils.get_attrs(interface, interface.config_attrs)
            # interfaces list members in dictionary are pointers to Interface
            # objects, so they are converted to str value to avoid false
            # negatives
            prev_intf_attrs["interfaces"] = list(
                map(str, prev_intf_attrs["interfaces"])
            )
            curr_intf_attrs["interfaces"] = list(
                map(str, curr_intf_attrs["interfaces"])
            )

            # need to compare if there are any changes after deleting
            result["changed"] = prev_intf_attrs != curr_intf_attrs
        ansible_module.exit_json(**result)

    if description:
        interface.description = description
    if enabled is not None:
        interface.admin_state = "up" if enabled else "down"
    if mtu:
        interface.mtu = mtu
    # Physical user_config attributes
    user_cfg = {
        "pause": pause,
        "eee": eee,
        "error_control": error_control,
        "speed_downshift": speed_downshift,
    }
    for key, val in user_cfg.items():
        if val is not None:
            if not isinstance(interface.user_config, dict):
                interface.user_config = {}
            interface.user_config[key] = val
    # sFlow per-interface enable lives in the other_config dict.
    if sflow_enabled is not None:
        if not isinstance(interface.other_config, dict):
            interface.other_config = {}
        interface.other_config["sflow-enabled"] = sflow_enabled
        if "other_config" not in interface.config_attrs:
            interface.config_attrs.append("other_config")
    # ARP inspection and DHCP snooping trust live in nested dicts.
    nested_updates = {
        "arp_inspection": {"trust": arp_inspection_trust},
        "dhcpv4_snooping_configuration": {
            "trusted": dhcpv4_snooping_trust,
            "max_bindings": dhcpv4_snooping_max_bindings,
        },
        "dhcpv6_snooping_configuration": {
            "trusted": dhcpv6_snooping_trust,
            "max_bindings": dhcpv6_snooping_max_bindings,
        },
    }
    for target, updates in nested_updates.items():
        wanted = {k: v for k, v in updates.items() if v is not None}
        if not wanted:
            continue
        if not isinstance(getattr(interface, target, None), dict):
            setattr(interface, target, {})
        current = getattr(interface, target)
        for key, value in wanted.items():
            current[key] = value
        if target not in interface.config_attrs:
            interface.config_attrs.append(target)
    # Top-level attributes
    top_level = {
        "udld_enable": udld_enable,
        "udld_interval": udld_interval,
        "udld_retries": udld_retries,
        "loop_protect_enable": loop_protect_enable,
        "loop_protect_action": loop_protect_action,
        "urpf_check": urpf_check,
        "ip_mtu": ip_mtu,
    }
    for key, val in top_level.items():
        if val is not None:
            setattr(interface, key, val)
            if key not in interface.config_attrs:
                interface.config_attrs.append(key)
    # Private VLAN port type: an empty string clears it (sent as null).
    if pvlan_port_type is not None:
        new_pvlan_port_type = (
            None if pvlan_port_type == "" else pvlan_port_type
        )
        if getattr(interface, "pvlan_port_type", None) != new_pvlan_port_type:
            interface.pvlan_port_type = new_pvlan_port_type
            if "pvlan_port_type" not in interface.config_attrs:
                interface.config_attrs.append("pvlan_port_type")
    if vsx_sync:
        if not device.materialized:
            device.get()
        if not device.vsx_capable():
            ansible_module.fail_json(msg="Device doesn't support VSX")
        clean_vsx_features = [
            vsx_sync_features_mapping(feature) for feature in vsx_sync
        ]
        interface.vsx_sync = clean_vsx_features

    modified |= interface.apply()
    if acl_type:
        if state == "delete":
            try:
                modified |= interface.clear_acl(acl_type, acl_direction)
            except Exception as e:
                ansible_module.fail_json(msg=str(e))
        else:
            try:
                modified |= interface.set_acl(acl_name, acl_type, acl_direction)
            except Exception as e:
                ansible_module.fail_json(msg=str(e))
    if configure_speed:
        # Ansible detects on/off as True/False, so we accept the boolean, and
        # convert to the str, which is what the REST API accepts
        if state == "delete":
            if speeds:
                del interface.user_config["speeds"]
                modified |= interface.apply()
            if duplex:
                del interface.user_config["duplex"]
                modified |= interface.apply()
            if (speeds and duplex) or autoneg:
                del interface.user_config["autoneg"]
                modified |= interface.apply()
        else:
            autoneg = "on" if autoneg else "off"
            _user_config = {"autoneg": autoneg}
            if speeds and duplex:
                _user_config["autoneg"] = "off"
            modified |= (
                "autoneg" not in interface.user_config
                or interface.user_config["autoneg"] != autoneg
            )

            status_int = Interface(session, name)
            status_int.get(selector="status")

            if speeds:
                _user_config["speeds"] = speeds
                playbook_speeds = set(speeds)
                if "speeds" in interface.user_config:
                    sw_str_speeds = interface.user_config["speeds"]
                    switch_speeds = set(
                        [int(s) for s in sw_str_speeds.split(",")]
                    )
                    modified |= switch_speeds != playbook_speeds
                else:
                    modified = True

            if duplex:
                _user_config["duplex"] = duplex
                modified |= (
                    "duplex" not in interface.user_config
                    or interface.user_config["duplex"] != duplex
                )

            if "forced_speeds" not in status_int.hw_intf_info:
                ansible_module.warn(
                    (
                        "Interface {0} might not support the combination of "
                        "speeds/duplex configured, check your hardware specifications "
                        "and/or CLI to make sure."
                    ).format(name)
                )
            try:
                interface.configure_speed_duplex(**_user_config)
            except Exception as exc:
                ansible_module.fail_json(msg=str(exc))

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
        if "unknown_unicast" in qos_rate:
            _unknown_unicast = qos_rate.pop("unknown_unicast")
            qos_rate["unknown-unicast"] = _unknown_unicast
        modified |= interface.update_interface_qos_rate(qos_rate)

    result["changed"] = modified
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
