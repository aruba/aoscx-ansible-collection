#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import get


class FactsBase(object):
    '''
    FactsBase class
    '''

    def __init__(self, module):
        self._module = module
        self.warnings = list()
        self.facts = dict()
        self.responses = None
        self._url = "/rest/v1/fullconfigs/running-config"
        self._fact_name = "config"
        self.data = None

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self.data = get(self._module, self._url)

        if self._fact_name == 'config':
            self.facts['config'] = self.data
            return

        if self._fact_name in self.data.keys():
            self.facts[self._fact_name] = self.data[self._fact_name]


class SoftwareInfo(FactsBase):
    '''
    Software Info facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'software_info'
        self._url = '/rest/v10.04/system?attributes=software_info'
        super(SoftwareInfo, self).populate()


class SoftwareImages(FactsBase):
    '''
    Software Images facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'software_images'
        self._url = '/rest/v10.04/system?attributes=software_images'
        super(SoftwareImages, self).populate()


class HostName(FactsBase):
    '''
    Host Name facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'hostname'
        self._url = '/rest/v10.04/system?attributes=hostname'
        super(HostName, self).populate()


class PlatformName(FactsBase):
    '''
    Platform Name facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'platform_name'
        self._url = '/rest/v10.04/system?attributes=platform_name'
        super(PlatformName, self).populate()


class ManagementInterface(FactsBase):
    '''
    Management Interface facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'mgmt_intf_status'
        self._url = '/rest/v10.04/system?attributes=mgmt_intf_status'
        super(ManagementInterface, self).populate()


class SoftwareVersion(FactsBase):
    '''
    Software Version facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'software_version'
        self._url = '/rest/v10.04/system?attributes=software_version'
        super(SoftwareVersion, self).populate()


class Config(FactsBase):
    '''
    Config facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'config'
        super(Config, self).populate()


class Default(FactsBase):
    '''
    Default facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'mgmt_intf_status'
        self._url = '/rest/v10.04/system?attributes=mgmt_intf_status'
        super(Default, self).populate()

        self._fact_name = 'software_version'
        self._url = '/rest/v10.04/system?attributes=software_version'
        super(Default, self).populate()


class DomainName(FactsBase):
    '''
    Domain Name facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'domain_name'
        self._url = '/rest/v10.04/system?attributes=domain_name'
        super(DomainName, self).populate()


class SubSystemFactsBase(FactsBase):
    '''
    SubSystem Base facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._url = '/rest/v10.04/system/subsystems?depth=4'
        self.data = get(self._module, self._url)
        output_data = {}

        for sub_system in self.data.keys():
            sub_system_details = self.data[sub_system]

            if self._fact_name in sub_system_details.keys():

                output_data[sub_system] = sub_system_details[self._fact_name]

        self.facts[self._fact_name] = output_data


class ProductInfo(SubSystemFactsBase):

    '''
    Product Info facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'product_info'
        super(ProductInfo, self).populate()


class PowerSupplies(SubSystemFactsBase):

    '''
    Power supplies facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'power_supplies'
        super(PowerSupplies, self).populate()


class PhysicalInterfaces(SubSystemFactsBase):

    '''
    Physical Interfaces facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'interfaces'
        super(PhysicalInterfaces, self).populate()


class Fans(SubSystemFactsBase):

    '''
    Fans facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'fans'
        super(Fans, self).populate()


class ResourceUtilization(SubSystemFactsBase):

    '''
    Resource utilization facts class
    '''

    def populate(self):
        '''
        Obtain and populate the facts
        '''
        self._fact_name = 'resource_utilization'
        super(ResourceUtilization, self).populate()
