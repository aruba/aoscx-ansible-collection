#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'certified'
}

DOCUMENTATION = '''
module: aoscx_acl
short_description: Module for configuration of Access Control Lists in AOSCX switches.
description: >
  This module provides the functionality for configuring Access Control Lists
  on AOSCX switches. For more detailed documentation see docs/aoscx_acl.md
  in this repository.
version_added: "2.8"
author: "Aruba Networking"
options:
  name:
    description: Name of the access control list
    required: true
    type: str
  type:
    description: Type of ACL
    required: true
    type: str
    choices:
      - ipv4
      - ipv6
      - mac
      - l4port
  state:
    description: The action taken with the current ACL
    required: false
    type: str
    choices:
      - create
      - update
      - delete
    default:
      - create
  acl_entries:
    description:
      - A dictionary, where the key is the sequence number of the Access Control
      - Entry, and the value is a dictionary representing the Access Control
      - Entry. A detailed description of these ACE dictionaries is provided in
      - the notes section, and in docs/aoscx_acl.md
    required: false
    type: dictionary

notes:
  ace_dictionary:
    description:
      - The ACEs are configured using a dictionary representation. A description
      - of all available fields are provided here. All fields are optional, but
      - there are certain internal dependencies that are related to how ACLs
      - work.
    available_fileds:
      comment:
        type: str
        description:
          - Comment associated with the ACE
      tcp_ack:
        type: boolean
        description:
          - TCP Acknowledge flag matching attribute
      tcp_cwr:
        type: boolean
        description:
          - TCP CWR flag matching attribute
      tcp_ece:
        type: boolean
        description:
          - TCP ECE flag matching attribute
      tcp_established:
        type: boolean
        description:
          - TCP established state (ACK or RST flag is set)
      tcp_fin:
        type: boolean
        description:
          - TCP FIN flag matching attribute
      tcp_psh:
        type: boolean
        description:
          - TCP PSH flag matching attribute
      tcp_rst:
        type: boolean
        description:
          - TCP RST flag matching attribute
      tcp_urg:
        type: boolean
        description:
          - TCP URG flag matching attribute
      src_l4_port_group:
        type: str
        description: >
          URL in string format of the ACL object group resource. This URL
          refers to the REST API interface and has the following format:
          `/system/acl_object_groups/{name},{object_type}`. This attribute is
          mutually exclusive with the `src_l4_port_min`, `src_l4_port_max`, and
          `src_l4_port_range_reverse` attributes, and if this attribute is
          configured, the other ones will be ignored. The referenced object
          group must be of type `l4port`.
      src_l4_port_max:
        type: int32
        description:
          - Maximum L4 port to match on the packet
      src_l4_port_min:
        type: int32
        description:
          - Minimum L4 port to match on the packet
      dst_l4_port_group:
        type: str
        description: >
          URL in string format of the ACL object group resource. This URL
          refers to the REST API interface and has the following format:
          `/system/acl_object_groups/{name},{object_type}`.  This attribute is
          mutually exclusive with the `dst_l4_port_min`, `dst_l4_port_max`, and
          `dst_l4_port_range_reverse` attributes. If this attribute is
          configured, the others will be ignored. The referenced object group
          must be of type `l4port`.
      dst_l4_port_max:
        type: int32
        description: >
          Maximum IP destination port matching attribute. Used in conjunction
          with `dst_l4_port_min` and `dst_l4_port_range_reverse`.
      dst_l4_port_min:
        type: int32
        description: >
          Minimum IP destination port matching attribute. Used in conjunction
          with `dst_l4_port_max` and `dst_l4_port_range_reverse`.
      src_ip_group:
        type: str
        description: >
          URL in string format of the ACL object group resource. This URL
          refers to the REST API interface and has the following format:
          `/system/acl_object_groups/{name},{object_type}`. This attribute is
          mutually exclusive with the source IP address attribute. If
          `src_ip_group` is configured, `src_ip` will be ignored. The
          referenced object group must be of type `ipv4` or `ipv6`.
      src_ip:
        type: str
        description: >
          String with source IP matching attribute. If no IP address is
          specified, the ACL Entry will not match on source IP address. The
          following IPv4 and IPV6 formats are accepted. IPv4 format
          (A.B.C.D/W.X.Y.Z) IPv6 format (A:B::C:D/W:X::Y:Z).
      dst_ip_group:
        type: str
        description: >
          URL in string format of the ACL object group resource. This URL
          refers to the REST API interface and has the following format:
          `/system/acl_object_groups/{name},{object_type}`. This attribute is
          mutually exclusive with the destination IP address attribute. If
          `dst_ip_group` is configured, `dst_ip` will be ignored. The
          referenced object group must be of type `ipv4` or `ipv6`.
      dst_ip:
        type: str
        description: >
          String with source IP matching attribute. If no IP address is
          specified, the ACL Entry will not match on destination IP address.
          The following IPv4 and IPv6 address formats are accepted. IPv4 format
          (A.B.C.D/W.X.Y.Z) IPv6 format (A:B::C:D/W:X::Y:Z).
      src_mac:
        type: str
        description: >
          String with source MAC matching attribute. Two formats are allowed
          (AAAA.BBBB.CCCC or AAAA.BBBB.CCCC/XXXX.YYYY.ZZZZ).
      dst_mac:
        type: str
        description: >
          String with destination MAC matching attribute. Two formats are
          allowed (AAAA.BBBB.CCCC or AAAA.BBBB.CCCC/XXXX.YYYY.ZZZZ).
      action:
        type: str
        description: >
          Define the action to take on an ACL match. There are two options:
          `permit`, and `deny`. `permit`: packets will be forwarded. `deny`:
          packets will be dropped. ACE will only be activated when an
          associated action is provided.
      count:
        type: boolean
        description: >
          When true, increment hit count for packets that match this ACL.
      dscp:
        type: int32
        description: Different Services Code Point matching attribute.
      ecn:
        type: int32
        description: Explicit Congestion Notification matching attribute.
      ethertype:
        type: int32
        description: Ethernet type matching attribute.
      fragment:
        type: boolean
        description: Fragment matching attribute.
      icmp_code:
        type: int32
        description: ICMP code matching attribute.
      icmp_type:
        type: int32
        description: ICMP type matching attribute.
      ip_precedence:
        type: int32
        description: IP Precedence matching attribute.
      log:
        type: boolean
        description: >
          ACE attribute log action; when true, log information for packets that
          match ACL.
      pcp:
        type: int32
        description: Priority Code Point matching attribute.
      protocol:
        type: int32
        description: IPv4 protocol matching attribute.
      ttl:
        type: int32
        description: Time-to-live matching attribute.
      tos:
        type: int32
        description: IP Type of service value matching attribute.
      vlan:
        type: int32
        description: VLAN ID matching attribute.
'''  # NOQA

EXAMPLES = '''
# Deny a host inside an allowed network

# The following example shows how to allow all incoming traffic from a certain
# IPv4 network, but deny a single host, and keep a count of how many packets
# are sent to the switch from that host. Two ACEs are added, the one with
# lowest sequence number is checked first for matches. One ACE is in charge of
# denying incoming traffic from the single host, while the other one allows
# incoming from the rest of the network.

- name: >
    Configure IPv4 ACL that allows traffic from a network except a single host.
  aoscx_acl:
    name: allow_network_deny_host
    type: ipv4
    acl_entries:
      1:
        comment: "Deny the host"
        action: deny
        count: true
        src_ip: 158.10.12.57/255.255.255.255
        protocol: tcp
      2:
        comment: "Allow the network"
        action: permit
        src_ip: 158.10.12.1/255.255.0.0
        protocol: tcp

# Deny a host and log urgent packets
# The following example shows how to deny all incoming and outgoing traffic
# from a single host, and log only when packet was urgent.

- name: Configure IPv6 ACL that denies all traffic and logs urgent packets
  aoscx_acl:
    name: deny_host_log_urgent
    acl_entries:
      9:
        comment: "match urgent packets for log"
        tcp_urg: true
        log: true
        src_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        dst_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        action: deny
      10:
        comment: "match the rest of the packets"
        log: false
        src_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        dst_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        action: deny

# Simple L4 example

# The following example shows how to configure rules with L4 ports. It will
# allow traffic form ports 5000, 5001 and 5002 to port 3657. Note that when
# a match for only one port is intended, `src/dst_l4_port_max` and
# `src/dst_l4_port_min` must be equal.

- name: Configure port range
  aoscx_acl:
    name: simple_ports
    type: ipv4
    acl_entries:
      1:
        comment: "Use a range of ports"
        src_ip: 100.10.25.2/255.255.255.0
        dst_ip: 100.10.25.2/255.255.255.0
        src_l4_port_max: 5002
        src_l4_port_min: 5000
        dst_l4_port_max: 3657
        dst_l4_port_min: 3567
        action: permit

# Remove an ACL

- name: Delete ipv4 ACL from config
  aoscx_acl:
    name: ipv4_acl
    type: ipv4
    state: delete
'''  # NOQA

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule  # NOQA
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_acl import ACL  # NOQA


protocol_dict = {
    "ah": 51,
    "esp": 50,
    "gre": 47,
    "icmp": 1,
    "icmpv6": 58,
    "igmp": 2,
    "ospf": 89,
    "pim": 103,
    "sctp": 132,
    "tcp": 6,
    "udp": 17
}


def translate_acl_entries_protocol(protocol_name):
    if protocol_name in protocol_dict:
        return protocol_dict[protocol_name]

    if (protocol_name == "ip") or (protocol_name == "any") or (
            protocol_name == "ipv6"):
        return ""

    return None


def _remove_invalid_addresses(parameters):
    """
    For user ease 'any' is accepted as an address, but for REST, to match any
        address the field as to be empty.
    """
    param_names = [
        "src_ip",
        "dst_ip",
        "src_mac",
        "dst_mac",
    ]
    for name in param_names:
        if name in parameters:
            if parameters[name] == "any":
                del(parameters[name])
    return parameters


def main():
    module_args = dict(
        name=dict(type='str', required=True),
        type=dict(type='str', required=True, choices=['ipv4', 'ipv6', 'mac']),
        acl_entries=dict(type='dict', default=None),
        state=dict(type='str', default='create', choices=['create',
                                                          'delete',
                                                          'update'])
    )

    # Version management
    try:

        from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import Session
        from pyaoscx.session import Session as Pyaoscx_Session
        from pyaoscx.acl_entry import AclEntry
        from pyaoscx.device import Device

        USE_PYAOSCX_SDK = True

    except ImportError:
        USE_PYAOSCX_SDK = False

    # Use PYAOSCX SDK
    if USE_PYAOSCX_SDK:
        from ansible.module_utils.basic import AnsibleModule

        # ArubaModule
        ansible_module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True)

        # Session
        session = Session(ansible_module)

        # Set Variables
        state = ansible_module.params['state']
        name = ansible_module.params['name']
        list_type = ansible_module.params['type']
        acl_entries = ansible_module.params['acl_entries']

        result = dict(
            changed=False
        )

        if ansible_module.check_mode:
            ansible_module.exit_json(**result)

        # Get session serialized information
        session_info = session.get_session()
        # Create pyaoscx.session object
        s = Pyaoscx_Session.from_session(
            session_info['s'], session_info['url'])

        # Create a Pyaoscx Device Object
        device = Device(s)
        if state == 'delete':
            # Create ACL Object
            acl = device.acl(name, list_type)
            # Delete it
            acl.delete()
            # Changed
            result['changed'] = True

        if state == 'create' or state == 'update':
            # Create ACL Object
            acl = device.acl(name, list_type)
            # Verify if interface was create
            if acl.was_modified():
                # Changed
                result['changed'] = True

            # Modified variable
            modified_op = False

            if acl_entries is not None:
                for sequence_number, config in acl_entries.items():
                    acl_entry = AclEntry(
                        acl.session,
                        sequence_number=int(sequence_number),
                        parent_acl=acl,
                        **_remove_invalid_addresses(config)
                    )
                    modified_op |= acl_entry.apply()

            # Changed
            if modified_op:
                result['changed'] = True

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args=module_args)
        acl = ACL()
        state = aruba_ansible_module.module.params['state']
        name = aruba_ansible_module.module.params['name']
        list_type = aruba_ansible_module.module.params['type']
        acl_entries = aruba_ansible_module.module.params['acl_entries']

        if (state == 'create') or (state == 'update'):
            aruba_ansible_module = acl.create_acl(
                aruba_ansible_module, name, list_type)
            if acl_entries is not None:
                for sequence_number in acl_entries.keys():
                    acl_entry = acl_entries[sequence_number]
                    if 'protocol' in acl_entry.keys():
                        translated_protocol_name = translate_acl_entries_protocol(
                            acl_entry['protocol'])
                        if (translated_protocol_name is not None) and (
                                translated_protocol_name != ""):
                            acl_entry['protocol'] = translated_protocol_name
                        elif (translated_protocol_name is not None) and (
                                translated_protocol_name == ""):
                            acl_entry.pop('protocol')

                    if 'count' in acl_entry.keys():
                        if acl_entry['count'] is False:
                            acl_entry.pop('count')

                    acl_entries[sequence_number] = acl_entry
                for sequence_number in acl_entries.keys():
                    aruba_ansible_module = acl.update_acl_entry(
                        aruba_ansible_module, name, list_type, sequence_number,
                        acl_entries[sequence_number], update_type='insert')

        if state == 'delete':
            aruba_ansible_module = acl.delete_acl(aruba_ansible_module, name,
                                                  list_type)

        aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
