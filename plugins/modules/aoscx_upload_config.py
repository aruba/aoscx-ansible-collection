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
  also upload the configuration from a TFTP server. A local configuration in
  CLI format can also be pushed directly in the REST payload, without TFTP.
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
  config_cli:
    description: >
      Local file name and path of a configuration in CLI format. Its content
      is sent directly to the switch in the REST request payload, no TFTP
      server is needed. Requires a pyaoscx version providing
      C(Configuration.upload_switch_config_cli_from_local).
      If the switch refuses the CLI format upload itself (HTTP 400, 404, 405
      or 415), the task fails stating it is probably not supported by the
      switch platform or firmware version.
    type: str
    required: false
  operation:
    description: >
      Operation to perform when uploading a CLI configuration with
      C(config_cli). C(replace) replaces the whole configuration, C(merge)
      merges the CLI configuration into the existing one. Only used with
      C(config_cli). If the switch rejects commands, the task fails and the
      errors are returned. With C(replace) nothing is applied, with C(merge)
      the valid lines are applied.
    type: str
    choices:
      - replace
      - merge
    default: replace
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

- name: Replace Running Config with a local CLI file (no TFTP)
  aoscx_upload_config:
    config_name: 'running-config'
    config_cli: '/user/admin/running.cli'

- name: Merge a local CLI file into the Running Config (no TFTP)
  aoscx_upload_config:
    config_name: 'running-config'
    config_cli: '/user/admin/vlans.cli'
    operation: merge

- name: Upload a local CLI file and show the commands rejected by the switch
  aoscx_upload_config:
    config_cli: '/user/admin/running.cli'
  register: upload
  ignore_errors: true

- name: Display the switch errors
  debug:
    var: upload.errors
  when: upload is failed
"""

RETURN = r"""
errors:
  description: >
    Errors returned by the switch when a CLI configuration (C(config_cli)) is
    rejected. Each error gives the line number in the file, the configuration
    context, the command and the error message.
  returned: failure with config_cli
  type: list
  elements: dict
  sample:
    - line: 34
      context: ["configure terminal", "interface 1/1/2"]
      command: "    vlan acess 10"
      message: "Invalid input: acess"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
    pyaoscx_error_message,
)


def main():
    module_args = {
        "config_name": {"type": "str", "default": "running-config"},
        "config_json": {"type": "str", "default": None},
        "config_file": {"type": "str", "default": None},
        "remote_config_file_tftp_path": {"type": "str", "default": None},
        "vrf": {"type": "str"},
        "config_cli": {"type": "str", "default": None},
        "operation": {
            "type": "str",
            "default": "replace",
            "choices": ["replace", "merge"],
        },
    }
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[
            ("remote_config_file_tftp_path", "config_file"),
            ("remote_config_file_tftp_path", "config_json"),
            ("config_json", "config_file"),
            ("config_cli", "config_file"),
            ("config_cli", "config_json"),
            ("config_cli", "remote_config_file_tftp_path"),
        ],
    )

    # Set Variables
    tftp_path = ansible_module.params["remote_config_file_tftp_path"]
    vrf = ansible_module.params["vrf"]
    config_name = ansible_module.params["config_name"]
    config_json = ansible_module.params["config_json"]
    config_file = ansible_module.params["config_file"]
    config_cli = ansible_module.params["config_cli"]
    operation = ansible_module.params["operation"]

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

    if config_cli:
        if not hasattr(config, "upload_switch_config_cli_from_local"):
            ansible_module.fail_json(
                msg="The installed pyaoscx version does not support "
                "uploading a CLI configuration (config_cli), please upgrade "
                "pyaoscx"
            )
        try:
            success = config.upload_switch_config_cli_from_local(
                config_cli, config_name=config_name, operation=operation
            )
        except Exception as e:
            errors = getattr(e, "errors", None)
            if errors is not None:
                if operation == "merge":
                    note = "valid lines were applied"
                else:
                    note = "configuration was not applied"
                ansible_module.fail_json(
                    msg="The switch rejected the CLI configuration ({0}, "
                    "{1}): {2}".format(operation, note, e.message),
                    errors=errors,
                    changed=operation == "merge",
                )
            ansible_module.fail_json(
                msg=pyaoscx_error_message(
                    session, "Could not upload CLI configuration", e
                )
            )
    else:
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
