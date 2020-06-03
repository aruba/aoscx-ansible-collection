#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf_base import VRF_Base
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf_10_04_1000 import VRF_10_04_1000


class VRF:
    '''
    VRF APIs to perform CRUD operations
    '''

    def get_vrf_version(self, aruba_ansible_module):
        '''
        Get the correct VRF implementation based on firmware
        '''
        firmware = aruba_ansible_module.switch_current_firmware
        regex = r'.(\d+).(\d+).(\d+)'
        comp_regex = re.compile(regex)
        output = re.search(comp_regex, firmware)
        if int(output.group(2)) == 3:
            return VRF_Base(aruba_ansible_module.running_config)

        if int(output.group(2)) == 4:
            if int(output.group(3)) <= 40:
                return VRF_Base(aruba_ansible_module.running_config)
            else:
                return VRF_10_04_1000(
                    aruba_ansible_module.running_config)

        return VRF_10_04_1000(aruba_ansible_module.running_config)

    def create_vrf(self, aruba_ansible_module, vrf_name):
        '''
        Create a new VRF
        '''
        vrfs = self.get_vrf_version(aruba_ansible_module)
        vrfs.create_vrf(vrf_name)
        aruba_ansible_module.running_config = vrfs.get_modified_config()
        return aruba_ansible_module

    def delete_vrf(self, aruba_ansible_module, vrf_name):
        '''
        Delete an exisiting VRF
        '''
        vrfs = self.get_vrf_version(aruba_ansible_module)
        try:
            vrfs.delete_vrf(vrf_name)
            aruba_ansible_module.running_config = vrfs.get_modified_config()
            return aruba_ansible_module
        except Exception as error:
            if "does not exist" in str(error):
                aruba_ansible_module.warnings.append(str(error))
                return aruba_ansible_module
            else:
                aruba_ansible_module.module.fail_json(msg=str(error))

    def check_vrf_exists(self, aruba_ansible_module, vrf_name):
        '''
        Check if the VRF exists on the switch
        '''
        vrfs = self.get_vrf_version(aruba_ansible_module)
        return vrfs.check_vrf_exists(vrf_name)

    def get_vrf_field_value(
            self,
            aruba_ansible_module,
            vrf_name,
            field):
        '''
        Get the particular VRF field value
        '''
        vrfs = self.get_vrf_version(aruba_ansible_module)
        try:
            return vrfs.get_vrf_field_value(vrf_name, field)
        except Exception as error:
            aruba_ansible_module.module.fail_json(msg=str(error))

    def update_vrf_fields(
            self,
            aruba_ansible_module,
            vrf_name,
            field,
            value):
        '''
        Update the value of the particular VRF field value
        '''
        vrfs = self.get_vrf_version(aruba_ansible_module)
        try:
            vrfs.update_vrf_field_value(vrf_name, field, value)
            aruba_ansible_module.running_config = vrfs.get_modified_config()
            return aruba_ansible_module
        except Exception as error:
            aruba_ansible_module.module.fail_json(msg=str(error))

    def delete_vrf_field(
            self,
            aruba_ansible_module,
            vrf_name,
            field,
            value):
        '''
        Delete the value of the particular VRF field value
        '''
        vrfs = self.get_vrf_version(aruba_ansible_module)
        try:
            vrfs.delete_vrf_field_value(vrf_name, field, value)
            aruba_ansible_module.running_config = vrfs.get_modified_config()
            return aruba_ansible_module
        except Exception as error:
            aruba_ansible_module.warnings.append(str(error))
