from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """author: Aruba Networking
connection: aoscx
short_description: Use pyaocx to run commands on AOS-CX switches
description:
- This connection plugin provides a connection to AOS-CX switches over a REST API.
options:
  host:
    description:
    - Specifies the remote device FQDN or IP address to establish the connection
      to.
    default: inventory_hostname
    vars:
    - name: ansible_host
  port:
    type: int
    description:
    - Specifies the port on the remote device that listens for connections when establishing
      the connection.
    - SSL is always used.
    ini:
    - section: defaults
      key: remote_port
    env:
    - name: ANSIBLE_REMOTE_PORT
    vars:
    - name: ansible_aoscx_port
  network_os:
    description:
    - Configures the device platform network operating system.  This value is used
      to load the correct plugin to communicate with the remote device
    vars:
    - name: ansible_network_os
  remote_user:
    description:
    - The username used to authenticate to the remote device when the API connection
      is first established.  If the remote_user is not specified, the connection will
      use the username of the logged in user.
    - Can be configured from the CLI via the C(--user) or C(-u) options.
    ini:
    - section: defaults
      key: remote_user
    env:
    - name: ANSIBLE_REMOTE_USER
    vars:
    - name: ansible_user
  password:
    description:
    - Configures the user password used to authenticate to the remote device when
      needed for the device API.
    vars:
    - name: ansible_password
    - name: ansible_aoscx_pass
    - name: ansible_aoscx_password
  validate_certs:
    type: boolean
    description:
    - Whether to validate SSL certificates
    default: true
    vars:
    - name: ansible_aoscx_validate_certs
  use_proxy:
    type: boolean
    description:
    - Whether to use https_proxy for requests.
    default: true
    vars:
    - name: ansible_aoscx_use_proxy
  persistent_connect_timeout:
    type: int
    description:
    - Configures, in seconds, the amount of time to wait when trying to initially
      establish a persistent connection.  If this value expires before the connection
      to the remote device is completed, the connection will fail.
    default: 30
    ini:
    - section: persistent_connection
      key: connect_timeout
    env:
    - name: ANSIBLE_PERSISTENT_CONNECT_TIMEOUT
    vars:
    - name: ansible_connect_timeout
  persistent_command_timeout:
    type: int
    description:
    - Configures, in seconds, the amount of time to wait for a command to return from
      the remote device.  If this timer is exceeded before the command returns, the
      connection plugin will raise an exception and close.
    default: 30
    ini:
    - section: persistent_connection
      key: command_timeout
    env:
    - name: ANSIBLE_PERSISTENT_COMMAND_TIMEOUT
    vars:
    - name: ansible_command_timeout
  persistent_log_messages:
    type: boolean
    description:
    - This flag will enable logging the command executed and response received from
      target device in the ansible log file. For this option to work 'log_path' ansible
      configuration option is required to be set to a file path with write access.
    - Be sure to fully understand the security implications of enabling this option
      as it could create a security vulnerability by logging sensitive information
      in log file.
    default: false
    ini:
    - section: persistent_connection
      key: log_messages
    env:
    - name: ANSIBLE_PERSISTENT_LOG_MESSAGES
    vars:
    - name: ansible_persistent_log_messages
"""
import json
from ansible.errors import AnsibleConnectionFailure, AnsibleError
from ansible.plugins.connection import ConnectionBase, NetworkConnectionBase, ensure_connect
from ansible.module_utils.six import PY3
from ansible.playbook.play_context import PlayContext

try:
    from pyaoscx.session import Session
    from pyaoscx.exceptions.login_error import LoginError
    import urllib3
    urllib3.disable_warnings()
    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

try:
    from requests.utils import dict_from_cookiejar
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class Connection(NetworkConnectionBase):
    """PYAOSCX connections"""

    transport = "arubanetworks.aoscx"  # FQ collection name
    has_pipelining = False

    def __init__(self, play_context, new_stdin, *args, **kwargs):
        super(Connection, self).__init__(play_context, new_stdin, *args, **kwargs)
        self.session = None
        self.base_url = None
        self.use_proxy = True
        self.__username = None
        self.__password = None

    def _connect(self):
        if not HAS_PYAOSCX:
            raise AnsibleError(
                'The "pyaoscx" python library is required to use the aoscx connection type.\n'
            )
        if not HAS_REQUESTS:
            raise AnsibleError(
                'The "requests" python library is required to use the aoscx connection type.\n'
            )
        if PY3 is False:
            raise AnsibleError(
                'AOSCX modules using the aoscx connection must be run with python3 as its interpreter.\n'
            )
        super(Connection, self)._connect()
        if not self._connected:
            if not self._network_os:
                raise AnsibleConnectionFailure(
                    "Unable to automatically determine host network os. Please "
                    "manually configure ansible_network_os value for this host"
                )
            self.queue_message(
                "log", "network_os is set to %s" % self._network_os
            )

            switchip = self.get_option("host")
            username = self.get_option("remote_user")
            password = self.get_option("password")
            self.use_proxy = self.get_option("use_proxy")
            self.base_url = "https://{0}/rest/v10.04/".format(switchip)
            # Set Credentials
            self.__username = username
            self.__password = password

            try:
                self.session = Session.login(self.base_url, username, password, self.use_proxy, True)
            except LoginError as err:
                raise AnsibleConnectionFailure(
                    err.message
                )
            self.queue_message(
                "vvvv",
                "created pyaoscx connection for network_os %s" % self._network_os,
            )
            self._connected = True

    @ensure_connect
    def get_session(self):
        cookies = dict_from_cookiejar(self.session.cookies)
        return dict(
            success=True, cookies=cookies,
            url=self.base_url, use_proxy=self.use_proxy,
            credentials=dict(
                username=self.__username,
                password=self.__password
            )
        )

    def close(self):
        if self.session is not None:
            login_session = dict(
                s=self.session,
                url=self.base_url,
                credentials=dict(
                    username=self.__username,
                    password=self.__password
                )
            )

            Session.logout(**login_session)
            self.use_proxy = None
            self.session = None
            self.base_url = None
        super(Connection, self).close()
