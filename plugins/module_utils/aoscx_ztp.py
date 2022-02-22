#!/usr/bin/env python
# -*- coding: utf-8 -*-

# (C) Copyright 2020-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time
import traceback

from contextlib import closing

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import missing_required_lib

PARAMIKO_IMP_ERR = None
try:
    import paramiko

    HAS_PARAMIKO_LIB = True
except ImportError:
    HAS_PARAMIKO_LIB = False
    PARAMIKO_IMP_ERR = traceback.format_exc()

CHANNEL_TIMEOUT = 8
READ_TIMEOUT = 10
READ_WAIT_TIME = 2
BUFFER_SIZE = 4096
BLANK_PASSWORD = ""
ENTER_PASSWORD_MSG = "Enter new password:"
CONFIRM_PASSWORD_MSG = "Confirm new password:"
SHELL_PROMPT = "#"


def connect_ztp_device(module, hostname, username, password):
    """Connects to a ZTP device using SSH and configures authentication.

    The function tries to login with the out-of-the-box values of a zeroized
    device, a zeroized device has username:'admin' and a blank password.

    When the connection is successful, the Switch will ask to setup a new
    password, the function enters and confirms the password.

    When the connection is unsuccessful, due to the Switch authentication
    already configured, or there is an error with the connection parameters,
    the function logs the error and returns.

    :param module: Ansible module.
    :param hostname: The Switch to connect to.
    :param username: The username to authenticate as.
    :param password: A password to use for authentication.
    """

    if not HAS_PARAMIKO_LIB:
        module.fail_json(
            msg=missing_required_lib("paramiko"), exception=PARAMIKO_IMP_ERR
        )

    with closing(paramiko.SSHClient()) as ssh_client:

        # Define SSH parameters
        paramiko_ssh_connection_args = {
            "hostname": hostname,
            "username": username,
            "password": BLANK_PASSWORD,
            "look_for_keys": False,
            "allow_agent": False,
        }

        # Default AutoAdd as Policy
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Connect to switch via SSH
            ssh_client.connect(**paramiko_ssh_connection_args)

            # Get shell
            shell_channel = ssh_client.invoke_shell()

            # Set channel response timeout
            shell_channel.settimeout(CHANNEL_TIMEOUT)

            # Wait for message and enter new password
            if wait_for_channel_msg(shell_channel, ENTER_PASSWORD_MSG):
                write_to_channel(shell_channel, password)
            else:
                return

            # Wait for message and confirm new password
            if wait_for_channel_msg(shell_channel, CONFIRM_PASSWORD_MSG):
                write_to_channel(shell_channel, password)
            else:
                return

            # Wait for CLI prompt
            wait_for_channel_msg(shell_channel, SHELL_PROMPT)

        except paramiko.ssh_exception.AuthenticationException as e:
            module.log("Unable to authenticate: {0}".format(to_text(e)))

        except Exception as e:
            module.log(to_text(e))


def wait_for_channel_msg(shell_channel, msg):
    """Waits until the message is read from the channel.

    :param shell_channel: The channel to read from.
    :param msg: The message itself.
    :return: `True` if successful, `False` otherwise.
    """
    retry = 0
    while retry < READ_TIMEOUT:
        read_buffer = read_from_channel(shell_channel)
        if msg in read_buffer:
            return True
        time.sleep(READ_WAIT_TIME)
        retry += READ_WAIT_TIME

    return False


def read_from_channel(shell_channel):
    """Reads the buffer from channel.

    :param shell_channel: The channel to read from.
    :return: The read lines.
    """
    recv = ""
    # Loop while channel is able to recv data
    while shell_channel.recv_ready():
        recv = shell_channel.recv(BUFFER_SIZE)
        if not recv:
            break
        recv = recv.decode("utf-8", "ignore")
    return recv


def write_to_channel(shell_channel, cmd):
    """Writes commands to the channel.

    :param shell_channel: The channel to write to.
    :param cmd: The command itself.
    """
    cmd = cmd.rstrip()
    cmd += "\n"
    cmd = cmd.encode("ascii", "ignore")
    shell_channel.send(cmd)
