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
module: aoscx_radius_proxy_client_group
version_added: "4.6.0"
short_description: Create, update or delete a RADIUS proxy client group on AOS-CX.
description: >
  This module provides configuration management of RADIUS proxy client groups
  on AOS-CX devices. A client group defines the downstream RADIUS clients (NAS
  devices) handled by the proxy and is identified by its name.
author: Aruba Networks (@ArubaNetworks)
options:
  group_name:
    description: Name of the RADIUS proxy client group.
    type: str
    required: true
  clients:
    description: >
      RADIUS clients (NAS devices) that are members of the group. The supplied
      list fully replaces the members. When omitted the members are left
      unchanged; an empty list removes all members. Ignored when I(state) is
      C(delete).
    type: list
    elements: dict
    required: false
    suboptions:
      address:
        description: Address of the RADIUS client (NAS).
        type: str
        required: true
      connection_type:
        description: Connection type of the client.
        type: str
        required: false
        default: udp
        choices:
          - udp
          - tcp
      secret_key:
        description: >
          Shared secret used with the client. It is write-only; the switch only
          ever returns it encrypted, so when a secret is supplied the module
          reports changed on every run.
        type: str
        required: false
  state:
    description: Create, update or delete the RADIUS proxy client group.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Create a RADIUS proxy client group with one client
  arubanetworks.aoscx.aoscx_radius_proxy_client_group:
    group_name: nas-group
    clients:
      - address: 192.0.2.50
        connection_type: udp
        secret_key: nas-secret
    state: create

- name: Remove all members from the group
  arubanetworks.aoscx.aoscx_radius_proxy_client_group:
    group_name: nas-group
    clients: []
    state: update

- name: Delete the RADIUS proxy client group
  arubanetworks.aoscx.aoscx_radius_proxy_client_group:
    group_name: nas-group
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the RADIUS proxy client group was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def build_clients(clients):
    """Build the {address: {connection_type, secret_key}} map and report
    whether any secret was supplied (which makes the result non-idempotent).
    """
    result = {}
    has_secret = False
    for entry in clients:
        member = {"connection_type": entry["connection_type"]}
        if entry["secret_key"] is not None:
            member["secret_key"] = entry["secret_key"]
            has_secret = True
        result[entry["address"]] = member
    return result, has_secret


def main():
    module_args = dict(
        group_name=dict(type="str", required=True),
        clients=dict(
            type="list",
            elements="dict",
            required=False,
            default=None,
            options=dict(
                address=dict(type="str", required=True),
                connection_type=dict(
                    type="str", required=False, default="udp",
                    choices=["udp", "tcp"],
                ),
                secret_key=dict(
                    type="str", required=False, default=None, no_log=True
                ),
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

    group_name = ansible_module.params["group_name"]
    clients = ansible_module.params["clients"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    if group_name in ("", ".", "..") or "/" in group_name:
        ansible_module.fail_json(
            msg="Invalid group name: {0}".format(group_name)
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        group = session.api.get_module(
            session, "RadiusProxyClientGroup", group_name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS proxy client "
                "groups. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        group.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # ----------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                group.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete client group: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    desired = None
    has_secret = False
    if clients is not None:
        desired, has_secret = build_clients(clients)

    # ----------------------------------------------------------- check mode
    if ansible_module.check_mode:
        result["changed"] = (not exists) or clients is not None
        ansible_module.exit_json(**result)

    # ----------------------------------------------------------- create/update
    created = False
    if not exists:
        try:
            group.create()
            group.get(selector="writable")
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not create client group: {0}".format(str(e))
            )
        created = True

    needs_update = False
    if desired is not None:
        current = getattr(group, "clients", None) or {}
        # Compare by the set of client addresses; a supplied secret cannot be
        # verified, so it forces an update.
        if set(current) != set(desired) or has_secret:
            needs_update = True
            group.clients = desired

    if needs_update:
        try:
            group.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update client group: {0}".format(str(e))
            )

    result["changed"] = created or needs_update
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
