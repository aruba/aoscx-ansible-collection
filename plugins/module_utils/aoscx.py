#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2020 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import copy
import json
import re
import traceback
from collections import OrderedDict
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import missing_required_lib
try:
    from ansible.module_utils.network.common.utils import to_list, ComplexList
except ImportError:
    from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import to_list, ComplexList
from ansible.module_utils.connection import Connection, ConnectionError
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_ztp import connect_ztp_device

REQUESTS_IMP_ERR = None
try:
    import requests
    HAS_REQUESTS_LIB = True
except ImportError:
    HAS_REQUESTS_LIB = False
    REQUESTS_IMP_ERR = traceback.format_exc()

_DEVICE_CONNECTION = None
_DEVICE_CONFIGS = {}
_DEVICE_ZTP = False

aoscx_provider_spec = {
    'host': dict(),
    'port': dict(type='int'),
    'username': dict(fallback=(env_fallback, ['ANSIBLE_NET_USERNAME'])),
    'password': dict(fallback=(env_fallback, ['ANSIBLE_NET_PASSWORD']), no_log=True),
    'ssh_keyfile': dict(fallback=(env_fallback, ['ANSIBLE_NET_SSH_KEYFILE']), type='path'),
    'authorize': dict(fallback=(env_fallback, ['ANSIBLE_NET_AUTHORIZE']), type='bool'),
    'auth_pass': dict(fallback=(env_fallback, ['ANSIBLE_NET_AUTH_PASS']), no_log=True),
    'timeout': dict(type='int')
}

aoscx_http_provider_spec = {
    'host': dict(),
    'port': dict(type='int'),
    'username': dict(fallback=(env_fallback, ['ANSIBLE_NET_USERNAME'])),
    'password': dict(fallback=(env_fallback, ['ANSIBLE_NET_PASSWORD']), no_log=True)
}

aoscx_argument_spec = {
    'provider': dict(type='dict', options=aoscx_provider_spec, removed_in_version='2.14.0', removed_from_collection='arubanetworks.aoscx'),
}

aoscx_http_argument_spec = {
    'provider': dict(type='dict', options=aoscx_http_provider_spec, removed_in_version='2.14.0', removed_from_collection='arubanetworks.aoscx'),
}


def get_provider_argspec():
    '''
    Returns the provider argument specification
    '''
    return aoscx_provider_spec


def check_args(module, warnings):
    '''
    Checks the argument
    '''
    pass


def get_config(module, flags=None):
    '''
    Obtains the switch configuration
    '''
    flags = [] if flags is None else flags

    cmd = 'show running-config '
    cmd += ' '.join(flags)
    cmd = cmd.strip()

    try:
        return _DEVICE_CONFIGS[cmd]
    except KeyError:
        try:
            out = exec_command(module, cmd)
        except ConnectionError as exc:
            module.fail_json(
                msg='unable to retrieve current config',
                err=to_text(exc, errors='surrogate_then_replace')
            )

        cfg = to_text(out, errors='surrogate_then_replace').strip()
        _DEVICE_CONFIGS[cmd] = cfg
        return cfg


def load_config(module, commands):
    '''
    Loads the configuration onto the switch
    '''
    try:
        out = exec_command(module, 'configure terminal')
    except ConnectionError as exc:
        module.fail_json(
            msg='unable to enter configuration mode',
            err=to_text(exc, errors='surrogate_then_replace')
        )

    for command in to_list(commands):
        if command == 'end':
            continue

        try:
            out = exec_command(module, command)
        except ConnectionError as exc:
            module.fail_json(
                msg='unable to enter configuration mode',
                err=to_text(exc, errors='surrogate_then_replace')
            )

    exec_command(module, 'end')


def exec_command(module, command):
    '''
    Execute command on the switch
    '''
    conn = create_ssh_connection(module)
    return conn.send_command(command)


def sanitize(resp):
    '''
    Sanitizes the string to remove additiona white spaces
    '''
    # Takes response from device and adjusts leading whitespace to just 1 space
    cleaned = []
    for line in resp.splitlines():
        cleaned.append(re.sub(r"^\s+", " ", line))
    return '\n'.join(cleaned).strip()


def natural_sort_key(s):
    '''
    Sort function for natural sort of alphanumeric values instead of ASCII
    :param s: str to be sorted
    :return: value to be compared
    '''
    _nsre = re.compile(r'\.*(\d+)$')
    if '%2F' in s:
        s = s.replace('%2F', '')
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def comp_sort(obj):
    '''
    Sorts list and dict objects within a nested JSON and returns the result
    :param obj: dict or list to be sorted
    :return: dict or list sorted
    '''
    data = OrderedDict()
    if isinstance(obj, dict):
        for key, value in sorted(obj.items(), key=lambda x: natural_sort_key(x[0])):
            if isinstance(value, dict) or isinstance(value, list):
                data[key] = comp_sort(value)
            else:
                data[key] = value
    elif isinstance(obj, list):
        try:
            return sorted(obj, key=natural_sort_key)
        except ExpectedError:
            is_dict_or_list = isinstance(value, dict) or isinstance(value,
                                                                    list)
            return [comp_sort(value) if is_dict_or_list else value for value in obj]
    return data


class HttpApi:
    '''
    Module utils class for AOS-CX HTTP API connection
    '''

    def __init__(self, module):
        self._module = module
        self._connection_obj = None

    @property
    def _connection(self):
        '''
        Creates HTTP API connection
        '''
        if not self._connection_obj:
            self._connection_obj = Connection(self._module._socket_path)
        return self._connection_obj

    def get(self, url, data=None):
        '''
        GET REST call
        '''
        res = self._connection.send_request(data=data, method='GET', path=url)
        return res

    def put(self, url, data=None, headers=None):
        '''
        PUT REST call
        '''
        if headers is None:
            headers = {}
        return self._connection.send_request(data=data, method='PUT', path=url,
                                             headers=headers)

    def post(self, url, data=None, headers=None):
        '''
        POST REST call
        '''
        if headers is None:
            headers = {}
        return self._connection.send_request(data=data, method='POST',
                                             path=url,
                                             headers=headers)

    def file_upload(self, url, files, headers=None):
        """
        Workaround with requests library for lack of support in httpapi for
        multipart POST
        See:
        ansible/blob/devel/lib/ansible/plugins/connection/httpapi.py
        ansible/blob/devel/lib/ansible/module_utils/urls.py
        """

        if not HAS_REQUESTS_LIB:
            self._module.fail_json(msg=missing_required_lib(
                "requests"), exception=REQUESTS_IMP_ERR)

        if headers is None:
            headers = {}
        connection_details = self._connection.get_connection_details()

        full_url = connection_details['url'] + url
        with open(files, 'rb') as file:
            file_param = {'fileupload': file}

            # Get Credentials
            user = connection_details['remote_user']
            password = connection_details['password']

            # Workaround for setting no_proxy based off acx_no_proxy flag
            if connection_details['no_proxy']:
                proxies = {'http': None, 'https': None}
                # Using proxies
                # Perform Login
                response_login = requests.post(
                    connection_details['url'] +
                    "/rest/v1/login?username={}&password={}".format(
                        user, password
                    ),
                    verify=False, timeout=5, proxies=proxies)
                # Perform File Upload
                res = requests.post(
                    url=full_url, files=file_param, verify=False,
                    proxies=proxies,
                    cookies=response_login.cookies
                )
                # Perform Logout
                response_logout = requests.post(
                    connection_details['url'] + "/rest/v1/logout",
                    verify=False, proxies=proxies,
                    cookies=response_login.cookies)

            else:
                # No proxies
                # Perform Login
                response_login = requests.post(
                    connection_details['url'] +
                    "/rest/v1/login?username={}&password={}".format(
                        user, password
                    ),
                    verify=False, timeout=5)
                # Perform File Upload
                res = requests.post(
                    url=full_url, files=file_param, verify=False,
                    cookies=response_login.cookies
                )
                # Perform Logout
                response_logout = requests.post(
                    connection_details['url'] + "/rest/v1/logout",
                    verify=False,
                    cookies=response_login.cookies)

        if res.status_code != 200:
            error_text = "Error while uploading firmware"
            raise ConnectionError(error_text, code=res.status_code)
        return res


def create_ssh_connection(module):
    connection = Connection(module._socket_path)

    global _DEVICE_ZTP
    if not _DEVICE_ZTP:
        # For zeroize devices, configure authentication
        connect_ztp_device(
            module,
            connection.get_option('host'),
            connection.get_option('remote_user'),
            connection.get_option('password'))
        _DEVICE_ZTP = True

    return connection


def get_connection(module, is_cli=False):
    '''
    Returns the connection plugin
    '''
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        if is_cli:
            if not hasattr(module, '_aoscx_connection'):
                module._aoscx_connection = create_ssh_connection(module)
            _DEVICE_CONNECTION = module._aoscx_connection
        else:
            conn = HttpApi(module)
            _DEVICE_CONNECTION = conn

    return _DEVICE_CONNECTION


def get(module, url, data=None):
    '''
    Perform GET REST call
    '''
    conn = get_connection(module)
    res = conn.get(url, data)
    return res


def put(module, url, data=None, headers=None):
    '''
    Perform PUT REST call
    '''
    if headers is None:
        headers = {}
    conn = get_connection(module)
    res = conn.put(url, data, headers)
    return res


def post(module, url, data=None, headers=None):
    '''
    Perform POST REST call
    '''
    if headers is None:
        headers = {}
    conn = get_connection(module)
    res = conn.post(url, data, headers)
    return res


def file_upload(module, url, files, headers=None):
    '''
    Upload File through REST
    '''
    if headers is None:
        headers = {}
    conn = get_connection(module)
    res = conn.file_upload(url, files, headers)
    return res


def to_command(module, commands):
    '''
    Convert command to ComplexList
    '''
    transform = ComplexList(dict(
        command=dict(key=True),
        prompt=dict(type='list'),
        answer=dict(type='list'),
        newline=dict(type='bool', default=True),
        sendonly=dict(type='bool', default=False),
        check_all=dict(type='bool', default=False),
    ), module)

    return transform(to_list(commands))


def run_commands(module, commands, check_rc=False):
    '''
    Execute command on the switch
    '''
    conn = get_connection(module, True)
    try:
        return conn.run_commands(commands=commands, check_rc=check_rc)
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc))


class ArubaAnsibleModule:
    '''
    Aruba ansible mdule wrapper class
    '''

    def __init__(self, module_args, store_config=True):
        '''
        module init function
        '''

        self.module = AnsibleModule(
            argument_spec=module_args,
            supports_check_mode=True
        )

        self.warnings = list()
        self.changed = False
        self.original_config = None
        self.running_config = None
        self.switch_current_firmware = None
        self.switch_platform = None
        self.get_switch_platform()
        self.get_switch_firmware_version()
        self.get_switch_config(store_config=store_config)

        if "10.00" in self.switch_current_firmware:
            self.module.fail_json(msg="Minimum supported "
                                      "firmware version is 10.03")

        if "10.01" in self.switch_current_firmware:
            self.module.fail_json(msg="Minimum supported "
                                      "firmware version is 10.03")

        if "10.02" in self.switch_current_firmware:
            self.module.fail_json(msg="Minimum supported "
                                      "firmware version is 10.03")

    def get_switch_platform(self):
        '''
        Returns the switch platform
        '''
        platform_url = '/rest/v1/system?attributes=platform_name'
        platform = get(self.module, platform_url)
        self.switch_platform = platform["platform_name"]

    def get_switch_firmware_version(self):
        '''
        Returns the switch firmware
        '''
        firmware_url = '/rest/v1/firmware'
        firmware_versions = get(self.module, firmware_url)
        self.switch_current_firmware = firmware_versions["current_version"]

    def get_firmware_upgrade_status(self):
        '''
        Returns the firmware upgrade status
        '''
        fimrware_status_url = '/rest/v1/firmware/status'
        firmware_update_status = get(self.module, fimrware_status_url)
        return firmware_update_status

    def get_switch_config(self, config_name='running-config',
                          store_config=True):
        '''
        Returns the switch config
        '''
        config_url = '/rest/v1/fullconfigs/{cfg}'.format(cfg=config_name)

        running_config = get(self.module, config_url)

        if store_config:
            self.running_config = copy.deepcopy(running_config)
            self.original_config = copy.deepcopy(running_config)

        return running_config

    def copy_switch_config_to_remote_location(self, config_name, config_type,
                                              destination, vrf):
        '''
        TFTP switch config to TFTP server
        '''
        config_url = ('/rest/v1/fullconfigs/'
                      '{cfg}?to={dest}&type={type}'
                      '&vrf={vrf}'.format(cfg=config_name,
                                          dest=destination,
                                          type=config_type,
                                          vrf=vrf))

        get(self.module, config_url)
        return

    def tftp_switch_config_from_remote_location(self, config_file_location,
                                                config_name, vrf):
        '''
        TFTP switch config from TFTP server
        '''
        config_url = ('/rest/v1/fullconfigs/'
                      '{cfg}?from={dest}&vrf={vrf}'
                      ''.format(cfg=config_name,
                                dest=config_file_location,
                                vrf=vrf))

        put(self.module, config_url)
        return

    def upload_switch_config(self, config, config_name='running-config'):
        '''
        Upload switch config
        '''
        config_url = '/rest/v1/fullconfigs/{cfg}'.format(cfg=config_name)
        config_json = json.dumps(config)
        put(self.module, config_url, config_json)
        return

    def update_switch_config(self):
        '''
        Update switch config
        '''
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
