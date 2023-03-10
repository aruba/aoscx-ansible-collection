#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.connection import Connection

try:
    from requests import Session as RequestsSession
    from requests.utils import add_dict_to_cookiejar

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

if HAS_REQUESTS:
    import urllib3

    urllib3.disable_warnings()

# guard against pyaoscx published v0.2.0 which does not have a firmware module
# yet
try:
    from pyaoscx import firmware
    from pyaoscx.session import Session as PyaoscxSession

    HAS_PYAOSCX_FIRMWARE = True
except ImportError:
    HAS_PYAOSCX_FIRMWARE = False


class Session(object):
    def __init__(self, ansible_module):
        if not HAS_REQUESTS:
            ansible_module.fail_json(
                msg="The 'requests' python library is required to use the "
                "aoscx connection type."
            )
        s = RequestsSession()
        connection = Connection(ansible_module._socket_path)
        session_data = connection.get_session()

        if session_data["success"] is False:
            ansible_module.fail_json(msg="Connection Failed")

        add_dict_to_cookiejar(s.cookies, session_data["cookies"])
        s.headers = session_data["headers"]
        if session_data["use_proxy"] is False:
            s.proxies = {"http": None, "https": None}
        self._session = dict(
            s=s,
            url=session_data["url"],
            credentials=session_data["credentials"],
        )

    def get_session(self):
        return self._session

    def check_supported_firmware(self, ansible_module):
        if HAS_PYAOSCX_FIRMWARE:
            version = firmware.get_firmware_version(**self._session)
            if version is None:
                ansible_module.fail_json(
                    msg="Unable to retrieve switch firmware version"
                )
            elif (
                "10.00" in version or "10.01" in version or "10.02" in version
            ):
                ansible_module.fail_json(
                    msg="Minimum supported firmware version is 10.03"
                )


def get_pyaoscx_session(ansible_module):
    # Get session's serialized information
    ansible_module_session = Session(ansible_module)
    ansible_module_session_info = ansible_module_session.get_session()
    # Create pyaoscx session object
    requests_session = ansible_module_session_info["s"]
    base_url = ansible_module_session_info["url"]
    auth = ansible_module_session_info["credentials"]
    return PyaoscxSession.from_session(requests_session, base_url, credentials=auth)
