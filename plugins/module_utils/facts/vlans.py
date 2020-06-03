#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import get


class VlansFacts(object):
    '''
    VLANs Facts Class
    '''

    def __init__(self, module, subspec='config', options='options'):
        '''
        init function
        '''
        self._module = module

    def populate_facts(self, connection, ansible_facts, data=None):
        '''
        Obtain and return VLAN facts
        '''
        vlans_url = '/rest/v10.04/system/vlans?depth=2'
        data = get(self._module, vlans_url)

        internal_vlan_list = []
        for vlan in data.keys():
            if 'type' in data[vlan].keys():
                if data[vlan]['type'] == 'internal':
                    internal_vlan_list.append(vlan)

        for vlan in internal_vlan_list:
            data.pop(vlan)

        facts = {
            'vlans': data
        }
        ansible_facts['ansible_network_resources'].update(facts)
        return ansible_facts
