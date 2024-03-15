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
module: aoscx_upload_config
version_added: "2.8.0"
short_description: Uploads a configuration onto the AOS-CX switch.
description: >
  This module uploads a configuration onto the switch stored locally or it can
  also upload the configuration from a TFTP server.
author: Aruba Networks (@ArubaNetworks)
options:
  config_name:
    description: >
      Switch config file to be uploaded to, only running-config or
      startup-config can be used
    type: str
    default: 'running-config'
    required: false
  config_json:
    description: >
      JSON file name and path for locally uploading configuration, only JSON
      version of configuration can be uploaded.
    type: str
    required: false
  config_file:
    description: >
      File name and path for locally uploading configuration, only JSON version
      of configuration can be uploaded.
    type: str
    required: false
  remote_config_file_tftp_path:
    description: >
      TFTP server address and path for uploading configuration, can be JSON or
      CLI format, must be reachable through provided vrf.
    type: str
    required: false
  vrf:
    description: >
      VRF to be used to contact TFTP server, required if
      remote_output_file_tftp_path is provided.
    type: str
    required: false
"""

EXAMPLES = """
- name: Copy Running Config from local JSON file as JSON
  aoscx_upload_config:
    config_name: 'running-config'
    config_file: '/user/admin/running.json'

- name: Copy Running Config from TFTP server as JSON
  aoscx_upload_config:
    config_name: 'running-config'
    remote_config_file_tftp_path: 'tftp://192.168.1.2/running.json'
    vrf: 'mgmt'

- name: Copy CLI from TFTP Server to Running Config
  aoscx_upload_config:
    config_name: 'running-config'
    remote_config_file_tftp_path: 'tftp://192.168.1.2/running.cli'
    vrf: 'mgmt'

- name: Copy CLI from TFTP Server to Startup Config
  aoscx_upload_config:
    config_name: 'startup-config'
    remote_config_file_tftp_path: 'tftp://192.168.1.2/startup.cli'
    vrf: 'mgmt'
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = {
        "config_name": {"type": "str", "default": "running-config"},
        "config_json": {"type": "str", "default": None},
        "config_file": {"type": "str", "default": None},
        "remote_config_file_tftp_path": {"type": "str", "default": None},
        "vrf": {"type": "str"},
    }
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ("remote_config_file_tftp_path", "config_file"),
            ("remote_config_file_tftp_path", "config_json"),
            ("config_json", "config_file"),
        ],
    )

    # Set Variables
    tftp_path = ansible_module.params["remote_config_file_tftp_path"]
    vrf = ansible_module.params["vrf"]
    config_name = ansible_module.params["config_name"]
    config_json = ansible_module.params["config_json"]
    config_file = ansible_module.params["config_file"]

    result = {"changed": False}

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

    # Create an instance of the Configuration class from Device
    config = device.configuration()  # Contains action methods

    # Upload configuration file/json to switch
    success = config.upload_switch_config(
        config_name=config_name,
        config_file=config_file,
        config_json=config_json,
        vrf=vrf,
        remote_file_tftp_path=tftp_path,
    )

    # Changed
    result["changed"] = success

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
