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
module: aoscx_checkpoint
version_added: "2.8.0"
short_description: >
  Creates a new checkpoint or copies an existing checkpoint to AOS-CX switch
  config.
description: >
  This module creates a new checkpoint or copies existing checkpoint to the
  running or startup config of an AOS-CX switch.
author: Aruba Networks (@ArubaNetworks)
options:
  source_config:
    description: >
      Name of the source configuration from which checkpoint needs to be
      created or copied.
    type: str
    required: false
    default: running-config
  destination_config:
    description: Name of the destination configuration or name of checkpoint.
    type: str
    required: false
    default: startup-config
"""

EXAMPLES = """
- name: Copy running-config to startup-config
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'startup-config'

- name: Copy startup-config to running-config
  aoscx_checkpoint:
    source_config: 'startup-config'
    destination_config: 'running-config'

- name: Copy running-config to backup checkpoint
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'checkpoint_20200128'
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
        put,
    )


def main():
    module_args = dict(
        source_config=dict(type="str", default="running-config"),
        destination_config=dict(type="str", default="startup-config"),
    )
    if USE_PYAOSCX_SDK:
        ansible_module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True
        )

        # Get playbook's arguments
        source_config = ansible_module.params["source_config"]
        destination_config = ansible_module.params["destination_config"]

        result = dict(changed=False)

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)

        session = get_pyaoscx_session(ansible_module)

        device = Device(session)

        # Create a Configuration Object
        config = device.configuration()
        success = config.create_checkpoint(source_config, destination_config)

        # Changed
        result["changed"] = success

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)

        source_config = aruba_ansible_module.module.params["source_config"]
        destination_config = aruba_ansible_module.module.params[
            "destination_config"
        ]

        url = "/rest/v1/fullconfigs/{0}?from=/rest/v1/fullconfigs/{1}".format(
            destination_config, source_config
        )
        put(aruba_ansible_module.module, url)
        result = dict(
            changed=aruba_ansible_module.changed,
            warnings=aruba_ansible_module.warnings,
        )
        result["changed"] = True
        aruba_ansible_module.module.exit_json(**result)


if __name__ == "__main__":
    main()
