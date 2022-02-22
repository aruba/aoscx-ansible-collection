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
      Config file or checkpoint to be uploaded to. When using TFTP only
      running-config or startup-config can be used.
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
    config_json: '/user/admin/running.json'

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

import json

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
        config_name=dict(type="str", default="running-config"),
        config_json=dict(type="str", default=None),
        config_file=dict(type="str", default=None),
        remote_config_file_tftp_path=dict(type="str", default=None),
        vrf=dict(type="str"),
    )
    if USE_PYAOSCX_SDK:
        ansible_module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True
        )

        # Set Variables
        tftp_path = ansible_module.params["remote_config_file_tftp_path"]
        vrf = ansible_module.params["vrf"]
        config_name = ansible_module.params["config_name"]
        config_json = ansible_module.params["config_json"]
        config_file = ansible_module.params["config_file"]

        result = dict(changed=False)

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)

        session = get_pyaoscx_session(ansible_module)

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

    # Use Older Version
    else:

        aruba_ansible_module = ArubaAnsibleModule(
            module_args=module_args, store_config=False
        )

        tftp_path = aruba_ansible_module.module.params[
            "remote_config_file_tftp_path"
        ]
        vrf = aruba_ansible_module.module.params["vrf"]
        config_name = aruba_ansible_module.module.params["config_name"]
        config_json = aruba_ansible_module.module.params["config_json"]
        config_file = aruba_ansible_module.module.params["config_file"]

        if tftp_path is not None:
            if vrf is None:
                aruba_ansible_module.module.fail_json(
                    msg="VRF needs to be provided in order to TFTP"
                    " the configuration onto the switch"
                )
            tftp_path_replace = tftp_path.replace("/", "%2F")
            tftp_path_encoded = tftp_path_replace.replace(":", "%3A")
            if config_name not in ("running-config", "startup-config"):
                aruba_ansible_module.module.fail_json(
                    msg="Only running-config or startup-config "
                    "can be uploaded using TFTP"
                )
            aruba_ansible_module.tftp_switch_config_from_remote_location(
                tftp_path_encoded, config_name, vrf
            )
        else:
            if config_json:
                with open(config_json) as json_file:
                    config_json = json.load(json_file)

            if config_file:
                with open(config_file) as json_file:
                    config_json = json.load(json_file)

            aruba_ansible_module.upload_switch_config(config_json, config_name)

        result = dict(
            changed=aruba_ansible_module.changed,
            warnings=aruba_ansible_module.warnings,
        )
        result["changed"] = True
        aruba_ansible_module.module.exit_json(**result)


if __name__ == "__main__":
    main()
