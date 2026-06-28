# module: aoscx_port_access_abp

description: This module provides configuration management of Port Access
Application Based Policies (ABP) on AOS-CX devices (system/port_access_abps).
An application based policy is an ordered list of entries; each entry
references an existing traffic class (system/classes) and applies an action set
(drop, dscp, local_priority or mirror) to the matching traffic. The policy can
then be applied to a port access role through its in_abp attribute. This module
requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16). The
referenced traffic classes must already exist; this module does not create
them. When the entries argument is supplied it fully replaces the existing
entries of the policy; when it is omitted the entries are left untouched. An
action field is only managed when it is supplied.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the application based policy. This is the index of the resource
      under system/port_access_abps.
    required: true
    type: str
  entries:
    description: >
      Ordered list of policy entries. When supplied the list fully replaces the
      existing entries of the policy. When omitted the entries are left
      untouched.
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: Sequence number of the entry within the policy.
        required: true
        type: int
      class_name:
        description: Name of the existing traffic class matched by this entry.
        required: true
        type: str
      class_type:
        description: Type of the referenced traffic class.
        required: true
        type: str
        choices:
          - abp-ipv4
          - abp-ipv6
      comment:
        description: Optional comment for the entry.
        required: false
        type: str
      drop:
        description: Drop packets matching the class of this entry.
        required: false
        type: bool
      dscp:
        description: DSCP value to set on packets matching the class.
        required: false
        type: int
      local_priority:
        description: Local priority to set on packets matching the class.
        required: false
        type: int
      mirror:
        description: Mirror session identifier for packets matching the class.
        required: false
        type: int
  state:
    description: Create, update or delete the application based policy.
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
- name: Create an application based policy
  aoscx_port_access_abp:
    name: app_policy
    entries:
      - sequence_number: 10
        class_name: streaming
        class_type: abp-ipv4
        drop: true
      - sequence_number: 20
        class_name: voice
        class_type: abp-ipv4
        dscp: 46
        local_priority: 7

- name: Delete an application based policy
  aoscx_port_access_abp:
    name: app_policy
    state: delete
```
