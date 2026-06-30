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
module: aoscx_mirror_endpoint
version_added: "4.6.0"
short_description: Manage remote mirror (ERSPAN) endpoints on AOS-CX
description: >
  This module provides configuration management of remote mirror endpoints
  on AOS-CX devices. A mirror endpoint defines an ERSPAN tunnel destination
  to which mirrored traffic is encapsulated and forwarded.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the mirror endpoint. This is the index of the resource under
      system/mirror_endpoints.
    required: true
    type: str
  admin:
    description: Administrative state of the mirror endpoint.
    required: false
    choices:
      - up
      - down
    type: str
  comment:
    description: A descriptive comment for the mirror endpoint.
    required: false
    type: str
  output_port:
    description: >
      List of port names through which the encapsulated mirrored traffic is
      sent. The ports must already exist on the device.
    required: false
    type: list
    elements: str
  tunnel:
    description: >
      ERSPAN tunnel parameters for the endpoint.
    required: false
    type: dict
    suboptions:
      dest_ip_address:
        description: Destination IP address of the ERSPAN tunnel.
        required: false
        type: str
      src_ip_address:
        description: Source IP address of the ERSPAN tunnel.
        required: false
        type: str
      dscp:
        description: DSCP value used for the tunnel encapsulation.
        required: false
        type: int
      id:
        description: ERSPAN session id carried in the tunnel header.
        required: false
        type: int
  state:
    description: Create, update or delete the mirror endpoint.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an ERSPAN mirror endpoint
  aoscx_mirror_endpoint:
    name: erspan-to-collector
    admin: up
    comment: collector-1
    output_port:
      - 1/1/10
    tunnel:
      src_ip_address: 10.0.0.1
      dest_ip_address: 10.0.0.2
      id: 100

- name: Update the tunnel destination of a mirror endpoint
  aoscx_mirror_endpoint:
    name: erspan-to-collector
    state: update
    tunnel:
      dest_ip_address: 10.0.0.3

- name: Delete a mirror endpoint
  aoscx_mirror_endpoint:
    name: erspan-to-collector
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        admin=dict(type="str", required=False, choices=["up", "down"]),
        comment=dict(type="str", required=False, default=None),
        output_port=dict(
            type="list", elements="str", required=False, default=None
        ),
        tunnel=dict(
            type="dict",
            required=False,
            default=None,
            options=dict(
                dest_ip_address=dict(type="str", required=False),
                src_ip_address=dict(type="str", required=False),
                dscp=dict(type="int", required=False),
                id=dict(type="int", required=False),
            ),
        ),
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
    admin = ansible_module.params["admin"]
    comment = ansible_module.params["comment"]
    output_port = ansible_module.params["output_port"]
    tunnel = ansible_module.params["tunnel"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # AnsibleModule keeps suboptions the user did not set as None; drop them
    # so they are not sent to the switch and do not cause false changes.
    if tunnel is not None:
        tunnel = {k: v for k, v in tunnel.items() if v is not None}

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        endpoint = session.api.get_module(session, "MirrorEndpoint", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support mirror endpoints. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        endpoint.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                endpoint.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete mirror endpoint: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    def materialize_ports(names):
        return [session.api.get_module(session, "Interface", n) for n in names]

    # ------------------------------------------------------- create / update
    if not exists:
        kwargs = {}
        if admin is not None:
            kwargs["admin"] = admin
        if comment is not None:
            kwargs["comment"] = comment
        if output_port is not None:
            kwargs["output_port"] = materialize_ports(output_port)
        if tunnel is not None:
            kwargs["tunnel"] = tunnel
        endpoint = session.api.get_module(
            session, "MirrorEndpoint", name, **kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                endpoint.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create mirror endpoint: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False

    if admin is not None and getattr(endpoint, "admin", None) != admin:
        changed = True
        endpoint.admin = admin

    if comment is not None and getattr(endpoint, "comment", None) != comment:
        changed = True
        endpoint.comment = comment

    # Port references are unordered; compare them by name regardless of order.
    if output_port is not None:
        current = sorted(
            p.name for p in (getattr(endpoint, "output_port", None) or [])
        )
        if current != sorted(output_port):
            changed = True
            endpoint.output_port = materialize_ports(output_port)

    # tunnel is a dictionary; only reconcile the keys provided and preserve
    # any existing keys the user did not mention.
    if tunnel is not None:
        current = dict(getattr(endpoint, "tunnel", None) or {})
        merged = dict(current)
        merged.update(tunnel)
        if merged != current:
            changed = True
            endpoint.tunnel = merged

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            endpoint.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update mirror endpoint: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
