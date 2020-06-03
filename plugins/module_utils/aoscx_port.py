#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule


class Port:

    def create_port(self, aruba_ansible_module, port_name):

        if 'Port' not in aruba_ansible_module.running_config.keys():
            aruba_ansible_module.running_config['Port'] = {}

        encoded_port_name = port_name.replace('/', "%2F")
        if encoded_port_name not in aruba_ansible_module.running_config['Port'].keys():  # NOQA

            aruba_ansible_module.running_config['Port'][encoded_port_name] = {
                "name": port_name
            }

        return aruba_ansible_module

    def check_port_exists(self, aruba_ansible_module, port_name):

        if 'Port' not in aruba_ansible_module.running_config.keys():
            return False

        encoded_port_name = port_name.replace('/', "%2F")
        if encoded_port_name not in aruba_ansible_module.running_config['Port'].keys():  # NOQA
            return False

        return True

    def delete_port(self, aruba_ansible_module, port_name, type=None):

        if aruba_ansible_module.switch_platform.startswith("6") and (type is None):  # NOQA
            encoded_port_name = port_name.replace('/', "%2F")
            aruba_ansible_module.running_config['Port'][encoded_port_name] = {
                "name": port_name,
                "admin": "down"
            }
            return aruba_ansible_module

        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.warnings.append("{port} is not configured"
                                                 "".format(port=port_name))
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")
        aruba_ansible_module.running_config['Port'].pop(encoded_port_name)

        return aruba_ansible_module

    def update_port_fields(self, aruba_ansible_module, port_name, port_fields):

        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.module.fail_json(msg="{port} is not "
                                                      "configured"
                                                      "".format(port=port_name)
                                                  )
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")

        for key in port_fields.keys():

            aruba_ansible_module.running_config['Port'][encoded_port_name][key] = port_fields[key]  # NOQA

        return aruba_ansible_module

    def delete_port_fields(self, aruba_ansible_module, port_name, field_names):

        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.module.fail_json(msg="{port} is not "
                                                      "configured"
                                                      "".format(port=port_name)
                                                  )
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")

        for field_name in field_names:
            aruba_ansible_module.running_config['Port'][encoded_port_name].pop(field_name)  # NOQA

        return aruba_ansible_module

    def get_port_field_values(self, aruba_ansible_module, port_name,
                              field_names):

        result = {}
        if not self.check_port_exists(aruba_ansible_module, port_name):
            aruba_ansible_module.module.fail_json(msg="{port} is not "
                                                      "configured"
                                                      "".format(port=port_name)
                                                  )
            return aruba_ansible_module

        encoded_port_name = port_name.replace('/', "%2F")

        for field_name in field_names:
            if field_name in aruba_ansible_module.running_config["Port"][encoded_port_name].keys():  # NOQA
                result[field_name] = aruba_ansible_module.running_config["Port"][encoded_port_name][field_name]  # NOQA
            else:
                result[field_name] = ""

        return result

    def get_configured_port_list(self, aruba_ansible_module):

        result = []

        if "Port" not in aruba_ansible_module.running_config.keys():
            return result

        for encoded_port_name in aruba_ansible_module.running_config["Port"].keys():  # NOQA

            port_name = encoded_port_name.replace("%2F", "/")

            result.append(port_name)

        return result
