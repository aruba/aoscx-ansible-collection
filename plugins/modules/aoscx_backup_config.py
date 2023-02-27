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
module: aoscx_backup_config
version_added: "2.8.0"
short_description: Download an existing configuration from AOS-CX switch.
description: >
  This module downloads an existing configuration from AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  config_name:
    description: >
      Config file or checkpoint to be downloaded. When using TFTP only
      running-config or startup-config can be used.
    type: str
    default: running-config
    required: false
  output_file:
    description: >
      File name and path for locally downloading configuration, only JSON
      version of configuration will be downloaded.
    type: str
    required: false
  remote_output_file_tftp_path:
    description: >
      TFTP server address and path for copying off configuration, must be
      reachable through provided vrf.
    type: str
    required: false
  config_type:
    description: >
      Configuration type to be downloaded, JSON or CLI version of the config.
    type: str
    choices:
      - json
      - cli
    default: json
    required: false
  vrf:
    description: >
      VRF to be used to contact TFTP server, required if
      remote_output_file_tftp_path is provided.
    type: str
    required: false
  sort_json:
    description: flag whether or not to sort JSON config
    type: bool
    default: True
    required: false
"""

EXAMPLES = """
 - name: Copy Running Config to local as JSON
   aoscx_backup_config:
     config_name: running-config
     output_file: /home/admin/running-config.json

 - name: Copy Startup Config to local as JSON
   aoscx_backup_config:
     config_name: startup-config
     output_file: /home/admin/startup-config.json

 - name: Copy Checkpoint Config to local as JSON
   aoscx_backup_config:
     config_name: checkpoint1
     output_file: /home/admin/checkpoint1.json

 - name: Copy Running Config to TFTP server as JSON
   aoscx_backup_config:
     config_name: running-config
     remote_output_file_tftp_path: tftp://192.168.1.2/running.json
     config_type: json
     vrf: mgmt

 - name: Copy Running Config to TFTP server as CLI
   aoscx_backup_config:
     config_name: running-config
     remote_output_file_tftp_path: tftp://192.168.1.2/running.cli
     config_type: cli
     vrf: mgmt

 - name: Copy Startup Config to TFTP server as CLI
   aoscx_backup_config:
     config_name: startup-config
     remote_output_file_tftp_path: tftp://192.168.1.2/startup.cli
     config_type: cli
     vrf: mgmt
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        config_name=dict(type="str", default="running-config"),
        output_file=dict(type="str", default=None),
        remote_output_file_tftp_path=dict(type="str", default=None),
        config_type=dict(type="str", default="json", choices=["json", "cli"]),
        vrf=dict(type="str"),
        sort_json=dict(type="bool", default=True),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    # Get playbook's arguments
    tftp_path = ansible_module.params["remote_output_file_tftp_path"]
    vrf = ansible_module.params["vrf"]
    config_name = ansible_module.params["config_name"]
    config_type = ansible_module.params["config_type"]
    config_file = ansible_module.params["output_file"]

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

    # Create a Configuration Object
    config = device.configuration()
    success = config.backup_configuration(
        config_name=config_name,
        output_file=config_file,
        vrf=vrf,
        config_type=config_type,
        remote_file_tftp_path=tftp_path,
    )

    # Changed
    result["changed"] = success

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
