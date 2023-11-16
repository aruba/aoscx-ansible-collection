#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2023 Hewlett Packard Enterprise Development LP.
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
module: aoscx_object_group
short_description: >
  Module for configuration of Object Groups in AOSCX switches.
description: >
  This module provides the functionality for configuring ACL Object Groups
  on AOSCX switches. For more detailed documentation see
  docs/aoscx_object_group.md in this repository.
version_added: "4.4.0"
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the Object Group
    required: true
    type: str
  type:
    description: Type of ACL
    required: true
    type: str
    choices:
      - ipv4
      - ipv6
      - l4port
  addresses:
    description: Entries of the Object Group type ipv4 or ipv6
    required: false
    type: dict
    suboptions:
      address:
        type: str
        required: true
        description: IPv4/6 Address
  ports:
    description: Entries of the Object Group type l4port
    required: false
    type: dict
    suboptions:
      port:
        type: str
        required: false
        description: >
          Single port number or name, also a port range specified
          by [min]-[max], example 20-100. To specify an open range
          just omit min or max; an example gt 50 the range is 51-,
          and lt 50 is -49
  state:
    description: The action taken with the current class
    required: false
    type: str
    choices:
      - create
      - update
      - delete
    default: create
"""

EXAMPLES = """
- name: Email ports
  aoscx_object_group:
    name: email_ports
    type: l4port
    ports:
      1: smtp
      2: pop3
      3: imap

- name: Some range examples
  aoscx_object_group:
    name: range_examples
    type: l4port
    ports:
      1: 21-23
      2: 100-120

- name: Implementing eq, gt, lt 22
  aoscx_object_group:
    name: eq_gt_lt_22
    type: l4port
    ports:
      1: 22
      2: 23-
      3: -21

- name: Some IPv4 addresses
  aoscx_object_group:
    name: some_ips
    type: ipv4
    addresses:
      1: 192.168.5.1/24
      2: 192.168.5.2/255.255.255.0
      3: 192.168.5.3

- name: Delete an L4 entry
  aoscx_object_group:
    name: email_ports
    type: l4port
    ports:
      1:
    state: delete

- name: Delete Object Group
  aoscx_object_group:
    name: email_ports
    type: l4port
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = {
        "name": {"type": "str", "required": True},
        "type": {
            "type": "str",
            "required": True,
            "choices": ["ipv4", "ipv6", "l4port"],
        },
        "addresses": {
            "type": "dict",
            "required": False,
            "default": None,
        },
        "ports": {
            "type": "dict",
            "required": False,
            "default": None,
        },
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
    }

    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        mutually_exclusive=[("ports", "addresses")],
    )

    result = {"changed": False}

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    state = ansible_module.params["state"]
    name = ansible_module.params["name"]
    group_type = ansible_module.params["type"]
    addresses = ansible_module.params["addresses"]
    ports = ansible_module.params["ports"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    object_group = session.api.get_module(
        session, "ObjectGroup", name, object_type=group_type
    )

    try:
        object_group.get()
        exists = True
    except Exception:
        exists = False

    modified = False
    if state == "delete" and exists:
        try:
            if addresses:
                for idx in addresses:
                    modified |= object_group.remove_ip_entry_from_group(idx)
            elif ports:
                for idx in ports:
                    modified |= object_group.remove_port_range_from_group(idx)
            else:
                object_group.delete()
                modified = True
        except Exception as e:
            ansible_module.fail_json(msg="Could not delete {0}".format(str(e)))
    else:
        if not exists:
            try:
                modified |= object_group.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create Object Group: {0}".format(str(e))
                )
        if ports:
            ports_dict = ports.copy()
            for idx, ports_data in ports_dict.items():
                if "-" in ports_data:
                    range_values = iter(ports_data.split("-"))
                    min_value = next(range_values)
                    max_value = next(range_values)
                    ports_kwargs = {}
                    if min_value.isnumeric():
                        ports_kwargs["port_min"] = int(min_value)
                    if max_value.isnumeric():
                        ports_kwargs["port_max"] = int(max_value)
                    try:
                        object_group.get()
                        modified |= object_group.update_port_range_to_group(
                            idx, **ports_kwargs
                        )
                    except Exception as e:
                        ansible_module.fail_json(msg=str(e))
                else:
                    try:
                        object_group.get()
                        modified = object_group.update_port_to_group(
                            idx, ports_data
                        )
                    except Exception as e:
                        ansible_module.fail_json(msg=str(e))
        if addresses:
            addresses_dict = addresses.copy()
            for idx, addr in addresses_dict.items():
                try:
                    object_group.get()
                    modified = object_group.update_ip_entry_to_group(
                        idx, addr
                    )
                except Exception as e:
                    ansible_module.fail_json(msg=str(e))

    if modified:
        result["changed"] = modified

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
