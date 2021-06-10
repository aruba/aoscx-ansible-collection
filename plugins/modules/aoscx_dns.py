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
module: aoscx_dns
version_added: "2.8"
short_description: Create or Delete DNS Client configuration on AOS-CX
description:
  - This modules provides configuration management of DNS on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
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
    type: str
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
    type: str
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
    type: str
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
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf import VRF


def main():
    '''
    Ansible module to configure DNS on AOS-CX switch
    '''
    module_args = dict(
        mgmt_nameservers=dict(type='dict', required=False),
        dns_domain_list=dict(type='dict', required=False),
        dns_domain_name=dict(type='str', required=False),
        dns_name_servers=dict(type='dict', required=False),
        vrf=dict(type='str', required=False),
        dns_host_v4_address_mapping=dict(type='dict', required=False),
        state=dict(type='str', default='create',
                   choices=['create', 'delete', 'update'])
    )

    # Version management
    try:
        from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import Session
        from pyaoscx.session import Session as Pyaoscx_Session
        from pyaoscx.pyaoscx_factory import PyaoscxFactory

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
        mgmt_nameservers = ansible_module.params['mgmt_nameservers']
        dns_domain_name = ansible_module.params['dns_domain_name']
        dns_domain_list = ansible_module.params['dns_domain_list']
        vrf_name = ansible_module.params['vrf']
        dns_name_servers = ansible_module.params['dns_name_servers']
        dns_host_v4_address_mapping = ansible_module.params[
            'dns_host_v4_address_mapping']
        state = ansible_module.params['state']

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

        # Create a Pyaoscx Factory Object
        pyaoscx_factory = PyaoscxFactory(s)

        if state == 'delete':
            # Modifed Variables
            modified_op = False
            modified_op2 = False

            # Create DNS object
            dns = pyaoscx_factory.dns(vrf=vrf_name)

            # Delete MGMT nameservers
            if mgmt_nameservers is not None:
                # Delete it
                modified_op = dns.delete_mgmt_nameservers()

            # Delete DNS
            dns.delete_dns(
                dns_domain_name,
                dns_domain_list,
                dns_name_servers,
                dns_host_v4_address_mapping,
            )
            # Check if dns was modified
            modified_op2 = dns.was_modified()

            # Changed
            result['changed'] = modified_op or modified_op2

        if state == 'create' or state == 'update':
            # Modifed Variables
            modified_op = False
            modified_op2 = False

            # Create DNS object
            dns = pyaoscx_factory.dns(
                vrf=vrf_name,
                domain_name=dns_domain_name,
                domain_list=dns_domain_list,
                domain_servers=dns_name_servers,
                host_v4_address_mapping=dns_host_v4_address_mapping
            )

            # Check if dns was modified
            modified_op = dns.was_modified()

            # Set MGMT name servers
            if mgmt_nameservers is not None:
                primary = None
                secondary = None
                # Get Primary and Secondary
                for key, value in mgmt_nameservers.items():
                    if key.lower() == 'primary':
                        primary = value
                    elif key.lower() == 'secondary':
                        secondary = value
                # Set up
                modified_op2 = dns.setup_mgmt_nameservers(
                    primary=primary,
                    secondary=secondary)

            # Changed
            result['changed'] = modified_op or modified_op2

        # Exit
        ansible_module.exit_json(**result)

    # Use Older version
    else:
        aruba_ansible_module = ArubaAnsibleModule(module_args)

        mgmt_nameservers = aruba_ansible_module.module.params['mgmt_nameservers']
        dns_domain_name = aruba_ansible_module.module.params['dns_domain_name']
        dns_domain_list = aruba_ansible_module.module.params['dns_domain_list']
        vrf_name = aruba_ansible_module.module.params['vrf']
        dns_name_servers = aruba_ansible_module.module.params['dns_name_servers']
        dns_host_v4_address_mapping = aruba_ansible_module.module.params[
            'dns_host_v4_address_mapping']
        state = aruba_ansible_module.module.params['state']

        vrf = VRF()

        if state == 'create' or state == 'update':
            if mgmt_nameservers is not None:
                if 'mode' in aruba_ansible_module.running_config['System']['mgmt_intf']:
                    mgmt_if_mode = aruba_ansible_module.running_config['System']['mgmt_intf']['mode']
                else:
                    mgmt_if_mode = 'dhcp'

                if mgmt_if_mode != 'static':
                    message_part1 = "The management interface must have static"
                    message_part2 = "IP to configure management interface name servers"
                    aruba_ansible_module.module.fail_json(
                        msg=message_part1 + message_part2)

                for key, value in mgmt_nameservers.items():
                    if key.lower() == 'primary':
                        aruba_ansible_module.running_config[
                            'System']['mgmt_intf']['dns_server_1'] = value
                    elif key.lower() == 'secondary':
                        aruba_ansible_module.running_config[
                            'System']['mgmt_intf']['dns_server_2'] = value

            if vrf_name is None:
                vrf_name = 'default'

            if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):
                aruba_ansible_module.module.fail_json(
                    msg="VRF {vrf} is not configured".format(vrf=vrf_name))
                return aruba_ansible_module

            if dns_domain_name is not None:
                aruba_ansible_module = vrf.update_vrf_fields(
                    aruba_ansible_module, vrf_name, "dns_domain_name", dns_domain_name)

            if dns_domain_list is not None:
                aruba_ansible_module = vrf.update_vrf_fields(
                    aruba_ansible_module, vrf_name, "dns_domain_list", dns_domain_list)

            if dns_name_servers is not None:
                aruba_ansible_module = vrf.update_vrf_fields(
                    aruba_ansible_module, vrf_name, "dns_name_servers", dns_name_servers)

            if dns_host_v4_address_mapping is not None:
                aruba_ansible_module = vrf.update_vrf_fields(
                    aruba_ansible_module,
                    vrf_name,
                    "dns_host_v4_address_mapping",
                    dns_host_v4_address_mapping)

        if state == 'delete':

            if vrf_name is None:
                vrf_name = 'default'

            if not vrf.check_vrf_exists(aruba_ansible_module, vrf_name):
                aruba_ansible_module.warnings.append(
                    "VRF {vrf} is not configured" "".format(vrf=vrf_name))
                return aruba_ansible_module

            if mgmt_nameservers is not None:

                for k in mgmt_nameservers.keys():
                    if k.lower() == 'primary':
                        aruba_ansible_module.running_config['System']['mgmt_intf'].pop(
                            'dns_server_1')
                    elif k.lower() == 'secondary':
                        aruba_ansible_module.running_config['System']['mgmt_intf'].pop(
                            'dns_server_2')

            if dns_domain_name is not None:
                aruba_ansible_module = vrf.delete_vrf_field(
                    aruba_ansible_module, vrf_name, "dns_domain_name", dns_domain_name)

            if dns_domain_list is not None:
                aruba_ansible_module = vrf.delete_vrf_field(
                    aruba_ansible_module, vrf_name, "dns_domain_list", dns_domain_list)

            if dns_name_servers is not None:
                aruba_ansible_module = vrf.delete_vrf_field(
                    aruba_ansible_module, vrf_name, "dns_name_servers", dns_name_servers)

            if dns_host_v4_address_mapping is not None:
                aruba_ansible_module = vrf.delete_vrf_field(
                    aruba_ansible_module,
                    vrf_name,
                    "dns_host_v4_address_mapping",
                    dns_host_v4_address_mapping)

        aruba_ansible_module.update_switch_config()


if __name__ == '__main__':
    main()
