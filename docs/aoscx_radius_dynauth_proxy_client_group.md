# module: aoscx_radius_dynauth_proxy_client_group

description: This module provides configuration management of RADIUS dynamic
authorization (Change of Authorization) proxy client groups on AOS-CX devices.
A client group references a set of RADIUS dynamic authorization (CoA) clients
and is identified by its name.

##### ARGUMENTS

```YAML
  group_name:
    description: Name of the proxy client group.
    required: true
    type: str
  clients:
    description: >
      RADIUS dynamic authorization (CoA) clients that are members of the group.
      The supplied list fully replaces the members. When omitted the members
      are left unchanged; an empty list removes all members. Each referenced
      CoA client must already exist. Ignored when state is delete.
    required: false
    type: list
    elements: dict
    suboptions:
      address:
        description: Address of the CoA client.
        required: true
        type: str
      connection_type:
        description: Connection type of the CoA client.
        required: false
        default: udp
        choices:
          - udp
          - tcp
        type: str
      vrf:
        description: VRF of the CoA client.
        required: false
        default: default
        type: str
  state:
    description: Create, update or delete the proxy client group.
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
- name: Create a proxy client group with two CoA clients
  aoscx_radius_dynauth_proxy_client_group:
    group_name: coa-group
    clients:
      - address: 192.0.2.41
        connection_type: udp
      - address: 192.0.2.42
        connection_type: udp

- name: Remove all members from the group
  aoscx_radius_dynauth_proxy_client_group:
    group_name: coa-group
    clients: []
    state: update

- name: Delete the proxy client group
  aoscx_radius_dynauth_proxy_client_group:
    group_name: coa-group
    state: delete
```
