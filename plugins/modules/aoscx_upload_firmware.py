#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'certified'
}

DOCUMENTATION = '''
---
module: aoscx_upload_firmware
version_added: "2.8"
short_description: Uploads a firmware image onto the AOS-CX switch.
description:
  - This module uploads a firmware image onto the switch stored locally or it can also upload
    the firmware from an HTTP server.
author: Aruba Networks (@ArubaNetworks)
options:
  partition_name:
    description: Name of the partition for the image to be uploaded.
    type: str
    default: 'primary'
    choices: ['primary', 'secondary']
    required: false
  firmware_file_path:
    description: File name and path for locally uploading firmware image
    type: str
    required: false
  remote_firmware_file_path:
    description: "HTTP server address and path for uploading firmware image,
      must be reachable through provided vrf
      ex) http://192.168.1.2:8000/TL_10_04_0030A.swi"
    type: str
    required: false
  vrf:
    description: VRF to be used to contact HTTP server, required if remote_firmware_file_path is provided
    type: str
    required: false
'''  # NOQA

EXAMPLES = '''
- name: Upload firmware to primary through HTTP
  aoscx_upload_firmware:
    partition_name: 'primary'
    remote_firmware_file_path: 'http://192.168.1.2:8000/TL_10_04_0030P.swi'
    vrf: 'mgmt'

- name: Upload firmware to secondary through local
  aoscx_upload_firmware:
    partition_name: 'secondary'
    firmware_file_path: '/tftpboot/TL_10_04_0030A.swi'
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule, \
    put, file_upload


def main():
    module_args = dict(
        partition_name=dict(type='str', default='primary',
                            choices=['primary', 'secondary']),
        firmware_file_path=dict(type='str', default=None),
        remote_firmware_file_path=dict(type='str', default=None),
        vrf=dict(type='str', default=None)
    )
    aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)
    http_path = aruba_ansible_module.module.params['remote_firmware_file_path']
    vrf = aruba_ansible_module.module.params['vrf']
    partition_name = aruba_ansible_module.module.params['partition_name']
    firmware_file_path = \
        aruba_ansible_module.module.params['firmware_file_path']

    unsupported_versions = [
        "10.00",
        "10.01",
        "10.02",
        "10.03",
    ]

    if http_path is not None:

        switch_current_firmware = aruba_ansible_module.switch_current_firmware
        for version in unsupported_versions:
            if version in switch_current_firmware:
                aruba_ansible_module.module.fail_json(
                    msg="Minimum supported firmware version is 10.04 for"
                        " remote firmware upload, your version is {firmware}"
                        "".format(firmware=switch_current_firmware))

        if vrf is None:
            aruba_ansible_module.module.fail_json(
                msg="VRF needs to be provided in order"
                    " to upload firmware from HTTP server")
        http_path_replace = http_path.replace("/", "%2F")
        http_path_encoded = http_path_replace.replace(":", "%3A")
        url = '/rest/v1/firmware?image={part}&from={path}&vrf={vrf}'\
            .format(part=partition_name,
                    path=http_path_encoded,
                    vrf=vrf)
        put(aruba_ansible_module.module, url)
    else:
        url = '/rest/v1/firmware?image={part}'.format(part=partition_name)
        file_upload(aruba_ansible_module, url, firmware_file_path)
    result = dict(changed=aruba_ansible_module.changed,
                  warnings=aruba_ansible_module.warnings)
    result["changed"] = True
    aruba_ansible_module.module.exit_json(**result)


if __name__ == '__main__':
    main()
