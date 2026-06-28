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
module: aoscx_radius_server
version_added: "4.6.0"
short_description: Create, update or delete a RADIUS server
description: >
  This module provides configuration management of RADIUS servers on AOS-CX
  devices (system/vrfs/{vrf}/radius_servers). A RADIUS server is identified by
  the combination of its address, UDP/TCP port and port type within a VRF.
  This module requires REST API version 10.16 (set ansible_aoscx_rest_version
  to 10.16). The address, port, port_type and vrf are set when the server is
  created and cannot be changed afterwards. The passkey is write-only; when it
  is supplied the module always (re)applies it, which is reported as a change.
author: Aruba Networks (@ArubaNetworks)
options:
  address:
    description: IP address or hostname of the RADIUS server.
    required: true
    type: str
  vrf:
    description: Name of the VRF the RADIUS server belongs to.
    required: false
    default: default
    type: str
  port:
    description: UDP/TCP port used to reach the RADIUS server (1-65535).
    required: false
    default: 1812
    type: int
  port_type:
    description: Transport used to reach the RADIUS server.
    required: false
    default: udp
    type: str
    choices:
      - udp
      - tcp
  passkey:
    description: >
      Shared secret used with the RADIUS server. This value is write-only; the
      switch only ever returns it encrypted, so when passkey is supplied the
      module always (re)applies it and reports a change.
    required: false
    type: str

  auth_type:
    description: Authentication protocol used with the RADIUS server.
    required: false
    type: str
    choices:
      - pap
      - chap
  accounting_udp_port:
    description: UDP port used for RADIUS accounting (1-65535).
    required: false
    type: int
  retries:
    description: Number of retransmissions before giving up (0-5).
    required: false
    type: int
  timeout:
    description: Time in seconds to wait for a server response (1-60).
    required: false
    type: int
  tls_initial_connection_timeout:
    description: >
      Time in seconds to wait when establishing a RadSec TLS connection
      (5-300).
    required: false
    type: int
  msg_authenticator_check:
    description: Enable Message-Authenticator attribute checking.
    required: false
    type: bool
  tracking_enable:
    description: Enable server-reachability tracking.
    required: false
    type: bool
  tracking_method:
    description: Method used to track the server reachability.
    required: false
    type: str
    choices:
      - status-server
      - keep-alive
      - access-request
  tracking_mode:
    description: When to track the server reachability.
    required: false
    type: str
    choices:
      - any
      - dead-only
  port_access:
    description: Method used by port-access to track the server.
    required: false
    type: str
    choices:
      - status-server
      - keep-alive
  server_group:
    description: >
      Mapping of AAA server group names to their priority for this server,
      for example {my-radius: 1}. The referenced groups must already exist.
      The supplied mapping fully replaces the current group membership.
    required: false
    type: dict
  state:
    description: Create, update or delete the RADIUS server.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a RADIUS server
  aoscx_radius_server:
    address: 192.0.2.10
    vrf: default
    passkey: my-secret
    auth_type: pap
    timeout: 10

- name: Create a RADIUS server bound to a server group
  aoscx_radius_server:
    address: 192.0.2.11
    vrf: default
    passkey: my-secret
    server_group:
      my-radius: 1

- name: Update the RADIUS server timeout
  aoscx_radius_server:
    address: 192.0.2.10
    state: update
    timeout: 20

- name: Delete a RADIUS server
  aoscx_radius_server:
    address: 192.0.2.10
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def server_group_uris(session, ansible_module, mapping):
    """Validate each group exists and return a {group_uri: priority} dict."""
    result = {}
    for name, priority in mapping.items():
        group = session.api.get_module(session, "AaaServerGroup", name)
        try:
            group.get()
        except Exception:
            ansible_module.fail_json(
                msg="Could not find AAA server group {0}".format(name)
            )
        uri = "{0}system/aaa_server_groups/{1}".format(
            session.resource_prefix, name
        )
        result[uri] = priority
    return result


def main():
    module_args = dict(
        address=dict(type="str", required=True),
        vrf=dict(type="str", required=False, default="default"),
        port=dict(type="int", required=False, default=1812),
        port_type=dict(
            type="str",
            required=False,
            default="udp",
            choices=["udp", "tcp"],
        ),
        passkey=dict(type="str", required=False, default=None, no_log=True),
        auth_type=dict(
            type="str",
            required=False,
            default=None,
            choices=["pap", "chap"],
        ),
        accounting_udp_port=dict(type="int", required=False, default=None),
        retries=dict(type="int", required=False, default=None),
        timeout=dict(type="int", required=False, default=None),
        tls_initial_connection_timeout=dict(
            type="int", required=False, default=None
        ),
        msg_authenticator_check=dict(
            type="bool", required=False, default=None
        ),
        tracking_enable=dict(type="bool", required=False, default=None),
        tracking_method=dict(
            type="str",
            required=False,
            default=None,
            choices=["status-server", "keep-alive", "access-request"],
        ),
        tracking_mode=dict(
            type="str",
            required=False,
            default=None,
            choices=["any", "dead-only"],
        ),
        port_access=dict(
            type="str",
            required=False,
            default=None,
            choices=["status-server", "keep-alive"],
        ),
        server_group=dict(type="dict", required=False, default=None),
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

    address = ansible_module.params["address"]
    vrf_name = ansible_module.params["vrf"]
    port = ansible_module.params["port"]
    port_type = ansible_module.params["port_type"]
    passkey = ansible_module.params["passkey"]
    state = ansible_module.params["state"]

    scalar_attrs = [
        "auth_type",
        "accounting_udp_port",
        "retries",
        "timeout",
        "tls_initial_connection_timeout",
        "msg_authenticator_check",
        "tracking_enable",
        "tracking_method",
        "tracking_mode",
        "port_access",
    ]
    supplied = {
        attr: ansible_module.params[attr]
        for attr in scalar_attrs
        if ansible_module.params[attr] is not None
    }

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    vrf = session.api.get_module(session, "Vrf", vrf_name)
    try:
        vrf.get()
    except Exception:
        ansible_module.fail_json(msg="Could not find VRF, make sure it exists")

    try:
        server = session.api.get_module(
            session,
            "RadiusServer",
            vrf,
            address=address,
            port=port,
            port_type=port_type,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS servers. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        server.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    desired_groups = None
    if ansible_module.params["server_group"] is not None:
        desired_groups = server_group_uris(
            session, ansible_module, ansible_module.params["server_group"]
        )

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                server.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete RADIUS server: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- create
    if not exists:
        create_kwargs = dict(supplied)
        if passkey is not None:
            create_kwargs["passkey"] = passkey
        if desired_groups is not None:
            create_kwargs["server_group"] = desired_groups
        server = session.api.get_module(
            session,
            "RadiusServer",
            vrf,
            address=address,
            port=port,
            port_type=port_type,
            **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                server.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create RADIUS server: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- update
    changed = False
    for attr, value in supplied.items():
        if getattr(server, attr, None) != value:
            changed = True
            setattr(server, attr, value)
            if attr not in server.config_attrs:
                server.config_attrs.append(attr)

    if desired_groups is not None:
        if getattr(server, "server_group", None) != desired_groups:
            changed = True
            server.server_group = desired_groups
            if "server_group" not in server.config_attrs:
                server.config_attrs.append("server_group")

    # passkey is write-only: re-apply whenever it is supplied.
    if passkey is not None:
        changed = True
        server.passkey = passkey
        if "passkey" not in server.config_attrs:
            server.config_attrs.append("passkey")

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            server.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update RADIUS server: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
