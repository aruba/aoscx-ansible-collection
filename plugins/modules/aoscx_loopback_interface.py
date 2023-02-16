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
module: aoscx_loopback_interface
version_added: "5.0.0"
short_description: Create or Delete Loopback Interface configuration on AOS-CX
description: >
  This modules provides configuration management of Loopback Interfacess on AOS-CX
  devices.
author: Alexis La Goutte (@alagoutte)
options:
  loopback_id:
    description: >
      The ID of this Loopback interface.
    required: true
    type: str
  ipv4:
    description: >
      The IPv4 address and subnet mask in the address/mask format. The first
      entry in the list is the primary IPv4, the remaining are secondary IPv4.
      To remove an IP address pass in the list without the IP address yo wish
      to remove, and use the update state.
    type: list
    elements: str
    required: false
  vrf:
    description: >
      The VRF the Loopback interface will belong to once created. If none provided,
      the interface will be in the Default VRF. If the Loopback interface is
      created and the user wants to change the interface loopback's VRF, the user
      must delete the Loopback interface then recreate the Loopback interface in the
      desired VRF.
    type: str
    required: false
  description:
    description: Loopback description
    required: false
    type: str
  state:
    description: Create or update or delete the Loopback.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
  - name: Create Loopback Interface 100
    aoscx_loopback_interface:
      loopback_id: 100
      description: Loopback100
      ipv4:
        - 10.10.20.1/24

  - name: Create Loopback Interface 200 with vrf red
    aoscx_loopback_interface:
      loopback_id: 200
      description: Loopback200
      ipv4:
        - 10.20.20.1/24
      vrf: red

  - name: Delete Loopback Interface 100
    aoscx_loopback_interface:
      loopback_id: 100
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
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_interface import (  # NOQA
        Interface,
        L3_Interface,
    )
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_port import (  # NOQA
        Port,
    )

def main():
    module_args = dict(
        loopback_id=dict(type="str", required=True),
        state=dict(default="create", choices=["create", "delete", "update"]),
        ipv4=dict(type="list", elements="str", default=None),
        description=dict(type="str", default=None),
        vrf=dict(type="str", default=None),
    )
    if USE_PYAOSCX_SDK:
        ansible_module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True
        )

        loopback_id = ansible_module.params["loopback_id"]
        ipv4 = ansible_module.params["ipv4"]
        vrf = ansible_module.params["vrf"]
        description = ansible_module.params["description"]
        state = ansible_module.params["state"]

        # Set IP variable as empty arrays
        if ipv4 == [""]:
            ipv4 = []

        # Set variables
        loopback_interface_id = "loopback" + loopback_id
        if vrf is not None:
            vrf_name = vrf
        else:
            vrf_name = "default"

        # Set result var
        result = dict(changed=False)

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)
        session = get_pyaoscx_session(ansible_module)
        device = Device(session)

        if state == "delete":
            # Create Interface Object
            loopback_interface = device.interface(loopback_interface_id)
            # Delete it
            loopback_interface.delete()
            # Changed
            result["changed"] = True

        if state == "create" or state == "update":
            # Create Interface with incoming attributes
            loopback_interface = device.interface(loopback_interface_id)
            # Verify if interface was create
            if loopback_interface.was_modified():
                # Changed
                result["changed"] = True

            # Configure SVI
            # Verify if object was changed
            modified_op = loopback_interface.configure_loopback(
                ipv4=ipv4,
                vrf=vrf,
                description=description,
            )

            if modified_op:
                # Changed
                result["changed"] = True

        # Exit
        ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
