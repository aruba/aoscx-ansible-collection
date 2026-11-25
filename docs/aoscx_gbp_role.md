# module: aoscx_gbp_role

description: This module provides configuration management of Group Based
Policy (GBP) roles on AOS-CX devices (C(gbp role <name> <id>) command, stored
in system/gbp_role_name_id_maps). A GBP role maps a role name to the role ID
carried in the traffic, and is referenced by the source and destination roles
of the gbp-ipv4, gbp-ipv6 and gbp-mac classes. GBP enforcement itself is
enabled with the gbp_enable option of the aoscx_system module. The built-in
roles (default, infra, internet, intranet) cannot be modified or deleted.
Requires a pyaoscx release that ships the GbpRole class.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the GBP role. This is the index of the resource under
      system/gbp_role_name_id_maps (up to 128 characters).
    required: true
    type: str
  role_id:
    description: >
      GBP role ID associated with the role (0 to 8191). Required to create
      the role.
    required: false
    type: int
  state:
    description: Create, update or delete the GBP role.
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
- name: Create the GBP role fabric_user1 with the role ID 1010
  aoscx_gbp_role:
    name: fabric_user1
    role_id: 1010

- name: Change the role ID of an existing GBP role
  aoscx_gbp_role:
    name: fabric_user1
    role_id: 1011
    state: update

- name: Delete a GBP role
  aoscx_gbp_role:
    name: fabric_user1
    state: delete
```
