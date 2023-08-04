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
module: aoscx_lag_interface
version_added: "4.1.0"
short_description: Module for configuring LAG Interfaces in AOS-CX switches.
description: >
  This module provides the functionality for configuring LAG Interfaces on
  AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      LAG Interface Name, the ID portion should be no lower than 1. Check your
      hardware specifications for its limitations. example: lag1, or lag256.
    type: str
    required: true
  interfaces:
    description: >
      List of interfaces in the LAG. Each interface added to a LAG interface
      will inherit the LAG manager state of the LAG, wether it is "up" or
      "down".
    type: list
    elements: str
    required: false
  lacp_mode:
    description: >
      Configures Link Aggregation Control Procotol (LACP) mode on this
      interface, `active` ports are allowed to initiate LACP negotiations.
      `passive` ports can participate in LACP negotiations initiated
      by a remote switch, but not initiate such negotiations. If
      LACP is enabled on a port whose partner switch does not support LACP, the
      bond will be disabled. Defaults to disabled.
    type: str
    choices:
      - active
      - passive
      - disabled
    required: false
  lacp_rate:
    description: >
      Configures Link Aggregation Control Protocol (LACP) rate on this
      Interface, by default LACP rate is `slow` and LAPCDUs will be sent
      every 30 seconds; if LACP rate is `fast` LACPDUs will be sent every
      second.
      This value can not be set if lacp mode is disabled.
    type: str
    choices:
      - slow
      - fast
  multi_chassis:
    description: >
      Option to specify whether the LAG is an MCLAG. This option is mutually
      exclusive with the `lacp_mode` option. As an MCLAG forces the lacp_mode
      to `active`.
    type: bool
    required: false
  lacp_fallback:
    description: >
      Enable LACP fallback mode, specified only for multi-chassis LAG.
    type: bool
    required: false
  static_multi_chassis:
    description: >
      Whether the MCLAG is static. Ignored if `multi_chassis` is not specified.
    type: bool
    required: false
  state:
    description: >
      Create, Update or Delete the Interface. After that a physical interface
      is removed from a LAG, interface will be shutdown (admin state in down).
      LAG interface
    type: str
    default: create
    choices:
      - create
      - update
      - delete
    required: false
"""

EXAMPLES = """
- name: Create LAG Interface 1.
  aoscx_lag_interface:
    name: lag1

- name: Set LAG 1 as dynamic.
  aoscx_lag_interface:
    name: lag1
    lacp_mode: active
    lacp_rate: fast

- name: Set 6 interfaces to LAG Interface 1.
  aoscx_lag_interface:
    state: update
    name: lag1
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3
      - 1/1/4
      - 1/1/5
      - 1/1/6

- name: Set 3 interfaces to LAG Interface 1.
  aoscx_lag_interface:
    state: override
    name: lag1
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3

- name: Create MCLAG Interface 64 with  3 interfaces.
  aoscx_lag_interface:
    state: create
    name: lag64
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3
    multi_chassis: true

- name: Create Static MCLAG Interface 32 with  3 interfaces.
  aoscx_lag_interface:
    state: create
    name: lag32
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3
    multi_chassis: true
    static_multi_chassis: true

- name: Remove all interfaces from LAG Interface 1.
  aoscx_lag_interface:
    state: override
    name: lag1
    interfaces: []

- name: Create MCLAG with LACP fallback mode set.
  aoscx_lag_interface:
    state: create
    name: lag256
    multi_chassis: true
    lacp_fallback: true

- name: Update static MCLAG, unset LACP fallback mode.
  aoscx_lag_interface:
    state: create
    name: lag256
    multi_chassis: true
    lacp_fallback: false

- name: Create static MCLAG with LACP fallback mode.
  aoscx_lag_interface:
    state: create
    name: lag2
    multi_chassis: true
    static_multi_chassis: true
    lacp_fallback: true

- name: Update static MCLAG, unset LACP fallback mode.
  aoscx_lag_interface:
    state: update
    name: lag256
    multi_chassis: true
    static_multi_chassis: true
    lacp_fallback: false

- name: Delete LAG Interface 128.
  aoscx_lag_interface:
    state: delete
    name: lag128
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def get_argument_spec():
    argument_spec = {
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
        "name": {
            "type": "str",
            "required": True,
        },
        "interfaces": {
            "type": "list",
            "elements": "str",
            "required": False,
        },
        "lacp_mode": {
            "type": "str",
            "choices": ["active", "passive", "disabled"],
            "required": False,
        },
        "lacp_rate": {
            "type": "str",
            "choices": ["slow", "fast"],
            "required": False,
        },
        "multi_chassis": {
            "type": "bool",
            "required": False,
        },
        "lacp_fallback": {
            "type": "bool",
            "required": False,
        },
        "static_multi_chassis": {
            "type": "bool",
            "required": False,
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        mutually_exclusive=[("multi_chassis", "lacp_mode")],
    )

    result = {"changed": False}

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    _params = ansible_module.params.copy()
    name = _params["name"]
    interfaces = _params["interfaces"]
    lacp_mode = _params["lacp_mode"]
    lacp_rate = _params["lacp_rate"]
    multi_chassis = _params["multi_chassis"]
    lacp_fallback = _params["lacp_fallback"]
    static_multi_chassis = _params["static_multi_chassis"]
    state = _params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(msg="Session error: {0}".format(e))

    Interface = session.api.get_module_class(session, "Interface")

    lag = Interface(session, name)
    try:
        lag.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete" and interfaces is None:
        if exists:
            lag.delete()
        result["changed"] |= exists
        ansible_module.exit_json(**result)

    if not exists:
        try:
            # MCLAG parameters must be set when the interface is created
            mc_lag = multi_chassis is not None and multi_chassis
            mclag_config = {"other_config": {"mclag_enabled": mc_lag}}
            # MCLAG is L2
            if mc_lag:
                mclag_config["routing"] = False
                mclag_config["vlan_mode"] = "access"
                vlan_id = session.api.get_module(session, "Vlan", 1)
                mclag_config["vlan_tag"] = vlan_id.get_info_format()
                if not static_multi_chassis:
                    mclag_config["lacp"] = "active"

            lag = Interface(session, name, **mclag_config)
            lag.create()
            result["changed"] = True
        except Exception as exc:
            ansible_module.fail_json(
                msg="Could not create LAG Interface, exc: {0}".format(exc)
            )

    _is_mclag = lag.other_config["mclag_enabled"] is True
    _is_static_mclag = _is_mclag and lag.lacp_mode == "disabled"
    if exists:
        if multi_chassis and not _is_mclag:
            _msg = "LAG exists, cannot be configured as multi-chassis"
            ansible_module.fail_json(msg=_msg)
        if (
            multi_chassis is not None
            and multi_chassis != _is_mclag
            or static_multi_chassis is not None
            and static_multi_chassis != _is_static_mclag
        ):
            _msg = (
                "The specified multi-chassis LAG exists with a different type"
                ", to change the type, the MCLAG must first be removed."
            )
            ansible_module.fail_json(msg=_msg)

    if lacp_mode and not _is_mclag:
        result["changed"] |= lacp_mode != lag.lacp_mode
        lag.lacp_mode = lacp_mode

    if lacp_rate:
        result["changed"] |= lacp_rate != lag.lacp_rate
        lag.lacp_rate = lacp_rate

    if lacp_fallback is not None:
        if lacp_fallback and _is_static_mclag:
            _msg = "Cannot enable LACP fallback on static MCLAG"
            ansible_module.fail_json(msg=_msg)
        elif lacp_fallback and not _is_mclag and lag.lacp_mode == "disabled":
            _msg = "Cannot enable LACP fallback on static LAG"
            ansible_module.fail_json(msg=_msg)
        elif _is_mclag:
            result["changed"] |= (
                "lacp-fallback" not in lag.other_config
                and lacp_fallback
                or "lacp-fallback" in lag.other_config
                and not lacp_fallback
            )
            if lacp_fallback:
                lag.other_config["lacp-fallback"] = lacp_fallback
            else:
                lag.other_config.pop("lacp-fallback", None)
        else:
            result["changed"] |= (
                "lacp-fallback-static" not in lag.other_config
                and lacp_fallback
                or "lacp-fallback-static" in lag.other_config
                and not lacp_fallback
            )
            if lacp_fallback:
                lag.other_config["lacp-fallback-static"] = lacp_fallback
            else:
                lag.other_config.pop("lacp-fallback-static", None)

    # explicitly check None because an empty list is a valid argument value
    if interfaces is not None:
        present = [i.name for i in lag.interfaces]
        if state == "delete":
            new_interfaces = list(set(present) - set(interfaces))
        else:
            new_interfaces = list(set(interfaces) | set(present))
        result["changed"] |= set(new_interfaces) != set(present)
        lag.interfaces = new_interfaces

    if result["changed"]:
        lag.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
