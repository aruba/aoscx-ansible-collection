#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'certified'
}

DOCUMENTATION = '''
---
module: aoscx_dns
version_added: "2.8"
short_description: Create or Delete DNS Client configuration on AOS-CX
description:
  - This modules provides configuration management of DNS on AOS-CX devices.
author:
  - Aruba Networks
options:
  mgmt_nameservers:
    description: Primary and secondary nameservers on mgmt interface. The key
      of the dictionary is primary or secondary and value is the respective IP
      address
    type: dict
    required: True
  dns_domain_name:
    description: Domain name used for name resolution by the DNS client, if
      'dns_domain_list' is not configured
    type: string
    required: True
  dns_domain_list:
    description: Domain list names to be used for address resolution, keyed by
      the resolution priority order
    type: dict
    required: True
  dns_name_servers:
    description: Name servers to be used for address resolution, keyed by the
      resolution priority order
    type: dict
    required: True
  vrf:
    description: VRF name where DNS configuration is added
    type: string
    required: False
  dns_host_v4_address_mapping:
    description: List of static host address configurations and the IPv4
      address associated with them
    type: dict
    required: True
  state:
    description: Create or Update or Delete DNS configuration on the switch.
    default: create
    choices: ['create', 'update', 'delete']
    required: False
'''

EXAMPLES = '''
- name: DNS configuration creation
  aoscx_dns:
    mgmt_nameservers:
     "Primary": "10.10.2.10"
     "Secondary": "10.10.2.10"
    dns_domain_name: "hpe.com"
    dns_domain_list:
      0: "hp.com"
      1: "aru.com"
      2: "sea.com"
    dns_name_servers:
      0: "4.4.4.8"
      1: "4.4.4.10"
    dns_host_v4_address_mapping:
      "host1": "5.5.44.5"
      "host2": "2.2.44.2"
    vrf: "green"


- name: DNS configuration update
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    dns_domain_name: "hpe.com"
    dns_domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    dns_name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    dns_host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: update

- name: DNS configuration deletion
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    dns_domain_name: "hp.com"
    dns_domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    dns_name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    dns_host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: delete
'''

RETURN = r''' # '''

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_vrf import VRF


def main():
    module_args = dict(
        mgmt_nameservers=dict(type='dict', required=False),
        dns_domain_list=dict(type='dict', required=False),
        dns_domain_name=dict(type='str', required=False),
        dns_name_servers=dict(type='dict', required=False),
        vrf=dict(type='str', required=False),
        dns_host_v4_address_mapping=dict(type='dict', required=False),
        state=dict(type='str', choices=['create', 'delete', 'update'])
    )

    aruba_ansible_module = ArubaAnsibleModule(module_args)

    mgmt_nameservers = aruba_ansible_module.module.params['mgmt_nameservers']
    dns_domain_name = aruba_ansible_module.module.params['dns_domain_name']
    dns_domain_list = aruba_ansible_module.module.params['dns_domain_list']
    vrf_name = aruba_ansible_module.module.params['vrf']
    dns_name_servers = aruba_ansible_module.module.params['dns_name_servers']
    dns_host_v4_address_mapping = aruba_ansible_module.module.params['dns_host_v4_address_mapping']  # NOQA
    state = aruba_ansible_module.module.params['state']

    vrf = VRF()

    if state == 'create' or state == 'update':
        if mgmt_nameservers is not None:
            mgmt_if_mode = aruba_ansible_module.running_config['System']['mgmt_intf']['mode']  # NOQA

            if mgmt_if_mode != 'static':

                aruba_ansible_module.module.fail_json(msg="The management interface must have static IP to configure management interface name servers")  # NOQA

            for k, v in mgmt_nameservers.iteritems():
                if k.lower() == 'primary':
                    aruba_ansible_module.running_config['System']['mgmt_intf']['dns_server_1'] = v  # NOQA
                elif k.lower() == 'secondary':
                    aruba_ansible_module.running_config['System']['mgmt_intf']['dns_server_2'] = v  # NOQA

        if vrf_name is None:
            vrf_name = 'default'

        if dns_domain_name is not None:
            aruba_ansible_module = vrf.update_vrf_dns_domain_name(aruba_ansible_module, vrf_name, dns_domain_name, update_type="insert")  # NOQA

        if dns_domain_list is not None:
            aruba_ansible_module = vrf.update_vrf_dns_domain_list(aruba_ansible_module, vrf_name, dns_domain_list, update_type="insert")  # NOQA

        if dns_name_servers is not None:
            aruba_ansible_module = vrf.update_vrf_dns_name_servers(aruba_ansible_module, vrf_name, dns_name_servers, update_type="insert")  # NOQA

        if dns_host_v4_address_mapping is not None:
            aruba_ansible_module = vrf.update_vrf_dns_host_v4_address_mapping(aruba_ansible_module, vrf_name, dns_host_v4_address_mapping, update_type="insert")  # NOQA

    if state == 'delete':

        if vrf_name is None:
            vrf_name = 'default'

        if mgmt_nameservers is not None:

            for k, v in mgmt_nameservers.iteritems():
                if k.lower() == 'primary':
                    aruba_ansible_module.running_config['System']['mgmt_intf'].pop('dns_server_1')  # NOQA
                elif k.lower() == 'secondary':
                    aruba_ansible_module.running_config['System']['mgmt_intf'].pop('dns_server_2')  # NOQA

        if dns_domain_name is not None:
            aruba_ansible_module = vrf.update_vrf_dns_domain_name(aruba_ansible_module, vrf_name, dns_domain_name, update_type="delete")  # NOQA

        if dns_domain_list is not None:
            aruba_ansible_module = vrf.update_vrf_dns_domain_list(aruba_ansible_module, vrf_name, dns_domain_list, update_type="delete")  # NOQA

        if dns_name_servers is not None:
            aruba_ansible_module = vrf.update_vrf_dns_name_servers(aruba_ansible_module, vrf_name, dns_name_servers, update_type="delete")  # NOQA

        if dns_host_v4_address_mapping is not None:
            aruba_ansible_module = vrf.update_vrf_dns_host_v4_address_mapping(aruba_ansible_module, vrf_name, dns_host_v4_address_mapping, update_type="delete")  # NOQA

    aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
