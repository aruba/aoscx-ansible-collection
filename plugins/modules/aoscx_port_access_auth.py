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
module: aoscx_port_access_auth
version_added: "4.6.0"
short_description: Configure port access authentication on an interface.
description:
  - This module configures per-method (dot1x, mac-auth) port access
    authentication settings on an AOS-CX interface.
author: Aruba Networks (@ArubaNetworks)
options:
  interface:
    description: Name of the interface to configure.
    required: true
    type: str
  authentication_method:
    description: Authentication method to configure.
    required: true
    type: str
  auth_enable:
    description: Enable authentication for this method.
    required: false
    type: bool
  reauth_enable:
    description: Enable periodic reauthentication.
    required: false
    type: bool
  reauth_period:
    description: Reauthentication period in seconds.
    required: false
    type: int
  cached_reauth_enable:
    description: Enable cached reauthentication.
    required: false
    type: bool
  cached_reauth_period:
    description: Cached reauthentication period in seconds.
    required: false
    type: int
  eapol_timeout:
    description: EAPOL timeout in seconds.
    required: false
    type: int
  max_retries:
    description: Maximum number of authentication retries.
    required: false
    type: int
  max_requests:
    description: Maximum number of EAPOL requests.
    required: false
    type: int
  quiet_period:
    description: Quiet period in seconds before retrying authentication.
    required: false
    type: int
  discovery_period:
    description: Discovery period in seconds.
    required: false
    type: int
  state:
    description: Configure or reset the authentication configuration.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Configure dot1x authentication on an interface
  arubanetworks.aoscx.aoscx_port_access_auth:
    interface: 1/1/1
    authentication_method: dot1x
    auth_enable: true
    reauth_enable: true
    reauth_period: 86400
    cached_reauth_enable: true
    cached_reauth_period: 86400
    eapol_timeout: 10
    max_requests: 1
    state: create

- name: Reset mac-auth configuration
  arubanetworks.aoscx.aoscx_port_access_auth:
    interface: 1/1/1
    authentication_method: mac-auth
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SCALARS = [
    "auth_enable",
    "reauth_enable",
    "reauth_period",
    "cached_reauth_enable",
    "cached_reauth_period",
    "eapol_timeout",
    "max_retries",
    "max_requests",
    "quiet_period",
    "discovery_period",
]


def main():
    module_args = dict(
        interface=dict(type="str", required=True),
        authentication_method=dict(type="str", required=True),
        auth_enable=dict(type="bool", default=None),
        reauth_enable=dict(type="bool", default=None),
        reauth_period=dict(type="int", default=None),
        cached_reauth_enable=dict(type="bool", default=None),
        cached_reauth_period=dict(type="int", default=None),
        eapol_timeout=dict(type="int", default=None),
        max_retries=dict(type="int", default=None),
        max_requests=dict(type="int", default=None),
        quiet_period=dict(type="int", default=None),
        discovery_period=dict(type="int", default=None),
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

    interface = ansible_module.params["interface"]
    method = ansible_module.params["authentication_method"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        config = session.api.get_module(
            session,
            "PortAccessAuthConfiguration",
            interface,
            authentication_method=method,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support port access auth "
                "configurations. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    config.get(selector="writable")

    supplied = {
        attr: ansible_module.params[attr]
        for attr in SCALARS
        if ansible_module.params[attr] is not None
    }

    changed = False
    for attr, value in supplied.items():
        new_value = None if state == "delete" else value
        if getattr(config, attr, None) != new_value:
            setattr(config, attr, new_value)
            if attr not in config.config_attrs:
                config.config_attrs.append(attr)
            changed = True

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            config.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update configuration: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
