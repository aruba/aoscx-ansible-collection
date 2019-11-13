#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = """
---
author: Aruba Networks (@ArubaNetworks)
httpapi: aoscx
short_description: Use REST to push configs to CX devices
description:
  - This ArubaOSCX module provides REST interactions with ArubaOS-CX devices
version_added: "2.8"
options:
  acx_no_proxy:
    type: bool
    default: True
    description:
      - Specifies whether to set no_proxy for devices
    env:
      - name: ANSIBLE_ACX_NO_PROXY
    vars:
      - name: ansible_acx_no_proxy
        version_added: '2.8'
"""

import json
import os
from ansible.module_utils._text import to_text
from ansible.module_utils.connection import ConnectionError
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.plugins.httpapi import HttpApiBase

# Removed the exception handling as only required pre 2.8 and collection is
# supported in >= 2.9
from ansible.utils.display import Display
display = Display()


class HttpApi(HttpApiBase):

    def set_no_proxy(self):
        try:
            no_proxy = boolean(self.get_option("acx_no_proxy"))
        except NameError:
            no_proxy = False
        if no_proxy:
            os.environ['no_proxy'] = "*"
            display.vvvv("no_proxy set to True")

    def login(self, username, password):
        self.set_no_proxy()
        path = ('/rest/v1/login?username={username}'
                '&password={password}'.format(username=username,
                                              password=password))
        method = 'POST'
        headers = {}

        self.send_request(data=None, path=path, method=method,
                          headers=headers)

    def logout(self):
        path = '/rest/v1/logout'
        data = None
        method = 'POST'
        self.send_request(data, path=path, method=method)

    def send_request(self, data, **message_kwargs):
        headers = {}
        if self.connection._auth:
            headers.update(self.connection._auth)
        response, response_data = self.connection.send(
            data=data, headers=headers, path=message_kwargs['path'],
            method=message_kwargs['method'])
        return self.handle_response(response, response_data)

    def handle_response(self, response, response_data):
        response_data_json = ''
        try:
            response_data_json = json.loads(to_text(response_data.getvalue()))
        except ValueError:

            response_data = response_data.read()
        if isinstance(response, HTTPError):
            if response_data:
                if 'errors' in response_data:
                    errors = response_data['errors']['error']
                    error_text = '\n'.join((error['error-message'] for error in errors))  # NOQA
                else:
                    error_text = response_data

                raise ConnectionError(error_text, code=response.code)
            raise ConnectionError(to_text(response), code=response.code)

        auth = self.update_auth(response, response_data)
        if auth:
            self.connection._auth = auth
        return response_data_json
