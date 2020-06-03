#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.vrfs.aoscx_vrf_base import VRF_Base


class VRF_10_04_1000(VRF_Base):

    '''
    VRF implementation for 10.04.1000 and above
    firmware.
    '''

    def __init__(self, running_config):
        '''
        Exact the VRF details from the root table.
        '''
        self.config = running_config
        if 'VRF' in self.config:
            self.vrfs = self.config['VRF']
        else:
            self.vrfs = {}

    def get_modified_config(self):
        '''
        Generate the modified running-configuration.
        '''
        self.config['VRF'] = self.vrfs
        return self.config
