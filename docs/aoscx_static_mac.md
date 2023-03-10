# module: aoscx_static_mac

Static MAC module for Ansible.

Version added: 4.1.0

 - [Synopsis](#synopsis)
 - [Parameters](#parameters)
 - [Examples](#examples)

# Synopsis

This module allows configuration management on Static MACs for AOSCX devices.

# Parameters

| Parameter  | Type | Choices/Defaults                          | Required | Comments                                                  |
|:-----------|:-----|:------------------------------------------|:--------:|:----------------------------------------------------------|
| `vlan`     | int  |                                           | [x]      | Vlan to which the Static MAC belongs.                     |
| `mac_addr` | str  |                                           | [x]      | Hexadecimal address of the Static MAC.                    |
| `port`     | str  |                                           | [x]      | Port or Interface to which the Static MAC is attached to. |
| `state`    | str  | [`create`, `update`, `delete`] / `create` | [ ]      | Create, update, or delete a Static MAC.                   |

# Examples

## Create Static MACs

```YAML
- name: Create Static MAC
  aoscx_static_mac:
    vlan: 23
    mac_addr: fa:23:13:a8:f2:11
    port: 1/1/24

- name: Create Static MAC
  aoscx_static_mac:
    vlan: 15
    mac_addr: fa:23:bb.a8:f2:11
    port: 1/1/21
```

## Update port of Static MAC

```YAML
- name: Create Static MAC
  aoscx_static_mac:
    vlan: 4
    mac_addr: aa:bb:cc:dd:ee:f4
    port: 1/1/24

- name: Update port of Static MAC
  aoscx_static_mac:
    vlan: 4
    mac_addr: aa:bb:cc:dd:ee:f4
    port: 1/1/2
    state: update
```

## Remove Static MACs

```YAML
- name: Delete Static MAC
  aoscx_static_mac:
    vlan: 2
    mac_addr: aa:b3:13:a8:f2:11
    port: 1/1/24
    state: delete
```
