# module: aoscx_vsx

VSX module for Ansible.

Version added: 2.8

 - [Synopsis](#Synpsis)
 - [Parameters](#Parameters)
 - [Examples](#Examples)

# Synopsis

VSX is a link aggregation technique, where two or more links across two
switches are aggregated together to form a LAG which will act as a single
logical interface. The IEEE standard 802.3ad, is limited to aggregating links
on a single switch or device. The multi chassis link aggregation (VSX) feature
uses a new proprietary technology to overcome this limitation and supports
link aggregation for the links spanning across multiple switches in the same
VRF. The two switches are connected through an inter switch link (ISL). VSX
provides node-level redundancy in a network when one of the switches fails.
The downstream device is configured as a 802.3ad LAG interface. Though the LAG
is connected to two separate devices they are seen as a single device. The
downstream devices can be any device that supports 802.3ad. In VSX, one device
acts as primary and the other device acts as secondary. If config-sync is
enabled, the configuration on primary device will be synced to secondary.

# Parameters

| Parameter                       | Type       | Choices                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Defaults  | Required | Comments                                                                          |
|---------------------------------|:-----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------|:---------|:----------------------------------------------------------------------------------|
| `config_sync_disable`           | bool       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Whether to disable VSX synchronization                                            |
| `config_sync_features`          | list       | [`aaa`,`acl-log-timer`,`arp-security`,`bfd-global`,`bgp`,`control-plane-acls`,`copp-policy`,`dhcp-server`,`dns`,`dhcp-relay`,`dhcp-snooping`,`hardware-high-capacity-tcam`,`evpn`,`icmp-tcp`,`gbp`,`lldp`,`loop-protect-global`,`keychain`,`mac-lockout`,`mclag-interfaces`,`mgmd-global`,`macsec`,`neighbor`,`ospf`,`qos-global`,`nd-snooping`,`route-map`,`sflow-global`,`snmp`,`ssh`,`static-routes`,`stp-global`,`rip`,`time`,`vsx-global`,`udp-forwarder`,`vrrp`] |           | [ ]      | Feature configurations to be globally synchronized between VSX peers.             |
| `device_role`                   | String     | [`primary`, `secondary`]                                                                                                                                                                                                                                                                                                                                                                                                                                               |           | [ ]      |                                                                                   |
| `isl_port`                      | String     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Port for Inter-Switch Link                                                        |
| `isl_timers`                    | Dictionary |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | See [isl_timers](#isl_timers-dictionary) below.                                   |
| `keepalive_peer_ip`             | String     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Must be together with keepalive_src_ip                                            |
| `keepalive_src_ip`              | String     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Must be together with keepalive_peer_ip                                           |
| `keepalive_timers`              | Dictionary |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | See [keepalive_timers](#keepalive_timers-dictionary) below.                                   |
| `keepalive_udp_port`            | Int        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | `7678`    | [ ]      |                                                                                   |
| `keepalive_vrf`                 | String     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | `default` | [ ]      |                                                                                   |
| `linkup_delay_timer`            | Int        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Seconds before ISL is considered fully established and VSX peers are synchronized |
| `software_update_abort_request` | Int        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Number of times a software update was requested to be aborted                     |
| `software_update_schedule_time` | Int        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Seconds from epoch when update should be performed                                |
| `software_update_url`           | String     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Only TFTP or USB are supported                                                    |
| `software_update_vrf`           | String     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | `default` | [ ]      |                                                                                   |
| `split_recovery_disable`        | bool       |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Whether to disable split brain recovery                                           |
| `state`                         | String     | [`create`, `delete`, `update`]                                                                                                                                                                                                                                                                                                                                                                                                                                         | `create`  | [ ]      | The action to be taken with the current VSX                                       |
| `system_mac`                    | String     |                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |           | [ ]      | Must be in xx:xx:xx:xx:xx:xx format                                               |


### isl_timers dictionary

| Parameter              | Type | Choices | Defaults | Required | Comments                             |
|------------------------|:-----|:--------|:---------|:---------|:-------------------------------------|
| `timeout`              | Int  |         |          | [ ]      | Seconds to wait for hellos from peer |
| `peer_detect_interval` | Int  |         |          | [ ]      | Seconds to wait for ISL after reboot |
| `hold_time`            | Int  |         |          | [ ]      | Seconds to wait for ISL port-flap    |
| `hello_interval`       | Int  |         |          | [ ]      | Seconds to wait for ISLP             |

### keepalive_timers dictionary

| Parameter        | Type | Choices | Defaults | Required | Comments                                       |
|------------------|:-----|:--------|:---------|:---------|:-----------------------------------------------|
| `hello_interval` | Int  |         |          | [ ]      | Keepalive hello interval in seconds            |
| `dead_interval`  | Int  |         |          | [ ]      | Seconds to wait for keepalive packet from peer |

## NOTE
If you require to remove configuration, you'll need to delete the VSX configuration, and recreate it without the attributes you wish to remove.  That is, if you for example require to remove only the `isl_timers` to make the switch use the factory defaults, you need to delete the VSX configuration and then re-create it without the `isl_timers`

# Examples

```YAML
- name: Delete VSX configuration
  aoscx_vsx:
    state: delete
```

```YAML
- name: Update VSX configuration for primary device, set ISL port
  aoscx_vsx:
    device_role: primary
    isl_port: 1/1/1
    state: update
```

```YAML
- name: >
    Create simple VSX configuration with lag as ISL port for secondary device
  aoscx_vsx:
    device_role: primary
    isl_port: lag1
    keepalive_vrf: red
    state: create
```

```YAML
- name: >
    Create detailed VSX configuration for primary device, use USB for software
    update, instead of TFTP server
  aoscx_vsx:
    config_sync_disable: false
    config_sync_features:
      - aaa
      - bgp
      - dns
      - vrrp
    device_role: primary
    isl_port: 1/1/8
    isl_timers:
      timeout: 20
      peer_detect_interval: 100
      hold_time: 3
      hello_interval: 5
    keepalive_peer_ip: 10.0.0.2
    keepalive_src_ip:  10.0.0.1
    keepalive_timers:
      hello_interval: 5
      dead_interval: 20
    keepalive_udp_port: 7678
    keepalive_vrf: default
    linkup_delay_timer: 90
    software_update_abort_request: 7
    software_update_schedule_time: 1635356306
    software_update_url: usb://boot_bank=primary
    software_update_vrf: default
    split_recovery_disable: false
    system_mac: 00:FF:11:EE:22:DD
```
