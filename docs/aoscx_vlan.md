# module: aoscx_vlan

description: This modules provides configuration management of VLANs on AOS-CX
devices.

##### ARGUMENTS

```YAML
  vlan_id:
    description: >
      The ID of this VLAN. Non-internal VLANs must have an 'id' between 1 and
      4094 to be effectively instantiated.
    required: true
    type: int
  name:
    description: VLAN name
    required: false
    type: str
  description:
    description: VLAN description
    required: false
    type: str
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
  acl_direction:
    description: Direction for which the ACL is to be applied or removed.
    required: true
    choices:
      - in
      - out
    type: str
  admin_state:
    description: The Admin State of the VLAN, options are 'up' and 'down'.
    required: false
    choices:
      - up
      - down
    type: str
  state:
    description: Create or update or delete the VLAN.
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
- name: Create VLAN 200 with description
  aoscx_vlan:
    vlan_id: 200
    description: This is VLAN 200

- name: Create VLAN 300 with description and name
  aoscx_vlan:
    vlan_id: 300
    name: UPLINK_VLAN
    description: This is VLAN 300

- name: Delete VLAN 300
  aoscx_vlan:
    vlan_id: 300
    state: delete

- name: Apply ipv4 ACL to VLAN
  aoscx_vlan:
    vlan_id: 300
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_direction: in

- name: Remove ipv4 ACL from VLAN
  aoscx_vlan:
    vlan_id: 300
    acl_name: ipv4_acl
    acl_type: ipv4
    acl_direction: in
    state: delete
```
