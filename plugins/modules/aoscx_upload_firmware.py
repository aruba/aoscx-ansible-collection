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
module: aoscx_upload_firmware
version_added: "2.8.0"
short_description: Uploads a firmware image onto the AOS-CX switch.
description: >
  This module uploads a firmware image onto the switch stored locally or it can
  also upload the firmware from an HTTP server.
author: Aruba Networks (@ArubaNetworks)
options:
  partition_name:
    description: Name of the partition for the image to be uploaded.
    type: str
    default: primary
    choices:
      - primary
      - secondary
    required: false
  firmware_file_path:
    description: File name and path for locally uploading firmware image
    type: str
    required: false
  remote_firmware_file_path:
    description: >
      HTTP server address and path for uploading firmware image, must be
      reachable through provided vrf.
    type: str
    required: false
  vrf:
    description: >
      VRF to be used to contact HTTP server, required if
      remote_firmware_file_path is provided.
    type: str
    required: false
  wait_firmware_upload:
    description: >
      If true, the result will be displayed after the firmware upload process
      is done. If false, the result must be checked on the switch by the user.
    type: bool
    required: false
    default: false
"""

EXAMPLES = """
- name: Upload firmware to primary through HTTP
  aoscx_upload_firmware:
    partition_name: primary
    remote_firmware_file_path: http://192.168.1.2:8000/TL_10_04_0030P.swi
    vrf: 'mgmt'

- name: Upload firmware to secondary through local
  aoscx_upload_firmware:
    partition_name: secondary
    firmware_file_path: /tftpboot/TL_10_04_0030A.swi
"""

RETURN = r""" # """

from time import sleep

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
        put,
        file_upload,
    )


def get_argument_spec():
    argument_spec = {
        "partition_name": {
            "type": "str",
            "required": False,
            "default": "primary",
            "choices": ["primary", "secondary"],
        },
        "firmware_file_path": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "remote_firmware_file_path": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "vrf": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "wait_firmware_upload": {
            "type": "bool",
            "required": False,
            "default": False,
        },
    }
    return argument_spec


def main():
    module_args = get_argument_spec()

    if USE_PYAOSCX_SDK:
        ansible_module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True
        )

        # Get playbook's arguments
        http_path = ansible_module.params["remote_firmware_file_path"]
        vrf = ansible_module.params["vrf"]
        partition_name = ansible_module.params["partition_name"]
        firmware_file_path = ansible_module.params["firmware_file_path"]
        partition_idx = "{0}_version".format(partition_name)
        wait = ansible_module.params["wait_firmware_upload"]

        result = dict(changed=False)

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)

        session = get_pyaoscx_session(ansible_module)
        device = Device(session)
        prev_firmware = device.get_firmware_info()

        # Bristol and Lemans have problems with library requests
        # PYAOSCX will try to user pycurl if available
        platform = prev_firmware[partition_idx].split(".")[0]
        needs_pycurl = platform in ["PL", "RL"]
        w_message = ""
        if needs_pycurl:
            import importlib.util

            pycurl_info = importlib.util.find_spec("pycurl")
            if pycurl_info is None:
                w_message = (
                    " (This platform has issues with firmware upload, "
                    "please install pycurl)"
                )

        try:
            success = device.upload_firmware(
                partition_name=partition_name,
                firmware_file_path=firmware_file_path,
                remote_firmware_file_path=http_path,
                vrf=vrf,
                try_pycurl=needs_pycurl,
            )
        except Exception as e:
            ansible_module.fail_json(msg="{0}{1}".format(e, w_message))

        if wait:
            for retry in range(10):
                try:
                    _result = device.get_firmware_status()
                except Exception:
                    # Reconnect and retry
                    session.open(
                        username=session.username(),
                        password=session.password(),
                        use_proxy=False,
                    )
                    _result = device.get_firmware_status()
                status = _result["status"]
                if status == "in_progress":
                    sleep(60)
            if status == "failure":
                ansible_module.fail_json(msg="Firmware upload failed")
            result["firmware_upload_result"] = status

        try:
            curr_firmware = device.get_firmware_info()
        except Exception:
            # Reconnect and retry
            session.open(
                username=session.username(),
                password=session.password(),
                use_proxy=False,
            )
            curr_firmware = device.get_firmware_info()

        # Changed
        result["changed"] = success and (
            prev_firmware[partition_idx] != curr_firmware[partition_idx]
        )

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)
        http_path = aruba_ansible_module.module.params[
            "remote_firmware_file_path"
        ]
        vrf = aruba_ansible_module.module.params["vrf"]
        partition_name = aruba_ansible_module.module.params["partition_name"]
        firmware_file_path = aruba_ansible_module.module.params[
            "firmware_file_path"
        ]

        unsupported_versions = [
            "10.00",
            "10.01",
            "10.02",
            "10.03",
        ]

        if http_path is not None:

            switch_current_firmware = (
                aruba_ansible_module.switch_current_firmware
            )
            for version in unsupported_versions:
                if version in switch_current_firmware:
                    aruba_ansible_module.module.fail_json(
                        msg="Minimum supported firmware version is 10.04 for"
                        " remote firmware upload, your version is {0}".format(
                            switch_current_firmware
                        )
                    )

            if vrf is None:
                aruba_ansible_module.module.fail_json(
                    msg="VRF needs to be provided in order"
                    " to upload firmware from HTTP server"
                )
            http_path_replace = http_path.replace("/", "%2F")
            http_path_encoded = http_path_replace.replace(":", "%3A")
            url = "/rest/v1/firmware?image={0}&from={1}&vrf={2}".format(
                partition_name, http_path_encoded, vrf
            )
            put(aruba_ansible_module.module, url)
        else:
            url = "/rest/v1/firmware?image={0}".format(partition_name)
            file_upload(aruba_ansible_module, url, firmware_file_path)
        result = dict(
            changed=aruba_ansible_module.changed,
            warnings=aruba_ansible_module.warnings,
        )
        result["changed"] = True
        aruba_ansible_module.module.exit_json(**result)


if __name__ == "__main__":
    main()
