# module: aoscx_radius_config_attribute

description: This module provides configuration management of the RADIUS
configuration attributes attached to an AAA server group on AOS-CX devices.
Each attribute controls whether a RADIUS attribute is included for its service.
The resource is identified by the AAA server group it applies to.

##### ARGUMENTS

```YAML
  server_group:
    description: >
      Name of the AAA server group the RADIUS configuration attributes apply
      to. The server group must already exist.
    required: true
    type: str
  server_group_type:
    description: Type of the referenced AAA server group.
    required: false
    default: radius
    choices:
      - radius
      - tacacs
    type: str
  framed_ip_addr:
    description: Include the Framed-IP-Address attribute (port-access service).
    required: false
    type: bool
  nas_id:
    description: Include the NAS-Identifier attribute (port-access service).
    required: false
    type: bool
  nas_ip_addr:
    description: Include the NAS-IP-Address attribute (user-management service).
    required: false
    type: bool
  tunnel_private_group_id:
    description: >
      Include the Tunnel-Private-Group-ID attribute (port-access service).
    required: false
    type: bool
  state:
    description: Create, update or delete the RADIUS configuration attributes.
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
- name: Enable NAS-Identifier and NAS-IP-Address for a server group
  aoscx_radius_config_attribute:
    server_group: my-radius-group
    nas_id: true
    nas_ip_addr: true

- name: Disable the NAS-Identifier attribute
  aoscx_radius_config_attribute:
    server_group: my-radius-group
    nas_id: false
    state: update

- name: Delete the RADIUS configuration attributes of a server group
  aoscx_radius_config_attribute:
    server_group: my-radius-group
    state: delete
```
