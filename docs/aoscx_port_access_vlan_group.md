# module: aoscx_port_access_vlan_group

description: This module provides configuration management of Port Access VLAN
Groups on AOS-CX devices (system/port_access_vlan_groups). A VLAN group bundles
a set of VLAN IDs that can be referenced by port access roles. This module
requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16).

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the port access VLAN group. This is the index of the resource
      under system/port_access_vlan_groups.
    required: true
    type: str
  vlans:
    description: >
      List of VLAN IDs that belong to the group. The list fully replaces the
      VLANs configured on the group.
    required: false
    type: list
    elements: int
  state:
    description: Create, update or delete the port access VLAN group.
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
- name: Create a port access VLAN group
  aoscx_port_access_vlan_group:
    name: guest-vlans
    vlans:
      - 10
      - 20

- name: Update the VLAN membership
  aoscx_port_access_vlan_group:
    name: guest-vlans
    vlans:
      - 10
      - 20
      - 30
    state: update

- name: Delete a port access VLAN group
  aoscx_port_access_vlan_group:
    name: guest-vlans
    state: delete
```
