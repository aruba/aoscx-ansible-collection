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
module: aoscx_dhcp_relay
version_added: "4.6.0"
short_description: Create, Update or Delete DHCP relays on AOS-CX
description: >
  This module provides configuration management of DHCP relays on AOS-CX
  devices. A DHCP relay duplicates DHCP broadcast packets received on a
  routed port and forwards them as unicast to a list of DHCP server
  destinations, for a given VRF.
author: Aruba Networks (@ArubaNetworks)
options:
  port:
    description: >
      Name of the routed port on which DHCP broadcast packets are received,
      for example C(1/1/3).
    required: true
    type: str
  vrf:
    description: VRF through which the configured DHCP servers are reachable.
    required: false
    default: default
    type: str
  ipv4_ucast_server:
    description: >
      List of IPv4 unicast server destinations (up to 8) to which DHCP
      packets are forwarded. Represents the full desired set: a server
      present on the switch but not listed here is removed. When omitted the
      IPv4 server list is left unchanged. Ignored when I(state) is C(delete).
    required: false
    type: list
    elements: str
  ipv6_ucast_server:
    description: >
      List of IPv6 unicast server destinations (up to 8) to which DHCP
      packets are forwarded. Represents the full desired set: a server
      present on the switch but not listed here is removed. When omitted the
      IPv6 server list is left unchanged. Ignored when I(state) is C(delete).
    required: false
    type: list
    elements: str
  bootp_gateway:
    description: >
      Gateway IPv4 address the DHCP relay agent uses as the source for relayed
      packets. When omitted it is left unchanged. Ignored when I(state) is
      C(delete).
    required: false
    type: str
  state:
    description: Create, update or delete the DHCP relay.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create a DHCP relay with two IPv4 servers
  aoscx_dhcp_relay:
    port: 1/1/3
    vrf: default
    ipv4_ucast_server:
      - 10.1.1.1
      - 10.1.1.2

- name: Configure a relay with a BOOTP gateway
  aoscx_dhcp_relay:
    port: 1/1/3
    vrf: default
    ipv4_ucast_server:
      - 10.1.1.1
    bootp_gateway: 10.1.1.254

- name: Update the IPv4 server list of an existing relay
  aoscx_dhcp_relay:
    port: 1/1/3
    state: update
    ipv4_ucast_server:
      - 10.1.1.1

- name: Delete a DHCP relay
  aoscx_dhcp_relay:
    port: 1/1/3
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the DHCP relay was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

# AOS-CX accepts at most 8 unicast servers per relay and per address family.
MAX_SERVERS = 8


def main():
    module_args = dict(
        port=dict(type="str", required=True),
        vrf=dict(type="str", default="default"),
        ipv4_ucast_server=dict(type="list", elements="str", default=None),
        ipv6_ucast_server=dict(type="list", elements="str", default=None),
        bootp_gateway=dict(type="str", default=None),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    port = ansible_module.params["port"]
    vrf = ansible_module.params["vrf"]
    ipv4_ucast_server = ansible_module.params["ipv4_ucast_server"]
    ipv6_ucast_server = ansible_module.params["ipv6_ucast_server"]
    bootp_gateway = ansible_module.params["bootp_gateway"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    # Defense in depth: port and vrf are interpolated into the REST URI,
    # reject values that could escape the resource path.
    for label, value in (("port", port), ("vrf", vrf)):
        if value in ("", ".", "..") or "," in value:
            ansible_module.fail_json(
                msg="Invalid {0}: {1}".format(label, value)
            )
    if "/" in vrf:
        ansible_module.fail_json(msg="Invalid vrf: {0}".format(vrf))

    for label, servers in (
        ("ipv4_ucast_server", ipv4_ucast_server),
        ("ipv6_ucast_server", ipv6_ucast_server),
    ):
        if servers is not None and len(servers) > MAX_SERVERS:
            ansible_module.fail_json(
                msg="{0} accepts at most {1} entries.".format(
                    label, MAX_SERVERS
                )
            )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        vrf_obj = session.api.get_module(session, "Vrf", vrf)
        port_obj = session.api.get_module(session, "Interface", port)
        relay = session.api.get_module(
            session, "DhcpRelay", vrf_obj, port=port_obj
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support DHCP relays. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        relay.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                relay.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete DHCP relay: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        kwargs = {}
        if ipv4_ucast_server is not None:
            kwargs["ipv4_ucast_server"] = ipv4_ucast_server
        if ipv6_ucast_server is not None:
            kwargs["ipv6_ucast_server"] = ipv6_ucast_server
        if bootp_gateway is not None:
            kwargs["other_config"] = {"bootp_gateway": bootp_gateway}
        relay = session.api.get_module(
            session, "DhcpRelay", vrf_obj, port=port_obj, **kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                relay.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create DHCP relay: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False

    def stage(attr, value):
        setattr(relay, attr, value)
        if attr not in relay.config_attrs:
            relay.config_attrs.append(attr)

    if ipv4_ucast_server is not None:
        current = getattr(relay, "ipv4_ucast_server", []) or []
        if sorted(current) != sorted(ipv4_ucast_server):
            changed = True
            stage("ipv4_ucast_server", ipv4_ucast_server)

    if ipv6_ucast_server is not None:
        current = getattr(relay, "ipv6_ucast_server", []) or []
        if sorted(current) != sorted(ipv6_ucast_server):
            changed = True
            stage("ipv6_ucast_server", ipv6_ucast_server)

    if bootp_gateway is not None:
        current_oc = getattr(relay, "other_config", {}) or {}
        if current_oc.get("bootp_gateway") != bootp_gateway:
            changed = True
            new_oc = dict(current_oc)
            new_oc["bootp_gateway"] = bootp_gateway
            stage("other_config", new_oc)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            relay.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update DHCP relay: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
