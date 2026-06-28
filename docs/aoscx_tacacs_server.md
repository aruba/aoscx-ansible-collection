# module: aoscx_tacacs_server

description: This module provides configuration management of TACACS+ servers on
AOS-CX devices (system/vrfs/{vrf}/tacacs_servers). A TACACS+ server is
identified by the combination of its address and TCP port within a VRF. This
module requires REST API version 10.16 (set ansible_aoscx_rest_version to
10.16). The address, tcp_port and vrf are set when the server is created and
cannot be changed afterwards. At least one server group must be supplied when
the server is created. The passkey is write-only; when it is supplied the
module always (re)applies it, which is reported as a change.

##### ARGUMENTS

```YAML
  address:
    description: IP address or hostname of the TACACS+ server.
    required: true
    type: str
  vrf:
    description: Name of the VRF the TACACS+ server belongs to.
    required: false
    default: default
    type: str
  tcp_port:
    description: TCP port used to reach the TACACS+ server (1-65535).
    required: false
    default: 49
    type: int
  passkey:
    description: >
      Shared secret used with the TACACS+ server. This value is write-only;
      the switch only ever returns it encrypted, so when passkey is supplied
      the module always (re)applies it and reports a change.
    required: false
    type: str
  group:
    description: >
      List of AAA server group names this server belongs to. The referenced
      groups must already exist. At least one group is required when the
      server is created. The supplied list fully replaces the current group
      membership.
    required: false
    type: list
    elements: str
  default_group_priority:
    description: >
      Priority of this server within the default tacacs group (1 or higher).
    required: false
    default: 1
    type: int
  user_group_priority:
    description: Priority of this server within a user-defined group.
    required: false
    type: int
  auth_type:
    description: Authentication protocol used with the TACACS+ server.
    required: false
    type: str
    choices:
      - pap
      - chap
  timeout:
    description: Time in seconds to wait for a server response (1-60).
    required: false
    type: int
  tracking_enable:
    description: Enable server-reachability tracking.
    required: false
    type: bool
  state:
    description: Create, update or delete the TACACS+ server.
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
- name: Create a TACACS+ server
  aoscx_tacacs_server:
    address: 192.0.2.20
    vrf: default
    passkey: my-secret
    group:
      - tacacs
    auth_type: pap
    timeout: 10

- name: Update the TACACS+ server timeout
  aoscx_tacacs_server:
    address: 192.0.2.20
    state: update
    timeout: 20

- name: Delete a TACACS+ server
  aoscx_tacacs_server:
    address: 192.0.2.20
    state: delete
```
