#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2020-2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_facts
version_added: "2.9.0"
short_description: Collects facts from remote AOS-CX device
description: >
  This module retrieves facts from Aruba devices running the AOS-CX operating
  system. Facts will be printed out when the playbook execution is done with
  increased verbosity.
author: Aruba Networks (@ArubaNetworks)
options:
  gather_subset:
    description: >
      Retrieve a subset of all device information. This can be a single
      category or it can be a list. As warning, leaving this field blank
      returns all facts, which may be an intensive process.
    type: list
    elements: str
    choices:
      - config
      - domain_name
      - fans
      - host_name
      - management_interface
      - physical_interfaces
      - platform_name
      - power_supplies
      - product_info
      - resource_utilization
      - software_images
      - software_info
      - software_version
    required: false
    default:
      - domain_name
      - fans
      - host_name
      - management_interface
      - physical_interfaces
      - platform_name
      - power_supplies
      - product_info
      - resource_utilization
      - software_images
      - software_info
      - software_version
  gather_network_resources:
    description: >
      Retrieve vlan, interface, or vrf information. This can be a single
      category or it can be a list. Leaving this field blank returns all all
      interfaces, vlans, and vrfs.
    type: list
    elements: str
    choices:
      - interfaces
      - vlans
      - vrfs
    required: false
  provider:
    description: A dict object containing connection details.
    suboptions:
      host:
        description: >
          Specifies the DNS host name or address for connecting to the remote
          device over the specified transport. The value of host is used as the
          destination address for the transport.
        required: true
        type: str
      password:
        description: >
          Specifies the password to use to authenticate the connection to the
          remote device. This value is used to authenticate the SSH session.
          If the value is not specified in the task, the value of environment
          variable ANSIBLE_NET_PASSWORD will be used instead.
        type: str
      port:
        description: >
          Specifies the port to use when building the connection to the remote
          device.
        type: int
      username:
        description: >
          Configures the username to use to authenticate the connection to the
          remote device. This value is used to authenticate the SSH session.
          If the value is not specified in the task, the value of environment
          variable ANSIBLE_NET_USERNAME will be used instead.
        type: str
    type: dict
"""

EXAMPLES = """
- name: >
    Retrieve all information from the device and save into a variable
    "facts_output".
  aoscx_facts:
  register: facts_output

- name: Retrieve power supply and domain name info from the device
  aoscx_facts:
    gather_subset:
      - domain_name
      - power_supplies

- name: >
    Retrieve VRF info, host name, and fan info from the device and save into a
    variable.
  aoscx_facts:
    gather_subset:
      - fans
      - host_name
    gather_network_resources:
      - vrfs
  register: facts_subset_output
"""

RETURN = r"""
ansible_net_gather_subset:
  description: The list of fact subsets collected from the device
  returned: always
  type: list
ansible_net_gather_network_resources:
  description: >
    The list of fact for network resource subsets collected from the device.
  returned: when the resource is configured
  type: list
ansible_net_domain_name:
  description: The domain name returned from the device
  returned: always
  type: str
ansible_net_hostname:
  description: The configured hostname of the device
  returned: always
  type: str
ansible_net_platform_name:
  description: The platform name returned from the device
  returned: always
  type: str
ansible_net_product_info:
  description: The product system information returned from the device
  returned: always
  type: dict
ansible_net_resource_utilization:
  description: The resource utilization of the remote device
  returned: always
  type: dict
ansible_net_software_images:
  description: The software images on the remote device
  returned: always
  type: dict
ansible_net_software_info:
  description: The details of the software image running on the remote device
  returned: always
  type: dict
ansible_net_software_version:
  description: The software version running on the remote device
  returned: always
  type: str
ansible_net_fans:
  description: The fan information returned from the device
  returned: always
  type: dict
ansible_net_power_supplies:
  description: All power supplies available on the device
  returned: always
  type: dict
ansible_net_interfaces:
  description: A dictionary of all interfaces running on the system
  returned: always
  type: dict
ansible_net_mgmt_intf_status:
  description: A dictionary of management interfaces running on the system
  returned: always
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.interface import Interface
    from pyaoscx.vlan import Vlan
    from pyaoscx.device import Device
    from pyaoscx.vrf import Vrf

    USE_PYAOSCX_SDK = True

except ImportError:
    USE_PYAOSCX_SDK = False

if USE_PYAOSCX_SDK:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )
else:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import (  # NOQA
        aoscx_http_argument_spec,
        get_connection,
    )
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.facts.facts import (  # NOQA
        Facts,
    )


def main():
    """
    Main entry point for module execution
    :returns: ansible_facts
    """
    argument_spec = {
        "gather_subset": dict(
            type="list",
            elements="str",
            default=[
                "domain_name",
                "fans",
                "host_name",
                "management_interface",
                "physical_interfaces",
                "platform_name",
                "power_supplies",
                "product_info",
                "resource_utilization",
                "software_images",
                "software_info",
                "software_version",
            ],
            choices=[
                "config",
                "domain_name",
                "fans",
                "host_name",
                "management_interface",
                "physical_interfaces",
                "platform_name",
                "power_supplies",
                "product_info",
                "resource_utilization",
                "software_images",
                "software_info",
                "software_version",
            ],
        ),
        "gather_network_resources": dict(
            type="list",
            elements="str",
            choices=["interfaces", "vlans", "vrfs"],
        ),
    }
    if USE_PYAOSCX_SDK:
        ansible_module = AnsibleModule(
            argument_spec=argument_spec, supports_check_mode=True
        )

        session = get_pyaoscx_session(ansible_module)

        warnings = []
        if ansible_module.params["gather_subset"] == "!config":
            warnings.append(
                "default value for `gather_subset` will be changed "
                "to `min` from `!config` v2.11 onwards"
            )

        # Declare the Ansible facts
        ansible_facts = {}

        # Retrieve variables from module parameters
        network_resource_list = ansible_module.params[
            "gather_network_resources"
        ]
        subset_list = ansible_module.params["gather_subset"]

        # Retrieve ansible_network_resources
        ansible_network_resources = {}
        if network_resource_list is not None:
            for resource in network_resource_list:
                if resource == "interfaces":
                    ansible_network_resources.update(
                        {"interfaces": Interface.get_facts(session)}
                    )
                elif resource == "vlans":
                    ansible_network_resources.update(
                        {"vlans": Vlan.get_facts(session)}
                    )
                elif resource == "vrfs":
                    ansible_network_resources.update(
                        {"vrfs": Vrf.get_facts(session)}
                    )

        ansible_facts.update(
            {"ansible_network_resources": ansible_network_resources}
        )

        # Retrieve ansible_net_gather_network_resources
        ansible_facts.update(
            {"ansible_net_gather_network_resources": network_resource_list}
        )

        # Retrieve ansible_net_gather_subset
        ansible_facts.update({"ansible_net_gather_subset": subset_list})

        # Retrieve device facts
        switch = Device(session)
        switch.get()
        switch.get_subsystems()  # subsystem

        # Set the subsystem attributes allowed to retrieve as facts
        allowed_subsystem_attributes = [
            "product_info",
            "power_supplies",
            "interfaces",
            "fans",
            "resource_utilization",
        ]

        # Set the default subsets that are always retreived as facts
        default_subset_list = ["management_interface", "software_version"]

        # Extend subset_list with default subsets
        subset_list.extend(default_subset_list)

        # Delete duplicates
        subset_list = list(dict.fromkeys(subset_list))

        # Iterate through given subset arguments in the gather_subset parameter
        # in argument_spec
        for subset in subset_list:

            # Argument translation for management_interface and
            # physical_interfaces
            if subset == "management_interface":
                subset = "mgmt_intf_status"
            elif subset == "physical_interfaces":
                subset = "interfaces"
            elif subset == "host_name":
                subset = "hostname"

            str_subset = "ansible_net_" + subset

            # Check if current subset is inside the Device object
            if hasattr(switch, subset):

                # Get attribute value and add it to Ansible facts dictionary
                ansible_facts[str_subset] = getattr(switch, subset)

            # Check if current subset is inside the allowed subsystem
            # attributes
            elif subset in allowed_subsystem_attributes:
                ansible_facts.update({str_subset: {}})

                # Iterate through Device subsystems
                for subsystem, value in switch.subsystems.items():

                    # Get attribute value and update the Ansible facts
                    # dictionary
                    ansible_facts[str_subset].update(
                        {subsystem: switch.subsystems[subsystem][subset]}
                    )

        ansible_module.exit_json(
            ansible_facts=ansible_facts, warnings=warnings
        )

    # USE OLD VERSION
    else:
        argument_spec.update(aoscx_http_argument_spec)

        module = AnsibleModule(
            argument_spec=argument_spec, supports_check_mode=True
        )

        module._connection = get_connection(module)

        warnings = []
        if module.params["gather_subset"] == "!config":
            warnings.append(
                "default value for `gather_subset` will be changed "
                "to `min` from `!config` v2.11 onwards"
            )

        result = Facts(module).get_facts()

        ansible_facts, additional_warnings = result
        warnings.extend(additional_warnings)

        module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == "__main__":
    main()
