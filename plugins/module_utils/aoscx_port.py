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

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule


class Port:

    def create_port(self, aruba_ansible_module, port_name):

        if not aruba_ansible_module.running_config.has_key('Port'):
            aruba_ansible_module.running_config['Port'] = {}

        encoded_port_name = port_name.replace('/', "%2F")
        if not aruba_ansible_module.running_config['Port'].has_key(encoded_port_name):

            aruba_ansible_module.running_config['Port'][encoded_port_name] = {
                "name" : port_name
            }

        return aruba_ansible_module

    def check_port_exists(self, aruba_ansible_module, port_name):

        if not aruba_ansible_module.running_config.has_key('Port'):
            return False

        encoded_port_name = port_name.replace('/', "%2F")
        if not aruba_ansible_module.running_config['Port'].has_key(encoded_port_name):
            return False

        return True

    def delete_port(self, aruba_ansible_module, port_name):

        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.warnings.append("{} is not configured".format(port_name))
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")
        aruba_ansible_module.running_config['Port'].pop(encoded_port_name)

        return aruba_ansible_module

    def update_port_fields(self, aruba_ansible_module, port_name, port_fields):

        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.module.fail_json("{} is not configured".format(port_name))
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")


        for key in port_fields.keys():

            aruba_ansible_module.running_config['Port'][encoded_port_name][key] = port_fields[key]

        return aruba_ansible_module

    def delete_port_fields(self, aruba_ansible_module, port_name, field_names):

        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.module.fail_json("{} is not configured".format(port_name))
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")

        for field_name in field_names:
            aruba_ansible_module.running_config['Port'][encoded_port_name].pop(field_name)

        return aruba_ansible_module

    def get_port_field_values(self, aruba_ansible_module, port_name, field_names):

        result = {}
        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.module.fail_json("{} is not configured".format(port_name))
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")

        for field_name in field_names:
            if aruba_ansible_module.running_config["Port"][encoded_port_name].has_key(field_name):
                result[field_name] = aruba_ansible_module.running_config["Port"][encoded_port_name][field_name]
            else:
                result[field_name] = ""

        return result

    def get_configured_port_list(self, aruba_ansible_module):

        result = []

        if not aruba_ansible_module.running_config.has_key("Port"):
            return result

        for encoded_port_name in aruba_ansible_module.running_config["Port"].keys():

            port_name = encoded_port_name.replace("%2F", "/")

            result.append(port_name)

        return result






