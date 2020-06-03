# module: aoscx_vlan_interface

description: This modules provides configuration management of VLAN Interfacess on AOS-CX devices.

##### ARGUMENTS
```YAML
  vlan_id:
    description: The ID of this VLAN interface. Non-internal VLANs must have
                 an 'id' between 1 and 4094 to be effectively instantiated.
    required: true
    type: str
  admin_state:
    description: Admin State status of vlan interface.
    choices: ['up', 'down']
    required: false
    type: str
  ipv4:
    description: "The IPv4 address and subnet mask in the address/mask format.
      The first entry in the list is the primary IPv4, the remainings are
      secondary IPv4. i.e. ['10.1.1.1/24', '10.2.1.3/255.255.254.0']. To remove
      an IP address pass in '' and set state: update."
    type: list
    required: False
  ipv6:
    description: "The IPv6 address and subnet mask in the address/mask format.
      It takes multiple IPv6 with comma separated in the list.
      i.e. ['2000:cc92::2/64', '3000:820a::43/64']  . To remove an IP address
      pass in '' and set state: update."
    type: list
    required: False
  vrf:
    description: "The VRF the vlan interface will belong to once created. If
      none provided, the interface will be in the Default VRF. If the VLAN
      interface is created and the user wants to change the interface vlan's
      VRF, the user must delete the VLAN interface then recreate the VLAN
      interface in the desired VRF."
    type: str
    required: False
  ip_helper_address:
    description: "Configure a remote DHCP server/relay IP address on the vlan
      interface. Here the helper address is same as the DHCP server address or
      another intermediate DHCP relay."
    type: list
    required: False
  description:
    description: VLAN description
    required: false
    type: str
  active_gateway_ip:
    description: Configure IPv4 active-gateway for vlan interface.
    type: str
    required: False
  active_gateway_mac_v4:
    description: "Configure virtual MAC address for IPv4 active-gateway for
      vlan interface. Must be used in conjunction of active_gateway_ip"
    type: str
    required: False
  state:
    description: Create or update or delete the VLAN.
    required: false
    choices: ['create', 'update', 'delete']
    default: create
    type: str
```

##### EXAMPLES
```YAML
  - name: Create VLAN Interface 100
    aoscx_vlan_interface:
      vlan_id: 100
      description: UPLINK_VLAN
      ipv4: ['10.10.20.1/24']
      ipv6: ['2000:db8::1234/64']

  - name: Create VLAN Interface 200
    aoscx_vlan_interface:
      vlan_id: 200
      description: UPLINK_VLAN
      ipv4: ['10.20.20.1/24']
      ipv6: ['3000:db8::1234/64']
      vrf: red
      ip_helper_address: ['10.40.20.1']

  - name: Delete VLAN Interface 100
    aoscx_vlan_interface:
      vlan_id: 100
      state: delete
```