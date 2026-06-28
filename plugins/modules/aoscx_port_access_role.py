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
module: aoscx_port_access_role
version_added: "4.6.0"
short_description: Create, update or delete a Port Access Role
description: >
  This module provides configuration management of Port Access Roles on AOS-CX
  devices (system/port_access_roles). A port access role is the local user
  role applied to authenticated clients (for example a role returned by a
  RADIUS server such as ClearPass). It groups the VLAN assignment and the
  per-client access settings. This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16). The reference attributes in_abp,
  in_gbp, in_policy, macsec_policy and ipfix_flow_monitor are not managed by
  this module.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the port access role. This is the index of the resource under
      system/port_access_roles.
    required: true
    type: str
  description:
    description: Description of the port access role.
    required: false
    type: str
  auth_mode:
    description: Authentication mode applied to clients using this role.
    required: false
    type: str
    choices:
      - client-mode
      - device-mode
      - proxy-mode
      - multi-domain
  vlan_mode:
    description: VLAN mode applied to clients using this role.
    required: false
    type: str
    choices:
      - trunk
      - access
      - native-tagged
      - native-untagged
  vlan_tag:
    description: Access or native VLAN ID assigned by this role.
    required: false
    type: int
  vlan_trunks:
    description: List of tagged trunk VLAN IDs assigned by this role.
    required: false
    type: list
    elements: int
  vlan_name_tag:
    description: Access or native VLAN name assigned by this role.
    required: false
    type: str
  vlan_name_trunks:
    description: List of tagged trunk VLAN names assigned by this role.
    required: false
    type: list
    elements: str
  reauth_period:
    description: Reauthentication period in seconds.
    required: false
    type: int
  cached_reauth_period:
    description: Cached reauthentication period in seconds.
    required: false
    type: int
  client_inactivity_monitor:
    description: Client inactivity monitoring mode.
    required: false
    type: str
    choices:
      - configured_timeout
      - dynamic_timeout
      - no_timeout
  client_inactivity_timeout:
    description: Client inactivity timeout in seconds.
    required: false
    type: int
  max_session_time:
    description: Maximum session time in seconds.
    required: false
    type: int
  mtu:
    description: MTU applied to clients using this role.
    required: false
    type: int
  poe_priority:
    description: PoE priority applied to clients using this role.
    required: false
    type: str
    choices:
      - low
      - high
      - critical
  poe_allocate_by_method:
    description: Method used to allocate PoE power.
    required: false
    type: str
    choices:
      - class
      - usage
  qos_trust_mode:
    description: QoS trust mode applied to clients using this role.
    required: false
    type: str
    choices:
      - none
      - cos
      - dscp
  stp_admin_edge_port:
    description: Whether the port is configured as an STP admin edge port.
    required: false
    type: bool
  device_traffic_class:
    description: Device traffic class assigned by this role.
    required: false
    type: str
    choices:
      - voice
  gateway_zone:
    description: User-based tunneling gateway zone.
    required: false
    type: str
  ubt_gateway_role:
    description: User-based tunneling gateway role.
    required: false
    type: str
  pvlan_port_type:
    description: Private VLAN port type.
    required: false
    type: str
    choices:
      - promiscuous
      - secondary
  app_recognition_enable:
    description: Whether application recognition is enabled for the role.
    required: false
    type: bool
  traffic_inspection_enable:
    description: Whether traffic inspection is enabled for the role.
    required: false
    type: bool
  captive_portal_profile:
    description: >
      Name of an existing captive portal profile
      (system/captive_portal_profiles) to associate with this role. The
      profile must already exist.
    required: false
    type: str
  state:
    description: Create, update or delete the port access role.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a port access role assigning an access VLAN
  aoscx_port_access_role:
    name: employee
    description: Corporate employees
    vlan_mode: access
    vlan_tag: 10

- name: Create a guest role with a captive portal profile
  aoscx_port_access_role:
    name: guest
    vlan_mode: access
    vlan_tag: 20
    captive_portal_profile: guest-portal
    client_inactivity_monitor: dynamic_timeout

- name: Delete a port access role
  aoscx_port_access_role:
    name: guest
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SCALAR_ATTRS = [
    "description",
    "auth_mode",
    "vlan_mode",
    "vlan_tag",
    "vlan_name_tag",
    "reauth_period",
    "cached_reauth_period",
    "client_inactivity_monitor",
    "client_inactivity_timeout",
    "max_session_time",
    "mtu",
    "poe_priority",
    "poe_allocate_by_method",
    "qos_trust_mode",
    "stp_admin_edge_port",
    "device_traffic_class",
    "gateway_zone",
    "ubt_gateway_role",
    "pvlan_port_type",
    "app_recognition_enable",
    "traffic_inspection_enable",
]

LIST_ATTRS = ["vlan_trunks", "vlan_name_trunks"]


def captive_portal_uri(session, ansible_module, profile_name):
    """
    Validate that the captive portal profile exists and return its URI.
    """
    profile = session.api.get_module(
        session, "CaptivePortalProfile", profile_name
    )
    try:
        profile.get()
    except Exception:
        ansible_module.fail_json(
            msg="Captive portal profile '{0}' does not exist".format(
                profile_name
            )
        )
    return "{0}system/captive_portal_profiles/{1}".format(
        session.resource_prefix, profile_name
    )


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False, default=None),
        auth_mode=dict(
            type="str",
            required=False,
            default=None,
            choices=[
                "client-mode",
                "device-mode",
                "proxy-mode",
                "multi-domain",
            ],
        ),
        vlan_mode=dict(
            type="str",
            required=False,
            default=None,
            choices=[
                "trunk",
                "access",
                "native-tagged",
                "native-untagged",
            ],
        ),
        vlan_tag=dict(type="int", required=False, default=None),
        vlan_trunks=dict(
            type="list", elements="int", required=False, default=None
        ),
        vlan_name_tag=dict(type="str", required=False, default=None),
        vlan_name_trunks=dict(
            type="list", elements="str", required=False, default=None
        ),
        reauth_period=dict(type="int", required=False, default=None),
        cached_reauth_period=dict(type="int", required=False, default=None),
        client_inactivity_monitor=dict(
            type="str",
            required=False,
            default=None,
            choices=[
                "configured_timeout",
                "dynamic_timeout",
                "no_timeout",
            ],
        ),
        client_inactivity_timeout=dict(
            type="int", required=False, default=None
        ),
        max_session_time=dict(type="int", required=False, default=None),
        mtu=dict(type="int", required=False, default=None),
        poe_priority=dict(
            type="str",
            required=False,
            default=None,
            choices=["low", "high", "critical"],
        ),
        poe_allocate_by_method=dict(
            type="str",
            required=False,
            default=None,
            choices=["class", "usage"],
        ),
        qos_trust_mode=dict(
            type="str",
            required=False,
            default=None,
            choices=["none", "cos", "dscp"],
        ),
        stp_admin_edge_port=dict(type="bool", required=False, default=None),
        device_traffic_class=dict(
            type="str", required=False, default=None, choices=["voice"]
        ),
        gateway_zone=dict(type="str", required=False, default=None),
        ubt_gateway_role=dict(type="str", required=False, default=None),
        pvlan_port_type=dict(
            type="str",
            required=False,
            default=None,
            choices=["promiscuous", "secondary"],
        ),
        app_recognition_enable=dict(type="bool", required=False, default=None),
        traffic_inspection_enable=dict(
            type="bool", required=False, default=None
        ),
        captive_portal_profile=dict(type="str", required=False, default=None),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    name = ansible_module.params["name"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        role = session.api.get_module(session, "PortAccessRole", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support port access roles. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        role.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                role.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete port access role: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # Gather supplied scalar/list attributes.
    supplied = {}
    for attr in SCALAR_ATTRS:
        value = ansible_module.params[attr]
        if value is not None:
            supplied[attr] = value
    for attr in LIST_ATTRS:
        value = ansible_module.params[attr]
        if value is not None:
            supplied[attr] = sorted(value)

    cpp_name = ansible_module.params["captive_portal_profile"]
    cpp_uri = None
    if cpp_name is not None:
        cpp_uri = captive_portal_uri(session, ansible_module, cpp_name)

    # --------------------------------------------------------------- create
    if not exists:
        kwargs = dict(supplied)
        if cpp_uri is not None:
            kwargs["captive_portal_profile"] = cpp_uri
        role = session.api.get_module(
            session, "PortAccessRole", name, **kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                role.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create port access role: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- update
    changed = False
    for attr, value in supplied.items():
        current = getattr(role, attr, None)
        if attr in LIST_ATTRS:
            current = sorted(current or [])
        if current != value:
            changed = True
            setattr(role, attr, value)
            if attr not in role.config_attrs:
                role.config_attrs.append(attr)

    if cpp_uri is not None:
        current_ref = getattr(role, "captive_portal_profile", None)
        if isinstance(current_ref, dict):
            current_uri = next(iter(current_ref.values()), None)
        else:
            current_uri = current_ref
        if current_uri != cpp_uri:
            changed = True
            role.captive_portal_profile = cpp_uri
            if "captive_portal_profile" not in role.config_attrs:
                role.config_attrs.append("captive_portal_profile")

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            role.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update port access role: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
