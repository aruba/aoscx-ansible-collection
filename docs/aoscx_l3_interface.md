# module: aoscx_l3_interface

description: This modules provides configuration management of Layer3
Interfaces on AOS-CX devices.

##### ARGUMENTS

```YAML
  interface:
    description: >
      Interface name, should be in the format chassis/slot/port, e.g. 1/2/3,
      1/1/32.
    type: str
    required: true
  description:
    description: Description of interface.
    type: str
    required: false
  ipv4:
    description: >
      The IPv4 address and subnet mask in the address/mask format. The first
      entry in the list is the primary IPv4, the remainings are secondary IPv4.
      To remove an IP address pass in the list without the IP address yo wish
      to remove, and use the update state.
    type: list
    elements: str
    required: false
  ipv6:
    description: >
      The IPv6 address and subnet mask in the address/mask format.
      The IPv6 address and subnet mask in the address/mask format. It takes
      multiple IPv6 with comma separated in the list. To remove an IP address
      pass in the list without the IP address yo wish to remove, and use the
      update state.
    type: list
    elements: str
    required: false
  vrf:
    description: >
      The VRF the interface will belong to once created. If none provided, the
      interface will be in the Default VRF. If an L3 interface is created and
      the user wants to change the interface's VRF, the user must delete the L3
      interface then recreate the interface in the desired VRF.
    type: str
    required: false
  interface_qos_schedule_profile:
    description: >
      Attaching existing QoS schedule profile to interface. *This parameter is
      deprecated and will be removed in a future version.
    type: dict
    required: false
  interface_qos_rate:
    description: >
      The rate limit value configured for broadcast/multicast/unknown unicast
      traffic. Dictionary should have the format 'type_of_traffic': speed
      e.g.
        'unknown-unicast': 100pps
        'broadcast': 200pps
        'multicast': 200pps
    type: dict
    required: false
  ip_helper_address:
    description: >
      Configure a remote DHCP server/relay IP address on the device interface.
      Here the helper address is same as the DHCP server address or another
      intermediate DHCP relay.
    type: list
    elements: str
    required: false
  state:
    description: Create, Update, or Delete Layer3 Interface
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
```

##### EXAMPLES

```YAML
- name: >
    Configure Interface 1/1/3 - enable interface and vsx-sync features
    IMPORTANT NOTE: the aoscx_interface module is needed to enable the
    interface and set the VSX features to be synced.
  aoscx_interface:
    name: 1/1/3
    enabled: true
    vsx_sync:
      - acl
      - irdp
      - qos
      - rate_limits
      - vlan
      - vsx_virtual
- name: >
    Creating new L3 interface 1/1/3 with IPv4 and IPv6 address on VRF red
    IMPORTANT NOTE: see the above task, it is needed to enable the interface
  aoscx_l3_interface:
    interface: 1/1/3
    description: Uplink Interface
    ipv4:
      - 10.20.1.3/24
    ipv6:
      - 2000:db8::1234/64
    vrf: red

- name: Creating new L3 interface 1/1/6 with IPv4 address on VRF default
  aoscx_l3_interface:
    interface: 1/1/6
    ipv4:
      - 10.33.4.15/24

- name: Deleting L3 Interface - 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    state: delete

- name: Create IP Helper Address on Interface 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    ip_helper_address:
      - 172.1.2.32

- name: Update IP Helper Address on Interface 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    ip_helper_address: 172.1.5.44
    state: update
```
