#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
author: Aruba Networks (@ArubaNetworks)
httpapi: aoscx
short_description: Use REST to push configs to CX devices
description: >
  This ArubaOSCX module provides REST interactions with ArubaOS-CX devices
version_added: "2.8.0"
options:
  acx_no_proxy:
    type: bool
    default: True
    description: Specifies whether to set no_proxy for devices.
    env:
      - name: ANSIBLE_ACX_NO_PROXY
    vars:
      - name: ansible_acx_no_proxy
        version_added: '2.8.0'
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
            self.no_proxy = boolean(self.get_option("acx_no_proxy"))
        except NameError:
            self.no_proxy = False
        if self.no_proxy:
            os.environ["no_proxy"] = "*"
            display.vvvv("no_proxy set to True")

    def login(self, username, password):
        self.set_no_proxy()
        path = "/rest/v1/login?username={0}&password={1}".format(
            username, password
        )
        method = "POST"
        headers = {}

        self.send_request(data=None, path=path, method=method, headers=headers)

    def logout(self):
        path = "/rest/v1/logout"
        data = None
        method = "POST"
        self.send_request(data, path=path, method=method)

    def send_request(self, data, **message_kwargs):
        headers = {}
        if "headers" in message_kwargs.keys():
            headers = message_kwargs["headers"]

        if self.connection._auth:
            headers.update(self.connection._auth)
        response, response_data = self.connection.send(
            data=data,
            headers=headers,
            path=message_kwargs["path"],
            method=message_kwargs["method"],
        )
        return self.handle_response(response, response_data)

    def get_connection_details(self):
        connection_details = {}
        if self.connection._auth:
            connection_details["auth"] = self.connection._auth
        connection_details["url"] = self.connection._url
        connection_details["no_proxy"] = self.no_proxy
        connection_details["remote_user"] = self.connection.get_option(
            "remote_user"
        )
        connection_details["password"] = self.connection.get_option("password")
        return connection_details

    def handle_response(self, response, response_data):
        response_data_json = ""
        try:
            response_data_json = json.loads(
                to_text(response_data.getvalue().decode())
            )
        except ValueError:
            response_data = response_data.read().decode()

        if isinstance(response, HTTPError):
            if response_data:
                if "errors" in response_data:
                    errors = response_data["errors"]["error"]
                    error_text = "\n".join(
                        (error["error-message"] for error in errors)
                    )
                else:
                    error_text = response_data

                raise ConnectionError(error_text, code=response.code)
            raise ConnectionError(to_text(response), code=response.code)

        auth = self.update_auth(response, response_data)
        if auth:
            self.connection._auth = auth
        return response_data_json

    def get_capabilities(self):
        result = {}

        return json.dumps(result)

    def handle_httperror(self, exc):
        """
        Method for dealing with HTTP error codes.
        """
        if exc.code == 401:
            if self.connection._auth:
                # Stored auth appears to be invalid, clear and retry
                self.connection._auth = None
                self.login(
                    self.connection.get_option("remote_user"),
                    self.connection.get_option("password"),
                )
                return True

            # Unauthorized and there's no token

            # If the out-of-the-box values were already tried, return.
            if getattr(self, "zeroize_auth", False):
                return exc

            setattr(self, "zeroize_auth", True)

            # Try to login with the out-of-the-box values of a zeroized
            # device, a zeroized device uses a blank password and won't
            # accept any operation on REST until a new password is set.
            login_path = "/rest/v1/login?username={0}".format(
                self.connection.get_option("remote_user")
            )

            login_resp = self.connection.send(
                data=None, path=login_path, method="POST"
            )

            if login_resp[0].code == 268:
                # Login was succesfull, but the session is restricted, the
                # administrator password must be set.
                admin_path = "/rest/v1/system/users/admin"
                data = {"password": self.connection.get_option("password")}

                admin_response = self.connection.send(
                    data=json.dumps(data), path=admin_path, method="PUT"
                )

                if admin_response[0].code == 200:
                    return login_resp[0]

        return exc
