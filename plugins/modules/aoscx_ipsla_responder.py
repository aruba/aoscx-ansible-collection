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
module: aoscx_ipsla_responder
version_added: "4.6.0"
short_description: Create or delete an IP SLA responder
description: >
  This module provides configuration management of IP SLA responders on
  AOS-CX devices (system/ipsla_responders). An IP SLA responder answers
  probes sent by IP SLA sources. IP SLA requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16). A responder has no modifiable
  attributes, so any change is applied by recreating the responder.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the IP SLA responder. This is the index of the resource under
      system/ipsla_responders.
    required: true
    type: str
  vrf:
    description: Name of the VRF the IP SLA responder belongs to.
    required: false
    default: default
    type: str
  type:
    description: Probe type the responder answers.
    required: false
    type: str
    choices:
      - udp_echo
      - tcp_connect
      - udp_jitter_voip
  responder_port_number:
    description: UDP/TCP port the responder listens on (1-65535).
    required: false
    type: int
  responder_type:
    description: IP address family used by the responder.
    required: false
    type: str
    choices:
      - ipv4
      - ipv6
  responder_ip:
    description: IP address the responder is bound to.
    required: false
    type: str
  persistence:
    description: Whether the responder survives a reboot.
    required: false
    type: str
    choices:
      - persistent
      - volatile
  state:
    description: Create or delete the IP SLA responder.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a UDP echo IP SLA responder
  aoscx_ipsla_responder:
    name: responder-1
    type: udp_echo
    vrf: default
    responder_port_number: 5000
    responder_type: ipv4

- name: Delete an IP SLA responder
  aoscx_ipsla_responder:
    name: responder-1
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
        vrf=dict(type="str", required=False, default="default"),
        type=dict(
            type="str",
            required=False,
            default=None,
            choices=["udp_echo", "tcp_connect", "udp_jitter_voip"],
        ),
        responder_port_number=dict(type="int", required=False, default=None),
        responder_type=dict(
            type="str",
            required=False,
            default=None,
            choices=["ipv4", "ipv6"],
        ),
        responder_ip=dict(type="str", required=False, default=None),
        persistence=dict(
            type="str",
            required=False,
            default=None,
            choices=["persistent", "volatile"],
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    name = ansible_module.params["name"]
    vrf_name = ansible_module.params["vrf"]
    state = ansible_module.params["state"]

    scalar_attrs = [
        "type",
        "responder_port_number",
        "responder_type",
        "responder_ip",
        "persistence",
    ]
    supplied = {
        attr: ansible_module.params[attr]
        for attr in scalar_attrs
        if ansible_module.params[attr] is not None
    }

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        responder = session.api.get_module(session, "IpslaResponder", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support IP SLA. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        responder.get(selector="configuration")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                responder.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete IP SLA responder: "
                    "{0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------------ create
    def build_responder():
        vrf = session.api.get_module(session, "Vrf", vrf_name)
        try:
            vrf.get()
        except Exception:
            ansible_module.fail_json(
                msg="Could not find VRF, make sure it exists"
            )
        return session.api.get_module(
            session, "IpslaResponder", name, vrf=vrf, **supplied
        )

    if not exists:
        new_responder = build_responder()
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                new_responder.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create IP SLA responder: "
                    "{0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # A responder has no modifiable attributes. Compare the supplied values
    # against the current configuration and recreate the responder if they
    # differ.
    differs = False
    current_vrf = getattr(responder, "vrf", None)
    if isinstance(current_vrf, dict) and current_vrf:
        current_vrf_name = list(current_vrf.keys())[0]
    else:
        current_vrf_name = None
    if current_vrf_name is not None and current_vrf_name != vrf_name:
        differs = True
    for attr, value in supplied.items():
        if getattr(responder, attr, None) != value:
            differs = True

    result["changed"] = differs
    if differs and not ansible_module.check_mode:
        try:
            responder.delete()
            build_responder().create()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update IP SLA responder: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
