# module: aoscx_acl

ACL module for Ansible.

Version added: 2.8

 - [Synopsis](#Synpsis)
 - [Parameters](#Parameters)
 - [Examples](#Examples)

# Synopsis

Access Control Lists (ACLs) allow a network administrator to define network
traffic addressing or other header content, and to use these rules to restrict,
alter or log the passage of traffic through the switch. Choosing the rule
criteria is called Classification, and one such rule set, or list, is called an
Access Control List.

There are three types of ACL: MAC, IPv4, and IPv6 -- which are each focused
on relevant frame/packet characteristics. ACLs can be configured to match on
almost any frame or packet header field and then take an appropriate action.

Network traffic passing through a switch can be blocked, permitted, counted, or
logged based on many different frame/packet characteristics including, but not
limited to:

 - Frame ingress VLAN ID
 - Source and/or destination Ethernet MAC, IPv4 or IPv6 address
 - Layer 2 (EtherType) and Layer3 (IP) protocol
 - Layer 4 application port(s)

An ACL can be applied to an interface or VLAN to affect/control traffic arriving
on the interface/VLAN ('in'), leaving the interface/VLAN ('out'), routed
traffic arriving on the VLAN's interface ('routed-in'), or routed traffic
leaving the VLAN's interface ('routed-out'). A given interface or VLAN supports
a single ACL application per type and direction. That is a single interface or
VLAN supports the following applications:

 - 1 MAC ACL ingress
 - 1 MAC ACL egress (platform dependent)
 - 1 IPv4 ACL ingress
 - 1 IPv4 ACL routed ingress (VLAN Interface only)
 - 1 IPv4 ACL egress
 - 1 IPv4 ACL routed egress (VLAN Interface only - platform dependent)
 - 1 IPv6 ACL ingress
 - 1 IPv6 ACL routed ingress (VLAN Interface only)
 - 1 IPv6 ACL egress (platform dependent)
 - 1 IPv6 ACL routed egress (VLAN Interface only - platform dependent)

Different ACLs of the same type can be used in opposite directions. If an ACL of
a particular type is applied in a direction that is already in use, the current
ACL will be replaced by the new ACL.

## Access control entries
An ACL contains one or more 'Access Control Entries' ('ACE') which are listed
according to priority by sequence number. A single ACE matches on one or more
characteristics of the particular traffic type and has a configured action to
either discard or allow the packet to continue through the switch. This occurs
by, beginning with the ACE with the lowest sequence number, comparing the
incoming or outgoing frame to its particular match characteristics and if there
is a match, the ACE's action - either permit or deny - is taken. If there is no
match, the match characteristics of the next ACE in sequence is compared to the
relevant frame/packet details and if there is a match the specified action is
taken. This process continues until a match is found, or the end of the list is
reached.

In the event that no ACEs in a given applied ACL match, the frame/packet will be
discarded. This is due to the presence of an invisible implicit deny rule at the
end of all applied ACLs whether populated or empty. This is a security feature
to ensure that any Access Controlled interface will only pass explicitly
permitted traffic. Note that due to this security feature, an ACE permitting
icmpv6 traffic must be added to the end of an IPv6 ACL to allow IPv6 neighbor
discovery packets, and an ACE permitting arp traffic must be added to the end
of a MAC ACL packet to allow address Resolution Protocol traffic.

# Parameters

| Parameter     | Type       | Choices/Defaults                        | Required | Comments                                      |
|---------------|:-----------|:----------------------------------------|:--------:|:----------------------------------------------|
| `name`        | String     |                                         | [x]      | Name of the access control list               |
| `type`        | String     | [`ipv4`, `ipv6`, `mac`, `l4port`]       | [x]      | Type of the ACL                               |
| `state`       | String     | [`create`, `delete`, `update`]/`create` | [ ]      | The action to be taken with the current ACL   |
| `acl_entries` | Dictionary |                                         | [ ]      | Explained in more detail [here](#acl_entries) |

## acl_entries

This parameter is a dictionary of dictionaries (use JSON for formatting
purposes) of the Access Control Entries (ACE) configured in the ACL. For more
information about the ACE you can refer to
[this section](#Access control entries). Each entry key should be a sequence
number, and the value the dictionary representing the ACE.

### ACE dictionary

The following is a brief explanation of the ACE dictionary used to configure
ACEs. All this information can also be reviewed online at the [Aruba
portal](https://developer.arubanetworks.com/aruba-aoscx/reference#acl_entry).


| Parameter           | Type               | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|---------------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `comment`           | String             | Comment associated with the ACE                                                                                                                                                                                                                                                                                                                                                                                                              |
| `tcp_ack`           | Boolean            | TCP Acknowledge flag matching attribute                                                                                                                                                                                                                                                                                                                                                                                                      |
| `tcp_cwr`           | Boolean            | TCP CWR flag matching attribute                                                                                                                                                                                                                                                                                                                                                                                                              |
| `tcp_ece`           | Boolean            | TCP ECE flag matching attribute                                                                                                                                                                                                                                                                                                                                                                                                              |
| `tcp_established`   | Boolean            | TCP established state (ACK or RST flag is set)                                                                                                                                                                                                                                                                                                                                                                                               |
| `tcp_fin`           | Boolean            | TCP FIN flag matching attribute                                                                                                                                                                                                                                                                                                                                                                                                              |
| `tcp_psh`           | Boolean            | TCP PSH flag matching attribute                                                                                                                                                                                                                                                                                                                                                                                                              |
| `tcp_rst`           | Boolean            | TCP RST flag matching attribute                                                                                                                                                                                                                                                                                                                                                                                                              |
| `tcp_urg`           | Boolean            | TCP URG flag matching attribute                                                                                                                                                                                                                                                                                                                                                                                                              |
| `src_l4_port_group` | URL                | URL in string format of the ACL object group resource. This URL refers to the REST API interface and has the following format: `"/system/acl_object_groups/{name},{object_type}"`. This attribute is mutually exclusive with the `src_l4_port_min`, `src_l4_port_max`, and `src_l4_port_range_reverse` attributes, and if this attribute is configured, the other ones will be ignored. The referenced object group must be of type `l4port` |
| `src_l4_port_max`   | Int32              | Maximum L4 port to match on the packet                                                                                                                                                                                                                                                                                                                                                                                                       |
| `src_l4_port_min`   | Int32              | Minimum L4 port to match on the packet                                                                                                                                                                                                                                                                                                                                                                                                       |
| `dst_l4_port_group` | URL                | URL in string format of the ACL object group resource. This URL refers to the REST API interface and has the following format: `"/system/acl_object_groups/{name},{object_type}"`.  This attribute is mutually exclusive with the `dst_l4_port_min`, `dst_l4_port_max`, and `dst_l4_port_range_reverse` attributes. If this attribute is configured, the others will be ignored. The referenced object group must be of type `l4port`        |
| `dst_l4_port_max`   | Int32              | Maximum IP destination port matching attribute. Used in conjunction with `dst_l4_port_min` and `dst_l4_port_range_reverse`                                                                                                                                                                                                                                                                                                                   |
| `dst_l4_port_min`   | Int32              | Minimum IP destination port matching attribute. Used in conjunction with `dst_l4_port_max` and `dst_l4_port_range_reverse`                                                                                                                                                                                                                                                                                                                   |
| `src_ip_group`      | URL                | URL in string format of the ACL object group resource. This URL refers to the REST API interface and has the following format: `"/system/acl_object_groups/{name},{object_type}"`. This attribute is mutually exclusive with the source IP address attribute. If `src_ip_group` is configured, `src_ip` will be ignored. The referenced object group must be of type `ipv4` or `ipv6`.                                                       |
| `src_ip`            | IP Network Address | String with source IP matching attribute. If no IP address is specified, the ACL Entry will not match on source IP address. The following IPv4 and IPV6 formats are accepted. IPv4 format (A.B.C.D/W.X.Y.Z) IPv6 format (A:B::C:D/W:X::Y:Z)                                                                                                                                                                                                  |
| `dst_ip_group`      | URL                | URL in string format of the ACL object group resource. This URL refers to the REST API interface and has the following format: `"/system/acl_object_groups/{name},{object_type}"`. This attribute is mutually exclusive with the destination IP address attribute. If `dst_ip_group` is configured, `dst_ip` will be ignored. The referenced object group must be of type `ipv4` or `ipv6`.                                                  |
| `dst_ip`            | IP Network Address | String with source IP matching attribute. If no IP address is specified, the ACL Entry will not match on destination IP address. The following IPv4 and IPv6 address formats are accepted. IPv4 format (A.B.C.D/W.X.Y.Z) IPv6 format (A:B::C:D/W:X::Y:Z)                                                                                                                                                                                     |
| `src_mac`           | MAC address        | String with source MAC matching attribute. Two formats are allowed (AAAA.BBBB.CCCC or AAAA.BBBB.CCCC/XXXX.YYYY.ZZZZ)                                                                                                                                                                                                                                                                                                                         |
| `dst_mac`           | MAC address        | String with destination MAC matching attribute. Two formats are allowed (AAAA.BBBB.CCCC or AAAA.BBBB.CCCC/XXXX.YYYY.ZZZZ)                                                                                                                                                                                                                                                                                                                    |
| `action`            | String             | Define the action to take on an ACL match. There are two options: `permit`, and `deny`. `permit`: packets will be forwarded. `deny`: packets will be dropped. ACE will only be activated when an associated action is provided.                                                                                                                                                                                                              |
| `count`             | Boolean            | When true, increment hit count for packets that match this ACL                                                                                                                                                                                                                                                                                                                                                                               |
| `dscp`              | Int32              | Different Services Code Point matching attribute                                                                                                                                                                                                                                                                                                                                                                                             |
| `ecn`               | Int32              | Explicit Congestion Notification matching attribute                                                                                                                                                                                                                                                                                                                                                                                          |
| `ethertype`         | Int32              | Ethernet type matching attribute                                                                                                                                                                                                                                                                                                                                                                                                             |
| `fragment`          | Boolean            | Fragment matching attribute                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `icmp_code`         | Int32              | ICMP code matching attribute                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `icmp_type`         | Int32              | ICMP type matching attribute                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `ip_precedence`     | Int32              | IP Precedence matching attribute                                                                                                                                                                                                                                                                                                                                                                                                             |
| `log`               | Boolean            | ACE attribute log action; when true, log information for packets that match ACL.                                                                                                                                                                                                                                                                                                                                                             |
| `pcp`               | Int32              | Priority Code Point matching attribute                                                                                                                                                                                                                                                                                                                                                                                                       |
| `protocol`          | Int32              | IPv4 protocol matching attribute                                                                                                                                                                                                                                                                                                                                                                                                             |
| `ttl`               | Int32              | Time-to-live matching attribute                                                                                                                                                                                                                                                                                                                                                                                                              |
| `tos`               | Int32              | IP Type of service value matching attribute                                                                                                                                                                                                                                                                                                                                                                                                  |
| `vlan`              | Int32              | VLAN ID matching attribute                                                                                                                                                                                                                                                                                                                                                                                                                   |

# Examples

## 1. Deny a host inside an allowed network

The following example shows how to allow all incoming traffic from a certain
IPv4 network, but deny a single host, and keep a count of how many packets are
sent to the switch from that host. Two ACEs are added, the one with lowest
sequence number is checked first for matches. One ACE is in charge of denying
incoming traffic from the single host, while the other one allows incoming from
the rest of the network.

```YAML
- name: Configure IPv4 ACL that allows traffic from a network except a single host
  aoscx_acl:
    name: allow_network_deny_host
    type: ipv4
    acl_entries:
      1:
        comment: "Deny the host"
        action: deny
        count: true
        src_ip: 158.10.12.57/255.255.255.255
        protocol: tcp
      2:
        comment: "Allow the network"
        action: permit
        src_ip: 158.10.12.1/255.255.0.0
        protocol: tcp
```

## 2. Deny a host and log urgent packets

The following example shows how to deny all incoming and outgoing traffic from a
single host, and log only when packet was urgent.

```YAML
- name: Configure IPv6 ACL that denies all traffic and logs urgent packets
  aoscx_acl:
    name: deny_host_log_urgent
    acl_entries:
      9:
        comment: "match urgent packets for log"
        tcp_urg: true
        log: true
        src_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        dst_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        action: deny
      10:
        comment: "match the rest of the packets"
        log: false
        src_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        dst_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff
        action: deny
```

## 3. Simple L4 example

The following example shows how to configure rules with L4 ports. It will allow
traffic form ports 5000, 5001 and 5002 to port 3657. Note that when
a match for only one port is intended, `src/dst_l4_port_max` and
`src/dst_l4_port_min` need to be equal.

```YAML
- name: Configure port range
  aoscx_acl:
    name: simple_ports
    type: ipv4
    acl_entries:
      1:
        comment: "Use a range of ports"
        src_ip: 100.10.25.2/255.255.255.0
        dst_ip: 100.10.25.2/255.255.255.0
        src_l4_port_max: 5002
        src_l4_port_min: 5000
        dst_l4_port_max: 3657
        dst_l4_port_min: 3567
        action: permit
```

## 4. Remove an ACL

```YAML
- name: Delete ipv4 ACL from config
  aoscx_acl:
    name: ipv4_acl
    type: ipv4
    state: delete
```
