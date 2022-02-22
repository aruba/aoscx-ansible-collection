# module: aoscx_acl_interface

description: This modules provides application management of Access Classifier
Lists on Interfaces on AOS-CX devices.

##### ARGUMENTS

```YAML
  acl_name:
    description: Name of the ACL being applied or removed from the interface.
    required: true
    type: str
  acl_type:
    description: Type of ACL being applied or removed from the interfaces.
    choices:
      - ipv4
      - ipv6
      - mac
    required: true
    type: str
  acl_interface_list:
    description: >
      List of interfaces for which the ACL is to be applied or removed.
    required: true
    type: list
    elements: str
  acl_direction:
    description: Direction for which the ACL is to be applied or removed.
    choices:
      - in
      - out
    default: in
    type: str
  state:
    description: Create or delete the ACL configuration from the interfaces.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
```

##### EXAMPLES

```YAML
- name: Apply ipv4 ACL to interfaces
  aoscx_acl_interface:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_interface_list:
      - 1/1/2
      - 1/2/23

- name: Remove ipv4 ACL from interfaces
  aoscx_acl_interface:
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_interface_list:
      - 1/1/2
      - 1/2/23
    state: delete

- name: Apply ipv6 ACL to Interfaces
  aoscx_acl_interface:
    acl_name: ipv6_acl
    acl_type: ipv6
    acl_interface_list:
      - 1/1/2
      - 1/2/23
```
