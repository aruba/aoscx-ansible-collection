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
module: aoscx_port_access_interface
version_added: "4.6.0"
short_description: Configure port access (NAC) settings on an interface.
description:
  - This module configures port access related settings (onboarding,
    client limit, BPDU allow, authentication mode, dot1x/mac-auth, client IP
    tracking, device fingerprint and application recognition) on an AOS-CX
    interface.
author: Aruba Networks (@ArubaNetworks)
options:
  interface:
    description: Name of the interface to configure.
    required: true
    type: str
  concurrent_onboarding:
    description: Enable concurrent onboarding for port access.
    required: false
    type: bool
  client_limit:
    description: Maximum number of authenticated clients on the interface.
    required: false
    type: int
  auth_mode:
    description: Port access authentication mode.
    required: false
    type: str
    choices:
      - client-mode
      - device-mode
      - proxy-mode
      - multi-domain
  allow_bpdu:
    description: Protocol BPDUs allowed before authentication.
    required: false
    type: list
    elements: str
    choices:
      - lldp
      - cdp
  client_ip_track:
    description: Client IP tracking configuration.
    required: false
    type: dict
    suboptions:
      admin_state:
        description: Enable or disable client IP tracking.
        type: str
      update_interval:
        description: Update interval in seconds.
        type: int
      client_limit:
        description: Maximum number of tracked clients.
        type: int
  device_fingerprint:
    description: Device fingerprint configuration.
    required: false
    type: dict
    suboptions:
      profile_name:
        description: Device fingerprint profile name to apply.
        type: str
      client_limit:
        description: Maximum number of fingerprinted clients.
        type: int
  state:
    description: Configure or reset port access settings on the interface.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Configure port access on an interface
  arubanetworks.aoscx.aoscx_port_access_interface:
    interface: 1/1/1
    concurrent_onboarding: true
    client_limit: 2
    allow_bpdu:
      - cdp
      - lldp
    client_ip_track:
      admin_state: enable
      update_interval: 60
    device_fingerprint:
      profile_name: ACLI-Device-Fingerprint
    state: create
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )

ATTR_MAP = {
    "concurrent_onboarding": "port_access_concurrent_onboarding",
    "client_limit": "port_access_clients_limit",
    "auth_mode": "port_access_auth_mode",
    "allow_bpdu": "port_access_allow_bpdu",
    "client_ip_track": "client_ip_track_configuration",
    "device_fingerprint": "device_fingerprint_configuration",
}

# Default values used to reset dict attributes on delete so the operation
# is idempotent.
DELETE_DEFAULTS = {
    "client_ip_track": {
        "admin_state": "auto",
        "client_limit": 128,
        "update_interval": 1800,
    },
    "device_fingerprint": {"client_limit": 256},
}


def main():
    module_args = dict(
        interface=dict(type="str", required=True),
        concurrent_onboarding=dict(type="bool", default=None),
        client_limit=dict(type="int", default=None),
        auth_mode=dict(
            type="str",
            default=None,
            choices=[
                "client-mode",
                "device-mode",
                "proxy-mode",
                "multi-domain",
            ],
        ),
        allow_bpdu=dict(
            type="list", elements="str", default=None,
            choices=["lldp", "cdp"],
        ),
        client_ip_track=dict(type="dict", default=None),
        device_fingerprint=dict(type="dict", default=None),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    name = ansible_module.params["interface"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    session = get_pyaoscx_session(ansible_module)
    device = Device(session)
    interface = device.interface(name)
    modified = interface.modified

    supplied = {
        attr: ansible_module.params[attr]
        for attr in ATTR_MAP
        if ansible_module.params[attr] is not None
    }

    for attr, value in supplied.items():
        target = ATTR_MAP[attr]
        if state == "delete":
            if isinstance(value, list):
                new_value = []
            elif isinstance(value, dict):
                new_value = DELETE_DEFAULTS.get(attr, {})
            elif isinstance(value, bool):
                new_value = False
            else:
                new_value = None
        else:
            new_value = value
        current = getattr(interface, target, None)
        if isinstance(new_value, dict) and isinstance(current, dict):
            if state == "delete":
                different = current != new_value
            elif not new_value:
                different = bool(current)
            else:
                different = any(
                    current.get(k) != v for k, v in new_value.items()
                )
                if different:
                    merged = dict(current)
                    merged.update(new_value)
                    new_value = merged
        elif isinstance(new_value, list) and isinstance(current, list):
            different = set(new_value) != set(current)
        else:
            different = current != new_value
        if different:
            setattr(interface, target, new_value)
            if target not in interface.config_attrs:
                interface.config_attrs.append(target)
            modified = True

    if not ansible_module.check_mode:
        modified |= interface.apply()

    result["changed"] = modified
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
