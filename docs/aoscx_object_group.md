# Object Group module for Ansible.

Version added: 4.4.0

 - [Synopsis](#Synpsis)
 - [Modules](#Modules)
 - [Tables](#Tables)
 - [Examples](#Examples)

## Synopsis

An object group is a configuration shortcut in which a user can define a 
reusable group of addresses or L4 ports that can then be applied to
ACLs.  The list of addresses or L4 ports will then be expanded automatically
in the ACE(s) to which it is assigned.
An object group specifying IPv4 or IPv6 addresses is referred to as an
address group. An object group specifying Layer 4 ports is referred to as a 
port group. Object groups are comprised of one or more entries.

## Modules:

- [aoscx_object_group](#aoscx_object_group)

---
## aoscx_classifier

### Parameters

| Parameter       | Type | Choices/Defaults                        | Required | Comments                                        |
|:----------------|:-----|:----------------------------------------|:--------:|:------------------------------------------------|
| `name`          | str  |                                         | [x]      | Name of the Obhect Group            |
| `type`          | str  | [`ipv4`, `ipv6`, `l4port`]              | [x]      | Type of the Object Group                                                                       
| `address`       | dict |                                         | [ ]      | Entries of the Object Group of type ipv4 or ipv6, the format is {index: "Ipv4/6 Address", ...}                                                                           |
| `ports`         | dict |                                         | [ ]      | Entries of the Object Group of type l4port, the format is {index: [port\_number, "[port\_max]-[port\_min]", "port\_name"], ...}, por for name see [ports](#ports_table)  |
| `state`         | str  | [`create`, `delete`, `update`]/`create` | [ ]      | The action to be taken with the current Object Group    |

## Tables

### ports_table

Valid L4 port names that can be passed as parameter; a numeric value can be
used even if the name is included in this table.

#### Valid L4 Port names.

| Valid Name     | Numeric Value  |
|:---------------|:--------------:|
| `ftp-data`     | 20             |
| `ftp`          | 21             |
| `ssh`          | 22             |
| `telnet`       | 23             |
| `smtp`         | 25             |
| `tacacs`       | 49             |
| `dns`          | 53             |
| `dhcp-server`  | 67             |
| `dhcp-client`  | 68             |
| `tftp`         | 69             |
| `http`         | 80             |
| `https`        | 443            |
| `pop3`         | 110            |
| `nntp`         | 119            |
| `ntp`          | 123            |
| `dce-rpc`      | 135            |
| `netbios-ns`   | 137            |
| `netbios-dgm`  | 138            |
| `netbios-ssn`  | 139            |
| `snmp`         | 161            |
| `snmp-trap`    | 162            |
| `bgp`          | 179            |
| `ldap`         | 389            |
| `microsoft-ds` | 445            |
| `isakmp`       | 500            |
| `syslog`       | 514            |
| `imap4`        | 585            |
| `radius`       | 1812           |
| `radius-acct`  | 1813           |
| `iscsi`        | 3260           |
| `rdp`          | 3389           |
| `nat-t`        | 4500           |
| `vxlan`        | 4789           |

## Examples

```YAML
- name: Email ports
  aoscx_object_group:
    name: email_ports
    type: l4port
    ports:
      1: smtp
      2: pop3
      3: imap

- name: Some range examples
  aoscx_object_group:
    name: range_examples
    type: l4port
    ports:
      1: 21-23
      2: 100-120

- name: Implementing eq, gt, lt 22
  aoscx_object_group:
    name: eq_gt_lt_22
    type: l4port
    ports:
      1: 22
      2: 23-
      3: -21

- name: Some IPv4 addresses
  aoscx_object_group:
    name: some_ips
    type: ipv4
    addresses:
      1: 192.168.5.1/24
      2: 192.168.5.2/255.255.255.0
      3: 192.168.5.3

- name: Delete an L4 entry
  aoscx_object_group:
    name: email_ports
    type: l4port
    ports:
      1:
    state: delete

- name: Delete Object Group
  aoscx_object_group:
    name: email_ports
    type: l4port
    state: delete
```
