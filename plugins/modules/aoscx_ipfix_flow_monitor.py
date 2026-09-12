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
module: aoscx_ipfix_flow_monitor
version_added: "4.6.0"
short_description: Create, update or delete an IPFIX flow monitor on AOS-CX
description: >
  This module provides configuration management of IPFIX flow monitors on
  AOS-CX devices. A flow monitor binds a flow record to one or more flow
  exporters and controls the flow cache timeouts. IPFIX requires REST API
  version 10.13 or later (set ansible_aoscx_rest_version to 10.13). The
  referenced flow record and flow exporters must already exist on the device.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the flow monitor. This is the index of the resource under
      system/ipfix_flow_monitors.
    required: true
    type: str
  description:
    description: Free form description of the flow monitor.
    required: false
    type: str
  cache_timeout_active:
    description: >
      Active flow cache timeout in seconds (30-604800).
    required: false
    type: int
  cache_timeout_inactive:
    description: >
      Inactive flow cache timeout in seconds (30-604800).
    required: false
    type: int
  exporters:
    description: >
      List of flow exporter names to bind to this monitor. The exporters must
      already exist on the device.
    required: false
    type: list
    elements: str
  record:
    description: >
      Name of the flow record to bind to this monitor. The record must already
      exist on the device.
    required: false
    type: str
  state:
    description: Create, update or delete the flow monitor.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an IPFIX flow monitor binding a record and an exporter
  aoscx_ipfix_flow_monitor:
    name: monitor-1
    description: Monitor ipv4 flows
    record: ipv4-record
    exporters:
      - collector-1
    cache_timeout_active: 60
    cache_timeout_inactive: 30

- name: Update the exporters bound to a flow monitor
  aoscx_ipfix_flow_monitor:
    name: monitor-1
    state: update
    exporters:
      - collector-1
      - collector-2

- name: Delete a flow monitor
  aoscx_ipfix_flow_monitor:
    name: monitor-1
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
        cache_timeout_active=dict(type="int", required=False, default=None),
        cache_timeout_inactive=dict(type="int", required=False, default=None),
        exporters=dict(
            type="list", elements="str", required=False, default=None
        ),
        record=dict(type="str", required=False, default=None),
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

    params = ansible_module.params
    name = params["name"]
    state = params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    def make_exporters(names):
        return [
            session.api.get_module(session, "IpfixFlowExporter", n)
            for n in names
        ]

    def make_record(record_name):
        return session.api.get_module(session, "IpfixFlowRecord", record_name)

    scalar_attrs = [
        "description",
        "cache_timeout_active",
        "cache_timeout_inactive",
    ]
    supplied = {
        attr: params[attr] for attr in scalar_attrs if params[attr] is not None
    }

    try:
        monitor = session.api.get_module(session, "IpfixFlowMonitor", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support IPFIX. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        monitor.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                monitor.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete flow monitor: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        create_kwargs = dict(supplied)
        if params["exporters"] is not None:
            create_kwargs["exporter"] = make_exporters(params["exporters"])
        if params["record"] is not None:
            create_kwargs["record"] = make_record(params["record"])
        monitor = session.api.get_module(
            session, "IpfixFlowMonitor", name, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                monitor.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create flow monitor: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(monitor, attr, None) != value:
            changed = True
            setattr(monitor, attr, value)
            if attr not in monitor.config_attrs:
                monitor.config_attrs.append(attr)

    # Reconcile the exporter references (order-insensitive comparison by name).
    if params["exporters"] is not None:
        current = sorted(
            obj.name for obj in (getattr(monitor, "exporter", None) or [])
        )
        desired = sorted(params["exporters"])
        if current != desired:
            changed = True
            monitor.exporter = make_exporters(params["exporters"])
            if "exporter" not in monitor.config_attrs:
                monitor.config_attrs.append("exporter")

    # Reconcile the record reference (single, compared by name).
    if params["record"] is not None:
        current_record = getattr(monitor, "record", None)
        current_name = current_record.name if current_record else None
        if current_name != params["record"]:
            changed = True
            monitor.record = make_record(params["record"])
            if "record" not in monitor.config_attrs:
                monitor.config_attrs.append("record")

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            monitor.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update flow monitor: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
