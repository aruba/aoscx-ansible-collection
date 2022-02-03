# module: aoscx_l3_interface

description: This modules provides configuration management of Layer3 Interfaces on AOS-CX devices.

##### ARGUMENTS
```YAML
  interface:
    description: Interface name, should be in the format chassis/slot/port,
      i.e. 1/2/3 , 1/1/32.
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
  ipv4:
    description: "The IPv4 address and subnet mask in the address/mask format.
      The first entry in the list is the primary IPv4, the remainings are
      secondary IPv4. i.e. ['10.1.1.1/24', '10.2.1.3/255.255.254.0']  To remove
      an IP address pass in '' and set 'state: update'."
    type: list
    required: False
  ipv6:
    description: "The IPv6 address and subnet mask in the address/mask format.
      It takes multiple IPv6 with comma separated in the list.
      i.e. ['2000:cc92::2/64', '3000:820a::43/64']  To remove
      an IP address pass in '' and set state: update."
    type: list
    required: False
  vrf:
    description: "The VRF the interface will belong to once created. If none
      provided, the interface will be in the Default VRF. If an L3 interface is
      created and the user wants to change the interface's VRF, the user must
      delete the L3 interface then recreate the interface in the desired VRF."
    type: str
    required: False
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
  ip_helper_address:
    description: "Configure a remote DHCP server/relay IP address on the device
      interface. Here the helper address is same as the DHCP server address or
      another intermediate DHCP relay."
    type: list
    required: False
  state:
    description: Create, Update, or Delete Layer3 Interface
    choices: ['create', 'delete', 'update']
    default: 'create'
    required: false
    type: str
```

##### EXAMPLES
```YAML
- name: Creating new L3 interface 1/1/3 with IPv4 and IPv6 address on VRF red
  aoscx_l3_interface:
    interface: 1/1/3
    description: Uplink Interface
    ipv4: ['10.20.1.3/24']
    ipv6: ['2000:db8::1234/64']
    vrf: red

- name: Creating new L3 interface 1/1/6 with IPv4 address on VRF default
  aoscx_l3_interface:
    interface: 1/1/6
    ipv4: ['10.33.4.15/24']

- name: Deleting L3 Interface - 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    state: delete

- name: Create IP Helper Address on Interface 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    ip_helper_address: ['172.1.2.32']

- name: Update IP Helper Address on Interface 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    ip_helper_address: ['172.1.5.44']
    state: update
    
- name: Set a rate limit for the interface
  aoscx_l3_interface:
    interface: 1/1/2
    interface_qos_rate:
      broadcast: 200pps
      multicast: 100kbps
```
