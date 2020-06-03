#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import get
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.facts.interfaces import InterfacesFacts
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.facts.legacy import Default, SoftwareInfo, \
    SoftwareImages, HostName, PlatformName, ManagementInterface, \
    SoftwareVersion, Config, ProductInfo, PowerSupplies, PhysicalInterfaces, \
    Fans, ResourceUtilization, DomainName
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.facts.vlans import VlansFacts
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.facts.vrfs import VrfsFacts
from ansible.module_utils.network.common.facts.facts import FactsBase


FACT_LEGACY_SUBSETS = dict(
    default=Default,
    software_info=SoftwareInfo,
    software_images=SoftwareImages,
    host_name=HostName,
    platform_name=PlatformName,
    management_interface=ManagementInterface,
    software_version=SoftwareVersion,
    config=Config,
    fans=Fans,
    power_supplies=PowerSupplies,
    product_info=ProductInfo,
    physical_interfaces=PhysicalInterfaces,
    resource_utilization=ResourceUtilization,
    domain_name=DomainName,
)

FACT_RESOURCE_SUBSETS = dict(
    vlans=VlansFacts,
    interfaces=InterfacesFacts,
    vrfs=VrfsFacts
)


class Facts(FactsBase):
    '''
    Base class for  AOS-CX Facts
    '''
    VALID_LEGACY_GATHER_SUBSETS = frozenset(FACT_LEGACY_SUBSETS.keys())
    VALID_RESOURCE_SUBSETS = frozenset(FACT_RESOURCE_SUBSETS.keys())

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None,
                  data=None):
        '''
        Returns the facts for aoscx
        '''

        if data is None:
            data = get_switch_running_config(self._module)
        if self.VALID_RESOURCE_SUBSETS:
            self.get_network_resources_facts(FACT_RESOURCE_SUBSETS,
                                             resource_facts_type, data)

        if self.VALID_LEGACY_GATHER_SUBSETS:
            self.get_network_legacy_facts(FACT_LEGACY_SUBSETS,
                                          legacy_facts_type)

        return self.ansible_facts, self._warnings


def get_switch_running_config(module):
    '''
    Gets the switch running-config
    '''
    config_url = '/rest/v1/fullconfigs/running-config'
    running_config = get(module, config_url)
    return running_config
