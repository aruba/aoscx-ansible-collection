#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2023 Hewlett Packard Enterprise Development LP.
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
module: aoscx_banner
version_added: "2.8.0"
short_description: Create or Delete Banner configuration on AOS-CX
description: >
  This modules provides configuration management of Banner on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  banner_type:
    description: Type of banner being configured on the switch.
    required: true
    choices:
      - banner
      - banner_exec
    type: str
  state:
    description: Create or Delete Banner on the switch.
    default: create
    choices:
      - create
      - delete
    required: false
    type: str
  banner:
    description : String to be configured as the banner.
    type: str
"""

EXAMPLES = """
- name: Adding or Updating Banner
  aoscx_banner:
    banner_type: banner
    banner: "Aruba Rocks!"

- name: Delete Banner
  aoscx_banner:
    banner_type: banner
    state: delete

- name: Delete Exec Banner
  aoscx_banner:
    banner_type: banner_exec
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        banner_type=dict(
            type="str", required=True, choices=["banner", "banner_exec"]
        ),
        banner=dict(type="str", required=False),
        state=dict(default="create", choices=["create", "delete"]),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    # Get playbook's arguments
    state = ansible_module.params["state"]
    banner_type = ansible_module.params["banner_type"]
    banner = ansible_module.params["banner"]

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        from pyaoscx.device import Device
    except Exception as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    device = Device(session)

    if state == "delete":
        modified_op = device.delete_banner(banner_type)

    if state in ("create", "update"):
        modified_op = device.update_banner(banner, banner_type)

    # Changed
    result["changed"] = modified_op

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
