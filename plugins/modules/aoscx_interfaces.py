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
module: aoscx_interfaces
version_added: "4.6.0"
short_description: Create, Update or Delete the settings of several interfaces on AOS-CX
description: >
  This module configures a list of existing interfaces (physical ports, LAGs)
  on AOS-CX devices in a single task. It covers the settings of the
  aoscx_interface, aoscx_l2_interface, aoscx_interface_stp,
  aoscx_port_access_interface and aoscx_port_access_auth modules commonly
  used on access ports, and reuses one REST session for every interface,
  which is much faster than one task per interface and per feature. Only the
  supplied settings are managed; omitted settings are left unchanged. The
  interfaces must already exist. The dot1x and mac_auth settings require a
  pyaoscx release that ships the PortAccessAuthConfiguration class, and the
  port access settings require REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
options:
  interfaces:
    description: >
      List of interfaces to configure. With I(state) C(delete), every
      supplied setting is reset to its default value, whatever the value
      given.
    required: true
    type: list
    elements: dict
    suboptions:
      name:
        description: Name of the interface, for example C(1/1/1) or C(lag10).
        required: true
        type: str
      description:
        description: Description of the interface (C(description)).
        required: false
        type: str
      enabled:
        description: >
          Administrative state of the interface, C(true) for C(no shutdown).
        required: false
        type: bool
      mtu:
        description: MTU of the interface (C(mtu)).
        required: false
        type: int
      loop_protect_enable:
        description: Enable loop protection (C(loop-protect)).
        required: false
        type: bool
      app_recognition_enable:
        description: >
          Enable application recognition on the interface
          (C(app-recognition enable)).
        required: false
        type: bool
      vlan_mode:
        description: >
          Layer 2 mode of the interface (C(vlan access) or C(vlan trunk)).
          Setting it also disables routing on the interface (C(no routing)).
          Required by the other VLAN options.
        required: false
        type: str
        choices:
          - access
          - trunk
      vlan_access:
        description: >
          Access VLAN ID. When omitted with I(vlan_mode) C(access), the
          current access VLAN is left unchanged.
        required: false
        type: int
      vlan_trunks:
        description: >
          Trunk allowed VLAN IDs, I(vlan_mode) must be C(trunk). The supplied
          list replaces the current trunk VLANs (order does not matter).
        required: false
        type: list
        elements: int
      trunk_allowed_all:
        description: >
          Allow all VLANs on the trunk, I(vlan_mode) must be C(trunk).
          Mutually exclusive with I(vlan_trunks).
        required: false
        type: bool
      native_vlan_id:
        description: >
          Native VLAN ID of the trunk, I(vlan_mode) must be C(trunk). Defaults
          to VLAN 1 on the switch.
        required: false
        type: int
      native_vlan_tag:
        description: >
          Accept only tagged packets on the trunk native VLAN
          (C(vlan trunk native <id> tag)), I(vlan_mode) must be C(trunk).
        required: false
        type: bool
      stp:
        description: Spanning tree settings of the interface.
        required: false
        type: dict
        suboptions:
          admin_edge:
            description: Administrative edge port (C(spanning-tree port-type admin-edge)).
            required: false
            type: bool
          bpdu_guard:
            description: BPDU guard (C(spanning-tree bpdu-guard)).
            required: false
            type: bool
          bpdu_filter:
            description: BPDU filter (C(spanning-tree bpdu-filter)).
            required: false
            type: bool
          root_guard:
            description: Root guard (C(spanning-tree root-guard)).
            required: false
            type: bool
          loop_guard:
            description: Loop guard (C(spanning-tree loop-guard)).
            required: false
            type: bool
          tcn_guard:
            description: TCN guard (C(spanning-tree tcn-guard)).
            required: false
            type: bool
          link_type:
            description: Link type (C(spanning-tree link-type)).
            required: false
            type: str
            choices:
              - auto
              - point_to_point
              - shared
      port_access:
        description: Port access settings of the interface.
        required: false
        type: dict
        suboptions:
          concurrent_onboarding:
            description: >
              Concurrent onboarding
              (C(port-access onboarding-method concurrent enable)).
            required: false
            type: bool
          client_limit:
            description: >
              Maximum number of authenticated clients
              (C(aaa authentication port-access client-limit)).
            required: false
            type: int
          auth_mode:
            description: Port access authentication mode.
            required: false
            type: str
            choices:
              - client-mode
              - device-mode
              - proxy-mode
              - multi-domain
          allow_bpdu:
            description: >
              Protocol BPDUs allowed before authentication
              (C(aaa authentication port-access allow-cdp-bpdu) and
              C(allow-lldp-bpdu)). Order does not matter.
            required: false
            type: list
            elements: str
            choices:
              - cdp
              - lldp
          allow_flood_traffic:
            description: >
              Allow flood traffic before authentication
              (C(port-access allow-flood-traffic enable)).
            required: false
            type: bool
          client_ip_track:
            description: Client IP tracking (C(client track ip)).
            required: false
            type: dict
            suboptions:
              admin_state:
                description: Tracking state.
                required: false
                type: str
                choices:
                  - enable
                  - disable
                  - auto
              update_interval:
                description: Update interval in seconds.
                required: false
                type: int
              client_limit:
                description: Maximum number of tracked clients.
                required: false
                type: int
          device_fingerprint:
            description: >
              Device fingerprinting
              (C(client device-fingerprint apply-profile)).
            required: false
            type: dict
            suboptions:
              profile_name:
                description: Name of an existing device fingerprint profile.
                required: false
                type: str
              client_limit:
                description: Maximum number of fingerprinted clients.
                required: false
                type: int
      dot1x:
        description: >
          802.1X authenticator settings of the interface
          (C(aaa authentication port-access dot1x authenticator)). With
          I(state) C(delete) the whole 802.1X configuration of the interface
          is removed.
        required: false
        type: dict
        suboptions:
          auth_enable:
            description: Enable the authentication method (C(enable)).
            required: false
            type: bool
          reauth_enable:
            description: Periodic re-authentication (C(reauth)).
            required: false
            type: bool
          reauth_period:
            description: Re-authentication period in seconds.
            required: false
            type: int
          cached_reauth_enable:
            description: Cached re-authentication (C(cached-reauth)).
            required: false
            type: bool
          cached_reauth_period:
            description: Cached re-authentication period in seconds.
            required: false
            type: int
          eapol_timeout:
            description: EAPOL timeout in seconds (802.1X only).
            required: false
            type: int
          max_retries:
            description: Maximum number of authentication retries.
            required: false
            type: int
          max_requests:
            description: Maximum number of EAPOL requests (802.1X only).
            required: false
            type: int
          quiet_period:
            description: Quiet period in seconds.
            required: false
            type: int
          discovery_period:
            description: Discovery period in seconds (802.1X only).
            required: false
            type: int
      mac_auth:
        description: >
          MAC authentication settings of the interface
          (C(aaa authentication port-access mac-auth)), same options as
          I(dot1x). With I(state) C(delete) the whole MAC authentication
          configuration of the interface is removed.
        required: false
        type: dict
        suboptions:
          auth_enable:
            description: Enable the authentication method (C(enable)).
            required: false
            type: bool
          reauth_enable:
            description: Periodic re-authentication (C(reauth)).
            required: false
            type: bool
          reauth_period:
            description: Re-authentication period in seconds.
            required: false
            type: int
          cached_reauth_enable:
            description: Cached re-authentication (C(cached-reauth)).
            required: false
            type: bool
          cached_reauth_period:
            description: Cached re-authentication period in seconds.
            required: false
            type: int
          eapol_timeout:
            description: EAPOL timeout in seconds (802.1X only).
            required: false
            type: int
          max_retries:
            description: Maximum number of authentication retries.
            required: false
            type: int
          max_requests:
            description: Maximum number of EAPOL requests (802.1X only).
            required: false
            type: int
          quiet_period:
            description: Quiet period in seconds.
            required: false
            type: int
          discovery_period:
            description: Discovery period in seconds (802.1X only).
            required: false
            type: int
  state:
    description: >
      Configure (C(create) or C(update), same behaviour) the supplied
      settings, or reset them to their default value (C(delete)).
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Configure the access ports 1/1/1 to 1/1/48 in a single task
  aoscx_interfaces:
    interfaces: "{{ access_ports }}"
  vars:
    access_ports: >-
      {%- set ports = [] -%}
      {%- for n in range(1, 49) -%}
      {%-   set _ = ports.append(dict(access_port, name='1/1/' ~ n)) -%}
      {%- endfor -%}
      {{ ports }}
    access_port:
      description: colorless_port
      enabled: true
      vlan_mode: access
      vlan_access: 1
      stp:
        admin_edge: true
        bpdu_guard: true
      port_access:
        client_limit: 2
        allow_bpdu: [cdp, lldp]
      dot1x:
        auth_enable: true
        reauth_enable: true
        reauth_period: 86400
      mac_auth:
        auth_enable: true

- name: Configure a trunk uplink and an access port
  aoscx_interfaces:
    interfaces:
      - name: 1/1/49
        description: uplink
        vlan_mode: trunk
        native_vlan_id: 1
        vlan_trunks: [10, 20, 30]
      - name: 1/1/1
        vlan_mode: access
        vlan_access: 10

- name: Remove the 802.1X configuration and the description of two ports
  aoscx_interfaces:
    interfaces:
      - {name: 1/1/1, description: x, dot1x: {}}
      - {name: 1/1/2, description: x, dot1x: {}}
    state: delete
"""

RETURN = r"""
changed:
  description: Whether at least one interface was modified.
  returned: always
  type: bool
changed_interfaces:
  description: Names of the interfaces that were (or would be) modified.
  returned: always
  type: list
  elements: str
  sample: ["1/1/1", "1/1/2"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
    pyaoscx_error_message,
)

AUTH_OPTIONS = [
    "auth_enable",
    "reauth_enable",
    "reauth_period",
    "cached_reauth_enable",
    "cached_reauth_period",
    "eapol_timeout",
    "max_retries",
    "max_requests",
    "quiet_period",
    "discovery_period",
]

AUTH_METHODS = {"dot1x": "dot1x", "mac_auth": "mac-auth"}

# Interface attributes set from top-level options, and their default value.
TOP_LEVEL = {
    "description": ("description", None),
    "loop_protect_enable": ("loop_protect_enable", False),
    "app_recognition_enable": ("app_recognition_enable", False),
}

# stp option -> (stp_config key, default value)
STP_KEYS = {
    "admin_edge": ("admin_edge_port_enable", False),
    "bpdu_guard": ("bpdu_guard_enable", False),
    "bpdu_filter": ("bpdu_filter_enable", False),
    "root_guard": ("root_guard_enable", False),
    "loop_guard": ("loop_guard_enable", False),
    "tcn_guard": ("restricted_port_tcn_disable", False),
    "link_type": ("link_type", "auto"),
}

# port_access option -> (interface attribute, default value)
PORT_ACCESS_ATTRS = {
    "concurrent_onboarding": ("port_access_concurrent_onboarding", False),
    "client_limit": ("port_access_clients_limit", 1),
    "auth_mode": ("port_access_auth_mode", None),
    "allow_bpdu": ("port_access_allow_bpdu", []),
    "allow_flood_traffic": ("port_access_allow_flood_traffic", False),
}

# port_access dictionary options -> (interface attribute, default value)
PORT_ACCESS_DICTS = {
    "client_ip_track": (
        "client_ip_track_configuration",
        {"admin_state": "auto", "client_limit": 128, "update_interval": 1800},
    ),
    "device_fingerprint": (
        "device_fingerprint_configuration",
        {"client_limit": 256},
    ),
}

VLAN_OPTIONS = [
    "vlan_mode",
    "vlan_access",
    "vlan_trunks",
    "trunk_allowed_all",
    "native_vlan_id",
    "native_vlan_tag",
]


AUTH_BOOLS = ["auth_enable", "reauth_enable", "cached_reauth_enable"]


class ConfigurationError(Exception):
    """Failure of one interface; the message is reported by main()."""


def auth_spec():
    return dict(
        (
            name,
            dict(type="bool" if name in AUTH_BOOLS else "int", required=False),
        )
        for name in AUTH_OPTIONS
    )


def build_argument_spec():
    interface_spec = dict(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False),
        enabled=dict(type="bool", required=False),
        mtu=dict(type="int", required=False),
        loop_protect_enable=dict(type="bool", required=False),
        app_recognition_enable=dict(type="bool", required=False),
        vlan_mode=dict(
            type="str", required=False, choices=["access", "trunk"]
        ),
        vlan_access=dict(type="int", required=False),
        vlan_trunks=dict(type="list", elements="int", required=False),
        trunk_allowed_all=dict(type="bool", required=False),
        native_vlan_id=dict(type="int", required=False),
        native_vlan_tag=dict(type="bool", required=False),
        stp=dict(
            type="dict",
            required=False,
            options=dict(
                admin_edge=dict(type="bool", required=False),
                bpdu_guard=dict(type="bool", required=False),
                bpdu_filter=dict(type="bool", required=False),
                root_guard=dict(type="bool", required=False),
                loop_guard=dict(type="bool", required=False),
                tcn_guard=dict(type="bool", required=False),
                link_type=dict(
                    type="str",
                    required=False,
                    choices=["auto", "point_to_point", "shared"],
                ),
            ),
        ),
        port_access=dict(
            type="dict",
            required=False,
            options=dict(
                concurrent_onboarding=dict(type="bool", required=False),
                client_limit=dict(type="int", required=False),
                auth_mode=dict(
                    type="str",
                    required=False,
                    choices=[
                        "client-mode",
                        "device-mode",
                        "proxy-mode",
                        "multi-domain",
                    ],
                ),
                allow_bpdu=dict(
                    type="list",
                    elements="str",
                    required=False,
                    choices=["cdp", "lldp"],
                ),
                allow_flood_traffic=dict(type="bool", required=False),
                client_ip_track=dict(
                    type="dict",
                    required=False,
                    options=dict(
                        admin_state=dict(
                            type="str",
                            required=False,
                            choices=["enable", "disable", "auto"],
                        ),
                        update_interval=dict(type="int", required=False),
                        client_limit=dict(type="int", required=False),
                    ),
                ),
                device_fingerprint=dict(
                    type="dict",
                    required=False,
                    options=dict(
                        profile_name=dict(type="str", required=False),
                        client_limit=dict(type="int", required=False),
                    ),
                ),
            ),
        ),
        dot1x=dict(type="dict", required=False, options=auth_spec()),
        mac_auth=dict(type="dict", required=False, options=auth_spec()),
    )
    return dict(
        interfaces=dict(
            type="list",
            elements="dict",
            required=True,
            options=interface_spec,
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )


def supplied(options):
    """Return the options of a dictionary that were given (not None)."""
    return dict((k, v) for k, v in (options or {}).items() if v is not None)


def same(current, wanted):
    """Compare two values, lists being compared without order."""
    if isinstance(current, list) or isinstance(wanted, list):
        return sorted(current or []) == sorted(wanted or [])
    return current == wanted


class InterfaceChanges(object):
    """Collect the attribute changes of one interface object."""

    def __init__(self, interface):
        self.interface = interface
        self.changed = False

    def set(self, attr, value):
        if same(getattr(self.interface, attr, None), value):
            return
        setattr(self.interface, attr, value)
        if attr not in self.interface.config_attrs:
            self.interface.config_attrs.append(attr)
        self.changed = True

    def merge(self, attr, values, replace=False):
        """Update some keys of a dictionary attribute."""
        current = getattr(self.interface, attr, None)
        current = dict(current) if isinstance(current, dict) else {}
        new = dict(values) if replace else dict(current, **values)
        self.set(attr, new)

    def user_config(self, key, value):
        """Set (or remove with None) a key of user_config."""
        current = getattr(self.interface, "user_config", None)
        current = dict(current) if isinstance(current, dict) else {}
        new = dict(current)
        if value is None:
            new.pop(key, None)
        else:
            new[key] = value
        self.set("user_config", new)


def desired_l2(name, entry):
    """
    Return the wanted (vlan_mode, vlan_tag, vlan_trunks) of an interface,
    each None when it must be left unchanged, as set by
    Interface.configure_l2().
    """
    mode = entry["vlan_mode"]
    if mode == "access":
        for option in (
            "vlan_trunks",
            "trunk_allowed_all",
            "native_vlan_id",
            "native_vlan_tag",
        ):
            if entry[option] is not None:
                raise ConfigurationError(
                    "{0}: {1} requires vlan_mode trunk".format(name, option)
                )
        return "access", entry["vlan_access"], None
    if entry["vlan_access"] is not None:
        raise ConfigurationError(
            "{0}: vlan_access requires vlan_mode access".format(name)
        )
    if entry["trunk_allowed_all"] and entry["vlan_trunks"] is not None:
        raise ConfigurationError(
            "{0}: vlan_trunks and trunk_allowed_all are mutually "
            "exclusive".format(name)
        )
    raw_mode = (
        "native-tagged" if entry["native_vlan_tag"] else "native-untagged"
    )
    trunks = None
    if entry["trunk_allowed_all"]:
        trunks = []
    elif entry["vlan_trunks"] is not None:
        trunks = sorted(set(entry["vlan_trunks"]))
    return raw_mode, entry["native_vlan_id"] or 1, trunks


def vlan_id(vlan):
    return None if vlan is None else str(getattr(vlan, "id", vlan))


def configure_interface(module, session, entry, delete):
    """
    Read one interface, set the supplied settings and apply them. Return True
    when the interface was (or, in check mode, would be) modified.
    """
    name = entry["name"]
    try:
        interface = session.api.get_module(session, "Interface", name)
        interface.get()
    except Exception as e:
        raise ConfigurationError(
            pyaoscx_error_message(
                session, "Could not read interface {0}".format(name), e
            )
        )
    changes = InterfaceChanges(interface)

    for option, (attr, default) in TOP_LEVEL.items():
        if entry[option] is not None:
            changes.set(attr, default if delete else entry[option])
    if entry["enabled"] is not None:
        if delete:
            changes.set("admin", None)
            changes.user_config("admin", None)
        else:
            state = "up" if entry["enabled"] else "down"
            changes.set("admin", state)
            changes.user_config("admin", state)
    if entry["mtu"] is not None:
        changes.user_config("mtu", None if delete else entry["mtu"])

    stp = supplied(entry["stp"])
    if stp:
        changes.merge(
            "stp_config",
            dict(
                (STP_KEYS[k][0], STP_KEYS[k][1] if delete else v)
                for k, v in stp.items()
            ),
        )

    port_access = supplied(entry["port_access"])
    for option, (attr, default) in PORT_ACCESS_ATTRS.items():
        if option in port_access:
            changes.set(attr, default if delete else port_access[option])
    for option, (attr, default) in PORT_ACCESS_DICTS.items():
        if option in port_access:
            if delete:
                changes.merge(attr, default, replace=True)
            else:
                changes.merge(attr, supplied(port_access[option]))

    l2 = None
    if any(entry[option] is not None for option in VLAN_OPTIONS):
        current_tag = vlan_id(getattr(interface, "vlan_tag", None))
        current_trunks = set(
            vlan_id(v) for v in getattr(interface, "vlan_trunks", None) or []
        )
        if delete:
            changes.set("vlan_mode", None)
            if current_tag is not None:
                changes.set("vlan_tag", None)
            if current_trunks:
                changes.set("vlan_trunks", [])
        else:
            if entry["vlan_mode"] is None:
                raise ConfigurationError(
                    "{0}: the VLAN options require vlan_mode".format(name)
                )
            l2 = desired_l2(name, entry)
            mode, tag, trunks = l2
            if (
                getattr(interface, "vlan_mode", None) != mode
                or getattr(interface, "routing", None) is not False
                or (tag is not None and current_tag != str(tag))
                or (
                    trunks is not None
                    and current_trunks != set(str(t) for t in trunks)
                )
            ):
                changes.changed = True
            else:
                l2 = None

    if not changes.changed or module.check_mode:
        return changes.changed

    try:
        if l2 is not None:
            # configure_l2() applies the other changes in the same PUT.
            mode, tag, trunks = l2
            return interface.configure_l2(
                vlan_mode=entry["vlan_mode"],
                vlan_tag=tag,
                vlan_ids_list=trunks,
                trunk_allowed_all=bool(entry["trunk_allowed_all"]),
                native_vlan_tag=bool(entry["native_vlan_tag"]),
            )
        return interface.apply()
    except Exception as e:
        raise ConfigurationError(
            pyaoscx_error_message(
                session, "Could not configure interface {0}".format(name), e
            )
        )


def configure_auth(module, session, entry, option, delete):
    """
    Create, update or delete the dot1x or mac-auth configuration of one
    interface. Return True when it was (or would be) modified.
    """
    if entry[option] is None:
        return False
    name = entry["name"]
    method = AUTH_METHODS[option]
    wanted = supplied(entry[option])
    feature = "{0} {1} configuration".format(name, method)
    try:
        config = session.api.get_module(
            session,
            "PortAccessAuthConfiguration",
            name,
            authentication_method=method,
        )
    except Exception as e:
        raise ConfigurationError(
            "This pyaoscx version does not support port access auth "
            "configurations. Upgrade pyaoscx. Details: {0}".format(str(e))
        )
    try:
        config.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    try:
        if delete:
            if exists and not module.check_mode:
                config.delete()
            return exists
        if not exists:
            if not module.check_mode:
                session.api.get_module(
                    session,
                    "PortAccessAuthConfiguration",
                    name,
                    authentication_method=method,
                    **wanted
                ).create()
            return True
        changed = False
        for attr, value in wanted.items():
            if getattr(config, attr, None) != value:
                setattr(config, attr, value)
                if attr not in config.config_attrs:
                    config.config_attrs.append(attr)
                changed = True
        if changed and not module.check_mode:
            config.update()
        return changed
    except Exception as e:
        raise ConfigurationError(pyaoscx_error_message(session, feature, e))


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(),
        supports_check_mode=True,
    )
    entries = ansible_module.params["interfaces"]
    delete = ansible_module.params["state"] == "delete"

    names = [entry["name"] for entry in entries]
    duplicates = sorted(set(n for n in names if names.count(n) > 1))
    if duplicates:
        ansible_module.fail_json(
            msg="Interfaces listed more than once: {0}".format(
                ", ".join(duplicates)
            )
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    changed_interfaces = []
    for entry in entries:
        changed = False
        try:
            # The authentication methods are removed before the interface
            # settings, and created after them.
            if delete:
                for option in AUTH_METHODS:
                    changed |= configure_auth(
                        ansible_module, session, entry, option, delete
                    )
            changed |= configure_interface(
                ansible_module, session, entry, delete
            )
            if not delete:
                for option in AUTH_METHODS:
                    changed |= configure_auth(
                        ansible_module, session, entry, option, delete
                    )
        except ConfigurationError as e:
            if changed:
                changed_interfaces.append(entry["name"])
            ansible_module.fail_json(
                msg=str(e),
                changed=bool(changed_interfaces),
                changed_interfaces=changed_interfaces,
            )
        if changed:
            changed_interfaces.append(entry["name"])

    ansible_module.exit_json(
        changed=bool(changed_interfaces),
        changed_interfaces=changed_interfaces,
    )


if __name__ == "__main__":
    main()
