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

import copy
import json
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

    def get_running_config(self):
        return self._connection.get_running_config()

    def put_running_config(self, updated_config):
        # updated_config = {}
        self._connection.put_running_config(updated_config)


def get_connection(module):
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        conn = HttpApi(module)
        _DEVICE_CONNECTION = conn
    return _DEVICE_CONNECTION


def get_running_config(module):
    conn = get_connection(module)
    run = conn.get_running_config()
    module.log(json.dumps(run))
    return run


def put_running_config(module, updated_config):
    conn = get_connection(module)
    conn.put_running_config(updated_config)


class ArubaAnsibleModule:

    def __init__(self, module_args):
        self.module = module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True
        )

        self.warnings = list()
        self.changed = False
        self.get_switch_config()

    def get_switch_config(self):

        running_config = get_running_config(self.module)
        self.running_config = copy.deepcopy(running_config)
        self.original_config = copy.deepcopy(running_config)

    def update_switch_config(self):

        self.result = dict(changed=self.changed, warnings=self.warnings)

        if self.original_config != self.running_config:
            put_running_config(self.module, self.running_config)
            self.result["changed"] = True

        else:
            self.result["changed"] = False
            self.module.log("============================ No Change ======="
                            "===========================")
            self.module.exit_json(**self.result)

        '''
         Writing debugging file
        '''
        with open('/tmp/debugging_running_config.json', 'w') as to_file:
            json.dump(self.running_config, to_file, indent=4)
            to_file.write("\n")

        self.module.exit_json(**self.result)
