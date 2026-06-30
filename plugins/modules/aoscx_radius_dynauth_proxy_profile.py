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
module: aoscx_radius_dynauth_proxy_profile
version_added: "4.6.0"
short_description: >
  Create, update or delete a RADIUS dynamic authorization proxy profile on
  AOS-CX.
description: >
  This module provides configuration management of RADIUS dynamic
  authorization (Change of Authorization) proxy profiles on AOS-CX devices. A
  profile ties together a proxy client group and a proxy server within a VRF,
  and is identified by its name.
author: Aruba Networks (@ArubaNetworks)
options:
  profile_name:
    description: Name of the proxy profile.
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
    description: Port used by the proxy profile.
    type: int
    required: false
  port_type:
    description: Transport used by the proxy profile.
    type: str
    required: false
    choices:
      - udp
      - tcp
  vrf:
    description: VRF the proxy profile belongs to.
    type: str
    required: false
    default: default
  client_group:
    description: >
      Name of the RADIUS dynamic authorization proxy client group referenced by
      this profile. The client group must already exist. Pass an empty string
      to clear the reference.
    type: str
    required: false
  server:
    description: >
      RADIUS dynamic authorization proxy server referenced by this profile. The
      server must already exist.
    type: dict
    required: false
    suboptions:
      address:
        description: Address of the proxy server.
        type: str
        required: true
      port:
        description: Port of the proxy server.
        type: int
        required: false
        default: 3799
      port_type:
        description: Transport of the proxy server.
        type: str
        required: false
        default: udp
        choices:
          - udp
          - tcp
      vrf:
        description: VRF of the proxy server.
        type: str
        required: false
        default: default
  state:
    description: Create, update or delete the proxy profile.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Create a proxy profile tying a client group and a server
  arubanetworks.aoscx.aoscx_radius_dynauth_proxy_profile:
    profile_name: coa-proxy
    enabled: true
    vrf: default
    client_group: coa-group
    server:
      address: 192.0.2.30
      port: 3799
      port_type: udp
    state: create

- name: Delete a proxy profile
  arubanetworks.aoscx.aoscx_radius_dynauth_proxy_profile:
    profile_name: coa-proxy
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the proxy profile was modified.
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
        vrf=dict(type="str", required=False, default="default"),
        client_group=dict(type="str", required=False, default=None),
        server=dict(
            type="dict",
            required=False,
            default=None,
            options=dict(
                address=dict(type="str", required=True),
                port=dict(type="int", required=False, default=3799),
                port_type=dict(
                    type="str", required=False, default="udp",
                    choices=["udp", "tcp"],
                ),
                vrf=dict(type="str", required=False, default="default"),
            ),
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

    params = ansible_module.params
    profile_name = params["profile_name"]
    enabled = params["enabled"]
    address = params["address"]
    port = params["port"]
    port_type = params["port_type"]
    vrf = params["vrf"]
    client_group = params["client_group"]
    server = params["server"]
    state = params["state"]

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
            session, "RadiusDynauthProxyProfile", profile_name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS dynamic "
                "authorization proxy profiles. Upgrade pyaoscx. Details: "
                "{0}".format(str(e))
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

    # Resolve and validate references before mutating anything.
    desired_cg = None
    if client_group is not None:
        if client_group == "":
            desired_cg = {}
        else:
            cg = session.api.get_module(
                session, "RadiusDynauthProxyClientGroup", client_group
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
                client_group: "{0}system/radius_dynauth_proxy_client_groups/"
                "{1}".format(rp, client_group)
            }

    desired_srv = None
    if server is not None:
        srv = session.api.get_module(
            session,
            "RadiusDynauthProxyServer",
            server["vrf"],
            address=server["address"],
            port=server["port"],
            port_type=server["port_type"],
        )
        try:
            srv.get()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not find proxy server {0}: {1}".format(
                    server["address"], str(e)
                )
            )
        srv_index = "{0}{1}{2}{1}{3}".format(
            server["address"], sep, server["port"], server["port_type"]
        )
        desired_srv = {
            srv_index: "{0}system/vrfs/{1}/radius_dynauth_proxy_servers/"
            "{2}".format(rp, server["vrf"], srv_index)
        }

    desired_vrf = {vrf: "{0}system/vrfs/{1}".format(rp, vrf)}

    # ----------------------------------------------------------- check mode
    if ansible_module.check_mode:
        result["changed"] = (not exists) or any(
            v is not None
            for v in (enabled, address, port, port_type, client_group, server)
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
        "enabled": enabled,
        "address": address,
        "port": port,
        "port_type": port_type,
    }
    for name, value in scalars.items():
        if value is not None and getattr(profile, name, None) != value:
            needs_update = True
            setattr(profile, name, value)

    if ref_name(getattr(profile, "vrf", None) or {}) != vrf:
        needs_update = True
        profile.vrf = desired_vrf

    if desired_cg is not None:
        current = getattr(profile, "dynauth_client_group", None) or {}
        if ref_name(current) != ref_name(desired_cg):
            needs_update = True
            profile.dynauth_client_group = desired_cg

    if desired_srv is not None:
        current = getattr(profile, "dynauth_server", None) or {}
        if ref_name(current) != ref_name(desired_srv):
            needs_update = True
            profile.dynauth_server = desired_srv

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
