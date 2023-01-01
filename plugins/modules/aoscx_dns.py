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
module: aoscx_dns
version_added: "2.8.0"
short_description: Create or Delete DNS Client configuration on AOS-CX
description: >
  This modules provides configuration management of DNS on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  mgmt_nameservers:
    description: >
      Primary and secondary nameservers on mgmt interface. The key of the
      dictionary is primary or secondary and value is the respective IP
      address.
    type: dict
    required: false
  domain_name:
    description: >
      Domain name used for name resolution by the DNS client, if
      'domain_list' is not configured.
    type: str
    required: false
  domain_list:
    description: >
      Domain list names to be used for address resolution, keyed by the
      resolution priority order.
    type: dict
    required: false
  name_servers:
    description: >
      Name servers to be used for address resolution, keyed by the resolution
      priority order.
    type: dict
    required: false
  vrf:
    description: VRF name where DNS configuration is added.
    type: str
    required: true
  host_v4_address_mapping:
    description: >
      List of static host address configurations and the IPv4 address
      associated with them.
    type: dict
    required: false
  host_v6_address_mapping:
    description: >
      List of static host address configurations and the IPv6 address
      associated with them.
    type: dict
    required: false
  state:
    description: Create or Update or Delete DNS configuration on the switch.
    default: create
    choices:
      - create
      - update
      - delete
    type: str
    required: false
"""

EXAMPLES = """
---
- name: DNS configuration creation
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.10"
      "Secondary": "10.10.2.10"
    domain_name: "hpe.com"
    domain_list:
      0: "hp.com"
      1: "aru.com"
      2: "sea.com"
    name_servers:
      0: "4.4.4.8"
      1: "4.4.4.10"
    host_v4_address_mapping:
      "host1": "5.5.44.5"
      "host2": "2.2.44.2"
    vrf: "green"

- name: DNS configuration update
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    domain_name: "hpe.com"
    domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: update

- name: DNS configuration deletion
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    domain_name: "hp.com"
    domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: delete
"""

RETURN = r""" # """


from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.dns import Dns
    from pyaoscx.vrf import Vrf

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "mgmt_nameservers": {
            "type": "dict",
            "required": False,
        },
        "domain_name": {
            "type": "str",
            "required": False,
        },
        "domain_list": {
            "type": "dict",
            "required": False,
        },
        "name_servers": {
            "type": "dict",
            "required": False,
        },
        "vrf": {
            "type": "str",
            "required": True,
        },
        "host_v4_address_mapping": {
            "type": "dict",
            "required": False,
        },
        "host_v6_address_mapping": {
            "type": "dict",
            "required": False,
        },
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
    }

    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(), supports_check_mode=True
    )

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    result = {"changed": False}

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    # Set Variables
    mgmt_nameservers = ansible_module.params["mgmt_nameservers"]
    domain_name = ansible_module.params["domain_name"]
    domain_list = ansible_module.params["domain_list"]
    vrf_name = ansible_module.params["vrf"]
    name_servers = ansible_module.params["name_servers"]
    host_v4_address_mapping = ansible_module.params["host_v4_address_mapping"]
    host_v6_address_mapping = ansible_module.params["host_v6_address_mapping"]
    state = ansible_module.params["state"]

    session = get_pyaoscx_session(ansible_module)

    vrf = Vrf(session, vrf_name)

    try:
        vrf.get()
    except Exception:
        ansible_module.fail_json(msg="VRF {0} doesn't exist.".format(vrf_name))

    dns = Dns(session, vrf_name)

    modified_op = False
    modified_op2 = False

    if state == "delete":
        if mgmt_nameservers != {}:
            modified_op = dns.delete_mgmt_nameservers(session)

        dns.delete_dns(
            domain_name,
            domain_list,
            name_servers,
            host_v4_address_mapping,
            host_v6_address_mapping,
        )
        modified_op2 = dns.was_modified()
        result["changed"] = modified_op or modified_op2

    else:
        dns = Dns(
            session,
            vrf_name=vrf_name,
            domain_name=domain_name,
            domain_list=domain_list,
            domain_servers=name_servers,
            host_v4_address_mapping=host_v4_address_mapping,
            host_v6_address_mapping=host_v6_address_mapping,
        )

        modified_op = dns.was_modified()

        # Set MGMT name servers
        if mgmt_nameservers != {}:
            primary = None
            secondary = None
            # Get Primary and Secondary
            for key, value in mgmt_nameservers.items():
                if key.lower() == "primary":
                    primary = value
                elif key.lower() == "secondary":
                    secondary = value
            modified_op2 = dns.setup_mgmt_nameservers(
                session, primary=primary, secondary=secondary
            )

        result["changed"] = modified_op or modified_op2

    if result["changed"]:
        dns.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
