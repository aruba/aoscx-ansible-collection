# module: aoscx_ipsla_responder

description: This module provides configuration management of IP SLA
responders on AOS-CX devices (system/ipsla_responders). An IP SLA responder
answers probes sent by IP SLA sources. IP SLA requires REST API version 10.16
(set ansible_aoscx_rest_version to 10.16). A responder has no modifiable
attributes, so any change is applied by recreating the responder.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the IP SLA responder. This is the index of the resource under
      system/ipsla_responders.
    required: true
    type: str
  vrf:
    description: Name of the VRF the IP SLA responder belongs to.
    required: false
    default: default
    type: str
  type:
    description: Probe type the responder answers.
    required: false
    type: str
    choices:
      - udp_echo
      - tcp_connect
      - udp_jitter_voip
  responder_port_number:
    description: UDP/TCP port the responder listens on (1-65535).
    required: false
    type: int
  responder_type:
    description: IP address family used by the responder.
    required: false
    type: str
    choices:
      - ipv4
      - ipv6
  responder_ip:
    description: IP address the responder is bound to.
    required: false
    type: str
  persistence:
    description: Whether the responder survives a reboot.
    required: false
    type: str
    choices:
      - persistent
      - volatile
  state:
    description: Create or delete the IP SLA responder.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
```

##### EXAMPLES

```YAML
- name: Create a UDP echo IP SLA responder
  aoscx_ipsla_responder:
    name: responder-1
    type: udp_echo
    vrf: default
    responder_port_number: 5000
    responder_type: ipv4

- name: Delete an IP SLA responder
  aoscx_ipsla_responder:
    name: responder-1
    state: delete
```
