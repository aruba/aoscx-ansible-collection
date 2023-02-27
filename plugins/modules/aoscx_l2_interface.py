#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_l2_interface
version_added: "2.8.0"
short_description: >
  Create or Update or Delete Layer2 Interface configuration on AOS-CX.
description: >
  This modules provides configuration management of Layer2 Interfaces on AOS-CX
  devices, including Port Security features. For platform 8360, Port Security
  is supported from REST v10.09 upwards.
author: Aruba Networks (@ArubaNetworks)
options:
  interface:
    description: >
      Interface name, should be in the format chassis/slot/port, i.e. 1/2/3,
      1/1/32. Please note, if the interface is a Layer3 interface in the
      existing configuration and the user wants to change the interface to be
      Layer2, the user must delete the L3 interface then recreate the interface
      as a Layer2.
    type: str
    required: true
  description:
    description: Description of interface.
    type: str
    required: false
  vlan_mode:
    description: VLAN mode on interface, access or trunk.
    choices:
      - access
      - trunk
    required: false
    type: str
  vlan_access:
    description: Access VLAN ID, vlan_mode must be set to access.
    required: false
    type: str
  vlan_trunks:
    description: List of trunk VLAN IDs, vlan_mode must be set to trunk.
    required: false
    type: list
    elements: str
  trunk_allowed_all:
    description: >
      Flag for vlan trunk allowed all on L2 interface, vlan_mode must be set to
      trunk.
    required: false
    type: bool
  native_vlan_id:
    description: VLAN trunk native VLAN ID, vlan_mode must be set to trunk.
    required: false
    type: str
  native_vlan_tag:
    description: >
      Flag for accepting only tagged packets on VLAN trunk native, vlan_mode
      must be set to trunk.
    required: false
    type: bool
  interface_qos_schedule_profile:
    description: >
      Attaching existing QoS schedule profile to interface. *This parameter is
      deprecated and will be removed in a future version.
    type: dict
    required: false
  interface_qos_rate:
    description: >
      The rate limit value configured for broadcast/multicast/unknown unicast
      traffic. Dictionary should have the format <type_of_traffic>: <speed>.
      e.g. unknown-unicast: 100pps
           broadcast: 200kbps
           multicast: 200pps
    type: dict
    required: false
  state:
    description: Create, Update, or Delete Layer2 Interface.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
  port_security_enable:
    description: Enable port security in this interface (aoscx connection).
    type: bool
    required: false
  port_security_client_limit:
    description: >
      Maximum amount of MACs allowed in the interface (aoscx connection). Only
      valid when port_security is enabled.
    type: int
    required: false
  port_security_sticky_learning:
    description: >
      Enable sticky MAC learning (aoscx connection). Only valid when
      port_security is enabled.
    type: bool
    required: false
  port_security_macs:
    description: >
      List of allowed MAC addresses (aoscx connection). Only valid when
      port_security is enabled.
    type: list
    elements: str
    required: false
  port_security_sticky_macs:
    description: >
      Configure the sticky MAC addresses for the interface (aoscx connection).
      Only valid when port_security is enabled.
    type: list
    required: false
    elements: dict
    suboptions:
      mac:
        description: a mac address.
        type: str
        required: true
      vlans:
        description: a list of VLAN IDs.
        type: list
        elements: int
        required: true
  port_security_violation_action:
    description: >
      Action to perform when a violation is detected (aoscx connection). Only
      valid when port_security is enabled.
    type: str
    choices:
      - notify
      - shutdown
    required: false
  port_security_recovery_time:
    description: >
      Time in seconds to wait for recovery after a violation (aoscx
      connection). Only valid when port_security is enabled.
    type: int
    required: false
"""

EXAMPLES = """
- name: Configure Interface 1/1/13 - set allowed MAC address
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_macs:
      - AA:BB:CC:DD:EE:FF

- name: >
    Configure Interface 1/1/13 - retain an allowed mac address by changing its
    setting to sticky mac.
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_sticky_learning: true
    port_security_sticky_macs:
      - mac: AA:BB:CC:DD:EE:FF
        vlans:
          - 1
          - 2
          - 3

- name: >
    Configure Interface 1/1/13 - retain an allowed mac address by changing its
    setting to sticky mac.
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_sticky_learning: true
    port_security_sticky_macs:
      - mac: AA:BB:CC:DD:EE:FF
        vlans: []

- name: >
    Configure Interface 1/1/13 - set intrusion action to disable the interface
    if it identifies a MAC address that is not on the allow list.
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_violation_action: shutdown
    port_security_recovery_time: 60

- name: >
    Configure Interface 1/1/13 - set port security to dynamically add the first
    8 addresses it sees to the allowed MAC address list.
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_client_limit: 8
    port_security_sticky_learning: true

- name: >
    Configure Interface 1/1/3 - enable port security for a total of 10 MAC
    addresses with sticky MAC learning, and two user set MAC addresses.
  aoscx_l2_interface:
    interface: 1/1/3
    port_security_enable: true
    port_security_client_limit: 10
    port_security_sticky_learning: true
    port_security_macs:
      - 11:22:33:44:55:66
      - AA:BB:CC:DD:EE:FF

- name: >
    Configure Interface 1/1/13 - remove allowed MAC address AA:BB:CC:DD:EE:FF
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_macs:
      - AA:BB:CC:DD:EE:FF
    state: delete

- name: Configure Interface 1/1/13 - delete configuration of client limit.
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_client_limit: 2
    state: delete

- name: >
    Configure Interface 1/1/13 - delete configuration of recovery time.
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_recovery_time: 60
    state: delete

- name: Configure Interface 1/1/13 - disable port security.
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: false

- name: >
    Configure Interface 1/1/2 - enable interface and vsx-sync features
    IMPORTANT NOTE: the aoscx_interface module is needed to enable the
    interface and set the VSX features to be synced.
  aoscx_interface:
    name: 1/1/2
    enabled: true
    vsx_sync:
      - acl
      - irdp
      - qos
      - rate_limits
      - vlan
      - vsx_virtual

- name: Configure Interface 1/1/3 - vlan trunk allowed all
  aoscx_l2_interface:
    interface: 1/1/3
    vlan_mode: trunk
    trunk_allowed_all: true

- name: Delete Interface 1/1/3
  aoscx_l2_interface:
    interface: 1/1/3
    state: delete

- name: Configure Interface 1/1/1 - vlan trunk allowed 200
  aoscx_l2_interface:
    interface: 1/1/1
    vlan_mode: trunk
    vlan_trunks: 200

- name: Configure Interface 1/1/1 - vlan trunk allowed 200,300
  aoscx_l2_interface:
    interface: 1/1/1
    vlan_mode: trunk
    vlan_trunks:
      - 200
      - 300

- name: >
    Configure Interface 1/1/1 - vlan trunks allowed 200, 300, vlan trunk native
    200.
  aoscx_l2_interface:
    interface: 1/1/3
    vlan_mode: trunk
    vlan_trunks:
      - 200
      - 300
    native_vlan_id: '200'

- name: Configure Interface 1/1/4 - vlan access 200
  aoscx_l2_interface:
    interface: 1/1/4
    vlan_mode: access
    vlan_access: '200'
- name: >
    Configure Interface 1/1/5 - vlan trunk allowed all, vlan trunk native 200
    tag.
  aoscx_l2_interface:
    interface: 1/1/5
    vlan_mode: trunk
    trunk_allowed_all: true
    native_vlan_id: '200'
    native_vlan_tag: true

- name: >
    Configure Interface 1/1/6 - vlan trunk allowed all, vlan trunk native 200.
  aoscx_l2_interface:
    interface: 1/1/6
    vlan_mode: trunk
    trunk_allowed_all: true
    native_vlan_id: '200'
"""

RETURN = r""" # """


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def get_argument_spec():
    module_args = {
        "state": {
            "type": "str",
            "default": "create",
            "choices": ["create", "delete", "update"],
        },
        "interface": {
            "type": "str",
            "required": True,
        },
        "description": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "vlan_mode": {
            "type": "str",
            "default": None,
            "required": False,
            "choices": ["access", "trunk"],
        },
        "vlan_access": {
            "type": "str",
            "default": None,
            "required": False,
        },
        "vlan_trunks": {
            "type": "list",
            "elements": "str",
            "default": None,
            "required": False,
        },
        "trunk_allowed_all": {
            "type": "bool",
            "default": None,
            "required": False,
        },
        "native_vlan_id": {
            "type": "str",
            "default": None,
            "required": False,
        },
        "native_vlan_tag": {
            "type": "bool",
            "default": None,
            "required": False,
        },
        "interface_qos_schedule_profile": {
            "type": "dict",
            "default": None,
            "required": False,
        },
        "interface_qos_rate": {
            "type": "dict",
            "default": None,
            "required": False,
        },
        "port_security_enable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "port_security_client_limit": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "port_security_sticky_learning": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "port_security_macs": {
            "type": "list",
            "elements": "str",
            "required": False,
            "default": None,
        },
        "port_security_sticky_macs": {
            "type": "list",
            "elements": "dict",
            "required": False,
            "default": None,
            "options": {
                "mac": {"type": "str", "required": True},
                "vlans": {
                    "type": "list",
                    "elements": "int",
                    "required": True,
                },
            },
        },
        "port_security_violation_action": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["notify", "shutdown"],
        },
        "port_security_recovery_time": {
            "type": "int",
            "required": False,
            "default": None,
        },
    }
    return module_args


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(), supports_check_mode=True
    )

    interface_name = ansible_module.params["interface"]
    description = ansible_module.params["description"]
    vlan_mode = ansible_module.params["vlan_mode"]
    vlan_access = ansible_module.params["vlan_access"]
    vlan_trunks = ansible_module.params["vlan_trunks"]
    trunk_allowed_all = ansible_module.params["trunk_allowed_all"]
    native_vlan_id = ansible_module.params["native_vlan_id"]
    native_vlan_tag = ansible_module.params["native_vlan_tag"]
    state = ansible_module.params["state"]
    port_security_enable = ansible_module.params["port_security_enable"]
    port_security_client_limit = ansible_module.params[
        "port_security_client_limit"
    ]
    port_security_sticky_learning = ansible_module.params[
        "port_security_sticky_learning"
    ]
    port_security_macs = ansible_module.params["port_security_macs"]
    port_security_sticky_macs = ansible_module.params[
        "port_security_sticky_macs"
    ]
    port_security_violation_action = ansible_module.params[
        "port_security_violation_action"
    ]
    port_security_recovery_time = ansible_module.params[
        "port_security_recovery_time"
    ]

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        from pyaoscx.device import Device
    except Exception as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    device = Device(session)
    if state == "delete" and port_security_enable is None:
        interface = device.interface(interface_name)
        interface.delete()

        result["changed"] = True
        ansible_module.exit_json(**result)
    vlan_tag = None
    if vlan_access is not None:
        vlan_tag = vlan_access
    elif native_vlan_id is not None:
        vlan_tag = native_vlan_id

    if isinstance(vlan_tag, str):
        vlan_tag = int(vlan_tag)

    interface = device.interface(interface_name)
    if interface.was_modified():
        result["changed"] = True
    modified_op = interface.configure_l2(
        description=description,
        vlan_mode=vlan_mode,
        vlan_tag=vlan_tag,
        vlan_ids_list=vlan_trunks,
        trunk_allowed_all=trunk_allowed_all,
        native_vlan_tag=native_vlan_tag,
    )

    if port_security_enable is not None and not port_security_enable:
        modified_op |= interface.port_security_disable()
    if port_security_enable or (
        hasattr(interface, "port_security")
        and interface.port_security["enable"]
    ):
        port_sec_kw = {}
        if state == "delete":
            if port_security_client_limit:
                port_sec_kw["client_limit"] = 1
            if port_security_sticky_learning is not None:
                port_sec_kw["sticky_mac_learning"] = False
            if port_security_macs:
                for mac in port_security_macs:
                    mac = mac.upper()
                    sw_static_macs = (
                        interface.port_security_static_client_mac_addr
                    )
                    if mac in sw_static_macs:
                        sw_static_macs.remove(mac)
                        modified_op |= interface.apply()
                    else:
                        ansible_module.fail_json(
                            msg="MAC address {0} is not configured".format(
                                mac
                            )
                        )
            if port_security_sticky_macs:
                for sticky_mac in port_security_sticky_macs:
                    mac = sticky_mac["mac"]
                    sw_sticky_macs = (
                        interface.port_security_static_sticky_client_mac_addr
                    )
                    sw_sticky_mac_vlans = sw_sticky_macs[mac]
                    if mac in sw_sticky_macs:
                        for vlan in sticky_mac["vlans"]:
                            if vlan in sw_sticky_mac_vlans:
                                sw_sticky_mac_vlans.remove(vlan)
                        if sw_sticky_mac_vlans == []:
                            del sw_sticky_macs[mac]
                    else:
                        ansible_module.fail_json(
                            msg="MAC address {0} is not configured".format(
                                mac
                            )
                        )
                modified_op |= interface.apply()
            if port_security_violation_action:
                port_sec_kw["violation_action"] = "notify"
            if port_security_recovery_time:
                port_sec_kw["violation_recovery_time"] = 10
        else:
            if port_security_client_limit:
                port_sec_kw["client_limit"] = port_security_client_limit
            if port_security_sticky_learning is not None:
                port_sec_kw[
                    "sticky_mac_learning"
                ] = port_security_sticky_learning
            if port_security_macs:
                port_sec_kw["allowed_mac_addr"] = port_security_macs
            if port_security_sticky_macs:
                converted_sticky_macs = {
                    el["mac"]: el["vlans"]
                    for el in port_security_sticky_macs
                }
                port_sec_kw[
                    "allowed_sticky_mac_addr"
                ] = converted_sticky_macs
            if port_security_violation_action:
                port_sec_kw[
                    "violation_action"
                ] = port_security_violation_action
            if port_security_recovery_time:
                port_sec_kw[
                    "violation_recovery_time"
                ] = port_security_recovery_time
        _result = False
        try:
            _result = interface.port_security_enable(**port_sec_kw)
        except Exception as exc:
            ansible_module.fail_json(msg=str(exc))

        modified_op |= _result
    if modified_op:
        result["changed"] = True

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
