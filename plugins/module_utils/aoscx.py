#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import copy
import json
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection, ConnectionError

_DEVICE_CONNECTION = None


class HttpApi:
    def __init__(self, module):
        self._module = module
        self._connection_obj = None

    @property
    def _connection(self):
        if not self._connection_obj:
            self._connection_obj = Connection(self._module._socket_path)
        return self._connection_obj

    def get(self, url, data=None):
        res = self._connection.send_request(data=data, method='GET', path=url)
        return res

    def put(self, url, data=None):
        return self._connection.send_request(data=data, method='PUT', path=url)

    def post(self, url, data=None):
        return self._connection.send_request(data=data, method='POST', path=url)


def get_connection(module):
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        conn = HttpApi(module)
        _DEVICE_CONNECTION = conn
    return _DEVICE_CONNECTION


def get(module, url, data=None):
    conn = get_connection(module)
    res = conn.get(url, data)
    return res


def put(module, url, data=None):
    conn = get_connection(module)
    res = conn.put(url, data)
    return res


def post(module, url, data=None):
    conn = get_connection(module)
    res = conn.post(url, data)
    return res


class Cli:
    def __init__(self, module):
        self._module = module
        self._connection_obj = None

    @property
    def _connection(self):
        if not self._connection_obj:
            self._connection_obj = Connection(self._module._socket_path)
        return self._connection_obj

    def run_commands(self, commands, check_rc=True):
        """Run list of commands on remote device and return results
        """
        connection = self._connection_obj
        try:
            response = connection.run_commands(commands=commands, check_rc=check_rc)
        except ConnectionError as exc:
            self._module.fail_json(msg=to_text(exc, errors='surrogate_then_replace'))
        return response


class ArubaAnsibleModule:

    def __init__(self, module_args, store_config=True):

        self.module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True
        )

        self.warnings = list()
        self.changed = False
        self.original_config = None
        self.running_config = None
        self.get_switch_config(store_config=store_config)

    def get_switch_config(self, config_name='running-config', store_config=True):

        config_url = '/rest/v1/fullconfigs/{cfg}'.format(cfg=config_name)

        running_config = get(self.module, config_url)

        if store_config:
            self.running_config = copy.deepcopy(running_config)
            self.original_config = copy.deepcopy(running_config)

        return running_config

    def copy_switch_config_to_remote_location(self, config_name, config_type, destination, vrf):

        config_url = ('/rest/v1/fullconfigs/{cfg}'
                      '?to={dest}&type={type}&vrf={vrf}'
                      ''.format(cfg=config_name,
                                dest=destination,
                                type=config_type,
                                vrf=vrf))

        get(self.module, config_url)
        return

    def tftp_switch_config_from_remote_location(self, config_file_location, config_name, vrf):

        config_url = ('/rest/v1/fullconfigs/{cfg}'
                      '?from={src}&vrf={vrf}'
                      ''.format(cfg=config_name,
                                src=config_file_location,
                                vrf=vrf))

        put(self.module, config_url)
        return

    def upload_switch_config(self, config, config_name='running-config'):

        config_url = '/rest/v1/fullconfigs/{cfg}'.format(cfg=config_name)
        config_json = json.dumps(config)
        put(self.module, config_url, config_json)
        return

    def update_switch_config(self):

        self.result = dict(changed=self.changed, warnings=self.warnings)

        if self.original_config != self.running_config:
            self.upload_switch_config(self.running_config)
            self.result["changed"] = True
        else:
            self.result["changed"] = False
            self.module.log("============================ No Change ======="
                            "===========================")
            self.module.exit_json(**self.result)

        with open('/tmp/debugging_running_config.json', 'w') as to_file:
            json.dump(self.running_config, to_file, indent=4)
            to_file.write("\n")

        self.module.exit_json(**self.result)
