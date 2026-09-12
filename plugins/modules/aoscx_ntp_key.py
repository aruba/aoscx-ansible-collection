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
module: aoscx_ntp_key
version_added: "4.6.0"
short_description: Create, update or delete an NTP authentication key
description: >
  This module provides configuration management of NTP authentication keys on
  AOS-CX devices (system/ntp_keys). An NTP key is identified by a numeric
  key_id and is used to authenticate NTP associations.
author: Aruba Networks (@ArubaNetworks)
notes:
  - When C(key_password) is supplied the module reports changed on every run
    because the secret cannot be read back from the switch for comparison.
options:
  key_id:
    description: >
      Numeric identifier of the NTP authentication key. This is the index of
      the resource under system/ntp_keys.
    required: true
    type: int
  key_password:
    description: >
      Authentication password of the NTP key. Required when creating the key.
    required: false
    type: str
  key_type:
    description: Digest algorithm used by the key.
    required: false
    type: str
    choices:
      - md5
      - sha1
      - aes128
  trust_enable:
    description: Whether the key is trusted for NTP authentication.
    required: false
    type: bool
  state:
    description: Create, update or delete the NTP key.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an NTP authentication key
  aoscx_ntp_key:
    key_id: 60001
    key_password: my_secret_key
    key_type: md5
    trust_enable: true

- name: Delete an NTP authentication key
  aoscx_ntp_key:
    key_id: 60001
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.ntp_key import NtpKey

    HAS_PYAOSCX_NTP = True
except ImportError:
    HAS_PYAOSCX_NTP = False

if HAS_PYAOSCX_NTP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        key_id=dict(type="int", required=True),
        key_password=dict(type="str", required=False, no_log=True),
        key_type=dict(
            type="str", required=False, choices=["md5", "sha1", "aes128"]
        ),
        trust_enable=dict(type="bool", required=False),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[("state", "create", ["key_password"])],
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_NTP:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support NTP keys. "
                "Upgrade pyaoscx."
            )
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    key_id = ansible_module.params["key_id"]
    key_password = ansible_module.params["key_password"]
    key_type = ansible_module.params["key_type"]
    trust_enable = ansible_module.params["trust_enable"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    ntp_key = NtpKey(session, key_id)
    try:
        ntp_key.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            ntp_key.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    kwargs = {}
    if key_password is not None:
        kwargs["key_password"] = key_password
    if key_type is not None:
        kwargs["key_type"] = key_type
    if trust_enable is not None:
        kwargs["trust_enable"] = trust_enable

    if exists:
        for key, value in kwargs.items():
            setattr(ntp_key, key, value)
    else:
        ntp_key = NtpKey(session, key_id, **kwargs)
    result["changed"] = ntp_key.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
