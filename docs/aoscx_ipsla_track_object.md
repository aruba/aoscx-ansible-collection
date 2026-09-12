# module: aoscx_ipsla_track_object

description: This module provides configuration management of IP SLA track
objects on AOS-CX devices (system/ipsla_track_objects). A track object follows
the state of one or more IP SLA sessions. IP SLA requires REST API version
10.16 (set ansible_aoscx_rest_version to 10.16). The tracked IP SLA sessions
are set when the track object is created and cannot be modified; changing them
recreates the track object.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the IP SLA track object. This is the index of the resource
      under system/ipsla_track_objects.
    required: true
    type: str
  tracked_ipsla_session:
    description: >
      List of IP SLA source names tracked by this object. Set on creation;
      changing this list recreates the track object.
    required: false
    type: list
    elements: str
  track_list_operator:
    description: >
      Operator combining the tracked sessions to compute the overall state.
    required: false
    type: str
    choices:
      - and
      - or
  up_delay:
    description: >
      Delay in seconds before the track object is declared up (0-180).
    required: false
    type: int
  down_delay:
    description: >
      Delay in seconds before the track object is declared down (0-180).
    required: false
    type: int
  state:
    description: Create, update or delete the IP SLA track object.
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
- name: Create an IP SLA track object
  aoscx_ipsla_track_object:
    name: track-gw
    tracked_ipsla_session:
      - probe-gw
    track_list_operator: or
    up_delay: 5

- name: Update the track object timers
  aoscx_ipsla_track_object:
    name: track-gw
    state: update
    up_delay: 10
    down_delay: 5

- name: Delete an IP SLA track object
  aoscx_ipsla_track_object:
    name: track-gw
    state: delete
```
