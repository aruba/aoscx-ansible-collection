# module: aoscx_traffic_insight_monitor

description: This module provides configuration management of Traffic Insight
monitors on AOS-CX devices (system/traffic_insight_monitors). A monitor is
attached to a Traffic Insight instance and identified by the compound index
made of the instance name, the monitor name and the monitor type. Traffic
Insight requires REST API version 10.13 or later (set
ansible_aoscx_rest_version to 10.13). The filter_by_single_value, group_by,
monitor_n_flows and running_stats_reset_interval attributes apply to the
topN-flows monitor type.

##### ARGUMENTS

```YAML
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
```

##### EXAMPLES

```YAML
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
```
