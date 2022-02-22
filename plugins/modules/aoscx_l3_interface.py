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
module: aoscx_l3_interface
version_added: "2.8.0"
short_description: >
  Create or Update or Delete Layer3 Interface configuration on AOS-CX.
description: >
  This modules provides configuration management of Layer3 Interfaces on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  interface:
    description: >
      Interface name, should be in the format chassis/slot/port, e.g. 1/2/3,
      1/1/32.
    type: str
    required: true
  description:
    description: Description of interface.
    type: str
    required: false
  ipv4:
    description: >
      The IPv4 address and subnet mask in the address/mask format. The first
      entry in the list is the primary IPv4, the remainings are secondary IPv4.
      To remove an IP address pass in the list without the IP address yo wish
      to remove, and use the update state.
    type: list
    elements: str
    required: false
  ipv6:
    description: >
      The IPv6 address and subnet mask in the address/mask format.
      The IPv6 address and subnet mask in the address/mask format. It takes
      multiple IPv6 with comma separated in the list. To remove an IP address
      pass in the list without the IP address yo wish to remove, and use the
      update state.
    type: list
    elements: str
    required: false
  vrf:
    description: >
      The VRF the interface will belong to once created. If none provided, the
      interface will be in the Default VRF. If an L3 interface is created and
      the user wants to change the interface's VRF, the user must delete the L3
      interface then recreate the interface in the desired VRF.
    type: str
    required: false
  interface_qos_schedule_profile:
    description: >
      Attaching existing QoS schedule profile to interface. *This parameter is
      deprecated and will be removed in a future version.
    type: dict
    required: false
  interface_qos_rate:
    description: >
      The rate limit value configured for broadcast/multicast/unknown unicast
      traffic. Dictionary should have the format 'type_of_traffic': speed
      e.g.
        'unknown-unicast': 100pps
        'broadcast': 200pps
        'multicast': 200pps
    type: dict
    required: false
  ip_helper_address:
    description: >
      Configure a remote DHCP server/relay IP address on the device interface.
      Here the helper address is same as the DHCP server address or another
      intermediate DHCP relay.
    type: list
    elements: str
    required: false
  state:
    description: Create, Update, or Delete Layer3 Interface
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: >
    Configure Interface 1/1/3 - enable interface and vsx-sync features
    IMPORTANT NOTE: the aoscx_interface module is needed to enable the
    interface and set the VSX features to be synced.
  aoscx_interface:
    name: 1/1/3
    enabled: true
    vsx_sync:
      - acl
      - irdp
      - qos
      - rate_limits
      - vlan
      - vsx_virtual
- name: >
    Creating new L3 interface 1/1/3 with IPv4 and IPv6 address on VRF red
    IMPORTANT NOTE: see the above task, it is needed to enable the interface
  aoscx_l3_interface:
    interface: 1/1/3
    description: Uplink Interface
    ipv4:
      - 10.20.1.3/24
    ipv6:
      - 2000:db8::1234/64
    vrf: red

- name: Creating new L3 interface 1/1/6 with IPv4 address on VRF default
  aoscx_l3_interface:
    interface: 1/1/6
    ipv4:
      - 10.33.4.15/24

- name: Deleting L3 Interface - 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    state: delete

- name: Create IP Helper Address on Interface 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    ip_helper_address:
      - 172.1.2.32

- name: Update IP Helper Address on Interface 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    ip_helper_address: 172.1.5.44
    state: update
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
        L3_Interface,
        Interface,
    )


def main():
    module_args = dict(
        interface=dict(type="str", required=True),
        description=dict(type="str", default=None),
        ipv4=dict(type="list", elements="str", default=None),
        ipv6=dict(type="list", elements="str", default=None),
        interface_qos_schedule_profile=dict(type="dict", default=None),
        interface_qos_rate=dict(type="dict", default=None),
        vrf=dict(type="str", default=None),
        ip_helper_address=dict(type="list", elements="str", default=None),
        state=dict(default="create", choices=["create", "delete", "update"]),
    )

    if USE_PYAOSCX_SDK:
        ansible_module = AnsibleModule(
            argument_spec=module_args, supports_check_mode=True
        )

        interface_name = ansible_module.params["interface"]
        description = ansible_module.params["description"]
        ipv4 = ansible_module.params["ipv4"]
        ipv6 = ansible_module.params["ipv6"]
        vrf = ansible_module.params["vrf"]
        ip_helper_addresses = ansible_module.params["ip_helper_address"]
        state = ansible_module.params["state"]

        # Set IP variable as empty arrays
        if ipv4 == [""]:
            ipv4 = []
        if ipv6 == [""]:
            ipv6 = []

        # Set Variables
        if vrf is None:
            vrf = "default"

        # Set result var
        result = dict(changed=False)

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)

        session = get_pyaoscx_session(ansible_module)
        device = Device(session)
        if state == "delete":
            # Create Interface Object
            interface = device.interface(interface_name)
            # Delete it
            interface.delete()

            # Changed
            result["changed"] = True
        else:
            # Create Interface Object
            interface = device.interface(interface_name)
            # Verify if interface was create
            if interface.was_modified():
                # Changed
                result["changed"] = True
            # Configure L4
            # Verify if object was changed
            modified_op = interface.configure_l3(
                ipv4=ipv4, ipv6=ipv6, vrf=vrf, description=description
            )

            if ip_helper_addresses is not None:
                # Create DHCP_Relay object
                dhcp_relay = device.dhcp_relay(vrf=vrf, port=interface_name)
                # Add helper addresses
                dhcp_relay.add_ipv4_addresses(ip_helper_addresses)

            if modified_op:
                # Changed
                result["changed"] = True

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args)

        interface_name = aruba_ansible_module.module.params["interface"]
        admin_state = aruba_ansible_module.module.params["admin_state"]
        description = aruba_ansible_module.module.params["description"]
        ipv4 = aruba_ansible_module.module.params["ipv4"]
        ipv6 = aruba_ansible_module.module.params["ipv6"]
        interface_qos_rate = aruba_ansible_module.module.params[
            "interface_qos_rate"
        ]
        interface_qos_schedule_profile = aruba_ansible_module.module.params[
            "interface_qos_schedule_profile"
        ]
        vrf = aruba_ansible_module.module.params["vrf"]
        ip_helper_address = aruba_ansible_module.module.params[
            "ip_helper_address"
        ]

        state = aruba_ansible_module.module.params["state"]

        l3_interface = L3_Interface()
        interface = Interface()
        if state == "create":
            aruba_ansible_module = l3_interface.create_l3_interface(
                aruba_ansible_module, interface_name
            )
            if vrf is None:
                vrf = "default"

            if vrf is not None:
                aruba_ansible_module = (
                    l3_interface.update_interface_vrf_details_from_l3(
                        aruba_ansible_module, vrf, interface_name
                    )
                )

        if state == "delete":
            aruba_ansible_module = l3_interface.delete_l3_interface(
                aruba_ansible_module, interface_name
            )

        if state in ("create", "update"):

            if admin_state is not None:
                aruba_ansible_module = interface.update_interface_admin_state(
                    aruba_ansible_module, interface_name, admin_state
                )

            if description is not None:
                aruba_ansible_module = interface.update_interface_description(
                    aruba_ansible_module, interface_name, description
                )

            if vrf is not None and vrf != "default":
                aruba_ansible_module = (
                    l3_interface.update_interface_vrf_details_from_l3(
                        aruba_ansible_module, vrf, interface_name
                    )
                )

            if interface_qos_rate is not None:
                aruba_ansible_module = l3_interface.update_interface_qos_rate(
                    aruba_ansible_module, interface_name, interface_qos_rate
                )

            if interface_qos_schedule_profile is not None:
                aruba_ansible_module = (
                    l3_interface.update_interface_qos_profile(
                        aruba_ansible_module,
                        interface_name,
                        interface_qos_schedule_profile,
                    )
                )

            if ipv4 is not None:
                aruba_ansible_module = (
                    l3_interface.update_interface_ipv4_address(
                        aruba_ansible_module, interface_name, ipv4
                    )
                )

            if ipv6 is not None:
                aruba_ansible_module = (
                    l3_interface.update_interface_ipv6_address(
                        aruba_ansible_module, interface_name, ipv6
                    )
                )

            if ip_helper_address is not None:
                if vrf is not None:
                    vrf = "default"
                aruba_ansible_module = (
                    l3_interface.update_interface_ip_helper_address(
                        aruba_ansible_module,
                        vrf,
                        interface_name,
                        ip_helper_address,
                    )
                )

        aruba_ansible_module.update_switch_config()


if __name__ == "__main__":
    main()
