#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
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

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_port import Port
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_interface import Interface
import json


class VLAN:

    def create_vlan(self, aruba_ansible_module, vlan_id):

        if not aruba_ansible_module.running_config.has_key("VLAN"):
            aruba_ansible_module.running_config["VLAN"] = {}

        vlan_id_str = str(vlan_id)
        if not aruba_ansible_module.running_config.has_key(vlan_id_str):
            aruba_ansible_module.running_config["VLAN"][vlan_id_str] = {
                "id" : vlan_id
            }

        return aruba_ansible_module

    def check_vlan_exist(self, aruba_ansible_module, vlan_id):

        if not aruba_ansible_module.running_config.has_key("VLAN"):
            return False

        vlan_id_str = str(vlan_id)

        if not aruba_ansible_module.running_config["VLAN"].has_key(vlan_id_str):
            return False

        return True

    def delete_vlan(self, aruba_ansible_module, vlan_id):

        port = Port()
        interface = Interface()

        interface_vlan_id = "vlan{}".format(vlan_id)

        if not self.check_vlan_exist(aruba_ansible_module, vlan_id):
            aruba_ansible_module.warnings.append("VLAN ID {} is not configured".format(vlan_id))
            return aruba_ansible_module

        if interface.check_interface_exists(aruba_ansible_module, interface_vlan_id):
            aruba_ansible_module.module.fail_json(msg="VLAN ID {} is configured as interface VLAN".format(vlan_id))
            return aruba_ansible_module

        port_list = port.get_configured_port_list(aruba_ansible_module)

        vlan_port_fields = ["vlan_tag", "vlan_mode", "vlans_per_protocol",
                            "vlan_trunks"]

        vlan_id_str = str(vlan_id)

        for port_name in port_list:

            vlan_field_values = port.get_port_field_values(aruba_ansible_module, port_name, vlan_port_fields)

            if vlan_field_values["vlan_tag"] == vlan_id_str:
                aruba_ansible_module = port.update_port_fields(aruba_ansible_module, port_name, {"vlan_tag": "1"})

            if vlan_id_str in vlan_field_values["vlan_trunks"] and type(vlan_field_values["vlan_trunks"]) is list:
                vlan_field_values["vlan_trunks"].remove(vlan_id_str)
                aruba_ansible_module = port.update_port_fields(aruba_ansible_module, port_name, {"vlan_trunks": vlan_field_values["vlan_trunks"]})

        aruba_ansible_module.running_config["VLAN"].pop(vlan_id_str)

        return aruba_ansible_module

    def update_vlan_fields(self, aruba_ansible_module, vlan_id, vlan_fields_details, update_type='update'):

        if not self.check_vlan_exist(aruba_ansible_module, vlan_id):
            aruba_ansible_module.warnings.append("VLAN ID {} is not configured".format(vlan_id))
            return aruba_ansible_module

        vlan_id_str = str(vlan_id)

        for key in vlan_fields_details.keys():
            if( update_type == 'update') or (update_type == 'insert'):
                aruba_ansible_module.running_config["VLAN"][vlan_id_str][key] = vlan_fields_details[key]
            elif update_type == 'delete':
                aruba_ansible_module.running_config["VLAN"][vlan_id_str].pop(key)
        return aruba_ansible_module

    def get_vlan_fields_values(self, aruba_ansible_module, vlan_id, vlan_fields):

        if not self.check_vlan_exist(aruba_ansible_module, vlan_id):
            aruba_ansible_module.warnings.append(
                "VLAN ID {} is not configured".format(vlan_id))
            return aruba_ansible_module

        vlan_id_str = str(vlan_id)

        result = {}
        for field in vlan_fields:

            if aruba_ansible_module.running_config["VLAN"][vlan_id_str].has_key(field):
                result[field] = aruba_ansible_module.running_config["VLAN"][vlan_id_str][field]

        return result






