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
module: aoscx_udp_bcast_forwarder
version_added: "4.6.0"
short_description: Create, Update or Delete UDP broadcast forwarders on AOS-CX
description: >
  This module provides configuration management of UDP broadcast forwarder
  servers on AOS-CX devices. A forwarder duplicates UDP broadcast packets
  received on a routed port to a list of unicast server destinations, for a
  given destination UDP port and VRF.
author: Aruba Networks (@ArubaNetworks)
options:
  src_port:
    description: >
      Name of the routed port on which UDP broadcast packets are received,
      for example C(1/1/1).
    required: true
    type: str
  udp_dport:
    description: >
      Destination UDP port used to match and forward the broadcast packets.
    required: true
    type: int
  dest_vrf:
    description: VRF through which the configured servers are reachable.
    required: false
    default: default
    type: str
  ipv4_ucast_server:
    description: >
      List of IPv4 unicast server destinations (up to 8) to which the UDP
      broadcast packets are forwarded. Represents the full desired set: a
      server present on the switch but not listed here is removed. Ignored
      when I(state) is C(delete).
    required: false
    type: list
    elements: str
  state:
    description: Create, update or delete the UDP broadcast forwarder.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create a UDP broadcast forwarder for DNS (port 53)
  aoscx_udp_bcast_forwarder:
    src_port: 1/1/1
    udp_dport: 53
    dest_vrf: default
    ipv4_ucast_server:
      - 10.0.0.1
      - 10.0.0.2

- name: Update the server list of an existing forwarder
  aoscx_udp_bcast_forwarder:
    src_port: 1/1/1
    udp_dport: 53
    state: update
    ipv4_ucast_server:
      - 10.0.0.1

- name: Delete a UDP broadcast forwarder
  aoscx_udp_bcast_forwarder:
    src_port: 1/1/1
    udp_dport: 53
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the UDP broadcast forwarder was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

# AOS-CX accepts at most 8 IPv4 unicast servers per forwarder.
MAX_SERVERS = 8


def main():
    module_args = dict(
        src_port=dict(type="str", required=True),
        udp_dport=dict(type="int", required=True),
        dest_vrf=dict(type="str", default="default"),
        ipv4_ucast_server=dict(type="list", elements="str", default=None),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    src_port = ansible_module.params["src_port"]
    udp_dport = ansible_module.params["udp_dport"]
    dest_vrf = ansible_module.params["dest_vrf"]
    ipv4_ucast_server = ansible_module.params["ipv4_ucast_server"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: src_port and dest_vrf are interpolated into the REST
    # URI, reject values that could escape the resource path.
    for label, value in (("src_port", src_port), ("dest_vrf", dest_vrf)):
        if value in ("", ".", "..") or "," in value:
            ansible_module.fail_json(
                msg="Invalid {0}: {1}".format(label, value)
            )
    if dest_vrf == "" or "/" in dest_vrf:
        ansible_module.fail_json(msg="Invalid dest_vrf: {0}".format(dest_vrf))

    if udp_dport < 0 or udp_dport > 65535:
        ansible_module.fail_json(msg="udp_dport must be between 0 and 65535.")

    if ipv4_ucast_server is not None and len(ipv4_ucast_server) > MAX_SERVERS:
        ansible_module.fail_json(
            msg="ipv4_ucast_server accepts at most {0} entries.".format(
                MAX_SERVERS
            )
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        vrf = session.api.get_module(session, "Vrf", dest_vrf)
        port = session.api.get_module(session, "Interface", src_port)
        forwarder = session.api.get_module(
            session,
            "UdpBcastForwarderServer",
            vrf,
            src_port=port,
            udp_dport=udp_dport,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support UDP broadcast "
                "forwarders. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        forwarder.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                forwarder.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete UDP forwarder: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    desired = ipv4_ucast_server if ipv4_ucast_server is not None else []

    # ------------------------------------------------------- create / update
    if not exists:
        forwarder = session.api.get_module(
            session,
            "UdpBcastForwarderServer",
            vrf,
            src_port=port,
            udp_dport=udp_dport,
            ipv4_ucast_server=desired,
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                forwarder.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create UDP forwarder: {0}".format(str(e))
                )
    else:
        current = getattr(forwarder, "ipv4_ucast_server", []) or []
        if ipv4_ucast_server is not None and sorted(current) != sorted(
            desired
        ):
            result["changed"] = True
            forwarder.ipv4_ucast_server = desired
            if "ipv4_ucast_server" not in forwarder.config_attrs:
                forwarder.config_attrs.append("ipv4_ucast_server")
            if not ansible_module.check_mode:
                try:
                    forwarder.update()
                except Exception as e:
                    ansible_module.fail_json(
                        msg="Could not update UDP forwarder: {0}".format(
                            str(e)
                        )
                    )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
