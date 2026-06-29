# module: aoscx_pbr_action_list

description: This module provides configuration management of Policy Based
Routing (PBR) action lists and their entries on AOS-CX devices. A PBR action
list groups ordered entries that decide how matched traffic is forwarded (to a
next-hop, out of an interface, or dropped). The switch does not allow modifying
an entry in place, so a changed entry is deleted and recreated.

##### ARGUMENTS

```YAML
  name:
    description: Name of the PBR action list.
    required: true
    type: str
  vsx_sync:
    description: >
      Attributes to synchronize between VSX peers for this action list. When
      omitted the value already on the switch is left untouched.
    required: false
    type: list
    elements: str
  entries:
    description: >
      List of action list entries. When provided this represents the full
      desired set of entries: entries present on the switch but not listed here
      are removed. Because the switch does not support modifying an entry in
      place, a changed entry is deleted and recreated. Ignored when state is
      delete.
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: >
          Sequence number of the entry. Entries are evaluated in ascending
          order.
        required: true
        type: int
      type:
        description: >
          Action taken by the entry. nexthop and default_nexthop require ip;
          interface requires interface; blackhole drops the traffic and takes
          no further argument.
        required: true
        choices:
          - nexthop
          - default_nexthop
          - interface
          - blackhole
        type: str
      ip:
        description: >
          Routing gateway address used by nexthop and default_nexthop entries,
          in IPv4 (A.B.C.D) or IPv6 (A:B::C:D) format.
        required: false
        type: str
      interface:
        description: >
          Name of the next-hop interface used by interface entries, for
          example 1/1/1.
        required: false
        type: str
  state:
    description: Create, update or delete the PBR action list.
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
- name: Create a PBR action list with a next-hop and a blackhole entry
  aoscx_pbr_action_list:
    name: PBR_WEB
    entries:
      - sequence_number: 10
        type: nexthop
        ip: 10.0.0.1
      - sequence_number: 20
        type: blackhole

- name: Forward matched traffic out of an interface
  aoscx_pbr_action_list:
    name: PBR_WEB
    state: update
    entries:
      - sequence_number: 10
        type: interface
        interface: 1/1/1

- name: Delete a PBR action list
  aoscx_pbr_action_list:
    name: PBR_WEB
    state: delete
```
