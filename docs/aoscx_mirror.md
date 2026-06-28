# module: aoscx_mirror

description: This module provides configuration management of traffic mirror
(port monitoring) sessions on AOS-CX devices. A mirror session copies traffic
from one or more source ports or VLANs to a destination (output) port. Source
ports, destination ports and VLANs must already exist on the device.

##### ARGUMENTS

```YAML
  mirror_id:
    description: >
      Numeric identifier of the mirror session. This is the index of the
      resource under system/mirrors.
    required: true
    type: int
  session_type:
    description: >
      Type of the mirror session. When omitted it is left unchanged.
    required: false
    choices:
      - none
      - port
      - cpu
      - tunnel
    type: str
  active:
    description: >
      Whether the mirror session is active. An inactive session is configured
      but does not mirror any traffic. When omitted it is left unchanged.
    required: false
    type: bool
  comment:
    description: A descriptive comment for the mirror session.
    required: false
    type: str
  output_port:
    description: >
      List of destination port names that receive the mirrored traffic. The
      ports must already exist on the device. The list is compared regardless
      of order.
    required: false
    type: list
    elements: str
  select_src_port:
    description: >
      List of port names whose ingress (received) traffic is mirrored. The
      ports must already exist on the device. The list is compared regardless
      of order.
    required: false
    type: list
    elements: str
  select_dst_port:
    description: >
      List of port names whose egress (transmitted) traffic is mirrored. The
      ports must already exist on the device. The list is compared regardless
      of order.
    required: false
    type: list
    elements: str
  select_rx_vlan:
    description: >
      List of VLAN ids whose ingress (received) traffic is mirrored. The
      VLANs must already exist on the device. The list is compared regardless
      of order.
    required: false
    type: list
    elements: int
  select_tx_vlan:
    description: >
      List of VLAN ids whose egress (transmitted) traffic is mirrored. The
      VLANs must already exist on the device. The list is compared regardless
      of order.
    required: false
    type: list
    elements: int
  state:
    description: Create, update or delete the mirror session.
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
- name: Create a port mirror session, source 1/1/1 RX, destination 1/1/10
  aoscx_mirror:
    mirror_id: 5
    session_type: port
    active: true
    comment: span-to-analyzer
    select_src_port:
      - 1/1/1
    output_port:
      - 1/1/10

- name: Add VLANs to the mirrored receive set
  aoscx_mirror:
    mirror_id: 5
    state: update
    select_rx_vlan:
      - 10
      - 20

- name: Deactivate a mirror session
  aoscx_mirror:
    mirror_id: 5
    state: update
    active: false

- name: Delete a mirror session
  aoscx_mirror:
    mirror_id: 5
    state: delete
```
