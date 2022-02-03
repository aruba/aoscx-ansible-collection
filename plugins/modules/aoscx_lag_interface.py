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
    description: List of interfaces in the LAG
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
  multi_chassis:
    description: >
      Option to specify whether the LAG is an MCLAG. This option is mutually
      exclusive with the `lacp_mode` option. As an MCLAG forces the lacp_mode
      to `active`.
    type: bool
    required: false
    default: false
  lacp_fallback:
    description: >
      Enable LACP fallback mode, specified only for multi-chassis LAG.
    type: bool
    required: false
    default: false
  static_multi_chassis:
    description: >
      Whether the MCLAG is static. Ignored if `multi_chassis` is not specified.
    type: bool
    required: false
  state:
    description: Create, Update or Delete the Interface.
    type: str
    default: create
    choices:
      - create
      - update
      - override
      - delete
    required: false
"""

EXAMPLES = """
- name: Create LAG Interface 1.
  aoscx_lag_interface:
    name: lag1

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

try:
    from pyaoscx.vlan import Vlan

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
            "default": "create",
            "choices": ["create", "update", "override", "delete"],
        },
        "name": {
            "type": "str",
            "required": True,
        },
        "interfaces": {
            "type": "list",
            "elements": "str",
            "required": False,
            "default": None,
        },
        "lacp_mode": {
            "type": "str",
            "choices": ["active", "passive", "disabled"],
            "required": False,
            "default": None,
        },
        "multi_chassis": {
            "type": "bool",
            "required": False,
            "default": False,
        },
        "lacp_fallback": {
            "type": "bool",
            "required": False,
            "default": False,
        },
        "static_multi_chassis": {
            "type": "bool",
            "required": False,
            "default": None,
        },
    }
    return argument_spec


def get_lacp_mode(lacp_mode):
    if lacp_mode == "disabled":
        return None
    return lacp_mode


def remove_interfaces_from_lag(_ints):
    for _int in _ints:
        if (
            hasattr(_int, "other_config")
            and "lacp-aggregation-key" in _int.other_config
        ):
            del _int.other_config["lacp-aggregation-key"]
            _int.update()


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        mutually_exclusive=[("multi_chassis", "lacp_mode")],
    )

    result = {"changed": False}

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    _params = ansible_module.params.copy()
    name = _params["name"]
    interfaces = _params["interfaces"]
    lacp_mode = _params["lacp_mode"]
    multi_chassis = _params["multi_chassis"]
    lacp_fallback = _params["lacp_fallback"]
    static_multi_chassis = _params["static_multi_chassis"]
    state = _params["state"]

    session = get_pyaoscx_session(ansible_module)

    Interface = session.api.get_module_class(session, "Interface")
    existing_interfaces = Interface.get_all(session)
    # Checking that it exists must be done this way to avoid creating when
    # using state == "delete"
    exists = name in existing_interfaces

    lag = Interface(session, name)

    if state == "delete":
        if exists:
            lag.get()
            remove_interfaces_from_lag(lag.interfaces)
            lag.delete()
        result["changed"] |= exists
        ansible_module.exit_json(**result)

    if exists:
        lag.get()
    else:
        try:
            lag.create()
        except Exception as exc:
            ansible_module.fail_json(
                msg="Could not create LAG Interface, exc: {0}".format(exc)
            )

    result["changed"] |= not exists

    if exists:
        _is_mclag = (
            "mclag_enabled" in lag.other_config
            and lag.other_config["mclag_enabled"] is True
        )
        _is_not_mclag = (
            "mclag_enabled" not in lag.other_config
            or lag.other_config["mclag_enabled"] is False
        )
        _is_static_mclag = _is_mclag and lag.lacp is None
        _is_mclag_negated = not _is_mclag

        _msg = None
        if multi_chassis and (_is_not_mclag or _is_mclag_negated):
            _msg = "LAG exists, cannot be configured as multi-chassis"
        if (
            multi_chassis != _is_mclag
            or static_multi_chassis is not None
            and static_multi_chassis != _is_static_mclag
        ):
            _msg = (
                "The specified multi-chassis LAG exists with a different type"
                ", to change the type, the MCLAG must first be removed."
            )
        result["msg"] = _msg
        if _msg:
            ansible_module.fail_json(**result)

    if lacp_mode:
        _new_lacp_mode = get_lacp_mode(lacp_mode)
        lacp_mode_change = _new_lacp_mode != lag.lacp
        result["changed"] = lacp_mode_change
        lag.lacp = _new_lacp_mode

    if multi_chassis:
        lag.other_config["mclag_enabled"] = True
        # boolean must be explicitly compared to None
        if lacp_fallback is not None:
            result["changed"] |= (
                "lacp-fallback" not in lag.other_config
                or lag.other_config["lacp-fallback"] != lacp_fallback
            )
            lag.other_config["lacp-fallback"] = lacp_fallback

        if not exists:
            # Taken from CLI's default behavior
            lag.routing = False

            status_lag = Interface(session, name)
            status_lag.get(selector="status")

            lag.vlan_mode = "access"

            _prev_vlan_tag = status_lag.applied_vlan_tag
            # possibly unneeded fallback
            _vlan_tag_id = 1
            if _prev_vlan_tag:
                _vlan_tag_id = next(iter(status_lag.applied_vlan_tag))
            lag.vlan_tag = Vlan(session, _vlan_tag_id)

            if not static_multi_chassis:
                _new_lacp_mode = "active"
                _new_lacp_mode = get_lacp_mode(_new_lacp_mode)
                if exists and lag.lacp != _new_lacp_mode:
                    _msg = "Cannot change LACP mode for a static MCLAG"
                    result["msg"] = _msg
                    ansible_module.fail_json(**result)
                # Taken from CLI's default behavior
                lag.lacp = _new_lacp_mode

    # explicitly check None because an empty list is a valid argument value
    if interfaces is not None:
        _prev_ints = {i.name: i for i in lag.interfaces}
        _prev_ints_idx = list(_prev_ints)
        _incoming_ints_idx = interfaces
        _kept_ints_idx = set(_prev_ints_idx) & set(_incoming_ints_idx)
        _kept_ints = {k: _prev_ints[k] for k in _kept_ints_idx}
        _deleted_ints_idx = sorted(
            list(set(_prev_ints_idx) - set(_incoming_ints_idx))
        )
        _deleted_ints = {k: _prev_ints[k] for k in _deleted_ints_idx}

        _new_ints_idx = set(_incoming_ints_idx) - set(_kept_ints_idx)

        _new_ints = _kept_ints
        for i in _new_ints_idx:
            _int = Interface(session, i)
            _int.get()
            _new_ints.update({i: _int})

        if state == "override":
            remove_interfaces_from_lag(_deleted_ints.values())
        else:
            _new_ints.update(_deleted_ints)

        _final_interfaces = [] if not _new_ints else list(_new_ints.values())
        lag.interfaces = _final_interfaces
        result["changed"] |= set(_prev_ints_idx) != set(_new_ints)

    if result["changed"]:
        lag.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
