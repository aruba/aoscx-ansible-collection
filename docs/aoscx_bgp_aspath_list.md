# module: aoscx_bgp_aspath_list

description: This module provides configuration management of BGP AS-Path
filters (also known as AS-Path lists) and their entries on AOS-CX devices.
AS-Path filters are used by routing policies to permit or deny routes based on
a regular expression matched against the BGP AS path.

##### ARGUMENTS

```YAML
  name:
    description: Name of the BGP AS-Path filter.
    required: true
    type: str
  description:
    description: Description of the BGP AS-Path filter.
    required: false
    type: str
  entries:
    description: >
      List of AS-Path filter entries that make up the filter. When provided
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
        description: Whether the entry permits or denies the matched AS path.
        required: true
        choices:
          - permit
          - deny
        type: str
      regex:
        description: >
          Regular expression matched against the BGP AS path, for example
          ^65000_ or _65001$.
        required: true
        type: str
  state:
    description: Create, update or delete the BGP AS-Path filter.
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
- name: Create a BGP AS-Path filter with two entries
  aoscx_bgp_aspath_list:
    name: FILTER_AS65000
    description: Filter routes from AS 65000
    entries:
      - preference: 10
        action: permit
        regex: '^65000_'
      - preference: 20
        action: deny
        regex: '_65001$'

- name: Add or update a single entry on an existing filter
  aoscx_bgp_aspath_list:
    name: FILTER_AS65000
    state: update
    entries:
      - preference: 10
        action: permit
        regex: '^65000_'
      - preference: 20
        action: deny
        regex: '_65001$'
      - preference: 30
        action: deny
        regex: '.*'

- name: Delete a BGP AS-Path filter
  aoscx_bgp_aspath_list:
    name: FILTER_AS65000
    state: delete
```
