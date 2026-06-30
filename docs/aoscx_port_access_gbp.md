# module: aoscx_port_access_gbp

description: This module provides configuration management of Port Access Group
Based Policies (GBP) on AOS-CX devices (system/port_access_gbps). A group based
policy is an ordered list of entries; each entry references an existing traffic
class (system/classes) and optionally drops or reflects the matching traffic.
The policy can then be applied to a port access role through its in_gbp
attribute. This module requires REST API version 10.16 (set
ansible_aoscx_rest_version to 10.16). The referenced traffic classes must
already exist; this module does not create them. The supplied entries fully
replace the existing entries of the policy.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the group based policy. This is the index of the resource under
      system/port_access_gbps.
    required: true
    type: str
  entries:
    description: >
      Ordered list of policy entries. The supplied list fully replaces the
      existing entries of the policy.
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: Sequence number of the entry within the policy.
        required: true
        type: int
      class_name:
        description: >
          Name of the existing traffic class (system/classes) matched by this
          entry. The class must already exist.
        required: true
        type: str
      class_type:
        description: Type of the referenced traffic class.
        required: true
        type: str
        choices:
          - gbp-ipv4
          - gbp-ipv6
          - gbp-mac
      comment:
        description: Optional comment for the entry.
        required: false
        type: str
      drop:
        description: >
          Drop packets matching the class of this entry. When omitted, the
          action set of the entry is not managed by this module.
        required: false
        type: bool
      reflect:
        description: >
          Reflect packets matching the class of this entry in the reverse
          direction only when the flow is learnt. When omitted, the action set
          of the entry is not managed by this module.
        required: false
        type: bool
  state:
    description: Create, update or delete the group based policy.
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
- name: Create a group based policy that drops traffic of a class
  aoscx_port_access_gbp:
    name: employee_r2r_policy
    entries:
      - sequence_number: 10
        class_name: employee_DENY
        class_type: gbp-ipv4
        drop: true
      - sequence_number: 20
        class_name: employee_ALLOW
        class_type: gbp-ipv4

- name: Delete a group based policy
  aoscx_port_access_gbp:
    name: employee_r2r_policy
    state: delete
```
