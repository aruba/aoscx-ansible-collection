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
module: aoscx_ipfix_flow_record
version_added: "4.6.0"
short_description: Create, update or delete an IPFIX flow record on AOS-CX
description: >
  This module provides configuration management of IPFIX flow records on
  AOS-CX devices. A flow record defines the key fields (match) and non-key
  fields (collect) included in exported IPFIX flows. IPFIX requires REST API
  version 10.13 or later (set ansible_aoscx_rest_version to 10.13).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the flow record. This is the index of the resource under
      system/ipfix_flow_records.
    required: true
    type: str
  description:
    description: Free form description of the flow record.
    required: false
    type: str
  match:
    description: >
      Key fields for the flow record, as a dictionary mapping a field name to
      a boolean. Valid keys are ipv4_source_address, ipv4_destination_address,
      ipv4_protocol, ipv4_version, ipv6_source_address,
      ipv6_destination_address, ipv6_protocol, ipv6_version,
      transport_source_port and transport_destination_port. The supplied
      dictionary fully replaces the current key fields.
    required: false
    type: dict
  collect:
    description: >
      Non-key fields for the flow record, as a dictionary mapping a field name
      to a boolean (for example counter_bytes, counter_packets,
      application_name, egress_interface). The supplied dictionary fully
      replaces the current non-key fields.
    required: false
    type: dict
  state:
    description: Create, update or delete the flow record.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an IPFIX flow record for IPv4 flows
  aoscx_ipfix_flow_record:
    name: ipv4-record
    description: Record ipv4 flows
    match:
      ipv4_source_address: true
      ipv4_destination_address: true
      ipv4_protocol: true
    collect:
      counter_bytes: true
      counter_packets: true

- name: Update the collected fields of a flow record
  aoscx_ipfix_flow_record:
    name: ipv4-record
    state: update
    collect:
      counter_bytes: true
      counter_packets: true
      application_name: true

- name: Delete a flow record
  aoscx_ipfix_flow_record:
    name: ipv4-record
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
        description=dict(type="str", required=False, default=None),
        match=dict(type="dict", required=False, default=None),
        collect=dict(type="dict", required=False, default=None),
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

    scalar_attrs = ["description", "match", "collect"]
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
        record = session.api.get_module(session, "IpfixFlowRecord", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support IPFIX. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        record.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                record.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete flow record: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        record = session.api.get_module(
            session, "IpfixFlowRecord", name, **supplied
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                record.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create flow record: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(record, attr, None) != value:
            changed = True
            setattr(record, attr, value)
            if attr not in record.config_attrs:
                record.config_attrs.append(attr)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            record.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update flow record: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
