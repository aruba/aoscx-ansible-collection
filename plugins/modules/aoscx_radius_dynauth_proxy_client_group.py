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
module: aoscx_radius_dynauth_proxy_client_group
version_added: "4.6.0"
short_description: >
  Create, update or delete a RADIUS dynamic authorization proxy client group on
  AOS-CX.
description: >
  This module provides configuration management of RADIUS dynamic
  authorization (Change of Authorization) proxy client groups on AOS-CX
  devices. A client group references a set of RADIUS dynamic authorization
  (CoA) clients and is identified by its name.
author: Aruba Networks (@ArubaNetworks)
options:
  group_name:
    description: Name of the proxy client group.
    type: str
    required: true
  clients:
    description: >
      RADIUS dynamic authorization (CoA) clients that are members of the group.
      The supplied list fully replaces the members. When omitted the members
      are left unchanged; an empty list removes all members. Each referenced
      CoA client must already exist. Ignored when I(state) is C(delete).
    type: list
    elements: dict
    required: false
    suboptions:
      address:
        description: Address of the CoA client.
        type: str
        required: true
      connection_type:
        description: Connection type of the CoA client.
        type: str
        required: false
        default: udp
        choices:
          - udp
          - tcp
      vrf:
        description: VRF of the CoA client.
        type: str
        required: false
        default: default
  state:
    description: Create, update or delete the proxy client group.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Create a proxy client group with two CoA clients
  arubanetworks.aoscx.aoscx_radius_dynauth_proxy_client_group:
    group_name: coa-group
    clients:
      - address: 192.0.2.41
        connection_type: udp
      - address: 192.0.2.42
        connection_type: udp
    state: create

- name: Remove all members from the group
  arubanetworks.aoscx.aoscx_radius_dynauth_proxy_client_group:
    group_name: coa-group
    clients: []
    state: update

- name: Delete the proxy client group
  arubanetworks.aoscx.aoscx_radius_dynauth_proxy_client_group:
    group_name: coa-group
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the proxy client group was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def build_clients(session, ansible_module, clients):
    """Resolve the desired clients {id: coa_client_uri} map.

    Validates that every referenced CoA client exists and builds the
    numeric-id keyed map the REST API expects.
    """
    result = {}
    for index, entry in enumerate(clients, start=1):
        address = entry["address"]
        connection_type = entry["connection_type"]
        vrf = entry["vrf"]
        client = session.api.get_module(
            session,
            "RadiusDynamicAuthorizationClient",
            vrf,
            address=address,
            connection_type=connection_type,
        )
        try:
            client.get()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not find CoA client {0},{1} in VRF {2}: {3}".format(
                    address, connection_type, vrf, str(e)
                )
            )
        sep = session.api.compound_index_separator
        uri = "{0}system/vrfs/{1}/radius_dynamic_authorization_clients/" \
              "{2}{3}{4}".format(
                  session.resource_prefix, vrf, address, sep, connection_type
              )
        result[str(index)] = uri
    return result


def normalize_clients(clients):
    """Reduce a {id: uri} map to the comparable set of client URIs."""
    return frozenset((clients or {}).values())


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
            session, "RadiusDynauthProxyClientGroup", group_name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS dynamic "
                "authorization proxy client groups. Upgrade pyaoscx. Details: "
                "{0}".format(str(e))
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
    if clients is not None:
        desired = build_clients(session, ansible_module, clients)

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
        if normalize_clients(current) != normalize_clients(desired):
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
