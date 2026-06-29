# module: aoscx_ipfix_flow_exporter

description: This module provides configuration management of IPFIX flow
exporters on AOS-CX devices. A flow exporter defines the destination to which
IPFIX flow data is exported, either a collector reachable by hostname or IP
address through a VRF, or a local Traffic Insight instance. IPFIX requires REST
API version 10.13 or later (set ansible_aoscx_rest_version to 10.13).

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the flow exporter. This is the index of the resource under
      system/ipfix_flow_exporters.
    required: true
    type: str
  description:
    description: Free form description of the flow exporter.
    required: false
    type: str
  destination_type:
    description: >
      Type of the export destination. Use hostname-or-ip-addr to export to a
      collector, or traffic-insight to export to a local Traffic Insight
      instance.
    required: false
    choices:
      - hostname-or-ip-addr
      - traffic-insight
    type: str
  destination:
    description: >
      Hostname or IP address of the collector. Used when destination_type is
      hostname-or-ip-addr.
    required: false
    type: str
  vrf:
    description: >
      Name of the VRF used to reach the collector. Used together with
      destination.
    required: false
    default: default
    type: str
  traffic_insight:
    description: >
      Name of the Traffic Insight instance to export to. Used when
      destination_type is traffic-insight.
    required: false
    type: str
  template_data_timeout:
    description: >
      Interval, in seconds, between transmissions of the IPFIX template and
      options data (0-86400).
    required: false
    type: int
  transport_port:
    description: >
      UDP destination port used to export flow data (1-65535).
    required: false
    type: int
  transport_protocol:
    description: Transport protocol used to export flow data.
    required: false
    default: udp
    choices:
      - udp
    type: str
  state:
    description: Create, update or delete the flow exporter.
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
- name: Create an IPFIX flow exporter to a collector
  aoscx_ipfix_flow_exporter:
    name: collector-1
    description: Export to collector 1
    destination_type: hostname-or-ip-addr
    destination: 10.0.0.5
    vrf: default
    transport_port: 4739
    template_data_timeout: 600

- name: Create an IPFIX flow exporter to a Traffic Insight instance
  aoscx_ipfix_flow_exporter:
    name: ti-exporter
    destination_type: traffic-insight
    traffic_insight: TI-01

- name: Delete a flow exporter
  aoscx_ipfix_flow_exporter:
    name: collector-1
    state: delete
```
