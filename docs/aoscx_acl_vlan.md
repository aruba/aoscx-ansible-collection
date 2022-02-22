# module: aoscx_acl_vlan

description: This modules provides application management of Access Classifier
Lists on VLANs on AOS-CX devices.

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
```
