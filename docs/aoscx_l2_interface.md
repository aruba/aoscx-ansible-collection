# module: aoscx_l2_interface

description: This modules provides configuration management of Layer2 Interfaces on AOS-CX devices.

##### ARGUMENTS
```YAML
  interface:
    description: Interface name, should be in the format chassis/slot/port,
      i.e. 1/2/3 , 1/1/32. Please note, if the interface is a Layer3 interface
      in the existing configuration and the user wants to change the interface
      to be Layer2, the user must delete the L3 interface then recreate the
      interface as a Layer2.
    type: str
    required: true
  admin_state:
    description: Admin State status of interface.
    default: 'up'
    choices: ['up', 'down']
    required: false
    type: str
  description:
    description: Description of interface.
    type: str
    required: false
  vlan_mode:
    description: VLAN mode on interface, access or trunk.
    choices: ['access', 'trunk']
    required: false
    type: str
  vlan_access:
    description: Access VLAN ID, vlan_mode must be set to access.
    required: false
    type: str
  vlan_trunks:
    description: List of trunk VLAN IDs, vlan_mode must be set to trunk.
    required: false
    type: list
  trunk_allowed_all:
    description: Flag for vlan trunk allowed all on L2 interface, vlan_mode
      must be set to trunk.
    required: false
    type: bool
  native_vlan_id:
    description: VLAN trunk native VLAN ID, vlan_mode must be set to trunk.
    required: false
    type: str
  native_vlan_tag:
    description: Flag for accepting only tagged packets on VLAN trunk native,
      vlan_mode must be set to trunk.
    required: false
    type: bool
  interface_qos_schedule_profile:
    description: Attaching existing QoS schedule profile to interface.
    type: dict
    required: False
  interface_qos_rate:
    description: "The rate limit value configured for
      broadcast/multicast/unknown unicast traffic. Dictionary should have the
      format ['type_of_traffic'] = speed i.e. {'unknown-unicast': 100pps,
      'broadcast': 200pps, 'multicast': 200pps}"
    type: dict
    required: False
  state:
    description: Create, Update, or Delete Layer2 Interface
    choices: ['create', 'delete', 'update']
    default: 'create'
    required: false
    type: str
```

##### EXAMPLES
```YAML
- name: Configure Interface 1/1/3 - vlan trunk allowed all
  aoscx_l2_interface:
    interface: 1/1/3
    vlan_mode: trunk
    trunk_allowed_all: True

- name: Delete Interface 1/1/3
  aoscx_l2_interface:
    interface: 1/1/3
    state: delete

- name: Configure Interface 1/1/1 - vlan trunk allowed 200
  aoscx_l2_interface:
    interface: 1/1/1
    vlan_mode: trunk
    vlan_trunks: '200'

- name: Configure Interface 1/1/1 - vlan trunk allowed 200,300
  aoscx_l2_interface:
    interface: 1/1/1
    vlan_mode: trunk
    vlan_trunks: ['200','300']

- name: Configure Interface 1/1/1 - vlan trunk allowed 200,300 , vlan trunk native 200
  aoscx_l2_interface:
    interface: 1/1/3
    vlan_mode: trunk
    vlan_trunks: ['200','300']
    native_vlan_id: '200'

- name: Configure Interface 1/1/4 - vlan access 200
  aoscx_l2_interface:
    interface: 1/1/4
    vlan_mode: access
    vlan_access: '200'

- name: Configure Interface 1/1/5 - vlan trunk allowed all, vlan trunk native 200 tag
  aoscx_l2_interface:
    interface: 1/1/5
    vlan_mode: trunk
    trunk_allowed_all: True
    native_vlan_id: '200'
    native_vlan_tag: True

- name: Configure Interface 1/1/6 - vlan trunk allowed all, vlan trunk native 200
  aoscx_l2_interface:
    interface: 1/1/6
    vlan_mode: trunk
    trunk_allowed_all: True
    native_vlan_id: '200'
```