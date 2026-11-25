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
module: aoscx_tacacs_server
version_added: "4.6.0"
short_description: Create, update or delete a TACACS+ server
description: >
  This module provides configuration management of TACACS+ servers on AOS-CX
  devices (system/vrfs/{vrf}/tacacs_servers). A TACACS+ server is identified by
  the combination of its address and TCP port within a VRF. This module
  requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16).
  The address, tcp_port and vrf are set when the server is created and cannot
  be changed afterwards. At least one server group must be supplied when the
  server is created. The passkey is write-only; when it is supplied the module
  always (re)applies it, which is reported as a change.
author: Aruba Networks (@ArubaNetworks)
notes:
  - When C(passkey) is supplied the module reports changed on every run
    because the secret cannot be read back from the switch for comparison.
options:
  address:
    description: IP address or hostname of the TACACS+ server.
    required: true
    type: str
  vrf:
    description: Name of the VRF the TACACS+ server belongs to.
    required: false
    default: default
    type: str
  tcp_port:
    description: TCP port used to reach the TACACS+ server (1-65535).
    required: false
    default: 49
    type: int
  passkey:
    description: >
      Shared secret used with the TACACS+ server. This value is write-only;
      the switch only ever returns it encrypted, so when passkey is supplied
      the module always (re)applies it and reports a change.
    required: false
    type: str
  group:
    description: >
      List of AAA server group names this server belongs to. The referenced
      groups must already exist. At least one group is required when the
      server is created. The supplied list fully replaces the current group
      membership.
    required: false
    type: list
    elements: str
  default_group_priority:
    description: >
      Priority of this server within the default tacacs group (1 or higher).
    required: false
    default: 1
    type: int
  user_group_priority:
    description: Priority of this server within a user-defined group.
    required: false
    type: int
  auth_type:
    description: Authentication protocol used with the TACACS+ server.
    required: false
    type: str
    choices:
      - pap
      - chap
  timeout:
    description: Time in seconds to wait for a server response (1-60).
    required: false
    type: int
  tracking_enable:
    description: Enable server-reachability tracking.
    required: false
    type: bool
  state:
    description: Create, update or delete the TACACS+ server.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a TACACS+ server
  aoscx_tacacs_server:
    address: 192.0.2.20
    vrf: default
    passkey: my-secret
    group:
      - tacacs
    auth_type: pap
    timeout: 10

- name: Update the TACACS+ server timeout
  aoscx_tacacs_server:
    address: 192.0.2.20
    state: update
    timeout: 20

- name: Delete a TACACS+ server
  aoscx_tacacs_server:
    address: 192.0.2.20
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def group_uris(session, ansible_module, names):
    """Validate each group exists and return a list of group URIs."""
    uris = []
    for name in names:
        group = session.api.get_module(session, "AaaServerGroup", name)
        try:
            group.get()
        except Exception:
            ansible_module.fail_json(
                msg="Could not find AAA server group {0}".format(name)
            )
        uris.append(
            "{0}system/aaa_server_groups/{1}".format(
                session.resource_prefix, name
            )
        )
    return uris


def current_group_names(server):
    """Return the set of group names currently bound to the server."""
    current = getattr(server, "group", None)
    if isinstance(current, dict):
        return set(current.keys())
    return set()


def main():
    module_args = dict(
        address=dict(type="str", required=True),
        vrf=dict(type="str", required=False, default="default"),
        tcp_port=dict(type="int", required=False, default=49),
        passkey=dict(type="str", required=False, default=None, no_log=True),
        group=dict(type="list", elements="str", required=False, default=None),
        default_group_priority=dict(type="int", required=False, default=1),
        user_group_priority=dict(type="int", required=False, default=None),
        auth_type=dict(
            type="str",
            required=False,
            default=None,
            choices=["pap", "chap"],
        ),
        timeout=dict(type="int", required=False, default=None),
        tracking_enable=dict(type="bool", required=False, default=None),
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
    tcp_port = ansible_module.params["tcp_port"]
    passkey = ansible_module.params["passkey"]
    group = ansible_module.params["group"]
    default_group_priority = ansible_module.params["default_group_priority"]
    state = ansible_module.params["state"]

    scalar_attrs = [
        "user_group_priority",
        "auth_type",
        "timeout",
        "tracking_enable",
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
            "TacacsServer",
            vrf,
            address=address,
            tcp_port=tcp_port,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support TACACS+ servers. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        server.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    desired_group_uris = None
    if group is not None:
        desired_group_uris = group_uris(session, ansible_module, group)

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                server.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete TACACS+ server: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- create
    if not exists:
        if not group:
            ansible_module.fail_json(
                msg="group is required to create a TACACS+ server"
            )
        create_kwargs = dict(supplied)
        create_kwargs["group"] = desired_group_uris
        create_kwargs["default_group_priority"] = default_group_priority
        if passkey is not None:
            create_kwargs["passkey"] = passkey
        server = session.api.get_module(
            session,
            "TacacsServer",
            vrf,
            address=address,
            tcp_port=tcp_port,
            **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                server.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create TACACS+ server: {0}".format(str(e))
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

    if (
        ansible_module.params["default_group_priority"] is not None
        and getattr(server, "default_group_priority", None)
        != default_group_priority
    ):
        changed = True
        server.default_group_priority = default_group_priority
        if "default_group_priority" not in server.config_attrs:
            server.config_attrs.append("default_group_priority")

    if desired_group_uris is not None:
        if current_group_names(server) != set(group):
            changed = True
            server.group = desired_group_uris
            if "group" not in server.config_attrs:
                server.config_attrs.append("group")

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
                msg="Could not update TACACS+ server: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
