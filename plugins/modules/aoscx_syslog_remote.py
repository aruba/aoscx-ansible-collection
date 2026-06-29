#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_syslog_remote
version_added: "4.6.0"
short_description: Create, update or delete a remote syslog server
description: >
  This module provides configuration management of remote syslog servers on
  AOS-CX devices (system/syslog_remotes).
author: Aruba Networks (@ArubaNetworks)
options:
  remote_host:
    description: IP address or hostname of the remote syslog server. Index
      under system/syslog_remotes.
    required: true
    type: str
  vrf:
    description: Name of the VRF used to reach the server.
    required: false
    type: str
    default: default
  transport:
    description: Transport protocol used to reach the server.
    required: false
    type: str
    choices:
      - udp
      - tcp
      - tls
  port_number:
    description: Destination port of the remote syslog server.
    required: false
    type: int
  severity:
    description: Minimum severity of logs sent to the server.
    required: false
    type: str
    choices:
      - debug
      - info
      - notice
      - warning
      - err
      - crit
      - alert
      - emerg
  include_auditable_events:
    description: Whether auditable events are forwarded to the server.
    required: false
    type: bool
  disable:
    description: Disable forwarding to this server without removing it.
    required: false
    type: bool
  state:
    description: Create, update or delete the remote syslog server.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a remote syslog server over TCP
  aoscx_syslog_remote:
    remote_host: 192.0.2.10
    transport: tcp
    port_number: 514
    severity: info

- name: Delete a remote syslog server
  aoscx_syslog_remote:
    remote_host: 192.0.2.10
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.syslog_remote import SyslogRemote
    from pyaoscx.vrf import Vrf

    HAS_PYAOSCX_SYSLOG = True
except ImportError:
    HAS_PYAOSCX_SYSLOG = False

if HAS_PYAOSCX_SYSLOG:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        remote_host=dict(type="str", required=True),
        vrf=dict(type="str", required=False, default="default"),
        transport=dict(
            type="str", required=False, choices=["udp", "tcp", "tls"]
        ),
        port_number=dict(type="int", required=False),
        severity=dict(
            type="str",
            required=False,
            choices=[
                "debug",
                "info",
                "notice",
                "warning",
                "err",
                "crit",
                "alert",
                "emerg",
            ],
        ),
        include_auditable_events=dict(type="bool", required=False),
        disable=dict(type="bool", required=False),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_SYSLOG:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support syslog remotes. "
            "Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    remote_host = ansible_module.params["remote_host"]
    vrf = ansible_module.params["vrf"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    remote = SyslogRemote(session, remote_host)
    try:
        remote.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            remote.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    kwargs = {}
    for field in (
        "transport",
        "port_number",
        "severity",
        "include_auditable_events",
        "disable",
    ):
        value = ansible_module.params[field]
        if value is not None:
            kwargs[field] = value

    if vrf is not None and not exists:
        vrf_obj = Vrf(session, vrf)
        vrf_obj.get()
        kwargs["vrf"] = vrf_obj.get_uri()

    changed = not exists
    for key, value in kwargs.items():
        if not exists or getattr(remote, key, None) != value:
            setattr(remote, key, value)
            if key not in remote.config_attrs:
                remote.config_attrs.append(key)
            changed = True

    if changed:
        remote.apply()
    result["changed"] = changed

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
