# module: aoscx_sflow_collector

description: This module provides configuration management of sFlow collectors
on AOS-CX devices. A collector is the destination (IP address, UDP port and
VRF) to which an sFlow instance exports its flow records. The collector is
identified by the compound index of VRF, IP address and UDP port, and has no
configurable attributes beyond that index.

##### ARGUMENTS

```YAML
  sflow_name:
    description: >
      Name of the parent sFlow instance under which the collector is
      configured. The instance must already exist.
    required: true
    type: str
  vrf:
    description: >
      Name of the VRF used to reach the collector. The VRF must already exist
      on the device.
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
    default: create
    choices:
      - create
      - delete
    type: str
```

##### EXAMPLES

```YAML
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
```
