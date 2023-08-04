# module: aoscx_lag_interface

LAG Interface module for Ansible.

Version added: 4.1.0

- [Synopsis](#Synopsis)
- [Parameters](#Parameters)
- [Examples](#Examples)

# Synopsis

This modules provides application management of LAG Interfaces on AOS-CX
devices.

# Parameters

| Parameter              | Type | [Choices]/Defaults                                    | Required | Comments                                                                                                                                                                                                                                                                                                        |
|:-----------------------|:-----|:------------------------------------------------------|:--------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `state`                | str  | [`create`, `delete`, `update`] / `create`             | [ ]      | The action to be taken with the current LAG Interface. `delete` removes the interfaces listed, if not, the LAG is deleted. After that a physical interface is removed from LAG, interface will be shutdown.                                                                                                                                                                                                                                                                             |
| `name`                 | str  |                                                       | [x]      | Name of the LAG Interface.                                                                                                                                                                                                                                                                                      |
| `interfaces`           | list |                                                       | [ ]      | List of interface names to make part of the LAG Interface. Each interface added to a LAG interface will inherit the LAG manager state of the LAG, wether it is `up` or `down`.                                                                                                                                  |
| `lacp_mode`            | str  | [`active`, `passive`, `disabled`] / `disabled`        | [ ]      | Configure LACP mode, `active` ports are allowed to initiate LACP negotiations. passive ports are allowed to participate in LACP negotiations initiated by a remote switch, but not initiate such negotiations. If LACP is enabled on a port whose partner switch does not support LACP, the bond gets disabled. |
| `lacp_rate`            | str  | [`slow`, `fast`]                                      |          | Configures Link Aggregation Control Protocol (LACP) rate on this interface, by default LACP rate is `slow` and LAPCDUs will be sent every 30 seconds; if LACP rate is `fast` LACPDUs will be sent every second.This value can not be set if lacp mode is `disabled`.                                            |
| `multi_chassis`        | bool |                                                       | [ ]      | Option to specify whether the LAG is a MCLAG. By default, sets `lacp_mode` to active, unless `static_multi_chassis` is enabled.                                                                                                                                                                                 |
| `lacp_fallback`        | bool |                                                       | [ ]      | Enable LACP fallback mode, specified only for multi-chassis LAGs.                                                                                                                                                                                                                                               |
| `static_multi_chassis` | bool |                                                       | [ ]      | Whether the MCLAG is static. Ignored if `multi_chassis` is not specified.                                                                                                                                                                                                                                       |

---

## Examples

```YAML
- name: Create LAG Interface 1.
  aoscx_lag_interface:
    name: lag1
```

```YAML
- name: Set 6 interfaces to LAG Interface 1.
  aoscx_lag_interface:
    state: update
    name: lag1
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3
      - 1/1/4
      - 1/1/5
      - 1/1/6
```

```YAML
- name: Configure LAG1 as dynamic.
  aoscx_lag_interface:
    state: update
    name: lag1
    lacp_mode: passive
    lacp_rate: fast
```

```YAML
- name: Delete 3 interfaces from LAG Interface 1.
  aoscx_lag_interface:
    state: delete
    name: lag1
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3
```

```YAML
- name: Create MCLAG Interface 64 with  3 interfaces.
  aoscx_lag_interface:
    state: create
    name: lag64
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3
    multi_chassis: true
```

```YAML
- name: Create Static MCLAG Interface 32 with  3 interfaces.
  aoscx_lag_interface:
    state: create
    name: lag32
    interfaces:
      - 1/1/1
      - 1/1/2
      - 1/1/3
    multi_chassis: true
    static_multi_chassis: true
```

```YAML
- name: Create MCLAG with LACP fallback mode set.
  aoscx_lag_interface:
    state: create
    name: lag256
    multi_chassis: true
    lacp_fallback: true
```

```YAML
- name: Update MCLAG, unset LACP fallback mode.
  aoscx_lag_interface:
    state: create
    name: lag256
    multi_chassis: true
    lacp_fallback: false
```

```YAML
- name: Create static MCLAG with LACP fallback mode.
  aoscx_lag_interface:
    state: create
    name: lag2
    multi_chassis: true
    static_multi_chassis: true
    lacp_fallback: true
```

```YAML
- name: Update static MCLAG, unset LACP fallback mode.
  aoscx_lag_interface:
    state: update
    name: lag256
    multi_chassis: true
    static_multi_chassis: true
    lacp_fallback: false
```

```YAML
- name: Delete LAG Interface 128.
  aoscx_lag_interface:
    state: delete
    name: lag128
```
