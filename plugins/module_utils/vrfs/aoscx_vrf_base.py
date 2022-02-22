#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2020-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf_entry import (  # NOQA
    VRF_Entry,
)


class VRF_Base:
    """
    VRF implementation for fimrware earlier than 10.04.1000
    """

    def __init__(self, running_config):
        """
        Extract the VRF details from system details
        """

        self.config = running_config
        if "vrfs" in self.config["System"].keys():
            self.vrfs = self.config["System"]["vrfs"]
        else:
            self.vrfs = {}

    def create_vrf(self, vrf_name):
        """
        Create a new VRF
        """
        vrf_entry = VRF_Entry(name=vrf_name, type="user")
        self.vrfs[vrf_name] = vrf_entry.__dict__

    def delete_vrf(self, vrf_name):
        """
        Delete an existing VRF
        """
        if vrf_name in self.vrfs.keys():
            error = (
                "VRF {vrf_name} is attached to {int}. Interface must be "
                "deleted and created under new VRF before VRF can be deleted."
            )
            if "Port" in self.config.keys():
                port_dict = self.config["Port"]
                for encoded_port_name in port_dict.keys():
                    temp_port_dict = port_dict[encoded_port_name]
                    if "vrf" in temp_port_dict.keys():
                        if temp_port_dict["vrf"] == vrf_name:
                            error.format(
                                vrf_name=vrf_name,
                                int=encoded_port_name.replace("%2F", "/"),
                            )
                            raise Exception(error)

            del self.vrfs[vrf_name]

        else:
            raise Exception("VRF {0} does not exist".format(vrf_name))

    def check_vrf_exists(self, vrf_name):
        """
        Check if the VRF is configured
        """
        if vrf_name in self.vrfs.keys():
            return True

        return False

    def get_vrf_field_value(self, vrf_name, field_name):
        """
        Get the value for a particular field of the VRF table
        """
        if vrf_name in self.vrfs.keys():
            vrf_entry = VRF_Entry(**self.vrfs[vrf_name])
            return vrf_entry.get_field(field_name)
        else:
            raise Exception("VRF {0} does not exist".format(vrf_name))

    def get_modified_config(self):
        """
        Generate the modified running-config
        """
        self.config["System"]["vrfs"] = self.vrfs
        return self.config

    def update_vrf_field_value(self, vrf_name, field, value):
        """
        Update a particular field of the VRF
        """
        if vrf_name in self.vrfs.keys():
            vrf_entry = VRF_Entry(**self.vrfs[vrf_name])
            fields = {field: value}
            vrf_entry.update_field(**fields)
            self.vrfs[vrf_name] = vrf_entry.__dict__
        else:
            raise Exception("VRF {0} does not exist".format(vrf_name))

    def delete_vrf_field_value(self, vrf_name, field, value):
        """
        Delete the value of the particular field of the VRF.
        """
        if vrf_name in self.vrfs.keys():
            try:
                vrf_entry = VRF_Entry(**self.vrfs[vrf_name])
                fields = {field: value}
                vrf_entry.delete_field(**fields)
                self.vrfs[vrf_name] = vrf_entry.__dict__
            except Exception as error:
                raise error
        else:
            raise Exception("VRF {0} does not exist".format(vrf_name))
