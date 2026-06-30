# module: aoscx_radius_proxy_client_group

description: This module provides configuration management of RADIUS proxy
client groups on AOS-CX devices. A client group defines the downstream RADIUS
clients (NAS devices) handled by the proxy and is identified by its name.

##### ARGUMENTS

```YAML
  group_name:
    description: Name of the RADIUS proxy client group.
    required: true
    type: str
  clients:
    description: >
      RADIUS clients (NAS devices) that are members of the group. The supplied
      list fully replaces the members. When omitted the members are left
      unchanged; an empty list removes all members. Ignored when state is
      delete.
    required: false
    type: list
    elements: dict
    suboptions:
      address:
        description: Address of the RADIUS client (NAS).
        required: true
        type: str
      connection_type:
        description: Connection type of the client.
        required: false
        default: udp
        choices:
          - udp
          - tcp
        type: str
      secret_key:
        description: >
          Shared secret used with the client. It is write-only; the switch only
          ever returns it encrypted, so when a secret is supplied the module
          reports changed on every run.
        required: false
        type: str
  state:
    description: Create, update or delete the RADIUS proxy client group.
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
- name: Create a RADIUS proxy client group with one client
  aoscx_radius_proxy_client_group:
    group_name: nas-group
    clients:
      - address: 192.0.2.50
        connection_type: udp
        secret_key: nas-secret

- name: Remove all members from the group
  aoscx_radius_proxy_client_group:
    group_name: nas-group
    clients: []
    state: update

- name: Delete the RADIUS proxy client group
  aoscx_radius_proxy_client_group:
    group_name: nas-group
    state: delete
```
