# module: aoscx_radius_dynauth_proxy_profile

description: This module provides configuration management of RADIUS dynamic
authorization (Change of Authorization) proxy profiles on AOS-CX devices. A
profile ties together a proxy client group and a proxy server within a VRF, and
is identified by its name.

##### ARGUMENTS

```YAML
  profile_name:
    description: Name of the proxy profile.
    required: true
    type: str
  enabled:
    description: Whether the proxy profile is enabled.
    required: false
    type: bool
  address:
    description: Source IPv4 address used by the proxy profile.
    required: false
    type: str
  port:
    description: Port used by the proxy profile.
    required: false
    type: int
  port_type:
    description: Transport used by the proxy profile.
    required: false
    choices:
      - udp
      - tcp
    type: str
  vrf:
    description: VRF the proxy profile belongs to.
    required: false
    default: default
    type: str
  client_group:
    description: >
      Name of the RADIUS dynamic authorization proxy client group referenced by
      this profile. The client group must already exist. Pass an empty string
      to clear the reference.
    required: false
    type: str
  server:
    description: >
      RADIUS dynamic authorization proxy server referenced by this profile. The
      server must already exist.
    required: false
    type: dict
    suboptions:
      address:
        description: Address of the proxy server.
        required: true
        type: str
      port:
        description: Port of the proxy server.
        required: false
        default: 3799
        type: int
      port_type:
        description: Transport of the proxy server.
        required: false
        default: udp
        choices:
          - udp
          - tcp
        type: str
      vrf:
        description: VRF of the proxy server.
        required: false
        default: default
        type: str
  state:
    description: Create, update or delete the proxy profile.
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
- name: Create a proxy profile tying a client group and a server
  aoscx_radius_dynauth_proxy_profile:
    profile_name: coa-proxy
    enabled: true
    vrf: default
    client_group: coa-group
    server:
      address: 192.0.2.30
      port: 3799
      port_type: udp

- name: Delete a proxy profile
  aoscx_radius_dynauth_proxy_profile:
    profile_name: coa-proxy
    state: delete
```
