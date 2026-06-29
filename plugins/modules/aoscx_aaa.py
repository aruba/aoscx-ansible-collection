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
module: aoscx_aaa
version_added: "4.6.0"
short_description: Configure global AAA settings.
description:
  - This module configures the global AAA settings on AOS-CX switches,
    including the RADIUS server groups used for port access and the AAA
    fail-through behaviour.
author: Aruba Networks (@ArubaNetworks)
notes:
  - When C(mac_auth_password) is supplied the module reports changed on every
    run because the secret cannot be read back from the switch for comparison.
options:
  portaccess_accounting_radius_server_group:
    description: >
      RADIUS server group used to send port access accounting updates.
    required: false
    type: str
  portaccess_local_accounting_enable:
    description: Enable local accounting for port access.
    required: false
    type: bool
  dot1x_radius_server_group:
    description: RADIUS server group used for 802.1X authentication.
    required: false
    type: str
  dot1x_auth_enable:
    description: Enable global 802.1X authentication.
    required: false
    type: bool
  dot1x_remote_auth_method:
    description: Remote authentication method used for 802.1X.
    required: false
    choices:
      - eap-radius
    type: str
  mac_auth_radius_server_group:
    description: RADIUS server group used for MAC authentication.
    required: false
    type: str
  mac_auth_enable:
    description: Enable global MAC authentication.
    required: false
    type: bool
  mac_auth_address_format:
    description: MAC address format used for MAC authentication.
    required: false
    choices:
      - no-delimiter
      - single-dash
      - multi-dash
      - multi-colon
      - no-delimiter-uppercase
      - single-dash-uppercase
      - multi-dash-uppercase
      - multi-colon-uppercase
    type: str
  mac_auth_radius_auth_method:
    description: RADIUS authentication method used for MAC authentication.
    required: false
    choices:
      - chap
      - pap
    type: str
  mac_auth_password:
    description: Password used for MAC authentication.
    required: false
    type: str
  accounting_fail_through:
    description: Enable fail-through for accounting.
    required: false
    type: bool
  authorization_fail_through:
    description: Enable fail-through for authorization.
    required: false
    type: bool
  fail_through:
    description: Enable fail-through for authentication.
    required: false
    type: bool
  state:
    description: Update or reset the global AAA settings.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Set the port access accounting server group
  arubanetworks.aoscx.aoscx_aaa:
    portaccess_accounting_radius_server_group: clearpass
    portaccess_local_accounting_enable: true
    state: create

- name: Clear the port access accounting server group
  arubanetworks.aoscx.aoscx_aaa:
    portaccess_accounting_radius_server_group: ""
    state: update
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SCALARS = [
    "portaccess_accounting_radius_server_group",
    "portaccess_local_accounting_enable",
    "dot1x_radius_server_group",
    "dot1x_auth_enable",
    "dot1x_remote_auth_method",
    "mac_auth_radius_server_group",
    "mac_auth_enable",
    "mac_auth_address_format",
    "mac_auth_radius_auth_method",
    "mac_auth_password",
    "accounting_fail_through",
    "authorization_fail_through",
    "fail_through",
]


def main():
    module_args = dict(
        portaccess_accounting_radius_server_group=dict(
            type="str", default=None
        ),
        portaccess_local_accounting_enable=dict(type="bool", default=None),
        dot1x_radius_server_group=dict(type="str", default=None),
        dot1x_auth_enable=dict(type="bool", default=None),
        dot1x_remote_auth_method=dict(
            type="str", default=None, choices=["eap-radius"]
        ),
        mac_auth_radius_server_group=dict(type="str", default=None),
        mac_auth_enable=dict(type="bool", default=None),
        mac_auth_address_format=dict(
            type="str",
            default=None,
            choices=[
                "no-delimiter",
                "single-dash",
                "multi-dash",
                "multi-colon",
                "no-delimiter-uppercase",
                "single-dash-uppercase",
                "multi-dash-uppercase",
                "multi-colon-uppercase",
            ],
        ),
        mac_auth_radius_auth_method=dict(
            type="str", default=None, choices=["chap", "pap"]
        ),
        mac_auth_password=dict(type="str", default=None, no_log=True),
        accounting_fail_through=dict(type="bool", default=None),
        authorization_fail_through=dict(type="bool", default=None),
        fail_through=dict(type="bool", default=None),
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

    state = ansible_module.params["state"]
    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        aaa = session.api.get_module(session, "Aaa")
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support the global AAA "
                "object. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    aaa.get()
    current = dict(aaa.aaa)

    supplied = {
        attr: ansible_module.params[attr]
        for attr in SCALARS
        if ansible_module.params[attr] is not None
    }

    if state == "delete":
        new_values = {}
        for attr in supplied:
            if isinstance(current.get(attr), bool):
                new_values[attr] = False
            else:
                new_values[attr] = ""
        supplied = new_values

    new_config = dict(current)
    new_config.update(supplied)

    changed = new_config != current
    if changed:
        aaa.aaa = new_config
        if not ansible_module.check_mode:
            try:
                aaa.apply()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not update AAA settings: {0}".format(str(e))
                )

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
