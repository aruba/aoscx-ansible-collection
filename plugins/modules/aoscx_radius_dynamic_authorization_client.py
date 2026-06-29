#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_radius_dynamic_authorization_client
version_added: "4.6.0"
short_description: Manage a RADIUS dynamic authorization (CoA) client.
description:
  - This module manages a RADIUS dynamic authorization (Change of
    Authorization) client on an AOS-CX switch. A client is uniquely
    identified by its VRF, address and connection type.
author: Aruba Networks (@ArubaNetworks)
notes:
  - When C(secret_key) is supplied the module reports changed on every run
    because the secret cannot be read back from the switch for comparison.
options:
  vrf:
    description: Name of the VRF the client belongs to.
    required: false
    default: default
    type: str
  address:
    description: IP address or hostname of the dynamic authorization client.
    required: true
    type: str
  connection_type:
    description: Transport used by the client.
    required: false
    default: udp
    choices:
      - udp
      - tcp
    type: str
  secret_key:
    description: Shared secret used to communicate with the client.
    required: false
    type: str
  replay_protection_enable:
    description: Enable replay protection for this client.
    required: false
    type: bool
  rfc5176_enforcement_mode:
    description: RFC 5176 enforcement mode.
    required: false
    choices:
      - strict
      - loose
    type: str
  time_window:
    description: Time window in seconds used for replay protection.
    required: false
    type: int
  state:
    description: Create, update or delete the client.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a UDP dynamic authorization client
  arubanetworks.aoscx.aoscx_radius_dynamic_authorization_client:
    vrf: default
    address: 10.14.120.70
    connection_type: udp
    secret_key: my-secret
    state: create

- name: Delete a dynamic authorization client
  arubanetworks.aoscx.aoscx_radius_dynamic_authorization_client:
    address: 10.14.120.70
    connection_type: udp
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SCALARS = [
    "secret_key",
    "replay_protection_enable",
    "rfc5176_enforcement_mode",
    "time_window",
]


def main():
    module_args = dict(
        vrf=dict(type="str", required=False, default="default"),
        address=dict(type="str", required=True),
        connection_type=dict(
            type="str", default="udp", choices=["udp", "tcp"]
        ),
        secret_key=dict(type="str", required=False, default=None, no_log=True),
        replay_protection_enable=dict(type="bool", default=None),
        rfc5176_enforcement_mode=dict(
            type="str", default=None, choices=["strict", "loose"]
        ),
        time_window=dict(type="int", default=None),
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

    vrf = ansible_module.params["vrf"]
    address = ansible_module.params["address"]
    connection_type = ansible_module.params["connection_type"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        client = session.api.get_module(
            session,
            "RadiusDynamicAuthorizationClient",
            vrf,
            address=address,
            connection_type=connection_type,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS dynamic "
                "authorization clients. Upgrade pyaoscx. Details: "
                "{0}".format(str(e))
            )
        )

    try:
        client.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    supplied = {
        attr: ansible_module.params[attr]
        for attr in SCALARS
        if ansible_module.params[attr] is not None
    }

    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                client.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete client: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        client = session.api.get_module(
            session,
            "RadiusDynamicAuthorizationClient",
            vrf,
            address=address,
            connection_type=connection_type,
            **supplied
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                client.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create client: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(client, attr, None) != value:
            setattr(client, attr, value)
            if attr not in client.config_attrs:
                client.config_attrs.append(attr)
            changed = True

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            client.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update client: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
