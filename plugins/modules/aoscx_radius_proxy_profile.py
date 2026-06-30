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
module: aoscx_radius_proxy_profile
version_added: "4.6.0"
short_description: Create, update or delete a RADIUS proxy profile on AOS-CX.
description: >
  This module provides configuration management of RADIUS proxy profiles on
  AOS-CX devices. A profile ties together a RADIUS proxy client group and an
  AAA server group within a VRF, and is identified by its name.
author: Aruba Networks (@ArubaNetworks)
options:
  profile_name:
    description: Name of the RADIUS proxy profile.
    type: str
    required: true
  enabled:
    description: Whether the proxy profile is enabled.
    type: bool
    required: false
  address:
    description: Source IPv4 address used by the proxy profile.
    type: str
    required: false
  port:
    description: Authentication UDP/TCP port used by the proxy profile.
    type: int
    required: false
  port_type:
    description: Transport used by the proxy profile.
    type: str
    required: false
    choices:
      - udp
      - tcp
  accounting_udp_port:
    description: Accounting UDP port used by the proxy profile.
    type: int
    required: false
  nas_id:
    description: NAS identifier sent by the proxy.
    type: str
    required: false
  nas_ip_addr:
    description: NAS IP address sent by the proxy.
    type: str
    required: false
  timeout:
    description: Request timeout in seconds.
    type: int
    required: false
  vrf:
    description: VRF the proxy profile belongs to.
    type: str
    required: false
    default: default
  client_group:
    description: >
      Name of the RADIUS proxy client group referenced by this profile. The
      client group must already exist. Pass an empty string to clear it.
    type: str
    required: false
  server_group:
    description: >
      Name of the AAA server group referenced by this profile. The server group
      must already exist.
    type: str
    required: false
  server_group_type:
    description: Type of the referenced AAA server group.
    type: str
    required: false
    default: radius
    choices:
      - radius
      - tacacs
  state:
    description: Create, update or delete the RADIUS proxy profile.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Create a RADIUS proxy profile tying a client group and a server group
  arubanetworks.aoscx.aoscx_radius_proxy_profile:
    profile_name: radius-proxy
    enabled: true
    vrf: default
    client_group: nas-group
    server_group: my-radius-group
    state: create

- name: Delete a RADIUS proxy profile
  arubanetworks.aoscx.aoscx_radius_proxy_profile:
    profile_name: radius-proxy
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the RADIUS proxy profile was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def ref_name(ref):
    """Return the single key (name) of a {name: uri} reference map."""
    if isinstance(ref, dict) and ref:
        return next(iter(ref))
    return None


def main():
    module_args = dict(
        profile_name=dict(type="str", required=True),
        enabled=dict(type="bool", required=False, default=None),
        address=dict(type="str", required=False, default=None),
        port=dict(type="int", required=False, default=None),
        port_type=dict(
            type="str", required=False, default=None, choices=["udp", "tcp"]
        ),
        accounting_udp_port=dict(type="int", required=False, default=None),
        nas_id=dict(type="str", required=False, default=None),
        nas_ip_addr=dict(type="str", required=False, default=None),
        timeout=dict(type="int", required=False, default=None),
        vrf=dict(type="str", required=False, default="default"),
        client_group=dict(type="str", required=False, default=None),
        server_group=dict(type="str", required=False, default=None),
        server_group_type=dict(
            type="str", required=False, default="radius",
            choices=["radius", "tacacs"],
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    p = ansible_module.params
    profile_name = p["profile_name"]
    vrf = p["vrf"]
    client_group = p["client_group"]
    server_group = p["server_group"]
    server_group_type = p["server_group_type"]
    state = p["state"]

    result = dict(changed=False)

    if profile_name in ("", ".", "..") or "/" in profile_name:
        ansible_module.fail_json(
            msg="Invalid profile name: {0}".format(profile_name)
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        profile = session.api.get_module(
            session, "RadiusProxyProfile", profile_name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS proxy profiles. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        profile.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # ----------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                profile.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete proxy profile: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    rp = session.resource_prefix
    sep = session.api.compound_index_separator

    desired_cg = None
    if client_group is not None:
        if client_group == "":
            desired_cg = {}
        else:
            cg = session.api.get_module(
                session, "RadiusProxyClientGroup", client_group
            )
            try:
                cg.get()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not find client group {0}: {1}".format(
                        client_group, str(e)
                    )
                )
            desired_cg = {
                client_group: "{0}system/radius_proxy_client_groups/"
                "{1}".format(rp, client_group)
            }

    desired_sg = None
    if server_group is not None:
        grp_index = "{0}{1}{2}".format(server_group, sep, server_group_type)
        sg = session.api.get_module(
            session, "AaaServerGroup", server_group,
            group_type=server_group_type,
        )
        try:
            sg.get()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not find AAA server group {0}: {1}".format(
                    server_group, str(e)
                )
            )
        # The switch normalizes the reference key to the group name only, so
        # compare against the name (not the compound name,type index).
        desired_sg = {
            server_group:
                "{0}system/aaa_server_groups/{1}".format(rp, grp_index)
        }

    desired_vrf = {vrf: "{0}system/vrfs/{1}".format(rp, vrf)}

    # ----------------------------------------------------------- check mode
    if ansible_module.check_mode:
        result["changed"] = (not exists) or any(
            p[k] is not None
            for k in (
                "enabled", "address", "port", "port_type",
                "accounting_udp_port", "nas_id", "nas_ip_addr", "timeout",
                "client_group", "server_group",
            )
        )
        ansible_module.exit_json(**result)

    # ----------------------------------------------------------- create/update
    created = False
    if not exists:
        try:
            profile.create()
            profile.get(selector="writable")
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not create proxy profile: {0}".format(str(e))
            )
        created = True

    needs_update = False

    scalars = {
        "enabled": p["enabled"],
        "address": p["address"],
        "port": p["port"],
        "port_type": p["port_type"],
        "accounting_udp_port": p["accounting_udp_port"],
        "nas_id": p["nas_id"],
        "nas_ip_addr": p["nas_ip_addr"],
        "timeout": p["timeout"],
    }
    for name, value in scalars.items():
        if value is not None and getattr(profile, name, None) != value:
            needs_update = True
            setattr(profile, name, value)

    if ref_name(getattr(profile, "vrf", None) or {}) != vrf:
        needs_update = True
        profile.vrf = desired_vrf

    if desired_cg is not None:
        current = getattr(profile, "client_group", None) or {}
        if ref_name(current) != ref_name(desired_cg):
            needs_update = True
            profile.client_group = desired_cg

    if desired_sg is not None:
        current = getattr(profile, "server_group", None) or {}
        if ref_name(current) != ref_name(desired_sg):
            needs_update = True
            profile.server_group = desired_sg

    if needs_update:
        try:
            profile.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update proxy profile: {0}".format(str(e))
            )

    result["changed"] = created or needs_update
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
