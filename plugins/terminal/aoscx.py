#!/usr/bin/env python
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


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


from ansible.plugins.terminal import TerminalBase
from ansible.errors import AnsibleConnectionFailure
from ansible.utils.display import Display
import re

display = Display()


class TerminalModule(TerminalBase):
    '''
    Terminal Module class for AOS-CX
    '''

    terminal_stdout_re = [re.compile(
        br"[\r\n]?[\w\+\-\.:\/\[\]]+(?:\([^\)]+\)){0,3}(?:[>#]) ?$")]


    def on_open_shell(self):
        '''
        Tasks to be executed immediately after connecting to switch.
        '''
        try:
            self._exec_cli_command(b'no page')
        except AnsibleConnectionFailure:
            raise AnsibleConnectionFailure('unable to remove terminal paging')

        try:
            self._exec_cli_command(b'terminal width 512')
            try:
                self._exec_cli_command(b'terminal width 0')
            except AnsibleConnectionFailure:
                pass
        except AnsibleConnectionFailure:
            display.display('WARNING: Unable to set terminal width, '
                            'command responses may be truncated')

    def on_become(self, passwd=None):
        '''
        Priveleged mode
        '''
        return

    def on_unbecome(self):
        '''
        Come out of priveleged mode
        '''
        return
