# module: aoscx_class

description: This module provides configuration management of traffic classes on
AOS-CX devices (system/classes). A traffic class is identified by the compound
index of its name and type, and contains an ordered list of match/ignore
entries that classify traffic in a similar way to access control lists. Traffic
classes are referenced by port access group based policies, application based
policies and port access policies (their gbp-, abp- and ipv4/ipv6/mac
variants). This module requires REST API version 10.16 (set
ansible_aoscx_rest_version to 10.16). The supplied entries fully replace the
existing entries of the class. The match fields of an entry cannot be modified
in place; when they change the entry is recreated.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the traffic class. Together with type it forms the index of the
      resource under system/classes.
    required: true
    type: str
  type:
    description: >
      Type of the traffic class. Together with name it forms the index of the
      resource; it cannot be changed after creation.
    required: true
    type: str
    choices:
      - ipv4
      - ipv6
      - mac
      - gbp-ipv4
      - gbp-ipv6
      - gbp-mac
      - abp-ipv4
      - abp-ipv6
  entries:
    description: >
      Ordered list of class entries. The supplied list fully replaces the
      existing entries of the class. When omitted, the entries are left
      untouched and only the existence of the class is reconciled. The valid
      match fields depend on the type of the class; fields that are not
      applicable are rejected by the switch.
    required: false
    type: list
    elements: dict
    suboptions:
      sequence_number:
        description: Sequence number of the entry within the class.
        required: true
        type: int
      action:
        description: >
          Whether traffic matching this entry is part of the class (match) or
          excluded from it (ignore).
        required: false
        type: str
        choices:
          - match
          - ignore
        default: match
      comment:
        description: Optional comment for the entry.
        required: false
        type: str
      count:
        description: Enable hit counters for the entry.
        required: false
        type: bool
      src_ip:
        description: >
          Source IP address and dotted netmask to match, for example
          10.0.0.0/255.255.255.0 (a host uses /255.255.255.255).
        required: false
        type: str
      dst_ip:
        description: >
          Destination IP address and dotted netmask to match, for example
          10.0.0.0/255.255.255.0 (a host uses /255.255.255.255).
        required: false
        type: str
      src_mac:
        description: Source MAC address (and optional mask) to match.
        required: false
        type: str
      dst_mac:
        description: Destination MAC address (and optional mask) to match.
        required: false
        type: str
      src_role:
        description: Source role name to match.
        required: false
        type: str
      dst_role:
        description: Destination role name to match.
        required: false
        type: str
      dst_fqdn_address:
        description: Destination fully qualified domain name to match.
        required: false
        type: str
      src_l4_port_min:
        description: Lower bound of the source layer 4 port range to match.
        required: false
        type: int
      src_l4_port_max:
        description: Upper bound of the source layer 4 port range to match.
        required: false
        type: int
      dst_l4_port_min:
        description: Lower bound of the destination layer 4 port range.
        required: false
        type: int
      dst_l4_port_max:
        description: Upper bound of the destination layer 4 port range.
        required: false
        type: int
      protocol:
        description: IP protocol number to match.
        required: false
        type: int
      ethertype:
        description: Ethertype value to match.
        required: false
        type: int
      icmp_type:
        description: ICMP type to match.
        required: false
        type: int
      icmp_code:
        description: ICMP code to match.
        required: false
        type: int
      dscp:
        description: DSCP value to match.
        required: false
        type: int
      ecn:
        description: ECN value to match.
        required: false
        type: int
      ip_precedence:
        description: IP precedence value to match.
        required: false
        type: int
      pcp:
        description: Priority code point value to match.
        required: false
        type: int
      tos:
        description: Type of service value to match.
        required: false
        type: int
      ttl:
        description: Time to live value to match.
        required: false
        type: int
      vlan:
        description: VLAN identifier to match.
        required: false
        type: int
      fragment:
        description: Match IP fragments.
        required: false
        type: bool
      arc_app:
        description: Application recognition application name to match.
        required: false
        type: str
      arc_app_category:
        description: Application recognition category to match.
        required: false
        type: str
      tcp_ack:
        description: Match the TCP ACK flag.
        required: false
        type: bool
      tcp_cwr:
        description: Match the TCP CWR flag.
        required: false
        type: bool
      tcp_ece:
        description: Match the TCP ECE flag.
        required: false
        type: bool
      tcp_established:
        description: Match established TCP connections (ACK or RST set).
        required: false
        type: bool
      tcp_fin:
        description: Match the TCP FIN flag.
        required: false
        type: bool
      tcp_psh:
        description: Match the TCP PSH flag.
        required: false
        type: bool
      tcp_rst:
        description: Match the TCP RST flag.
        required: false
        type: bool
      tcp_syn:
        description: Match the TCP SYN flag.
        required: false
        type: bool
      tcp_urg:
        description: Match the TCP URG flag.
        required: false
        type: bool
  state:
    description: Create, update or delete the traffic class.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
```

##### EXAMPLES

```YAML
- name: Create an IPv4 traffic class matching HTTPS to a subnet
  aoscx_class:
    name: web_traffic
    type: ipv4
    entries:
      - sequence_number: 10
        action: match
        protocol: 6
        dst_ip: 10.0.0.0/255.255.255.0
        dst_l4_port_min: 443
        dst_l4_port_max: 443
        count: true
        comment: https

- name: Remove all entries of a traffic class but keep the class
  aoscx_class:
    name: web_traffic
    type: ipv4
    entries: []

- name: Delete a traffic class
  aoscx_class:
    name: web_traffic
    type: ipv4
    state: delete
```
