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
module: aoscx_captive_portal_profile
version_added: "4.6.0"
short_description: Create, update or delete a Captive Portal Profile
description: >
  This module provides configuration management of Captive Portal Profiles on
  AOS-CX devices (system/captive_portal_profiles). A captive portal profile
  defines the redirect URL used to onboard clients, and can be referenced by a
  port access role. This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the captive portal profile. This is the index of the resource
      under system/captive_portal_profiles.
    required: true
    type: str
  url:
    description: Captive portal redirect URL.
    required: false
    type: str
  url_hash_key:
    description: >
      Key used to compute the hash appended to the captive portal URL.
    required: false
    type: str
  state:
    description: Create, update or delete the captive portal profile.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a captive portal profile
  aoscx_captive_portal_profile:
    name: guest-portal
    url: https://cp.example.com/guest

- name: Update the captive portal URL
  aoscx_captive_portal_profile:
    name: guest-portal
    url: https://cp.example.com/guest2
    state: update

- name: Delete a captive portal profile
  aoscx_captive_portal_profile:
    name: guest-portal
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
        url=dict(type="str", required=False, default=None),
        url_hash_key=dict(type="str", required=False, default=None),
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
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        profile = session.api.get_module(session, "CaptivePortalProfile", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support captive portal "
                "profiles. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        profile.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                profile.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete captive portal profile: {0}".format(
                        str(e)
                    )
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    supplied = {}
    for attr in ("url", "url_hash_key"):
        value = ansible_module.params[attr]
        if value is not None:
            supplied[attr] = value

    # --------------------------------------------------------------- create
    if not exists:
        profile = session.api.get_module(
            session, "CaptivePortalProfile", name, **supplied
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                profile.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create captive portal profile: "
                    "{0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- update
    changed = False
    for attr, value in supplied.items():
        if getattr(profile, attr, None) != value:
            changed = True
            setattr(profile, attr, value)
            if attr not in profile.config_attrs:
                profile.config_attrs.append(attr)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            profile.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update captive portal profile: {0}".format(
                    str(e)
                )
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
