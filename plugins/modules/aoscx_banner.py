#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
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

try:
    from pyaoscx.device import Device

    USE_PYAOSCX_SDK = True
except ImportError:
    USE_PYAOSCX_SDK = False

if USE_PYAOSCX_SDK:
    from ansible.module_utils.basic import AnsibleModule
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )
else:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import (  # NOQA
        ArubaAnsibleModule,
    )


def main():
    module_args = dict(
        banner_type=dict(
            type="str", required=True, choices=["banner", "banner_exec"]
        ),
        banner=dict(type="str", required=False),
        state=dict(default="create", choices=["create", "delete"]),
    )
    if USE_PYAOSCX_SDK:
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

        session = get_pyaoscx_session(ansible_module)

        device = Device(session)

        if state == "delete":
            modified_op = device.delete_banner(banner_type)

        if state in ("create", "update"):
            modified_op = device.update_banner(banner, banner_type)

        # Changed
        result["changed"] = modified_op

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args)
        state = aruba_ansible_module.module.params["state"]
        banner_type = aruba_ansible_module.module.params["banner_type"]
        banner = aruba_ansible_module.module.params["banner"]

        if state == "delete":
            if (
                "other_config"
                in aruba_ansible_module.running_config["System"].keys()
            ):
                if (
                    banner_type
                    in aruba_ansible_module.running_config["System"][
                        "other_config"
                    ].keys()
                ):
                    aruba_ansible_module.running_config["System"][
                        "other_config"
                    ].pop(banner_type)
                else:
                    aruba_ansible_module.warnings.append(
                        "{0} has already been removed".format(banner_type)
                    )
            else:
                aruba_ansible_module.warnings.append(
                    "{0} has already been removed".format(banner_type)
                )

            aruba_ansible_module.module.log(
                "Banner is removed from the switch."
            )

        if state == "create":

            if banner is None:
                banner = ""

            if (
                "other_config"
                not in aruba_ansible_module.running_config["System"].keys()
            ):
                aruba_ansible_module.running_config["System"][
                    "other_config"
                ] = {}

            if (
                banner_type
                not in aruba_ansible_module.running_config["System"][
                    "other_config"
                ].keys()
            ):
                aruba_ansible_module.running_config["System"]["other_config"][
                    banner_type
                ] = banner

            elif (
                banner
                != aruba_ansible_module.running_config["System"][
                    "other_config"
                ][banner_type]
            ):
                aruba_ansible_module.running_config["System"]["other_config"][
                    banner_type
                ] = banner

            aruba_ansible_module.module.log("Banner is added to the switch.")

        aruba_ansible_module.update_switch_config()


if __name__ == "__main__":
    main()
