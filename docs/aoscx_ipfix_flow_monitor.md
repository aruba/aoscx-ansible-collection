# module: aoscx_ipfix_flow_monitor

description: This module provides configuration management of IPFIX flow
monitors on AOS-CX devices. A flow monitor binds a flow record to one or more
flow exporters and controls the flow cache timeouts. IPFIX requires REST API
version 10.13 or later (set ansible_aoscx_rest_version to 10.13). The
referenced flow record and flow exporters must already exist on the device.

##### ARGUMENTS

```YAML
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
```

##### EXAMPLES

```YAML
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
```
