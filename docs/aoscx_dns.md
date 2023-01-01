# Domain Name System

Domain Name System (DNS) module for Ansible

Version added: 4.1.0

 - [Synopsis](#synopsis)
 - [Parameters](#parameters)
 - [Examples](#examples)

## Synopsis

This module allows configuration management on DNS for AOSCX devices.

## Parameters

| Parameter                 | Type | Choices/Defaults                          | Required | Comments                                                                                                                                       |
|:--------------------------|:-----|:------------------------------------------|:--------:|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| `mgmt_nameservers`        | dict |                                           | [ ]      | Primary and secondary nameservers on mgmt interface. The key of the dictionary is primary or secondary and value is the respective IP address. |
| `domain_name`             | str  |                                           | [ ]      | Domain name used for name resolution by the DNS client, if `domain_list` is not configured.                                                    |
| `domain_list`             | dict |                                           | [ ]      | Domain list names to be used for address resolution, keyed by the resolution priority order.                                                   |
| `name_servers`            | dict |                                           | [ ]      | Name servers to be used for address resolution, keyed by the resolution priority order.                                                        |
| `vrf`                     | str  |                                           | [x]      | VRF name where DNS configuration is added.                                                                                                     |
| `host_v4_address_mapping` | dict |                                           | [ ]      | List of static host address configurations and the IPv4 address associated with them.                                                          |
| `host_v6_address_mapping` | dict |                                           | [ ]      | List of static host address configurations and the IPv6 address associated with them.                                                          |
| `state`                   | str  | [`create`, `update`, `delete`] / `create` | [ ]      | Create, update, or delete a DNS.                                                                                                               |

## Examples

### Create DNS

Before Device Configuration
```
vrf green
ntp server pool.ntp.org minpoll 4 maxpoll 4 iburst
ntp enable
!
!
!
!
!
!
ssh server vrf mgmt
vlan 1
interface mgmt
    no shutdown
    ip static 172.25.0.2/24
```

Playbook:
```YAML
- name: DNS configuration creation
  aoscx_dns:
    mgmt_nameservers:
     "Primary": "10.10.2.10"
     "Secondary": "10.10.2.10"
    domain_name: "hpe.com"
    domain_list:
      0: "hp.com"
      1: "aru.com"
      2: "sea.com"
    name_servers:
      0: "4.4.4.8"
      1: "4.4.4.10"
    host_v4_address_mapping:
      "host1": "5.5.44.5"
      "host2": "2.2.44.2"
    vrf: "green"
```

After Device Configuration:
```
vrf green
ntp server pool.ntp.org minpoll 4 maxpoll 4 iburst
ntp enable
!
!
!
!
!
!
ssh server vrf mgmt
vlan 1
interface mgmt
    no shutdown
    ip static 172.25.0.2/24
    nameserver 10.10.2.10
ip dns domain-name hpe.com vrf green
ip dns domain-list hp.com vrf green
ip dns domain-list aru.com vrf green
ip dns domain-list sea.com vrf green
ip dns server-address 4.4.4.8 vrf green
ip dns server-address 4.4.4.10 vrf green
ip dns host host1 5.5.44.5 vrf green
ip dns host host2 2.2.44.2 vrf green
```

### Update DNS

Before Device Configuration:
```
vrf green
ntp server pool.ntp.org minpoll 4 maxpoll 4 iburst
ntp enable
!
!
!
!
!
!
ssh server vrf mgmt
vlan 1
interface mgmt
    no shutdown
    ip static 172.25.0.2/24
    nameserver 10.10.2.10
ip dns domain-name hpe.com vrf green
ip dns domain-list hp.com vrf green
ip dns domain-list aru.com vrf green
ip dns domain-list sea.com vrf green
ip dns server-address 4.4.4.8 vrf green
ip dns server-address 4.4.4.10 vrf green
ip dns host host1 5.5.44.5 vrf green
ip dns host host2 2.2.44.2 vrf green
```

Playbook:
```YAML
- name: DNS configuration update
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    domain_name: "hpe.com"
    domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: update
```

After Device Configuration:
```
vrf green
ntp server pool.ntp.org minpoll 4 maxpoll 4 iburst
ntp enable
!
!
!
!
!
!
ssh server vrf mgmt
vlan 1
interface mgmt
    no shutdown
    ip static 172.25.0.2/24
    nameserver 10.10.2.15
ip dns domain-name hpe.com vrf green
ip dns domain-list hpe.com vrf green
ip dns domain-list aruba.com vrf green
ip dns domain-list seach.com vrf green
ip dns server-address 4.4.4.10 vrf green
ip dns server-address 4.4.4.12 vrf green
ip dns host host1 5.5.5.5 vrf green
ip dns host host2 2.2.45.2 vrf green
```

### Delete DNS

Before Device Configuration:
```
vrf green
ntp server pool.ntp.org minpoll 4 maxpoll 4 iburst
ntp enable
!
!
!
!
!
!
ssh server vrf mgmt
vlan 1
interface mgmt
    no shutdown
    ip static 172.25.0.2/24
    nameserver 10.10.2.15
ip dns domain-name hpe.com vrf green
ip dns domain-list hpe.com vrf green
ip dns domain-list aruba.com vrf green
ip dns domain-list seach.com vrf green
ip dns server-address 4.4.4.10 vrf green
ip dns server-address 4.4.4.12 vrf green
ip dns host host1 5.5.5.5 vrf green
ip dns host host2 2.2.45.2 vrf green
```

Playbook:
```YAML
- name: DNS configuration deletion
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    domain_name: "hp.com"
    domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: delete
```

After Device Configuration:
```
vrf green
ntp server pool.ntp.org minpoll 4 maxpoll 4 iburst
ntp enable
!
!
!
!
!
!
ssh server vrf mgmt
vlan 1
interface mgmt
    no shutdown
    ip static 172.25.0.2/24
```
