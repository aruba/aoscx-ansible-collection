# module: aoscx_acl_vlan

description: This module provides application management of Access Classifier
Lists on VLANs on AOS-CX devices. This modules is deprecated and will be
removed in a future version, please use `aoscx_vlan` or `aoscx_vlan_interface`
instead.

##### ARGUMENTS

```YAML
  acl_name:
    description: Name of the ACL being applied or removed from the VLAN.
    required: true
    type: str

  acl_type:
    description: Type of ACL being applied or removed from the VLAN.
    choices:
      - ipv4
      - ipv6
      - mac
    required: true
    type: str

  acl_vlan_list:
    description: List of VLANs for which the ACL is to be applied or removed.
    required: true
    type: list

  acl_direction:
    description: Direction for which the ACL is to be applied or removed.
    required: true
    choices:
      - in
      - out
    default: in
    type: str

  state:
    description: Create or delete the ACL configuration from the VLANs.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
```

##### EXAMPLES

```YAML
- name: Apply ipv4 ACL to VLANs
  aoscx_acl_vlan:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_vlan_list:
      - 2
      - 4

- name: Remove ipv4 ACL from VLANs
  aoscx_acl_vlan:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_vlan_list:
      - 2
      - 4
    state: delete

- name: Apply ipv6 ACL to VLANs
  aoscx_acl_vlan:
    acl_name: ipv6_acl
    acl_type: ipv6
    acl_vlan_list:
      - 2
      - 4

- name: Apply ipv4 ACL IN to VLAN (new method)
  aoscx_vlan:
    vlan_id: {{item}}
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_direction: in
  loop: [2, 4]

- name: Remove ipv4 ACL IN from VLAN (new method)
  aoscx_vlan:
    vlan_id: {{item}}
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_direction: in
    state: delete
  loop: [2, 4]

- name: Apply ipv4 ACL ROUTED-IN to VLAN (new method)
  aoscx_vlan_interface:
    vlan_id: {{item}}
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_direction: routed-in
  loop: [2, 4]

- name: Remove ipv4 ACL ROUTED-IN from VLAN (new method)
  aoscx_vlan_interface:
    vlan_id: {{item}}
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_direction: routed-in
    state: delete
  loop: [2, 4]
```
