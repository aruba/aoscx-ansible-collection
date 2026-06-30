#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_vxlan_interface
version_added: "4.6.0"
short_description: Create, update or delete a VXLAN tunnel interface on AOS-CX.
description: >
  This module provides configuration management of the VXLAN tunnel interface
  (for example C(vxlan1)) on AOS-CX devices: its source IPv4 address, the
  destination UDP port, the administrative state and the description. The
  VNI-to-VLAN and VNI-to-VRF mappings carried by the interface are managed with
  the M(arubanetworks.aoscx.aoscx_vni) module.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the VXLAN tunnel interface, in the format C(vxlanN), for example
      C(vxlan1).
    type: str
    required: true
  source_ip:
    description: >
      Source IPv4 address used for VXLAN encapsulation, for example
      C(10.0.0.1). Equivalent to the CLI C(source ip) command.
    type: str
    required: false
  dest_udp_port:
    description: >
      Destination UDP port used by the VXLAN tunnel. When omitted the switch
      default (4789) is kept.
    type: int
    required: false
  description:
    description: Description of the VXLAN interface.
    type: str
    required: false
  enabled:
    description: >
      Administrative state of the interface. C(true) brings the interface up
      (C(no shutdown)), C(false) shuts it down. When omitted, a newly created
      interface is brought up and an existing interface is left unchanged.
    type: bool
    required: false
  state:
    description: Create, update or delete the VXLAN interface.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Create VXLAN interface vxlan1 with a source IP and bring it up
  arubanetworks.aoscx.aoscx_vxlan_interface:
    name: vxlan1
    source_ip: 10.141.254.11
    enabled: true
    state: create

- name: Update the destination UDP port and description of vxlan1
  arubanetworks.aoscx.aoscx_vxlan_interface:
    name: vxlan1
    dest_udp_port: 4789
    description: EVPN-VXLAN overlay
    state: update

- name: Shut down the VXLAN interface
  arubanetworks.aoscx.aoscx_vxlan_interface:
    name: vxlan1
    enabled: false
    state: update

- name: Delete the VXLAN interface
  arubanetworks.aoscx.aoscx_vxlan_interface:
    name: vxlan1
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        source_ip=dict(type="str", required=False, default=None),
        dest_udp_port=dict(type="int", required=False, default=None),
        description=dict(type="str", required=False, default=None),
        enabled=dict(type="bool", required=False, default=None),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    name = ansible_module.params["name"]
    source_ip = ansible_module.params["source_ip"]
    dest_udp_port = ansible_module.params["dest_udp_port"]
    description = ansible_module.params["description"]
    enabled = ansible_module.params["enabled"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: the interface name is interpolated into REST URIs, so
    # reject values that could escape the intended resource path.
    if name in ("", ".", "..") or "/" in name or "," in name:
        ansible_module.fail_json(
            msg="Invalid VXLAN interface name: {0}".format(name)
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    interface = session.api.get_module(session, "Interface", name)
    try:
        interface.get()
        exists = True
    except Exception:
        exists = False

    # ----------------------------------------------------------------- delete
    if state == "delete":
        if exists:
            if getattr(interface, "type", None) != "vxlan":
                ansible_module.fail_json(
                    msg="Interface {0} is not a VXLAN interface.".format(name)
                )
            if not ansible_module.check_mode:
                interface.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    # ----------------------------------------------------------- create/update
    if exists and getattr(interface, "type", None) != "vxlan":
        ansible_module.fail_json(
            msg="Interface {0} already exists and is not a VXLAN "
            "interface.".format(name)
        )

    if ansible_module.check_mode:
        # Report a change when the interface does not exist yet or when any
        # configurable value is supplied; the actual diff is computed by the
        # SDK on a real run.
        result["changed"] = (not exists) or any(
            value is not None
            for value in (source_ip, dest_udp_port, description, enabled)
        )
        ansible_module.exit_json(**result)

    changed = False
    if not exists:
        interface.type = "vxlan"
        interface.apply()
        changed = True

    if source_ip is not None:
        interface.options["local_ip"] = source_ip
    if dest_udp_port is not None:
        interface.options["vxlan_dest_udp_port"] = str(dest_udp_port)
    if description is not None:
        interface.description = description
    if enabled is not None:
        interface.admin_state = "up" if enabled else "down"
    elif not exists:
        # A freshly created VXLAN interface is brought up by default.
        interface.admin_state = "up"

    changed = interface.apply() or changed

    result["changed"] = changed
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
