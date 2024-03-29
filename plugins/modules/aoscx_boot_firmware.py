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
module: aoscx_boot_firmware
version_added: "2.8.0"
short_description: >
  Boots the AOS-CX switch with image present to the specified partition.
description: >
  This module boots the AOS-CX switch with the image present to the specified
  partition.
author: Aruba Networks (@ArubaNetworks)
options:
  partition_name:
    description: Name of the partition for device to boot to.
    type: str
    choices:
      - primary
      - secondary
    default: primary
    required: false
"""

EXAMPLES = """
- name: Boot to primary
  aoscx_boot_firmware:
    partition_name: primary

- name: Boot to secondary
  aoscx_boot_firmware:
    partition_name: secondary
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        partition_name=dict(
            type="str", default="primary", choices=["primary", "secondary"]
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    # Get playbook's arguments
    partition_name = ansible_module.params["partition_name"]

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

    success = device.boot_firmware(partition_name)

    # Changed
    result["changed"] = success

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
