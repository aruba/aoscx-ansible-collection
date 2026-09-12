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
module: aoscx_traffic_insight_monitor
version_added: "4.6.0"
short_description: Create, update or delete a Traffic Insight monitor
description: >
  This module provides configuration management of Traffic Insight monitors on
  AOS-CX devices (system/traffic_insight_monitors). A monitor is attached to a
  Traffic Insight instance and identified by the compound index made of the
  instance name, the monitor name and the monitor type. Traffic Insight
  requires REST API version 10.13 or later (set ansible_aoscx_rest_version to
  10.13). The filter_by_single_value, group_by, monitor_n_flows and
  running_stats_reset_interval attributes apply to the topN-flows monitor type.
author: Aruba Networks (@ArubaNetworks)
options:
  traffic_insight_instance:
    description: >
      Name of the parent Traffic Insight instance the monitor is attached to.
      The instance must already exist.
    required: true
    type: str
  monitor_name:
    description: Name of the monitor.
    required: true
    type: str
  monitor_type:
    description: Type of the monitor.
    required: true
    choices:
      - topN-flows
      - application-flows
      - dns-average-latency
      - dns-onboarding-latency
      - raw-flows
      - dropped-flows
      - congested-flows
    type: str
  filter_by_single_value:
    description: >
      Filter applied to the monitor, as a dictionary. Applies to the
      topN-flows monitor type.
    required: false
    type: dict
  group_by:
    description: >
      Grouping key for the monitor. Applies to the topN-flows monitor type.
    required: false
    choices:
      - srcip
      - dstip
      - srcport
      - dstport
      - ipproto
      - srcip_dstip
      - srcip_dstport
      - appid
      - srcip_appid
      - egress_interface
      - egress_interface_queue
    type: str
  monitor_n_flows:
    description: >
      Number of flows tracked by the monitor (1 to 20). Applies to the
      topN-flows monitor type.
    required: false
    type: int
  running_stats_reset_interval:
    description: >
      Interval, in seconds, between running statistics resets (360 to 2700).
      Applies to the topN-flows monitor type.
    required: false
    type: int
  state:
    description: Create, update or delete the Traffic Insight monitor.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a topN-flows monitor grouped by application
  aoscx_traffic_insight_monitor:
    traffic_insight_instance: TI-01
    monitor_name: TopN-apps
    monitor_type: topN-flows
    group_by: appid
    monitor_n_flows: 10
    running_stats_reset_interval: 600

- name: Create an application-flows monitor
  aoscx_traffic_insight_monitor:
    traffic_insight_instance: TI-01
    monitor_name: apps
    monitor_type: application-flows

- name: Update the number of tracked flows
  aoscx_traffic_insight_monitor:
    traffic_insight_instance: TI-01
    monitor_name: TopN-apps
    monitor_type: topN-flows
    state: update
    monitor_n_flows: 20

- name: Delete a Traffic Insight monitor
  aoscx_traffic_insight_monitor:
    traffic_insight_instance: TI-01
    monitor_name: TopN-apps
    monitor_type: topN-flows
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        traffic_insight_instance=dict(type="str", required=True),
        monitor_name=dict(type="str", required=True),
        monitor_type=dict(
            type="str",
            required=True,
            choices=[
                "topN-flows",
                "application-flows",
                "dns-average-latency",
                "dns-onboarding-latency",
                "raw-flows",
                "dropped-flows",
                "congested-flows",
            ],
        ),
        filter_by_single_value=dict(
            type="dict", required=False, default=None
        ),
        group_by=dict(
            type="str",
            required=False,
            default=None,
            choices=[
                "srcip",
                "dstip",
                "srcport",
                "dstport",
                "ipproto",
                "srcip_dstip",
                "srcip_dstport",
                "appid",
                "srcip_appid",
                "egress_interface",
                "egress_interface_queue",
            ],
        ),
        monitor_n_flows=dict(type="int", required=False, default=None),
        running_stats_reset_interval=dict(
            type="int", required=False, default=None
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
    )

    instance_name = ansible_module.params["traffic_insight_instance"]
    monitor_name = ansible_module.params["monitor_name"]
    monitor_type = ansible_module.params["monitor_type"]
    state = ansible_module.params["state"]

    scalar_attrs = [
        "filter_by_single_value",
        "group_by",
        "monitor_n_flows",
        "running_stats_reset_interval",
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
        instance = session.api.get_module(
            session, "TrafficInsight", instance_name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support Traffic Insight. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        instance.get()
    except Exception:
        ansible_module.fail_json(
            msg="Traffic Insight instance '{0}' does not exist".format(
                instance_name
            )
        )

    monitor = session.api.get_module(
        session,
        "TrafficInsightMonitor",
        instance,
        monitor_name=monitor_name,
        monitor_type=monitor_type,
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
                    msg="Could not delete Traffic Insight monitor: "
                    "{0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        monitor = session.api.get_module(
            session,
            "TrafficInsightMonitor",
            instance,
            monitor_name=monitor_name,
            monitor_type=monitor_type,
            **supplied
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                monitor.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create Traffic Insight monitor: "
                    "{0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(monitor, attr, None) != value:
            changed = True
            setattr(monitor, attr, value)
            if attr not in monitor.config_attrs:
                monitor.config_attrs.append(attr)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            monitor.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update Traffic Insight monitor: "
                "{0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
