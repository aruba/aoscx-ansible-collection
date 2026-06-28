# module: aoscx_port_access_policy

description: This module provides configuration management of Port Access
Policies on AOS-CX devices (system/port_access_policies). A port access policy
is an ordered list of entries; each entry references an existing traffic class
(system/classes) and applies an action set (drop, reflect, dscp, rate limiting,
redirect to captive portal, ...) to the matching traffic. The policy can then
be applied to a port access role through its in_policy attribute. This module
requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16). The
referenced traffic classes must already exist; this module does not create
them. When the entries argument is supplied it fully replaces the existing
entries of the policy; when it is omitted the entries are left untouched. An
action field is only managed when it is supplied.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the port access policy. This is the index of the resource under
      system/port_access_policies.
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
          - ipv4
          - ipv6
          - mac
      comment:
        description: Optional comment for the entry.
        required: false
        type: str
      drop:
        description: Drop packets matching the class of this entry.
        required: false
        type: bool
      reflect:
        description: Reflect packets matching the class of this entry.
        required: false
        type: bool
      dscp:
        description: DSCP value to set on packets matching the class.
        required: false
        type: int
      cir:
        description: Committed information rate in kbps.
        required: false
        type: int
      cbs:
        description: Committed burst size in bytes.
        required: false
        type: int
      pcp:
        description: Priority code point to set on packets matching the class.
        required: false
        type: int
      ecn:
        description: ECN value to set on packets matching the class.
        required: false
        type: int
      ip_precedence:
        description: IP precedence to set on packets matching the class.
        required: false
        type: int
      local_priority:
        description: Local priority to set on packets matching the class.
        required: false
        type: int
      exceed_drop:
        description: Drop packets that exceed the committed rate.
        required: false
        type: bool
      redirect:
        description: Redirect packets matching the class of this entry.
        required: false
        type: str
        choices:
          - captive-portal
  state:
    description: Create, update or delete the port access policy.
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
- name: Create a port access policy
  aoscx_port_access_policy:
    name: guest_policy
    entries:
      - sequence_number: 10
        class_name: guest_http
        class_type: ipv4
        redirect: captive-portal
      - sequence_number: 20
        class_name: guest_voice
        class_type: ipv4
        dscp: 46
        cir: 1000
        cbs: 5000

- name: Delete a port access policy
  aoscx_port_access_policy:
    name: guest_policy
    state: delete
```
