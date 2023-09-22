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
      To remove an IP address pass in the list and use the delete state.
    type: list
    elements: str
    required: false
  ipv6:
    description: >
      The IPv6 address and subnet mask in the address/mask format. It takes
      multiple IPv6 with comma separated in the list. To remove an IP address
      pass in the list and use the delete state.
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
      - 10.0.1.1/24

- name: Delete IPv4 addresses on VRF default from L3 Interface 1/1/6
  aoscx_l3_interface:
    interface: 1/1/6
    ipv4:
      - 10.0.1.1/24
    state: delete

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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
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

    # Set result var
    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        from pyaoscx.device import Device
        from pyaoscx.utils import util as utils
    except Exception as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    device = Device(session)
    interface = device.interface(interface_name)
    modified = interface.modified
    exists = not modified
    if state == "delete" and not ipv4 and not ipv6:
        is_special_type = interface.type in [
            "lag",
            "loopback",
            "tunnel",
            "vlan",
            "vxlan",
        ]
        if is_special_type:
            # report only if created before this run
            interface.delete()
            result["changed"] = not modified
        else:
            # physical interfaces cannot be deleted, in this case default
            # values are loaded
            prev_intf_attrs = utils.get_attrs(
                interface, interface.config_attrs
            )
            interface.delete()
            Interface = session.api.get_module_class(session, "Interface")
            interface = Interface(session, interface_name)
            interface.get()
            curr_intf_attrs = utils.get_attrs(
                interface, interface.config_attrs
            )
            # interfaces list members in dictionary are pointers to Interface
            # objects, so they are converted to str value to avoid false
            # negatives
            prev_intf_attrs["interfaces"] = list(
                map(str, prev_intf_attrs["interfaces"])
            )
            curr_intf_attrs["interfaces"] = list(
                map(str, curr_intf_attrs["interfaces"])
            )

            # need to compare if there are any changes after deleting
            result["changed"] = prev_intf_attrs != curr_intf_attrs
    else:
        new_ipv6_list = None
        new_ipv4_list = None
        # Verify if interface was create
        if interface.was_modified():
            # Changed
            result["changed"] = True
        modified = False
        if state == "delete":
            if ipv4:
                new_ipv4_set = set()
                if interface.ip4_address_secondary:
                    new_ipv4_set = set(interface.ip4_address_secondary) - set(
                        ipv4
                    )
                    modified |= (
                        set(interface.ip4_address_secondary) != new_ipv4_set
                    )
                new_ipv4_list = list(new_ipv4_set)
                if interface.ip4_address:
                    if interface.ip4_address not in ipv4:
                        new_ipv4_list.insert(0, interface.ip4_address)
                    else:
                        modified = True
            if ipv6:
                new_ipv6_list = (
                    list(set(interface.ip6_addresses) - set(ipv6))
                    if interface.ip6_addresses
                    else []
                )
                modified |= interface.ip6_addresses is not None and set(
                    new_ipv6_list
                ) != set(interface.ip6_addresses)
            vrf = interface.vrf if interface.vrf is not None else "default"
        else:
            if not exists and vrf is None:
                vrf = "default"
            modified_vrf = False
            if exists:
                current_vrf = (
                    interface.vrf.name
                    if interface.vrf is not None
                    else "default"
                )
                modified_vrf = vrf is not None and current_vrf != vrf
                vrf = current_vrf if vrf is None else vrf
            if ipv4:
                primary = ipv4[0]
                new_ipv4_set = set(ipv4)
                if interface.ip4_address_secondary and not modified_vrf:
                    new_ipv4_set |= set(interface.ip4_address_secondary)
                    modified |= new_ipv4_set != set(
                        interface.ip4_address_secondary
                    )
                if interface.ip4_address and not modified_vrf:
                    new_ipv4_set -= set([interface.ip4_address])
                new_ipv4_list = list(new_ipv4_set)
                if interface.ip4_address and not modified_vrf:
                    new_ipv4_list.insert(0, interface.ip4_address)
                else:
                    new_ipv4_list.remove(primary)
                    new_ipv4_list.insert(0, primary)
                    modified = True

            if ipv6:
                new_ipv6_list = (
                    list(set(ipv6) | set(interface.ip6_addresses))
                    if not modified_vrf
                    else ipv6
                )
                modified |= modified_vrf or (
                    set(ipv6) != set(interface.ip6_addresses)
                )

        try:
            interface.configure_l3(
                ipv4=new_ipv4_list,
                ipv6=new_ipv6_list,
                vrf=vrf,
                description=description,
            )
        except Exception as e:
            ansible_module.fail_json(msg=str(e))

        if ip_helper_addresses is not None:
            # Create DHCP_Relay object
            dhcp_relay = device.dhcp_relay(vrf=vrf, port=interface_name)
            # Add helper addresses
            dhcp_relay.add_ipv4_addresses(ip_helper_addresses)

        if modified:
            # Changed
            result["changed"] = True

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
