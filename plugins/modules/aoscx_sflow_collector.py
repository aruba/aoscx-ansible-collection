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
module: aoscx_sflow_collector
version_added: "4.6.0"
short_description: Create or delete an sFlow collector on AOS-CX
description: >
  This module provides configuration management of sFlow collectors on
  AOS-CX devices. A collector is the destination (IP address, UDP port and
  VRF) to which an sFlow instance exports its flow records. The collector is
  identified by the compound index of VRF, IP address and UDP port, and has
  no configurable attributes beyond that index.
author: Aruba Networks (@ArubaNetworks)
options:
  sflow_name:
    description: >
      Name of the parent sFlow instance under which the collector is
      configured. The instance must already exist.
    required: true
    type: str
  vrf:
    description: >
      Name of the VRF used to reach the collector. The VRF must already
      exist on the device.
    required: false
    default: default
    type: str
  ip_address:
    description: IP address of the sFlow collector.
    required: true
    type: str
  udp_port:
    description: UDP port on which the collector receives sFlow datagrams.
    required: false
    default: 6343
    type: int
  state:
    description: Create or delete the sFlow collector.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Add a collector to the global sFlow instance
  aoscx_sflow_collector:
    sflow_name: global
    vrf: default
    ip_address: 10.0.0.50
    udp_port: 6343

- name: Delete an sFlow collector
  aoscx_sflow_collector:
    sflow_name: global
    vrf: default
    ip_address: 10.0.0.50
    udp_port: 6343
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        sflow_name=dict(type="str", required=True),
        vrf=dict(type="str", required=False, default="default"),
        ip_address=dict(type="str", required=True),
        udp_port=dict(type="int", required=False, default=6343),
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

    sflow_name = ansible_module.params["sflow_name"]
    vrf_name = ansible_module.params["vrf"]
    ip_address = ansible_module.params["ip_address"]
    udp_port = ansible_module.params["udp_port"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        sflow = session.api.get_module(session, "SFlow", sflow_name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support sFlow. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        sflow.get(selector="writable")
    except Exception:
        ansible_module.fail_json(
            msg="Parent sFlow instance '{0}' does not exist.".format(
                sflow_name
            )
        )

    try:
        vrf = session.api.get_module(session, "Vrf", vrf_name)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not reference VRF '{0}': {1}".format(vrf_name, str(e))
        )

    collector = session.api.get_module(
        session,
        "SFlowCollector",
        vrf,
        ip_address=ip_address,
        udp_port=udp_port,
        parent_sflow=sflow,
    )

    try:
        collector.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                collector.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete sFlow collector: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- create
    if not exists:
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                collector.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create sFlow collector: {0}".format(str(e))
                )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
