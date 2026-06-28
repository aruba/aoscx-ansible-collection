# module: aoscx_ipsla_source

description: This module provides configuration management of IP SLA sources
on AOS-CX devices (system/ipsla_sources). An IP SLA source originates probes
used to measure reachability, latency and jitter. IP SLA requires REST API
version 10.16 (set ansible_aoscx_rest_version to 10.16). The type and vrf are
set when the source is created and cannot be changed afterwards.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the IP SLA source. This is the index of the resource under
      system/ipsla_sources.
    required: true
    type: str
  vrf:
    description: >
      Name of the VRF the IP SLA source belongs to. Set on creation only.
    required: false
    default: default
    type: str
  type:
    description: >
      Probe type of the IP SLA source. Required when the source is created
      and cannot be changed afterwards.
    required: false
    type: str
    choices:
      - icmp_echo
      - udp_echo
      - tcp_connect
      - udp_jitter_voip
      - http
      - https
      - dns
      - dhcp
  enable:
    description: Enable or disable the IP SLA source.
    required: false
    type: bool
  frequency:
    description: >
      Interval in seconds between two consecutive probes (5-604800).
    required: false
    type: int
  history_interval:
    description: >
      Number of probes whose statistics are kept in the history (10-7200).
    required: false
    type: int
  ipsla_timeout:
    description: >
      Time in seconds to wait for a probe response (5-604800).
    required: false
    type: int
  payload_size:
    description: Probe payload size in bytes (0-1440).
    required: false
    type: int
  source_ip:
    description: Source IP address used by the probes.
    required: false
    type: str
  source_port_number:
    description: Source UDP/TCP port used by the probes (1-65535).
    required: false
    type: int
  tos:
    description: Type of Service value carried by the probes (0-255).
    required: false
    type: int
  domain_name_server:
    description: DNS server used to resolve the probe destination.
    required: false
    type: str
  state:
    description: Create, update or delete the IP SLA source.
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
- name: Create an ICMP echo IP SLA source
  aoscx_ipsla_source:
    name: probe-gw
    type: icmp_echo
    vrf: default
    frequency: 30
    tos: 8

- name: Update the probe frequency
  aoscx_ipsla_source:
    name: probe-gw
    state: update
    frequency: 60

- name: Delete an IP SLA source
  aoscx_ipsla_source:
    name: probe-gw
    state: delete
```
