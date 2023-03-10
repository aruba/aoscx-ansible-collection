# L2 Interface

L2 Interface module for Ansible.

Version added: 2.8

 - [Synopsis](#Synopsis)
 - [Parameters](#Parameters)
 - [Examples](#Examples)

## Synopsis

This modules provides configuration management of Layer2 Interfaces on AOS-CX
devices, including Port Security features. For platform 8360, Port Security is
supported from REST v10.09 upwards.


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
| `port_security_enable`           | bool |                                         | [ ]      | Enable port security in this interface (aoscx connection)                                                                                                                                                                                                                                                 |
| `port_security_client_limit`     | int  |                                         | [ ]      | Maximum amount of MACs allowed in the interface (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                              |
| `port_security_sticky_learning`  | bool |                                         | [ ]      | Enable sticky MAC learning (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                                                   |
| `port_security_macs`             | list |                                         | [ ]      | List of allowed MAC addresses (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                     |
| `port_security_sticky_macs`      | list |                                         | [ ]      | Configure the sticky MAC addresses for the interface (aoscx connection). Only valid when port_security is enabled                                                                                                                                                              |
| `port_security_violation_action` | str  | [`notify`, `shutdown`]                  | [ ]      | Action to perform  when a violation is detected (aoscx connection). Only valid when port_security is enabled                                                                                                                                                                                              |
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

### `port_security_sticky_macs` list's dictionary elements:

| Parameters        | Type | Choices/Defaults | Required | Comments                  |
|:------------------|:-----|:----------------:|:--------:|:--------------------------|
| `mac`             | str  |                  | [x]      | MAC Address.              |
| `vlans`           | list |                  | [x]      | List of integer VLAN IDs. |

See an example [here](#allow-mac-addresses-to-a-port)

## Examples

Below you can find task examples of this module's implementation:

### Allow VLAN access

Before Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/4 - vlan access 200
  aoscx_l2_interface:
    interface: 1/1/4
    vlan_mode: access
    vlan_access: 200
```

After Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 200
```

### Allow VLAN trunk

Before Device Configuration:
```
interface 1/1/1
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/1 - vlan trunk allowed 200
  aoscx_l2_interface:
    interface: 1/1/1
    vlan_mode: trunk
    vlan_trunks: 200
```

After Device Configuration:
```
interface 1/1/1
    no shutdown
    vlan trunk native 1
    vlan trunk allowed 200
```

Before Device Configuration:
```
interface 1/1/1
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/1 - vlan trunk allowed 200,300
  aoscx_l2_interface:
    interface: 1/1/1
    vlan_mode: trunk
    vlan_trunks:
      - 200
      - 300
```

After Device Configuration:
```
interface 1/1/1
    no shutdown
    vlan trunk native 1
    vlan trunk allowed 200,300
```

Before Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: >
    Configure Interface 1/1/3 - vlan trunk allowed 200,300 and vlan trunk
    native 200.
  aoscx_l2_interface:
    interface: 1/1/3
    vlan_mode: trunk
    vlan_trunks:
      - 200
      - 300
    native_vlan_id: 200
```

After Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan trunk native 200
    vlan trunk allowed 200,300
```

Before Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/3 - vlan trunk allowed all
  aoscx_l2_interface:
    interface: 1/1/3
    vlan_mode: trunk
    trunk_allowed_all: True
```

After Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan trunk native 1
    vlan trunk allowed all
```

Before Device Configuration:
```
interface 1/1/5
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: >
    Configure Interface 1/1/5 - vlan trunk allowed all, vlan trunk native 200
    tag.
  aoscx_l2_interface:
    interface: 1/1/5
    vlan_mode: trunk
    trunk_allowed_all: True
    native_vlan_id: 200
    native_vlan_tag: True
```

After Device Configuration:
```
interface 1/1/5
    no shutdown
    vlan trunk native 200 tag
    vlan trunk allowed all
```

Before Device Configuration:
```
interface 1/1/6
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: >
    Configure Interface 1/1/6 - vlan trunk allowed all, vlan trunk native 200.
  aoscx_l2_interface:
    interface: 1/1/6
    vlan_mode: trunk
    trunk_allowed_all: True
    native_vlan_id: 200
```

After Device Configuration:
```
interface 1/1/6
    no shutdown
    vlan trunk native 200
    vlan trunk allowed all
```

### Enable Port Security

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - enable port security
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

### Set client limit

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set client limit
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_client_limit: 2
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        client-limit 2
```

### Enable sticky learning

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - enable sticky learning
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_sticky_learning: true
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        sticky-learn enable
```

### Set allowed MAC address

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set allowed MAC address
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_macs:
      - 12:34:56:78:90:00
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        mac-address 12:34:56:78:90:00
```

### Set sticky MAC address

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set sticky mac
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_sticky_macs:
      - mac: 12:34:56:78:90:00
        vlans:
          - 1
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        sticky-learn mac-address 12:34:56:78:90:00 vlan 1
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set sticky mac
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_sticky_macs:
      - mac: 12:34:56:78:90:00
        vlans:
          - 1
          - 2
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        sticky-learn mac-address 12:34:56:78:90:00 vlan 1
        sticky-learn mac-address 12:34:56:78:90:00 vlan 2
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set sticky mac
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_sticky_macs:
      - mac: 12:34:56:78:90:00
        vlans: []
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        sticky-learn mac-address 12:34:56:78:90:00 vlan 1
```

### Set violation action

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access security violation action shutdown
    port-access port-security
        enable
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set intrusion action
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_violation_action: notify
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set intrusion action
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_violation_action: shutdown
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access security violation action shutdown
    port-access port-security
        enable
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set intrusion action with recovery time
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_recovery_time: 60
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access security violation action shutdown recovery-timer 60
    port-access port-security
        enable
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - set intrusion action with recovery time
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_violation_action: shutdown
    port_security_recovery_time: 60
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access security violation action shutdown
    port-access security violation action shutdown recovery-timer 60
    port-access port-security
        enable
```

### Delete configuration of Port Security

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        client-limit 2
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - delete configuration of client limit
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: true
    port_security_client_limit: 2
    state: delete
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
        sticky-learn enable
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - delete configuration of sticky learning
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_sticky_learning: true
    state: delete
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access security violation action shutdown
    port-access port-security
        enable
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - delete intrusion action
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_violation_action: shutdown
    state: delete
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access security violation action shutdown recovery-timer 60
    port-access port-security
        enable
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - delete recovery time
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_recovery_time: 60
    state: delete
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port_security_violation_action: shutdown
    port-access security violation action shutdown recovery-timer 60
    port-access port-security
        enable
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - delete violation action and recovery time
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_violation_action: shutdown
    port_security_recovery_time: 60
    state: delete
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

### Remove allowed MAC address

Before Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan access 1
    port-access port-security
        enable
        mac-address 12:34:56:78:90:00
        mac-address 12:34:56:78:90:01
```

Playbook:
```YAML
- name: >
    Configure Interface 1/1/3 -  remove allowed MAC address 12:34:56:78:90:00
  aoscx_l2_interface:
    interface: 1/1/3
    port_security_enable: true
    port_security_macs:
      - 12:34:56:78:90:00
    state: delete
```

After Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan access 1
    port-access port-security
        enable
        mac-address 12:34:56:78:90:01
```

### Remove allowed sticky MAC address

Before Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan trunk native 1
    vlan trunk allowed all
    port-access port-security
        enable
        sticky-learn mac-address 12:34:56:78:90:00 vlan 1
        sticky-learn mac-address 12:34:56:78:90:00 vlan 2
```

Playbook:
```YAML
- name: Configure Interface 1/1/3 - set sticky mac
  aoscx_l2_interface:
    interface: 1/1/13
    port_security_enable: true
    port_security_sticky_macs:
      - mac: 12:34:56:78:90:00
        vlans:
          - 1
    state: delete
```

After Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan trunk native 1
    vlan trunk allowed all
    port-access port-security
        enable
        sticky-learn mac-address 12:34:56:78:90:00 vlan 2
```

### Disable Port Security

Before Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
    port-access port-security
        enable
```

Playbook:
```YAML
- name: Configure Interface 1/1/13 - disable port security
  aoscx_l2_interface:
    name: 1/1/13
    port_security_enable: false
```

After Device Configuration:
```
interface 1/1/13
    no shutdown
    vlan access 1
```

### Interface QoS rate example:

The following example shows how to configure an Interface's QoS broadcast,
multicast, and unknown-unicast traffic rates.

Before Device Configuration:
```
interface 1/1/2
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Set the interface QoS rate limits
  aoscx_l2_interface:
    interface: 1/1/2
    interface_qos_rate:
      broadcast: 200pps
      multicast: 100kbps
      unknown-unicast: 150pps
```

After Device Configuration:
```
interface 1/1/2
    no shutdown
    vlan access 1
```

### Delete Interface

Before Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan trunk native 200
    vlan trunk allowed all
```

Playbook:
```YAML
- name: Delete Interface 1/1/3
  aoscx_l2_interface:
    interface: 1/1/3
    state: delete
```

After Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan access 1
```
