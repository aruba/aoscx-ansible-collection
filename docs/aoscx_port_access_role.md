# module: aoscx_port_access_role

description: This module provides configuration management of Port Access Roles
on AOS-CX devices (system/port_access_roles). A port access role is the local
user role applied to authenticated clients (for example a role returned by a
RADIUS server such as ClearPass). It groups the VLAN assignment and the
per-client access settings. This module requires REST API version 10.16 (set
ansible_aoscx_rest_version to 10.16). The reference attributes macsec_policy
and ipfix_flow_monitor are not managed by this module.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the port access role. This is the index of the resource under
      system/port_access_roles.
    required: true
    type: str
  description:
    description: Description of the port access role.
    required: false
    type: str
  auth_mode:
    description: Authentication mode applied to clients using this role.
    required: false
    type: str
    choices:
      - client-mode
      - device-mode
      - proxy-mode
      - multi-domain
  vlan_mode:
    description: VLAN mode applied to clients using this role.
    required: false
    type: str
    choices:
      - trunk
      - access
      - native-tagged
      - native-untagged
  vlan_tag:
    description: Access or native VLAN ID assigned by this role.
    required: false
    type: int
  vlan_trunks:
    description: List of tagged trunk VLAN IDs assigned by this role.
    required: false
    type: list
    elements: int
  vlan_name_tag:
    description: Access or native VLAN name assigned by this role.
    required: false
    type: str
  vlan_name_trunks:
    description: List of tagged trunk VLAN names assigned by this role.
    required: false
    type: list
    elements: str
  reauth_period:
    description: Reauthentication period in seconds.
    required: false
    type: int
  cached_reauth_period:
    description: Cached reauthentication period in seconds.
    required: false
    type: int
  client_inactivity_monitor:
    description: Client inactivity monitoring mode.
    required: false
    type: str
    choices:
      - configured_timeout
      - dynamic_timeout
      - no_timeout
  client_inactivity_timeout:
    description: Client inactivity timeout in seconds.
    required: false
    type: int
  max_session_time:
    description: Maximum session time in seconds.
    required: false
    type: int
  mtu:
    description: MTU applied to clients using this role.
    required: false
    type: int
  poe_priority:
    description: PoE priority applied to clients using this role.
    required: false
    type: str
    choices:
      - low
      - high
      - critical
  poe_allocate_by_method:
    description: Method used to allocate PoE power.
    required: false
    type: str
    choices:
      - class
      - usage
  qos_trust_mode:
    description: QoS trust mode applied to clients using this role.
    required: false
    type: str
    choices:
      - none
      - cos
      - dscp
  stp_admin_edge_port:
    description: Whether the port is configured as an STP admin edge port.
    required: false
    type: bool
  device_traffic_class:
    description: Device traffic class assigned by this role.
    required: false
    type: str
    choices:
      - voice
  gateway_zone:
    description: User-based tunneling gateway zone.
    required: false
    type: str
  ubt_gateway_role:
    description: User-based tunneling gateway role.
    required: false
    type: str
  pvlan_port_type:
    description: Private VLAN port type.
    required: false
    type: str
    choices:
      - promiscuous
      - secondary
  app_recognition_enable:
    description: Whether application recognition is enabled for the role.
    required: false
    type: bool
  traffic_inspection_enable:
    description: Whether traffic inspection is enabled for the role.
    required: false
    type: bool
  captive_portal_profile:
    description: >
      Name of an existing captive portal profile
      (system/captive_portal_profiles) to associate with this role. The
      profile must already exist.
    required: false
    type: str
  in_gbp:
    description: >
      Name of an existing port access group based policy
      (system/port_access_gbps) to apply to clients using this role. The
      policy must already exist.
    required: false
    type: str
  in_abp:
    description: >
      Name of an existing port access application based policy
      (system/port_access_abps) to apply to clients using this role. The
      policy must already exist.
    required: false
    type: str
  in_policy:
    description: >
      Name of an existing port access policy (system/port_access_policies) to
      apply to clients using this role. The policy must already exist.
    required: false
    type: str
  state:
    description: Create, update or delete the port access role.
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
- name: Create a port access role assigning an access VLAN
  aoscx_port_access_role:
    name: employee
    description: Corporate employees
    vlan_mode: access
    vlan_tag: 10

- name: Create a guest role with a captive portal profile
  aoscx_port_access_role:
    name: guest
    vlan_mode: access
    vlan_tag: 20
    captive_portal_profile: guest-portal
    client_inactivity_monitor: dynamic_timeout

- name: Create a role applying an existing group based policy
  aoscx_port_access_role:
    name: employee
    vlan_mode: access
    vlan_tag: 10
    in_gbp: employee_r2r_policy

- name: Delete a port access role
  aoscx_port_access_role:
    name: guest
    state: delete
```
