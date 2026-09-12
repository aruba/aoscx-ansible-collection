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
module: aoscx_app_recognition
version_added: "4.6.0"
short_description: Configure global application recognition settings.
description:
  - This module configures the global application recognition settings on
    AOS-CX switches.
author: Aruba Networks (@ArubaNetworks)
options:
  enable:
    description: Enable or disable application recognition globally.
    required: false
    type: bool
  mode:
    description: Application recognition mode.
    required: false
    type: str
    choices:
      - fast
      - default
  abp_session_limit_exceed_action:
    description: Action when the ABP session limit is exceeded.
    required: false
    type: str
    choices:
      - drop-new-flows
      - log-only
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
- name: Enable application recognition
  arubanetworks.aoscx.aoscx_app_recognition:
    enable: true
    mode: default
    state: create
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

SCALARS = ["enable", "mode", "abp_session_limit_exceed_action"]


def main():
    module_args = dict(
        enable=dict(type="bool", default=None),
        mode=dict(type="str", default=None, choices=["fast", "default"]),
        abp_session_limit_exceed_action=dict(
            type="str", default=None, choices=["drop-new-flows", "log-only"]
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

    state = ansible_module.params["state"]
    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        app = session.api.get_module(session, "AppRecognition")
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support application "
                "recognition. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    app.get(selector="writable")

    if state == "delete":
        supplied = {"enable": False}
    else:
        supplied = {
            attr: ansible_module.params[attr]
            for attr in SCALARS
            if ansible_module.params[attr] is not None
        }

    changed = False
    for attr, value in supplied.items():
        if getattr(app, attr, None) != value:
            setattr(app, attr, value)
            if attr not in app.config_attrs:
                app.config_attrs.append(attr)
            changed = True

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            app.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update settings: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
