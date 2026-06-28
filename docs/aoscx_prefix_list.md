# module: aoscx_prefix_list

description: This module provides configuration management of IPv4/IPv6 prefix
lists and their entries on AOS-CX devices. Prefix lists are used by routing
policies (for example route maps and BGP filters) to permit or deny prefixes.

##### ARGUMENTS

```YAML
  name:
    description: Name of the prefix list.
    required: true
    type: str
  address_family:
    description: >
      Address family of the prefix list. This is only used when the prefix
      list is created and cannot be modified afterwards. Defaults to ipv4 on
      creation.
    required: false
    choices:
      - ipv4
      - ipv6
    type: str
  description:
    description: Description of the prefix list.
    required: false
    type: str
  entries:
    description: >
      List of prefix list entries that make up the prefix list. When provided
      this represents the full desired set of entries: entries present on the
      switch but not listed here are removed. Ignored when state is delete.
    required: false
    type: list
    elements: dict
    suboptions:
      preference:
        description: >
          Sequence number of the entry. Entries are evaluated in ascending
          order of preference.
        required: true
        type: int
      action:
        description: Whether the entry permits or denies the matched prefix.
        required: true
        choices:
          - permit
          - deny
        type: str
      prefix:
        description: >
          The IPv4 or IPv6 prefix and mask in the address/mask format, for
          example 10.0.0.0/8 or 2001:db8::/32.
        required: true
        type: str
      ge:
        description: >
          Minimum prefix length to be matched (greater than or equal to). Must
          be in the range 0-128.
        required: false
        type: int
      le:
        description: >
          Maximum prefix length to be matched (less than or equal to). Must be
          in the range 0-128.
        required: false
        type: int
  state:
    description: Create, update or delete the prefix list.
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
- name: Create an IPv4 prefix list with two entries
  aoscx_prefix_list:
    name: PERMIT_RFC1918
    address_family: ipv4
    description: Permit RFC1918 networks
    entries:
      - preference: 10
        action: permit
        prefix: 10.0.0.0/8
        le: 32
      - preference: 20
        action: permit
        prefix: 192.168.0.0/16
        le: 32

- name: Create an IPv6 prefix list
  aoscx_prefix_list:
    name: PERMIT_V6_DOC
    address_family: ipv6
    entries:
      - preference: 10
        action: permit
        prefix: '2001:db8::/32'

- name: Add or update a single entry on an existing prefix list
  aoscx_prefix_list:
    name: PERMIT_RFC1918
    state: update
    entries:
      - preference: 10
        action: permit
        prefix: 10.0.0.0/8
        le: 32
      - preference: 20
        action: permit
        prefix: 192.168.0.0/16
        le: 32
      - preference: 30
        action: deny
        prefix: 0.0.0.0/0

- name: Delete a prefix list
  aoscx_prefix_list:
    name: PERMIT_RFC1918
    state: delete
```
