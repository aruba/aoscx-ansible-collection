# L2 Interface

L2 Interface module for Ansible.

Version added: 2.8

 - [Synopsis](#Synopsis)
 - [Parameters](#Parameters)
 - [Examples](#Examples)

## Synopsis

This modules provides configuration management of Layer2 Interfaces on AOS-CX
devices, including Speeds and Port Security features.

## Parameters

| Parameter                        | Type | Choices/Defaults                        | Required | Comments                                                                                                                                                                                                                                                                                                  |
|:---------------------------------|:-----|:----------------------------------------|:--------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `interface`                      | str  |                                         | [x]      | Interface name, should be in the format chassis/slot/port, i.e. 1/2/3 , 1/1/32. Please note, if the interface is a Layer3 interface in the existing configuration and the user wants to change the interface to be Layer2, the user must delete the L3 interface then recreate the interface as a Layer2. |
| `description`                    | str  |                                         | [x]      | Description of interface.                                                                                                                                                                                                                                                                                 |
| `vlan_mode`                      | str  | [`access`, `trunk`]                     | [ ]      | VLAN mode on interface, access or trunk.                                                                                                                                                                                                                                                                  |
| `vlan_access`                    | str  |                                         | [ ]      | Access VLAN ID, vlan_mode must be set to access.                                                                                                                                                                                                                                                          |
| `vlan_trunks`                    | list |                                         | [ ]      | List of trunk VLAN IDs, vlan_mode must be set to trunk.                                                                                                                                                                                                                                                   |
| `trunk_allowed_all`              | bool |                                         | [ ]      | Flag for vlan trunk allowed all on L2 interface, vlan_mode must be set to trunk.                                                                                                                                                                                                                          |
| `native_vlan_id`                 | str  |                                         | [ ]      | VLAN trunk native VLAN ID, vlan_mode must be set to trunk.                                                                                                                                                                                                                                                |
| `native_vlan_tag`                | bool |                                         | [ ]      | Flag for accepting only tagged packets on VLAN trunk native, vlan_mode must be set to trunk.                                                                                                                                                                                                              |
| `interface_qos_schedule_profile` | dict |                                         | [ ]      | Attaching existing QoS schedule profile to interface. \*This parameter is deprecated and will be removed in a future version                                                                                                                                                                              |
| `interface_qos_rate`             | dict |                                         | [ ]      | The rate limit value configured for broadcast/multicast/unknown unicast traffic.                                                                                                                                                                                                                          |
| `speeds`                         | str  |                                         | [ ]      | Configure the speeds of the interface in megabits per second (aoscx connection). If this value is specified, `duplex` must also be specified                                                                                                                                                              |
| `duplex`                         | bool |                                         | [ ]      | Enable full duplex or disable for half duplex (aoscx connection). If this value is specified, `speeds` must also be specified                                                                                                                                                                             |
| `port_security_enable`           | bool |                                         | [ ]      | Enable port security in this interface (aoscx connection)                                                                                                                                                                                                                                                 |
| `port_security_client_limit`     | int  |                                         | [ ]      | Maximum amount of MACs allowed in the interface (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                              |
| `port_security_sticky_learning`  | bool |                                         | [ ]      | Enable sticky MAC learning (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                                                   |
| `port_security_macs`             | list |                                         | [ ]      | List of allowed MAC addresses (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                                                |
| `port_security_sticky_macs`      | dict |                                         | [ ]      | Configure the sticky MAC addresses for the interface (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                         |
| `port_security_violation_action` | str  | [`notify`, `shutdown`]/`notify`         | [ ]      | Action to perform  when a violation is detected (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                              |
| `port_security_recovery_time`    | int  |                                         | [ ]      | Time in seconds to wait for recovery after a violation (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                       |
| `state`                          | str  | [`create`, `delete`, `update`]/`create` | [ ]      | Create, Update, or Delete Layer2 Interface                                                                                                                                                                                                                                                                |

### `interface_qos_schedule_profile` dictionary parameters:

| Parameters | Type | Choices/Defaults | Required | Comments                        |
|:-----------|:-----|:-----------------|:--------:|:--------------------------------|
| `qos`      | str  |                  | [x]      | Name of a QoS Schedule Profile. |

### `interface_qos_rate` dictionary parameters:

| Parameters        | Type | Choices/Defaults | Required | Comments                        |
|:------------------|:-----|:----------------:|:--------:|:--------------------------------|
| `unknown-unicast` | str  |                  | [ ]      | Unknow Unicast type of traffic. |
| `broadcast`       | str  |                  | [ ]      | Broadcast type of traffic.      |
| `multicast`       | str  |                  | [ ]      | Multicast type of traffic.      |

See an example [here](#interface-qos-rate-example)

### `port_security_sticky_macs` dictionary:

Dictionary where each key is a string (MAC Address name), and value is a string
(MAC Address).

See an example [here](#allow-mac-addresses-to-a-port)

## Examples

Below you can find task examples of this module's implementation:

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
    vlan_trunks:
      - '200'
      - '300'

- name: >
    Configure Interface 1/1/1 - vlan trunk allowed 200,300 and vlan trunk
    native 200.
  aoscx_l2_interface:
    interface: 1/1/3
    vlan_mode: trunk
    vlan_trunks:
      - '200'
      - '300'
    native_vlan_id: '200'

- name: Configure Interface 1/1/4 - vlan access 200
  aoscx_l2_interface:
    interface: 1/1/4
    vlan_mode: access
    vlan_access: '200'

- name: >
    Configure Interface 1/1/5 - vlan trunk allowed all, vlan trunk native 200
    tag.
  aoscx_l2_interface:
    interface: 1/1/5
    vlan_mode: trunk
    trunk_allowed_all: True
    native_vlan_id: '200'
    native_vlan_tag: True

- name: >
    Configure Interface 1/1/6 - vlan trunk allowed all, vlan trunk native 200.
  aoscx_l2_interface:
    interface: 1/1/6
    vlan_mode: trunk
    trunk_allowed_all: True
    native_vlan_id: '200'

- name: >
    Configure Interface 1/1/2 - enable full duplex at 1000 Mbit/s.
    IMPORTANT: The Interface must be enabled first.
  aoscx_l2_interface:
    interface: 1/1/2
    duplex: full
    speeds:
      - '1000'

- name: >
    Configure Interface 1/1/3 - enable port security for a total of 10 MAC
    addresses with sticky MAC learning, and two user set MAC addresses.
  aoscx_l2_interface:
    interface: 1/1/3
    port_security_enable: true
    port_security_client_limit: 10
    port_security_sticky_learning: true
    port_security_macs:
      - 11:22:33:44:55:66
      - aa:bb:cc:dd:ee:ff
```

### Interface QoS rate example:

The following example shows how to configure an Interface's QoS broadcast,
multicast, and unknown-unicast traffic rates.

```YAML
- name: Set the interface QoS rate limits
  aoscx_l2_interface:
    interface: 1/1/2
    interface_qos_rate:
      broadcast: 200pps
      multicast: 100kbps
      unknown-unicast: 150pps
```

### Allow Mac addresses to a port

The following example shows how to configure an instrusion action to disable
the interface if it sees a MAC address that is not on the allowed list.

```YAML
- name: >
    Configure Interface 1/1/13 sticky macs
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_sticky_macs:
      'mac1': 'aa:bb:cc:dd:ee:ff'
      'mac2': 'ab:cd:ef:12:34:56'
    port_security_violation_action: 'shutdown'
    port_security_recovery_time: 60
```
