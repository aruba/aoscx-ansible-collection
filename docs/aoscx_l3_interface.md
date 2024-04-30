# Layer 3 Interfaces

Configuration management of Layer3 Interfaces on AOS-CX devices.

Version added: 2.8.0

 - [Synopsis](#synopsis)
 - [Parameters](#parameters)
 - [Examples](#examples)

## Synopsis

This modules provides configuration management of Layer3 Interfaces on AOS-CX devices.
There is an issue on platform 6200, so it is necessary to use REST version 10.09.
There are two methods to configure REST version:
- Parameter `ansible_aoscx_rest_version` in inventory file or variable in
  the playbook.
  Example:
```
ansible_aoscx_rest_version: 10.09
```
- Environment variable `ANSIBLE_AOSCX_REST_VERSION`.
  Example:
```
export ANSIBLE_AOSCX_REST_VERSION=10.09
```

## Parameters

| Parameter                        | Type | Choices/Defaults                          | Required | Comments                                                                                                                                                                                                                                                                             |
|:---------------------------------|:-----|:------------------------------------------|:--------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `interface`                      | str  |                                           | [x]      | Interface name, should be in the format chassis/slot/port, e.g. 1/2/3                                                                                                                                                                                                                |
| `ipv4`                           | list |                                           | [ ]      | The IPv4 address and subnet mask in the address/mask format. The first entry in the list is the primary IPv4, the remainings are secondary IPv4; to remove an IP address pass in the list and use the delete state.                                                                  |
| `ipv6`                           | str  |                                           | [ ]      | The IPv6 address and subnet mask in the address/mask format. To remove an IP address pass in the list and use the delete state.                                                                                                                                                      |
| `vrf`                            | str  |                                           | [ ]      | VRF to which the port belongs if the port is routing. If none provided, the interface will be in the Default VRF. If the VRF is removed or changed all configuration is erased from the interface.                                                             |
| `interface_qos_schedule_profile` | dict |                                           | [ ]      | Attaching existing QoS schedule profile to interface. This parameter is deprecated and will be removed in a future version.                                                                                                                                                          |
| `interface_qos_rate`             | dict |                                           | [ ]      | The rate limit value configured for broadcast/multicast/unknown unicast traffic. Dictionary should have the format `type_of_traffic`: speed e.g. {'unknown-unicast': '100pps', 'broadcast': '200pps', 'multicast': '200pps'}                                                         |
| `ip_helper_address`              | str  |                                           | [ ]      | Configure a remote DHCP server/relay IP address on the device interface. Here the helper address is same as the DHCP server address or another intermediate DHCP relay.                                                                                                              |
| `state`                          | str  | [`create`, `update`, `delete`] / `create` | [ ]      | Create, Update, or Delete Layer3 Interface                                                                                                                                                                                                                                    |
## Examples

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

- name: Creating new L3 interface 1/1/6 with IPv4 addresses on VRF default
  aoscx_l3_interface:
    interface: 1/1/6
    ipv4:
      - 10.33.4.15/24
      - 10.0.1.1/24

- name: Delete IPv4 addresses on VRF default from L3 Interface 1/1/6
  aoscx_l3_interface:
    interface: 1/1/6
    ipv4:
      - 10.0.1.1/24
    state: delete

- name: Delete VRF attach of the Interface 1/1/3
  aoscx_l3_interface:
    interface: 1/1/3
    vrf: red
    state: delete

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
