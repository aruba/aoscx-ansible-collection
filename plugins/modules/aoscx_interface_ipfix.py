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
module: aoscx_interface_ipfix
version_added: "4.6.0"
short_description: Attach an ingress IPFIX flow monitor to an interface.
description:
  - This module attaches or detaches an ingress IPFIX flow monitor on an
    AOS-CX interface. One IPv4 and one IPv6 monitor can be attached. IPFIX
    requires REST API version 10.13 or later.
author: Aruba Networks (@ArubaNetworks)
options:
  interface:
    description: Name of the interface to configure.
    required: true
    type: str
  monitor:
    description: Name of the IPFIX flow monitor to attach. Required unless
      state is delete.
    required: false
    type: str
  address_family:
    description: Address family of the ingress monitor.
    required: false
    choices:
      - ipv4
      - ipv6
    default: ipv4
    type: str
  state:
    description: Attach or detach the monitor.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Attach the app-vis monitor on ingress
  arubanetworks.aoscx.aoscx_interface_ipfix:
    interface: 1/1/1
    monitor: app-vis
    address_family: ipv4
    state: create

- name: Detach the IPv4 ingress monitor
  arubanetworks.aoscx.aoscx_interface_ipfix:
    interface: 1/1/1
    address_family: ipv4
    state: delete
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


def main():
    module_args = dict(
        interface=dict(type="str", required=True),
        monitor=dict(type="str", default=None),
        address_family=dict(
            type="str", default="ipv4", choices=["ipv4", "ipv6"]
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_if=[
            ("state", "create", ("monitor",)),
            ("state", "update", ("monitor",)),
        ],
    )

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    name = ansible_module.params["interface"]
    monitor = ansible_module.params["monitor"]
    address_family = ansible_module.params["address_family"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    session = get_pyaoscx_session(ansible_module)
    device = Device(session)
    interface = device.interface(name)

    current = getattr(interface, "ipfix_flow_monitor_in", None)
    if not isinstance(current, dict):
        current = {}

    new_config = dict(current)
    if state == "delete":
        new_config.pop(address_family, None)
    else:
        try:
            mon = session.api.get_module(session, "IpfixFlowMonitor", monitor)
            monitor_uri = mon.get_uri()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not resolve IPFIX monitor: {0}".format(str(e))
            )
        new_config[address_family] = monitor_uri

    # Compare by the monitor name (last path segment) to avoid spurious
    # changes from differing URI prefixes.
    def names(cfg):
        return {
            af: uri.rstrip("/").split("/")[-1] for af, uri in cfg.items()
        }

    changed = names(new_config) != names(current)
    if changed:
        interface.ipfix_flow_monitor_in = new_config
        if "ipfix_flow_monitor_in" not in interface.config_attrs:
            interface.config_attrs.append("ipfix_flow_monitor_in")
        if not ansible_module.check_mode:
            interface.apply()

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
