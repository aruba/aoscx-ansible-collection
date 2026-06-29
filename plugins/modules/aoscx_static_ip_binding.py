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
module: aoscx_static_ip_binding
version_added: "4.6.0"
short_description: Create, update or delete a static IP source binding.
description:
  - This module manages static IP source bindings on AOS-CX switches. A
    binding is uniquely identified by its VLAN and IP address.
author: Aruba Networks (@ArubaNetworks)
options:
  vlan:
    description: VLAN identifier the binding applies to.
    required: true
    type: int
  ip_address:
    description: IP address of the binding.
    required: true
    type: str
  address_family:
    description: Address family of the binding.
    required: false
    choices:
      - ipv4
      - ipv6
    default: ipv4
    type: str
  mac:
    description: MAC address bound to the IP address.
    required: false
    type: str
  port:
    description: Name of the interface the binding is bound to.
    required: false
    type: str
  state:
    description: Create, update or delete the binding.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a static IP binding
  arubanetworks.aoscx.aoscx_static_ip_binding:
    vlan: 10
    ip_address: 10.0.0.5
    mac: "00:11:22:33:44:55"
    port: 1/1/1
    state: create

- name: Delete a static IP binding
  arubanetworks.aoscx.aoscx_static_ip_binding:
    vlan: 10
    ip_address: 10.0.0.5
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        vlan=dict(type="int", required=True),
        ip_address=dict(type="str", required=True),
        address_family=dict(
            type="str", required=False, default="ipv4",
            choices=["ipv4", "ipv6"],
        ),
        mac=dict(type="str", required=False, default=None),
        port=dict(type="str", required=False, default=None),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    vlan = ansible_module.params["vlan"]
    ip_address = ansible_module.params["ip_address"]
    address_family = ansible_module.params["address_family"]
    mac = ansible_module.params["mac"]
    port = ansible_module.params["port"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    supplied = {
        "address_family": address_family,
    }
    vlan_obj = session.api.get_module(session, "Vlan", vlan)
    vlan_uri = vlan_obj.get_uri()
    if mac is not None:
        supplied["mac"] = mac
    if port is not None:
        interface = session.api.get_module(session, "Interface", port)
        supplied["port"] = interface.get_uri()

    try:
        binding = session.api.get_module(
            session, "StaticIpBinding", vlan, ip_address=ip_address
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support static IP bindings. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        binding.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                binding.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete binding: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        binding = session.api.get_module(
            session, "StaticIpBinding", vlan, ip_address=ip_address, **supplied
        )
        binding.vlan = vlan_uri
        if "vlan" not in binding.config_attrs:
            binding.config_attrs.append("vlan")
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                binding.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create binding: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        current = getattr(binding, attr, None)
        if attr == "address_family":
            # Not returned by the writable selector; set only on create.
            continue
        # URI references may be returned with a different prefix, or as a
        # dict mapping; compare the last path segment to avoid spurious
        # changes.
        if attr == "port" and current and value:
            if isinstance(current, dict):
                current = next(iter(current.values()), "")
            different = str(current).rstrip("/").split("/")[-1] != \
                value.rstrip("/").split("/")[-1]
        else:
            different = current != value
        if different:
            setattr(binding, attr, value)
            if attr not in binding.config_attrs:
                binding.config_attrs.append(attr)
            changed = True

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            binding.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update binding: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
