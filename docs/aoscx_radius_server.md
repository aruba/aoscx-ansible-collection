# module: aoscx_radius_server

description: This module provides configuration management of RADIUS servers on
AOS-CX devices (system/vrfs/{vrf}/radius_servers). A RADIUS server is
identified by the combination of its address, UDP/TCP port and port type within
a VRF. This module requires REST API version 10.16 (set
ansible_aoscx_rest_version to 10.16). The address, port, port_type and vrf are
set when the server is created and cannot be changed afterwards. The passkey is
write-only; when it is supplied the module always (re)applies it, which is
reported as a change.

##### ARGUMENTS

```YAML
  address:
    description: IP address or hostname of the RADIUS server.
    required: true
    type: str
  vrf:
    description: Name of the VRF the RADIUS server belongs to.
    required: false
    default: default
    type: str
  port:
    description: UDP/TCP port used to reach the RADIUS server (1-65535).
    required: false
    default: 1812
    type: int
  port_type:
    description: Transport used to reach the RADIUS server.
    required: false
    default: udp
    type: str
    choices:
      - udp
      - tcp
  passkey:
    description: >
      Shared secret used with the RADIUS server. This value is write-only; the
      switch only ever returns it encrypted, so when passkey is supplied the
      module always (re)applies it and reports a change.
    required: false
    type: str
  auth_type:
    description: Authentication protocol used with the RADIUS server.
    required: false
    type: str
    choices:
      - pap
      - chap
  accounting_udp_port:
    description: UDP port used for RADIUS accounting (1-65535).
    required: false
    type: int
  retries:
    description: Number of retransmissions before giving up (0-5).
    required: false
    type: int
  timeout:
    description: Time in seconds to wait for a server response (1-60).
    required: false
    type: int
  tls_initial_connection_timeout:
    description: >
      Time in seconds to wait when establishing a RadSec TLS connection
      (5-300).
    required: false
    type: int
  msg_authenticator_check:
    description: Enable Message-Authenticator attribute checking.
    required: false
    type: bool
  tracking_enable:
    description: Enable server-reachability tracking.
    required: false
    type: bool
  tracking_method:
    description: Method used to track the server reachability.
    required: false
    type: str
    choices:
      - status-server
      - keep-alive
      - access-request
  tracking_mode:
    description: When to track the server reachability.
    required: false
    type: str
    choices:
      - any
      - dead-only
  port_access:
    description: Method used by port-access to track the server.
    required: false
    type: str
    choices:
      - status-server
      - keep-alive
  server_group:
    description: >
      Mapping of AAA server group names to their priority for this server,
      for example {my-radius: 1}. The referenced groups must already exist.
      The supplied mapping fully replaces the current group membership.
    required: false
    type: dict
  state:
    description: Create, update or delete the RADIUS server.
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
- name: Create a RADIUS server
  aoscx_radius_server:
    address: 192.0.2.10
    vrf: default
    passkey: my-secret
    auth_type: pap
    timeout: 10

- name: Create a RADIUS server bound to a server group
  aoscx_radius_server:
    address: 192.0.2.11
    vrf: default
    passkey: my-secret
    server_group:
      my-radius: 1

- name: Update the RADIUS server timeout
  aoscx_radius_server:
    address: 192.0.2.10
    state: update
    timeout: 20

- name: Delete a RADIUS server
  aoscx_radius_server:
    address: 192.0.2.10
    state: delete
```
