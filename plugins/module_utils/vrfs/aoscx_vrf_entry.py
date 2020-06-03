#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class VRF_Entry:
    '''
    Represent a VRF entry
    '''

    def __init__(self, **kwargs):
        '''
        New VRF Entry
        '''
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

    def update_field(self, **kwargs):
        '''
        Update a particular field of the VRF
        '''
        for key in kwargs.keys():
            value = kwargs[key]
            if hasattr(self, key):
                if isinstance(getattr(self, key), list):
                    current_values = getattr(self, key)
                    current_values.append(value)
                    setattr(self, key, current_values)
                elif isinstance(getattr(self, key), dict):
                    current_values = getattr(self, key)
                    for k in value.keys():
                        val = value[k]
                        current_values[k] = val
                    setattr(self, key, current_values)
                else:
                    setattr(self, key, value)
            else:
                setattr(self, key, value)

    def delete_field(self, **kwargs):
        '''
        Delete the value of particular field of the VRF
        '''
        for key in kwargs.keys():
            value = kwargs[key]
            if hasattr(self, key):
                if isinstance(getattr(self, key), list):
                    current_values = getattr(self, key)
                    if value in current_values:
                        current_values.remove(value)
                        setattr(self, key, current_values)
                    else:
                        name = getattr(self, "name")
                        raise Exception(
                            "VRF {name} does not have {key} set as {value}".format(
                                name=name, key=key, value=value))
                elif isinstance(getattr(self, key), dict):
                    current_values = getattr(self, key)
                    for k in value:
                        if k in current_values.keys():
                            del current_values[k]
                        else:
                            name = getattr(self, "name")
                            raise Exception(
                                "VRF {name} does not have {key} with sub option {value}".format(
                                    name=name, key=key, value=value))
                    setattr(self, key, current_values)
                else:
                    delattr(self, key)
            else:
                name = getattr(self, "name")
                raise Exception(
                    "VRF {name} has no field {key}".format(
                        name=name, key=key))

    def get_field(self, field):
        '''
        Get the value of the particular field of the VRF
        '''
        return getattr(self, field, None)
