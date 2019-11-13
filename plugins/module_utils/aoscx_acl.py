#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import ArubaAnsibleModule  # NOQA
from random import randint


class ACL:

    def create_acl(self, aruba_ansible_module, acl_name, acl_type):

        if "ACL" not in aruba_ansible_module.running_config.keys():
            aruba_ansible_module.running_config["ACL"] = {}

        acl_index = acl_name + "/" + acl_type

        if acl_index not in aruba_ansible_module.running_config["ACL"].keys():
            aruba_ansible_module.running_config["ACL"][acl_index] = {
                "name": acl_name,
                "list_type": acl_type,
                "cfg_version": randint(-900719925474099, 900719925474099)
            }

        return aruba_ansible_module

    def check_acl_exist(self, aruba_ansible_module, acl_name, acl_type):

        if "ACL" not in aruba_ansible_module.running_config.keys():
            return False

        acl_index = acl_name + "/" + acl_type

        if acl_index not in aruba_ansible_module.running_config["ACL"].keys():
            return False

        return True

    def delete_acl(self, aruba_ansible_module, acl_name, acl_type):

        if not self.check_acl_exist(aruba_ansible_module, acl_name, acl_type):
            aruba_ansible_module.warnings.append("ACL " + acl_name + " of "
                                                 "type " + acl_type + " not "
                                                 "does not exist ")
            return aruba_ansible_module

        acl_index = acl_name + "/" + acl_type

        aruba_ansible_module.running_config["ACL"].pop(acl_index)

        return aruba_ansible_module

    def update_acl_fields(self, aruba_ansible_module, acl_name, acl_type,
                          acl_fields):

        if not self.check_acl_exist(aruba_ansible_module, acl_name, acl_type):
            aruba_ansible_module.warnings.append("ACL " + acl_name + " of "
                                                 "type " + acl_type + " not "
                                                 "does not exist ")
            return aruba_ansible_module

        acl_index = acl_name + "/" + acl_type

        for key in acl_fields.keys():

            if key in aruba_ansible_module.running_config["ACL"][acl_index].keys():  # NOQA
                if aruba_ansible_module.running_config["ACL"][acl_index][key] != acl_fields[key]:  # NOQA
                    aruba_ansible_module.running_config["ACL"][acl_index][key] = acl_fields[key]  # NOQA
                    aruba_ansible_module.running_config["ACL"][acl_index]["cfg_version"] = randint(-900719925474099, 900719925474099)  # NOQA
            else:
                aruba_ansible_module.running_config["ACL"][acl_index][key] = acl_fields[key]  # NOQA
                aruba_ansible_module.running_config["ACL"][acl_index]["cfg_version"] = randint(-900719925474099, 900719925474099)  # NOQA

        return aruba_ansible_module

    def update_acl_entry(self, aruba_ansible_module, acl_name, acl_type, acl_entry_sequence_number, acl_entry_details, update_type="insert"):  # NOQA
        if not self.check_acl_exist(aruba_ansible_module, acl_name, acl_type):
            aruba_ansible_module.warnings.append("ACL {acl_name} of type "
                                                 "{acl_type} not does "
                                                 "not exist "
                                                 "".format(acl_name=acl_name,
                                                           acl_type=acl_type))
            return aruba_ansible_module

        acl_index = acl_name + "/" + acl_type

        if (update_type == 'insert') or (update_type == 'update'):

            if "cfg_aces" not in aruba_ansible_module.running_config["ACL"][acl_index].keys():  # NOQA
                aruba_ansible_module.running_config["ACL"][acl_index]["cfg_aces"] = {}  # NOQA

            if aruba_ansible_module.running_config["ACL"][acl_index]["cfg_aces"].has_key(acl_entry_sequence_number):  # NOQA
                if aruba_ansible_module.running_config["ACL"][acl_index]["cfg_aces"][acl_entry_sequence_number] != acl_entry_details:  # NOQA
                    aruba_ansible_module.running_config["ACL"][acl_index]["cfg_aces"][acl_entry_sequence_number] = acl_entry_details  # NOQA
                    aruba_ansible_module.running_config["ACL"][acl_index]["cfg_version"] = randint(-900719925474099, 900719925474099)  # NOQA
            else:
                aruba_ansible_module.running_config["ACL"][acl_index]["cfg_aces"][acl_entry_sequence_number] = acl_entry_details  # NOQA
                aruba_ansible_module.running_config["ACL"][acl_index]["cfg_version"] = randint(-900719925474099, 900719925474099)  # NOQA

            return aruba_ansible_module

        if update_type == 'delete':

            if "cfg_aces" not in aruba_ansible_module.running_config["ACL"][acl_index].keys():  # NOQA
                aruba_ansible_module.running_config["ACL"][acl_index]["cfg_aces"] = {}  # NOQA
                aruba_ansible_module.running_config["ACL"][acl_index]["cfg_aces"].pop(acl_entry_sequence_number)  # NOQA
                return aruba_ansible_module
