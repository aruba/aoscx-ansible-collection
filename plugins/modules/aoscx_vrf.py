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
module: aoscx_vrf
version_added: "2.8.0"
short_description: Create or Delete VRF configuration on AOS-CX
description: >
  This modules provides configuration management of VRFs on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: The name of the VRF
    required: true
    type: str
  rd:
    description: The Route Distinguisher (RD) of the VRF (use XXXXX:YYYYY for the format)
    required: false
    type: str
  state:
    description: Create or delete the VRF.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a VRF
  aoscx_vrf:
    name: red
    state: create

- name: Create a VRF with RD
  aoscx_vrf:
    name: red
    rd: 100:1
    state: create

- name: Delete a VRF
  aoscx_vrf:
    name: red
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def get_argument_spec():
    argument_spec = {
        "name": {
            "type": "str",
            "required": True,
        },
        "rd": {
            "type": "str",
            "required": False,
        },

        "state": {
            "type": "str",
            "default": "create",
            "choices": [
                "create",
                "delete",
            ],
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
    )

    # Get playbook's arguments
    vrf_name = ansible_module.params["name"]
    state = ansible_module.params["state"]
    rd = ansible_module.params["rd"]

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)
    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    # device = Device(session)
    Vrf = session.api.get_module_class(session, "Vrf")
    vrf = Vrf(session, vrf_name)
    modified = False

    try:
        vrf.get()
        vrf_exists = True
    except Exception:
        vrf_exists = False

    if state == "delete":
        if vrf_exists:
            vrf.delete()
            # Changed
            modified = True

    if state == "create":

        # Create VRF with incoming attributes
        if not vrf_exists:
            # Changed
            vrf.create()
            modified = True
        try:
            vrf.apply()
        except Exception as e:
            ansible_module.fail_json(msg=str(e))

        # Configure RD (Route Distinguisher)
        if rd:
           modified |= vrf.rd != rd
           vrf.rd = rd
           vrf.apply()

    result["changed"] = modified
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
