# module: aoscx_sflow

description: This module provides configuration management of sFlow (traffic
sampling) instances on AOS-CX devices. An sFlow instance controls how the
device samples traffic and exports flow records to collectors.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the sFlow instance. This is the index of the resource under
      system/sflows.
    required: true
    type: str
  agent_address:
    description: >
      Source IP address (IPv4 or IPv6) used by the sFlow agent in exported
      datagrams. When omitted it is left unchanged.
    required: false
    type: str
  enabled:
    description: >
      Whether the sFlow instance is enabled. When omitted it is left
      unchanged.
    required: false
    type: bool
  header:
    description: >
      Maximum number of bytes copied from each sampled packet header. When
      omitted it is left unchanged.
    required: false
    type: int
  max_datagram:
    description: >
      Maximum size in bytes of an exported sFlow datagram. When omitted it is
      left unchanged.
    required: false
    type: int
  mode:
    description: >
      Direction of traffic that is sampled. When omitted it is left unchanged.
    required: false
    choices:
      - both
      - egress
      - ingress
    type: str
  polling:
    description: >
      Counter polling interval in seconds. When omitted it is left unchanged.
    required: false
    type: int
  sampling:
    description: >
      Packet sampling rate (one in N packets). When omitted it is left
      unchanged.
    required: false
    type: int
  state:
    description: Create, update or delete the sFlow instance.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
```

##### EXAMPLES

```YAML
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
```
