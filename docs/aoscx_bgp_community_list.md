# module: aoscx_bgp_community_list

description: This module provides configuration management of BGP community
filters (also known as community lists) and their entries on AOS-CX devices.
Community filters are used by routing policies to permit or deny routes based
on a string matched against the BGP communities carried by a route.

##### ARGUMENTS

```YAML
  name:
    description: Name of the BGP community filter.
    required: true
    type: str
  type:
    description: >
      Kind of community filter. Required when creating the filter. The
      *-list types match standard community values, while the
      *-expanded-list types match a regular expression.
    required: false
    choices:
      - community-list
      - community-expanded-list
      - extcommunity-list
      - extcommunity-expanded-list
    type: str
  description:
    description: Description of the BGP community filter.
    required: false
    type: str
  entries:
    description: >
      List of community filter entries that make up the filter. When provided
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
        description: Whether the entry permits or denies the matched route.
        required: true
        choices:
          - permit
          - deny
        type: str
      match_string:
        description: >
          Community value or regular expression matched against the BGP
          communities of a route, for example 65000:1 or _65001:.
        required: true
        type: str
  state:
    description: Create, update or delete the BGP community filter.
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
- name: Create a BGP community filter with two entries
  aoscx_bgp_community_list:
    name: COMM_AS65000
    type: community-list
    description: Match communities from AS 65000
    entries:
      - preference: 10
        action: permit
        match_string: '65000:1'
      - preference: 20
        action: deny
        match_string: '65000:666'

- name: Add or update a single entry on an existing filter
  aoscx_bgp_community_list:
    name: COMM_AS65000
    state: update
    entries:
      - preference: 10
        action: permit
        match_string: '65000:1'
      - preference: 20
        action: deny
        match_string: '65000:666'
      - preference: 30
        action: permit
        match_string: '65000:2'

- name: Create an expanded community filter matching a regular expression
  aoscx_bgp_community_list:
    name: COMM_REGEX
    type: community-expanded-list
    entries:
      - preference: 10
        action: permit
        match_string: '_65001:'

- name: Delete a BGP community filter
  aoscx_bgp_community_list:
    name: COMM_AS65000
    state: delete
```
