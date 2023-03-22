#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_mac
version_added: "4.1.0"
short_description: Collects information on MAC configuration.
description: >
  This module retrieves information of MAC addresses from Aruba devices
  running the AOS-CX operating system. MAC addresses information will be
  printed out when the playbook execution is done with increased verbosity.
author: Aruba Networks (@ArubaNetworks)
options:
  all_vlans:
    description: >
      Option to fetch all MACs from all VLANs in a device. This option is
      mutually exclusive with the `vlan` option.
    type: bool
    required: false
  vlan:
    description: >
      VLAN ID the MAC addresses are attached to. This option is mutually
      exclusive with the all_vlans option.
    type: int
    required: false
  sources:
    description: >
      List of sources of the MAC addresses to filter which ones will be
      included in the output.
    type: list
    elements: str
    required: false
    choices:
      - dynamic
      - evpn
      - hsc
      - static
      - port-access-security
      - vrrp
      - vsx
    default:
      - dynamic
      - evpn
      - hsc
      - static
      - port-access-security
      - vrrp
      - vsx
"""

EXAMPLES = """
---
- name: Fetch all MAC addresses from all vlans
  aoscx_mac:
    all_vlans: true

- name: Fetch all MAC addresses from VLAN 1
  aoscx_mac:
    vlan: 1

- name: Fetch MAC addresses from VLAN 3 that are static and dynamic.
  aoscx_mac:
    vlan: 3
    sources:
      - static
      - dynamic

- name: Fetch MAC addresses from all VLANs that are static only.
  aoscx_mac:
    all_vlans: true
    sources:
      - static
"""

RETURN = r"""
ansible_mac_addresses:
  description: The MAC addresses from given source(s) from given VLAN(s)
  returned: always
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.mac import Mac
    from pyaoscx.vlan import Vlan

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "vlan": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "all_vlans": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "sources": {
            "type": "list",
            "required": False,
            "elements": "str",
            "choices": [
                "dynamic",
                "evpn",
                "hsc",
                "static",
                "port-access-security",
                "vrrp",
                "vsx",
            ],
            "default": [
                "dynamic",
                "evpn",
                "hsc",
                "static",
                "port-access-security",
                "vrrp",
                "vsx",
            ],
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        mutually_exclusive=[
            ("all_vlans", "vlan"),
        ],
        required_one_of=[
            ("all_vlans", "vlan"),
        ],
    )

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    # Get playbook's arguments
    vlan_id = ansible_module.params["vlan"]
    sources = list(set(ansible_module.params["sources"]))
    all_vlans = ansible_module.params["all_vlans"]

    if "vrrp" in sources:
        sources[sources.index("vrrp")] = "VRRP"

    session = get_pyaoscx_session(ansible_module)

    vlan = None
    if all_vlans:
        macs = Mac.get_all(session)
    elif vlan_id:
        vlan = Vlan(session, vlan_id)
        try:
            vlan.get()
        except Exception:
            ansible_module.fail_json("Vlan {0} does not exist".format(vlan_id))
        macs = Mac.get_all(session, vlan)

    mac_addresses = {}
    for mac in macs.values():
        if vlan:
            _vlan = vlan
        else:
            _vlan = mac._parent_vlan
        key = "vlan_" + str(_vlan.id)
        if key not in mac_addresses:
            mac_addresses.update({key: {}})
        if mac.from_id in sources:
            if mac.from_id not in mac_addresses[key]:
                mac_addresses[key].update({mac.from_id: []})
            port = mac.port
            mac_addresses[key][mac.from_id].append(
                {"mac": str(mac), "port": port.name}
            )

    result["ansible_mac_addresses"] = mac_addresses
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
