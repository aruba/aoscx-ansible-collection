# module: aoscx_radius_dynauth_proxy_server

description: This module provides configuration management of RADIUS dynamic
authorization (Change of Authorization) proxy servers on AOS-CX devices. A
proxy server lives under a VRF and is identified by the combination of its
address, port and port type.

##### ARGUMENTS

```YAML
  vrf:
    description: VRF the proxy server belongs to.
    required: false
    default: default
    type: str
  address:
    description: IPv4 address or hostname of the proxy server.
    required: true
    type: str
  port:
    description: UDP/TCP port of the proxy server.
    required: false
    default: 3799
    type: int
  port_type:
    description: Transport used by the proxy server.
    required: false
    default: udp
    choices:
      - udp
      - tcp
    type: str
  secret_key:
    description: >
      Shared secret used with the proxy server. It is write-only; the switch
      only ever returns it encrypted, so when secret_key is supplied the
      module reports changed on every run.
    required: false
    type: str
  state:
    description: Create, update or delete the proxy server.
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
- name: Create a RADIUS dynamic authorization proxy server
  aoscx_radius_dynauth_proxy_server:
    vrf: default
    address: 192.0.2.30
    port: 3799
    port_type: udp
    secret_key: my-secret

- name: Delete a RADIUS dynamic authorization proxy server
  aoscx_radius_dynauth_proxy_server:
    vrf: default
    address: 192.0.2.30
    port: 3799
    port_type: udp
    state: delete
```
