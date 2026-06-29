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
module: aoscx_radius_dynamic_authorization
version_added: "4.6.0"
short_description: Configure global RADIUS dynamic authorization (CoA).
description:
  - This module configures the global RADIUS dynamic authorization (Change of
    Authorization) settings on AOS-CX switches.
author: Aruba Networks (@ArubaNetworks)
options:
  enable:
    description: Enable or disable RADIUS dynamic authorization globally.
    required: false
    type: bool
  tcp_port:
    description: TCP port used by the dynamic authorization server.
    required: false
    type: int
  udp_port:
    description: UDP port used by the dynamic authorization server.
    required: false
    type: int
  state:
    description: Update or reset the global settings.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Enable RADIUS dynamic authorization
  arubanetworks.aoscx.aoscx_radius_dynamic_authorization:
    enable: true
    state: create

- name: Disable RADIUS dynamic authorization
  arubanetworks.aoscx.aoscx_radius_dynamic_authorization:
    enable: false
    state: update
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SCALARS = ["enable", "tcp_port", "udp_port"]


def main():
    module_args = dict(
        enable=dict(type="bool", default=None),
        tcp_port=dict(type="int", default=None),
        udp_port=dict(type="int", default=None),
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
        dynauth = session.api.get_module(
            session, "RadiusDynamicAuthorization"
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS dynamic "
                "authorization. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    dynauth.get()
    current = dict(dynauth.radius_dynamic_authorization)

    if state == "delete":
        supplied = {"enable": False}
    else:
        supplied = {
            attr: ansible_module.params[attr]
            for attr in SCALARS
            if ansible_module.params[attr] is not None
        }

    new_config = dict(current)
    new_config.update(supplied)

    changed = new_config != current
    if changed:
        dynauth.radius_dynamic_authorization = new_config
        if not ansible_module.check_mode:
            try:
                dynauth.apply()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not update settings: {0}".format(str(e))
                )

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
