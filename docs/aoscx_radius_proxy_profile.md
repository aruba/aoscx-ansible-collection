# module: aoscx_radius_proxy_profile

description: This module provides configuration management of RADIUS proxy
profiles on AOS-CX devices. A profile ties together a RADIUS proxy client group
and an AAA server group within a VRF, and is identified by its name.

##### ARGUMENTS

```YAML
  profile_name:
    description: Name of the RADIUS proxy profile.
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
    description: Authentication UDP/TCP port used by the proxy profile.
    required: false
    type: int
  port_type:
    description: Transport used by the proxy profile.
    required: false
    choices:
      - udp
      - tcp
    type: str
  accounting_udp_port:
    description: Accounting UDP port used by the proxy profile.
    required: false
    type: int
  nas_id:
    description: NAS identifier sent by the proxy.
    required: false
    type: str
  nas_ip_addr:
    description: NAS IP address sent by the proxy.
    required: false
    type: str
  timeout:
    description: Request timeout in seconds.
    required: false
    type: int
  vrf:
    description: VRF the proxy profile belongs to.
    required: false
    default: default
    type: str
  client_group:
    description: >
      Name of the RADIUS proxy client group referenced by this profile. The
      client group must already exist. Pass an empty string to clear it.
    required: false
    type: str
  server_group:
    description: >
      Name of the AAA server group referenced by this profile. The server group
      must already exist.
    required: false
    type: str
  server_group_type:
    description: Type of the referenced AAA server group.
    required: false
    default: radius
    choices:
      - radius
      - tacacs
    type: str
  state:
    description: Create, update or delete the RADIUS proxy profile.
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
- name: Create a RADIUS proxy profile tying a client group and a server group
  aoscx_radius_proxy_profile:
    profile_name: radius-proxy
    enabled: true
    vrf: default
    client_group: nas-group
    server_group: my-radius-group

- name: Delete a RADIUS proxy profile
  aoscx_radius_proxy_profile:
    profile_name: radius-proxy
    state: delete
```
