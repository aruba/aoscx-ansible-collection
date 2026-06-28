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
module: aoscx_sflow
version_added: "4.6.0"
short_description: Create, update or delete an sFlow instance on AOS-CX
description: >
  This module provides configuration management of sFlow (traffic sampling)
  instances on AOS-CX devices. An sFlow instance controls how the device
  samples traffic and exports flow records to collectors.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the sFlow instance. This is the index of the resource under
      system/sflows.
    required: true
    type: str
  agent_address:
    description: >
      Source IP address (IPv4 or IPv6) used by the sFlow agent in exported
      datagrams.
    required: false
    type: str
  enabled:
    description: Whether the sFlow instance is enabled.
    required: false
    type: bool
  header:
    description: >
      Maximum number of bytes copied from each sampled packet header.
    required: false
    type: int
  max_datagram:
    description: Maximum size in bytes of an exported sFlow datagram.
    required: false
    type: int
  mode:
    description: Direction of traffic that is sampled.
    required: false
    choices:
      - both
      - egress
      - ingress
    type: str
  polling:
    description: Counter polling interval in seconds.
    required: false
    type: int
  sampling:
    description: Packet sampling rate (one in N packets).
    required: false
    type: int
  state:
    description: Create, update or delete the sFlow instance.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an sFlow instance sampling both directions
  aoscx_sflow:
    name: global
    enabled: true
    mode: both
    sampling: 4096
    polling: 30
    agent_address: 10.0.0.1

- name: Update the sFlow sampling rate
  aoscx_sflow:
    name: global
    state: update
    sampling: 2048

- name: Disable an sFlow instance
  aoscx_sflow:
    name: global
    state: update
    enabled: false

- name: Delete an sFlow instance
  aoscx_sflow:
    name: global
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
        agent_address=dict(type="str", required=False, default=None),
        enabled=dict(type="bool", required=False, default=None),
        header=dict(type="int", required=False, default=None),
        max_datagram=dict(type="int", required=False, default=None),
        mode=dict(
            type="str",
            required=False,
            choices=["both", "egress", "ingress"],
        ),
        polling=dict(type="int", required=False, default=None),
        sampling=dict(type="int", required=False, default=None),
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

    name = ansible_module.params["name"]
    state = ansible_module.params["state"]

    # Writable scalar attributes managed by this module.
    scalar_attrs = [
        "agent_address",
        "enabled",
        "header",
        "max_datagram",
        "mode",
        "polling",
        "sampling",
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
        sflow = session.api.get_module(session, "SFlow", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support sFlow. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        sflow.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                sflow.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete sFlow instance: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        sflow = session.api.get_module(session, "SFlow", name, **supplied)
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                sflow.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create sFlow instance: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(sflow, attr, None) != value:
            changed = True
            setattr(sflow, attr, value)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            sflow.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update sFlow instance: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
