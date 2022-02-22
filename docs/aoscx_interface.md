# module: aoscx_interface

Interface module for Ansible.

Version added: 4.0.0

 - [Synopsis](#Synpsis)
 - [Parameters](#Parameters)
 - [Examples](#Examples)

# Synopsis

This module manages the interface attributes of Aruba AOSCX network devices.

# Parameters

| Parameter        | Type | Choices/Defaults                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Required | Comments                                                                                                                   |
|:-----------------|:-----|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|:---------------------------------------------------------------------------------------------------------------------------|
| `name`           | str  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [x]      | Name of the interface. Should be in the format chassis/slot/port e.g. 1/2/3.                                               |
| `enabled`        | bool |                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [ ]      | Administrative state of the interface. Use true to administratively enable it.                                             |
| `description`    | str  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [ ]      | Description of the interface.                                                                                              |
| `duplex`         | str  | [`full`, `half`]                                                                                                                                                                                                                                                                                                                                                                                                                                                           | [ ]      | Configure the interface for full duplex or half duplex. If this value is specified, `speeds` must also be specified.       |
| `speeds`         | list |                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [ ]      | Configure the speeds of the interface in megabits per second. If this value is specified, `duplex` must also be specified. |
| `qos`            | str  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [ ]      | Name of existing QoS configuration to apply to the interface.                                                              |
| `no_qos`         | bool |                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [ ]      | Flag to remove the existing Qos of the interface. Use True to remove it.                                                   |
| `queue_profile`  | str  |                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | [ ]      | Name of queue profile to apply to interface.                                                                               |
| `qos_trust_mode` | str  | [`cos`, `dscp`, `name`, `global`]                                                                                                                                                                                                                                                                                                                                                                                                                                          | [ ]      | Specifies the interface QoS Trust Mode. 'global' configures the interface to use the global configuration instead.         |
| `state`          | str  | [`create`, `delete`, `update`]/`create`                                                                                                                                                                                                                                                                                                                                                                                                                                    | [ ]      | The action to be taken with the current Interface.                                                                         |
| `vsx_sync`       | list | [`acl`, `irdp`, `qos`, `rate_limits`, `vlan`, `vsx_virtual`, `virtual_gw_l3_src_mac_enable`, `policy`, `threshold_profile`, `macsec_policy`, `mka_policy`, `portfilter`, `client_ip_track_configuration`, `mgmd_acl`, `mgmd_enable`, `mgmd_robustness`, `mgmd_querier_max_response_time`, `mgmd_mld_version`, `mgmd_querier_interval`, `mgmd_last_member_query_interval`, `mgmd_querier_enable`, `mgmd_mld_static_groups`, `mgmd_igmp_static_groups`, `mgmd_igmp_version`] | [ ]      | Controls which attributes should be synchonized between VSX peers.                                                         |


# Examples

## Enable full duplex at 1000 Mbits/s

Ansible version:

```YAML
- name: Configure Interface 1/1/2 - enable full duplex at 1000 Mbit/s
  aoscx_interface:
    name: 1/1/2
    duplex: full
    speeds:
      - '1000'
    enabled: true
```

CLI version:

```
interface 1/1/2
speed 1000-full
```

## Administratively disable an interface

Ansible version:

```YAML
- name: Administratively disable interface 1/1/2
  aoscx_interface:
    name: 1/1/2
    enabled: false
```

CLI version:

```
interface 1/1/2
shutdown
```

## Configure a QoS trust mode

It is possible to set an specific trust mode for a particular interface, or to
configure an interface to use the global default trust mode of the device.

```YAML
- name: Set a QoS trust mode for interface 1/1/2
  aoscx_interface:
    name: 1/1/2
    qos_trust_mode: cos

- name: Set interface 1/1/3 to use global trust mode
  aoscx_interface:
    name: 1/1/3
    qos_trust_mode: global
```

## Configure a Queue Profile trust mode

```YAML
- name: Set a Queue Profile for interface 1/1/2
  aoscx_interface:
    name: 1/1/2
    queue_profile: STRICT-PROFILE

- name: Set interface 1/1/3 to use global Queue Profile
  aoscx_interface:
    name: 1/1/3
    use_global_queue_profile: true
```

## Associate QoS Schedule Profiles to an interface

To assign a Schedule Profile to an interface, you have to specify the name, to
remove it simply use the `no_qos` option.

```YAML
- name: Configure Schedule Profile on an interface
  aoscx_interface:
    name: 1/1/2
    qos: STRICT-PROFILE

- name: Remove a Schedule Profile from an interface
  aoscx_interface:
    name: 1/1/3
    no_qos: true
```

## Set QoS rate for an interface

```YAML
- name: Set the QoS rate to the 1/1/17 Interface
  aoscx_interface:
    name: 1/1/17
    qos_rate:
      broadcast: 200pps
      unknown-unicast: 100kbps
      multicast: 200pps
```

## Enable vsx-sync for interface 1/1/2

```YAML
- name: Configure Interface 1/1/2 - enable vsx-sync features
  aoscx_interface:
    name: 1/1/2
    duplex: full
    speeds:
      - '1000'
    vsx_sync:
      - acl
      - irdp
      - qos
      - rate_limits
      - vlan
      - vsx_virtual
```
