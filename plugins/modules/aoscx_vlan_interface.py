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
module: aoscx_vlan_interface
version_added: "2.8.0"
short_description: Create or Delete VLAN Interface configuration on AOS-CX
description: >
  This modules provides configuration management of VLAN Interfacess on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  vlan_id:
    description: >
      The ID of this VLAN interface. Non-internal VLANs must have an 'id'
      between 1 and 4094 to be effectively instantiated.
    required: true
    type: str
  admin_state:
    description: Admin State status of vlan interface.
    choices:
      - up
      - down
    required: false
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
  ipv6:
    description: >
      The IPv6 address and subnet mask in the address/mask format. It takes
      multiple IPv6 with comma separated in the list. To remove an IP address
      pass in the list without the IP address yo wish to remove, and use the
      update state.
    type: list
    elements: str
    required: false
  vrf:
    description: >
      The VRF the vlan interface will belong to once created. If none provided,
      the interface will be in the Default VRF. If the VLAN interface is
      created and the user wants to change the interface vlan's VRF, the user
      must delete the VLAN interface then recreate the VLAN interface in the
      desired VRF.
    type: str
    default: default
    required: false
  ip_helper_address:
    description: >
      Configure a remote DHCP server/relay IP address on the vlan interface.
      Here the helper address is same as the DHCP server address or another
      intermediate DHCP relay.
    type: list
    elements: str
    required: false
  description:
    description: VLAN description
    required: false
    type: str
  active_gateway_ip:
    description: Configure IPv4 active-gateway for vlan interface.
    type: str
    required: false
  active_gateway_mac_v4:
    description: >
      Configure virtual MAC address for IPv4 active-gateway for vlan interface.
      Must be used in together with active_gateway_ip.
    type: str
    required: false
  state:
    description: Create or update or delete the VLAN.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
  - name: Create VLAN Interface 100
    aoscx_vlan_interface:
      vlan_id: 100
      description: UPLINK_VLAN
      ipv4:
        - 10.10.20.1/24
      ipv6:
        - 2000:db8::1234/64

  - name: Create VLAN Interface 200
    aoscx_vlan_interface:
      vlan_id: 200
      description: UPLINK_VLAN
      ipv4:
        - 10.20.20.1/24
      ipv6:
        - 3000:db8::1234/64
      vrf: red
      ip_helper_address:
        - 10.40.20.1

  - name: Delete VLAN Interface 100
    aoscx_vlan_interface:
      vlan_id: 100
      state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        vlan_id=dict(type="str", required=True),
        admin_state=dict(type="str", required=False, choices=["up", "down"]),
        state=dict(default="create", choices=["create", "delete", "update"]),
        ipv4=dict(type="list", elements="str", default=None),
        description=dict(type="str", default=None),
        ipv6=dict(type="list", elements="str", default=None),
        vrf=dict(type="str", default="default"),
        ip_helper_address=dict(type="list", elements="str", default=None),
        active_gateway_ip=dict(type="str", default=None),
        active_gateway_mac_v4=dict(type="str", default=None),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    vlan_id = ansible_module.params["vlan_id"]
    admin_state = ansible_module.params["admin_state"]
    ipv4 = ansible_module.params["ipv4"]
    ipv6 = ansible_module.params["ipv6"]
    vrf = ansible_module.params["vrf"]
    description = ansible_module.params["description"]
    ip_helper_address = ansible_module.params["ip_helper_address"]
    active_gateway_ip = ansible_module.params["active_gateway_ip"]
    active_gateway_mac_v4 = ansible_module.params["active_gateway_mac_v4"]
    state = ansible_module.params["state"]

    # Set IP variable as empty arrays
    if ipv4 == [""]:
        ipv4 = []
    if ipv6 == [""]:
        ipv6 = []

    # Set variables
    vlan_interface_id = "vlan" + vlan_id

    # Set result var
    result = dict(changed=False)

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

    if state == "delete":
        # Create Interface Object
        vlan_interface = device.interface(vlan_interface_id)
        # Delete it
        vlan_interface.delete()
        # Changed
        result["changed"] = True

    if state == "create" or state == "update":
        # Create Interface with incoming attributes
        vlan_interface = device.interface(vlan_interface_id)
        # Verify if interface was create
        if vlan_interface.was_modified():
            # Changed
            result["changed"] = True

        if admin_state:
            vlan_interface.admin_state = admin_state

        # Configure SVI
        # Verify if object was changed
        modified_op = vlan_interface.configure_svi(
            vlan=int(vlan_id),
            ipv4=ipv4,
            ipv6=ipv6,
            vrf=vrf,
            description=description,
        )

        if active_gateway_ip and active_gateway_mac_v4:
            modified_op2 = vlan_interface.set_active_gateway(
                active_gateway_ip, active_gateway_mac_v4
            )
            modified_op = modified_op2 or modified_op

        if ip_helper_address:
            # Create DHCP_Relay object
            dhcp_relay = device.dhcp_relay(vrf=vrf, port=vlan_interface_id)
            # Add helper addresses
            modified_dhcp_relay = dhcp_relay.add_ipv4_addresses(
                ip_helper_address
            )
            modified_op = modified_op or modified_dhcp_relay

        if modified_op:
            # Changed
            result["changed"] = True

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
