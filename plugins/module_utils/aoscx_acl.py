#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from random import randint

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import (  # NOQA
    ArubaAnsibleModule,
)


class ACL:
    def create_acl(self, aruba_ansible_module, acl_name, acl_type):

        if "ACL" not in aruba_ansible_module.running_config.keys():
            aruba_ansible_module.running_config["ACL"] = {}

        acl_index = acl_name + "/" + acl_type

        if acl_index not in aruba_ansible_module.running_config["ACL"].keys():
            aruba_ansible_module.running_config["ACL"][acl_index] = {
                "name": acl_name,
                "list_type": acl_type,
                "cfg_version": randint(-900719925474099, 900719925474099),
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
            aruba_ansible_module.warnings.append(
                "ACL " + acl_name + " of "
                "type " + acl_type + " not "
                "does not exist "
            )
            return aruba_ansible_module

        acl_index = acl_name + "/" + acl_type

        aruba_ansible_module.running_config["ACL"].pop(acl_index)

        return aruba_ansible_module

    def update_acl_fields(
        self, aruba_ansible_module, acl_name, acl_type, acl_fields
    ):

        if not self.check_acl_exist(aruba_ansible_module, acl_name, acl_type):
            aruba_ansible_module.warnings.append(
                "ACL " + acl_name + " of "
                "type " + acl_type + " not "
                "does not exist "
            )
            return aruba_ansible_module

        acl_index = acl_name + "/" + acl_type

        for key in acl_fields.keys():

            if (
                key
                in aruba_ansible_module.running_config["ACL"][acl_index].keys()
            ):
                if (
                    aruba_ansible_module.running_config["ACL"][acl_index][key]
                    != acl_fields[key]
                ):
                    aruba_ansible_module.running_config["ACL"][acl_index][
                        key
                    ] = acl_fields[key]
                    aruba_ansible_module.running_config["ACL"][acl_index][
                        "cfg_version"
                    ] = randint(-900719925474099, 900719925474099)
            else:
                aruba_ansible_module.running_config["ACL"][acl_index][
                    key
                ] = acl_fields[key]
                aruba_ansible_module.running_config["ACL"][acl_index][
                    "cfg_version"
                ] = randint(-900719925474099, 900719925474099)

        return aruba_ansible_module

    def update_acl_entry(
        self,
        aruba_ansible_module,
        acl_name,
        acl_type,
        acl_entry_sequence_number,
        acl_entry_details,
        update_type="insert",
    ):
        if not self.check_acl_exist(aruba_ansible_module, acl_name, acl_type):
            aruba_ansible_module.warnings.append(
                "ACL {0} of type {1} does not exist ".format(
                    acl_name, acl_type
                )
            )
            return aruba_ansible_module

        acl_index = acl_name + "/" + acl_type

        if (update_type == "insert") or (update_type == "update"):

            if (
                "cfg_aces"
                not in aruba_ansible_module.running_config["ACL"][
                    acl_index
                ].keys()
            ):
                aruba_ansible_module.running_config["ACL"][acl_index][
                    "cfg_aces"
                ] = {}

            if (
                "acl_entry_sequence_number"
                in aruba_ansible_module.running_config["ACL"][acl_index][
                    "cfg_aces"
                ].keys()
            ):
                if (
                    aruba_ansible_module.running_config["ACL"][acl_index][
                        "cfg_aces"
                    ][acl_entry_sequence_number]
                    != acl_entry_details
                ):
                    aruba_ansible_module.running_config["ACL"][acl_index][
                        "cfg_aces"
                    ][acl_entry_sequence_number] = acl_entry_details
                    aruba_ansible_module.running_config["ACL"][acl_index][
                        "cfg_version"
                    ] = randint(-900719925474099, 900719925474099)
            else:
                aruba_ansible_module.running_config["ACL"][acl_index][
                    "cfg_aces"
                ][acl_entry_sequence_number] = acl_entry_details
                aruba_ansible_module.running_config["ACL"][acl_index][
                    "cfg_version"
                ] = randint(-900719925474099, 900719925474099)

            return aruba_ansible_module

        if update_type == "delete":

            if (
                "cfg_aces"
                not in aruba_ansible_module.running_config["ACL"][
                    acl_index
                ].keys()
            ):
                aruba_ansible_module.running_config["ACL"][acl_index][
                    "cfg_aces"
                ] = {}
                aruba_ansible_module.running_config["ACL"][acl_index][
                    "cfg_aces"
                ].pop(acl_entry_sequence_number)
                return aruba_ansible_module
