# module: aoscx_aaa_server_group

description: This module provides configuration management of AAA server
groups on AOS-CX devices (system/aaa_server_groups). A server group bundles
RADIUS or TACACS+ servers so they can be referenced together by AAA methods.
This module requires REST API version 10.16 (set ansible_aoscx_rest_version to
10.16). The built-in groups (local, none, radius, tacacs) cannot be modified or
deleted.

##### ARGUMENTS

```YAML
  group_name:
    description: >
      Name of the AAA server group. This is the index of the resource under
      system/aaa_server_groups (up to 32 characters).
    required: true
    type: str
  group_type:
    description: >
      Type of the servers grouped together. Set when the group is created.
    required: false
    type: str
    choices:
      - none
      - local
      - radius
      - tacacs
  state:
    description: Create, update or delete the AAA server group.
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
- name: Create a RADIUS server group
  aoscx_aaa_server_group:
    group_name: my-radius
    group_type: radius

- name: Create a TACACS+ server group
  aoscx_aaa_server_group:
    group_name: my-tacacs
    group_type: tacacs

- name: Delete a server group
  aoscx_aaa_server_group:
    group_name: my-radius
    state: delete
```
