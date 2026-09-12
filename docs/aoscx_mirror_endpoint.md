# module: aoscx_mirror_endpoint

description: This module provides configuration management of remote mirror
endpoints on AOS-CX devices. A mirror endpoint defines an ERSPAN tunnel
destination to which mirrored traffic is encapsulated and forwarded. The
output ports must already exist on the device.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the mirror endpoint. This is the index of the resource under
      system/mirror_endpoints.
    required: true
    type: str
  admin:
    description: Administrative state of the mirror endpoint.
    required: false
    choices:
      - up
      - down
    type: str
  comment:
    description: A descriptive comment for the mirror endpoint.
    required: false
    type: str
  output_port:
    description: >
      List of port names through which the encapsulated mirrored traffic is
      sent. The ports must already exist on the device. The list is compared
      regardless of order.
    required: false
    type: list
    elements: str
  tunnel:
    description: >
      ERSPAN tunnel parameters for the endpoint. Only the supplied keys are
      reconciled; existing keys that are not mentioned are preserved.
    required: false
    type: dict
    suboptions:
      dest_ip_address:
        description: Destination IP address of the ERSPAN tunnel.
        required: false
        type: str
      src_ip_address:
        description: Source IP address of the ERSPAN tunnel.
        required: false
        type: str
      dscp:
        description: DSCP value used for the tunnel encapsulation.
        required: false
        type: int
      id:
        description: ERSPAN session id carried in the tunnel header.
        required: false
        type: int
  state:
    description: Create, update or delete the mirror endpoint.
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
- name: Create an ERSPAN mirror endpoint
  aoscx_mirror_endpoint:
    name: erspan-to-collector
    admin: up
    comment: collector-1
    output_port:
      - 1/1/10
    tunnel:
      src_ip_address: 10.0.0.1
      dest_ip_address: 10.0.0.2
      id: 100

- name: Update the tunnel destination of a mirror endpoint
  aoscx_mirror_endpoint:
    name: erspan-to-collector
    state: update
    tunnel:
      dest_ip_address: 10.0.0.3

- name: Delete a mirror endpoint
  aoscx_mirror_endpoint:
    name: erspan-to-collector
    state: delete
```
