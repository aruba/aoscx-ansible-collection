# module: aoscx_traffic_insight

description: This module provides configuration management of the Traffic
Insight instance on AOS-CX devices (system/traffic_insights). Traffic Insight
requires REST API version 10.13 or later (set ansible_aoscx_rest_version to
10.13). Note that the switch supports a single Traffic Insight instance at a
time.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the Traffic Insight instance. This is the index of the resource
      under system/traffic_insights.
    required: true
    type: str
  enable:
    description: Enable or disable the Traffic Insight instance.
    required: false
    type: bool
  source:
    description: >
      List of data sources feeding the Traffic Insight instance. The only
      supported source is ipfix. The supplied list fully replaces the current
      sources.
    required: false
    type: list
    elements: str
    choices:
      - ipfix
  state:
    description: Create, update or delete the Traffic Insight instance.
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
- name: Create a Traffic Insight instance
  aoscx_traffic_insight:
    name: TI-01
    enable: true
    source:
      - ipfix

- name: Disable a Traffic Insight instance
  aoscx_traffic_insight:
    name: TI-01
    state: update
    enable: false

- name: Delete a Traffic Insight instance
  aoscx_traffic_insight:
    name: TI-01
    state: delete
```
