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
module: aoscx_snmpv3_user
version_added: "4.6.0"
short_description: Create, update or delete an SNMPv3 user
description: >
  This module provides configuration management of SNMPv3 users on AOS-CX
  devices (system/snmpv3_users). Requires REST API v10.16
  (set ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
notes:
  - When C(auth_pass_phrase) or C(priv_pass_phrase) are supplied the module
    reports changed on every run because the secret cannot be read back from
    the switch for comparison.
options:
  user_name:
    description: Name of the SNMPv3 user. Index under system/snmpv3_users.
    required: true
    type: str
  access_level:
    description: Access level granted to the user.
    required: false
    type: str
    choices:
      - ro
      - rw
  auth_protocol:
    description: Authentication protocol of the user.
    required: false
    type: str
    choices:
      - md5
      - sha
      - sha224
      - sha256
      - sha384
      - sha512
      - none
  auth_pass_phrase:
    description: Authentication pass phrase. Required when auth_protocol is
      not none.
    required: false
    type: str
  priv_protocol:
    description: Privacy protocol of the user.
    required: false
    type: str
    choices:
      - aes
      - aes192
      - aes256
      - des
      - none
  priv_pass_phrase:
    description: Privacy pass phrase. Required when priv_protocol is not none.
    required: false
    type: str
  remote_engine_id:
    description: Remote engine ID for the user.
    required: false
    type: str
  state:
    description: Create, update or delete the SNMPv3 user.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an SNMPv3 user with auth and priv
  aoscx_snmpv3_user:
    user_name: monitor
    access_level: ro
    auth_protocol: sha
    auth_pass_phrase: my_auth_secret
    priv_protocol: aes
    priv_pass_phrase: my_priv_secret

- name: Delete an SNMPv3 user
  aoscx_snmpv3_user:
    user_name: monitor
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.snmpv3_user import Snmpv3User

    HAS_PYAOSCX_SNMP = True
except ImportError:
    HAS_PYAOSCX_SNMP = False

if HAS_PYAOSCX_SNMP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        user_name=dict(type="str", required=True),
        access_level=dict(type="str", required=False, choices=["ro", "rw"]),
        auth_protocol=dict(
            type="str",
            required=False,
            choices=[
                "md5",
                "sha",
                "sha224",
                "sha256",
                "sha384",
                "sha512",
                "none",
            ],
        ),
        auth_pass_phrase=dict(type="str", required=False, no_log=True),
        priv_protocol=dict(
            type="str",
            required=False,
            choices=["aes", "aes192", "aes256", "des", "none"],
        ),
        priv_pass_phrase=dict(type="str", required=False, no_log=True),
        remote_engine_id=dict(type="str", required=False),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_SNMP:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support SNMP. Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    user_name = ansible_module.params["user_name"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    user = Snmpv3User(session, user_name)
    try:
        user.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            user.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    kwargs = {}
    for field in (
        "access_level",
        "auth_protocol",
        "auth_pass_phrase",
        "priv_protocol",
        "priv_pass_phrase",
        "remote_engine_id",
    ):
        value = ansible_module.params[field]
        if value is not None:
            kwargs[field] = value

    for key, value in kwargs.items():
        setattr(user, key, value)
    result["changed"] = user.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
