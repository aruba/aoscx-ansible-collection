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
---
module: aoscx_acl
version_added: "2.8"
short_description: Manage ACL configuration for AOS-CX.
description:
  - This modules provides configuration management and creation of Access Classifier Lists on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the Access Classifier List
    type: str
    required: true
  type:
    description: Type of the Access Classifier List
    type: str
    choices: ['ipv4', 'ipv6', 'mac']
    required: true
  acl_entries:
    description: "Dictionary of dictionaries of Access Classifier Entries
      configured in Access Classifier List. Each entry key of the dictionary
      should be the sequence number of the ACL entry. Each ACL entry dictionary
      should have the minimum following keys - action , src_ip, dst_ip. See
      below for examples of options and values."
    type: dict
    required: false
  state:
    description: Create, Update, or Delete Access Classifier List
    type: str
    choices: ['create', 'delete', 'update']
    default: 'create'
    required: false
'''  # NOQA

EXAMPLES = r'''
- name: Configure IPv4 ACL with entry - 1 deny tcp 10.10.12.12 10.10.12.11 count
  aoscx_acl:
    name: ipv4_acl_example
    type: ipv4
    acl_entries: {
      '1': {action: deny, # ACL Entry Action - choices: ['permit', 'deny']
            count: true, # Enable 'count' on the ACL Entry - choices: ['permit', 'deny']
            dst_ip: 10.10.12.11/255.255.255.255,  # Matching Destination IPv4 address, format IP/MASK
            protocol: tcp,  # Matching protocol
            src_ip: 10.10.12.12/255.255.255.255 # Matching Source IPv4 address, format IP/MASK
            }
      }

- name: Configure IPv6 ACL with entry - 809 permit icmpv6 2001:db8::11 2001:db8::12
  aoscx_acl:
    name: ipv6_acl_example
    type: ipv6
    acl_entries: {
      '809': {action: permit, # ACL Entry Action - choices: ['permit', 'deny']
              count: false, # Enable 'count' on the ACL Entry - choices: ['permit', 'deny']
              dst_ip: 2001:db8::11/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff,  # Matching Destination IPv6 address, format IP/MASK
              protocol: icmpv6,  # Matching protocol
              src_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff # Matching Source IPv6 address, format IP/MASK
              }
      }

- name: Change existing IPv4 ACL Entry - 1 permit tcp 10.10.12.12 10.10.12.11 count
  aoscx_acl:
    name: ipv4_acl_example
    type: ipv4
    acl_entries: {
      '1': {action: permit, # ACL Entry Action - choices: ['permit', 'deny']
            count: true, # Enable 'count' on the ACL Entry - choices: ['permit', 'deny']
            dst_ip: 10.10.12.11/255.255.255.255,  # Matching Destination IPv4 address, format IP/MASK
            protocol: tcp,  # Matching protocol
            src_ip: 10.10.12.12/255.255.255.255 # Matching Source IPv4 address, format IP/MASK
            }
      }
    state: update

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


def main():
    module_args = dict(
        name=dict(type='str', required=True),
        type=dict(type='str', required=True, choices=['ipv4', 'ipv6', 'mac']),
        acl_entries=dict(type='dict', default=None),
        state=dict(type='str', default='create', choices=['create',
                                                          'delete',
                                                          'update'])
    )

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
