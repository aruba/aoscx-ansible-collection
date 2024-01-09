#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2023 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
module: aoscx_acl
short_description: >
  Module for configuration of Access Control Lists in AOSCX switches.
description: >
  This module provides the functionality for configuring Access Control Lists
  on AOSCX switches. For more detailed documentation see docs/aoscx_acl.md in
  this repository.
version_added: "2.8.0"
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the access control list.
    required: true
    type: str
  type:
    description: Type of ACL
    required: true
    type: str
    choices:
      - ipv4
      - ipv6
      - mac
  state:
    description: The action taken with the current ACL
    required: false
    type: str
    choices:
      - create
      - update
      - delete
    default: create
  acl_entries:
    description: >
      A dictionary, where the key is the sequence number of the Access Control
      Entry, and the value is a dictionary representing the Access Control
      Entry. A detailed description of these ACE dictionaries is provided in
      the notes section, and in docs/aoscx_acl.md
      The ACEs are configured using a dictionary representation. A description
      of all available fields are provided here. All fields are optional, but
      there are certain internal dependencies that are related to how ACLs
      work.
    required: false
    type: dict
    suboptions:
      comment:
        type: str
        required: false
        description: Comment associated with the ACE
      tcp_flags:
        type: list
        elements: str
        required: false
        description: >
          TCP Flags: ack, cwr, ece, established, fin, psh, rst, syn, urg
      tcp_ack:
        type: bool
        required: false
        description: TCP Acknowledge flag matching attribute
      tcp_cwr:
        type: bool
        required: false
        description: TCP CWR flag matching attribute
      tcp_ece:
        type: bool
        required: false
        description: TCP ECE flag matching attribute
      tcp_established:
        type: bool
        required: false
        description: TCP established state (ACK or RST flag is set)
      tcp_fin:
        type: bool
        required: false
        description: TCP FIN flag matching attribute
      tcp_psh:
        type: bool
        required: false
        description: TCP PSH flag matching attribute
      tcp_rst:
        type: bool
        required: false
        description: TCP RST flag matching attribute
      tcp_urg:
        type: bool
        required: false
        description: TCP URG flag matching attribute
      src_l4_port_group:
        type: str
        required: false
        description: >
          Name of the ACL object group. This attribute is mutually
          exclusive with the `src_l4_port_min`, `src_l4_port_max`, and
          `src_l4_port_range_reverse` attributes, and if this attribute is
          configured, the other ones will be ignored. The object group
          must be of type `l4port`.
      src_l4_port_max:
        type: int
        required: false
        description: >
          Maximum L4 port to match on the packet. Use only if
          `src_l4_port` is not specified.
      src_l4_port_min:
        type: int
        required: false
        description: >
          Minimum L4 port to match on the packet. Use only if
          `src_l4_port` is not specified.
      src_l4_port:
        type: str
        required: false
        description: >
          Range of L4 ports or L4 source port to match on the
          packet. Use only if `src_l4_port_min` and `src_l4_port_max` are not
          specified.
      dst_l4_port_group:
        type: str
        required: false
        description: >
          Name of the ACL object group. This attribute is mutually
          exclusive with the `dst_l4_port_min`, `dst_l4_port_max`, and
          `dst_l4_port_range_reverse` attributes. If this attribute is
          configured, the others will be ignored. The object group must be
          of type `l4port`.
      dst_l4_port_max:
        type: int
        required: false
        description: >
          Maximum IP destination port matching attribute. Used in conjunction
          with `dst_l4_port_min` and `dst_l4_port_range_reverse`. Use only if
          `dst_l4_port` is not specified.
      dst_l4_port_min:
        type: int
        required: false
        description: >
          Minimum IP destination port matching attribute. Used in conjunction
          with `dst_l4_port_max` and `dst_l4_port_range_reverse`. Use only if
          `dst_l4_port` is not specified.
      dst_l4_port:
        type: str
        required: false
        description: >
          Range of L4 ports or L4 destination port to match on the
          packet. Use only if `dst_l4_port_min` and `dst_l4_port_max` are not
          specified.
      src_ip_group:
        type: str
        required: false
        description: >
          Name of the ACL object group resource. This attribute is
          mutually exclusive with the source IP address attribute. If
          `src_ip_group` is configured, `src_ip` will be ignored. The
          object group must be of type `ipv4` or `ipv6`.
      src_ip:
        type: str
        required: false
        description: >
          String with source IP matching attribute. If no IP address is
          specified, the ACL Entry will not match on source IP address. The
          following IPv4 and IPV6 formats are accepted. IPv4 format with prefix
          length or subnet mask (A.B.C.D/W or A.B.C.D/W.X.Y.Z). IPv6 format
          (A:B::C:D/W). To match any address the field can be left empty or use
          the 'any' keyword.
      dst_ip_group:
        type: str
        required: false
        description: >
          Name of the ACL object group resource. This attribute is
          mutually exclusive with the destination IP address attribute. If
          `dst_ip_group` is configured, `dst_ip` will be ignored. The
          object group must be of type `ipv4` or `ipv6`.
      dst_ip:
        type: str
        required: false
        description: >
          String with source IP matching attribute. If no IP address is
          specified, the ACL Entry will not match on destination IP address.
          The following IPv4 and IPv6 address formats are accepted. IPv4 format
          with prefix length or subnet mask (A.B.C.D/W or A.B.C.D/W.X.Y.Z).
          IPv6 format (A:B::C:D/W). To match any address the field can be left
          empty or use the 'any' keyword.
      src_mac:
        type: str
        required: false
        description: >
          String with source MAC matching attribute. Two formats are allowed
          (AAAA.BBBB.CCCC or AAAA.BBBB.CCCC/XXXX.YYYY.ZZZZ).
      dst_mac:
        type: str
        required: false
        description: >
          String with destination MAC matching attribute. Two formats are
          allowed (AAAA.BBBB.CCCC or AAAA.BBBB.CCCC/XXXX.YYYY.ZZZZ).
      action:
        type: str
        required: false
        description: >
          Define the action to take on an ACL match. There are two options:
          `permit`, and `deny`. `permit`: packets will be forwarded. `deny`:
          packets will be dropped. ACE will only be activated when an
          associated action is provided.
      count:
        type: bool
        required: false
        description: >
          When true, increment hit count for packets that match this ACL.
      dscp:
        type: str
        required: false
        description: Different Services Code Point matching attribute.
      ecn:
        type: int
        required: false
        description: Explicit Congestion Notification matching attribute.
      ethertype:
        type: str
        required: false
        description: Ethernet type matching attribute.
      fragment:
        type: bool
        required: false
        description: Fragment matching attribute.
      icmp_code:
        type: int
        required: false
        description: ICMP code matching attribute.
      icmp_type:
        type: str
        required: false
        description: ICMP type matching attribute.
      ip_precedence:
        type: int
        required: false
        description: IP Precedence matching attribute.
      log:
        type: bool
        required: false
        description: >
          ACE attribute log action; when true, log information for packets that
          match ACL.
      pcp:
        type: int
        required: false
        description: Priority Code Point matching attribute.
      protocol:
        type: int
        description: IPv4 protocol matching attribute.
      ttl:
        type: int
        description: Time-to-live matching attribute.
      tos:
        type: int
        description: IP Type of service value matching attribute.
      vlan:
        type: int
        description: VLAN ID matching attribute.
"""

EXAMPLES = """
# Deny a host inside an allowed network
# The following example shows how to allow all incoming traffic from a certain
# IPv4 network, but deny a single host, and keep a count of how many packets
# are sent to the switch from that host. Two ACEs are added, the one with
# lowest sequence number is checked first for matches. One ACE is in charge of
# denying incoming traffic from the single host, while the other one allows
# incoming from the rest of the network.
- name: >
    Configure IPv4 ACL to allow traffic from a network except a single host.
  aoscx_acl:
    name: allow_network_deny_host
    type: ipv4
    acl_entries:
      1:
        comment: "Deny the host"
        action: deny
        count: true
        src_ip: 158.10.12.57/32
        protocol: tcp
      2:
        comment: "Allow the network"
        action: permit
        src_ip: 158.10.12.1/16
        protocol: tcp

# Deny a host and log urgent packets
# The following example shows how to deny all incoming and outgoing traffic
# from a single host, and log only when packet was urgent.
- name: Configure IPv6 ACL that denies all traffic and logs urgent packets
  aoscx_acl:
    name: deny_host_log_urgent
    acl_entries:
      9:
        comment: "match urgent packets for log"
        tcp_urg: true
        log: true
        src_ip: 2001:db8::12/32
        dst_ip: 2001:db8::12/32
        action: deny
      10:
        comment: "match the rest of the packets"
        log: false
        src_ip: 2001:db8::12/32
        dst_ip: 2001:db8::12/32
        action: deny

# Deny a network
# The following example shows how to deny all incoming and outgoing traffic
# from a network.
- name: Configure IPv6 ACL that denies all traffic
  aoscx_acl:
    name: deny_network
    acl_entries:
      10:
        action: deny
        count: True
        protocol: tcp
        src_ip: 2001:db8::/32

# Simple L4 example
# The following example shows how to configure rules with L4 ports. It will
# allow traffic form ports 5000, 5001 and 5002 to port 3657. Note that when
# a match for only one port is intended, `src/dst_l4_port_max` and
# `src/dst_l4_port_min` must be equal.
- name: Configure port range
  aoscx_acl:
    name: simple_ports
    type: ipv4
    acl_entries:
      1:
        comment: "Use a range of ports"
        src_ip: 100.10.25.2/24
        dst_ip: 100.10.25.2/24
        src_l4_port_max: 5002
        src_l4_port_min: 5000
        dst_l4_port_max: 3657
        dst_l4_port_min: 3567
        action: permit

- name: Configure port range
  aoscx_acl:
    name: simple_ports
    type: ipv4
    acl_entries:
      1:
        comment: "Use a range of ports"
        src_ip: 100.10.25.2/24
        dst_ip: 100.10.25.2/24
        src_l4_port: 5000-5002
        dst_l4_port: 3567-3657
        action: permit

- name: Configure port
  aoscx_acl:
    name: simple_ports
    type: ipv4
    acl_entries:
      1:
        comment: " Use a port"
        src_ip: 100.10.25.2/24
        dst_ip: 100.10.25.2/24
        src_l4_port: 5000
        dst_l4_port: 3567
        action: permit

- name: Delete ACL entry
  aoscx_acl:
    name: simple_ports
    type: ipv4
    acl_entries:
      1:
        comment: "Use a range of ports"
        src_ip: 100.10.25.2/24
        dst_ip: 100.10.25.2/24
        src_l4_port_max: 5002
        src_l4_port_min: 5000
        dst_l4_port_max: 3657
        dst_l4_port_min: 3567
        action: permit
    state: delete

- name: Delete ipv4 ACL from config
  aoscx_acl:
    name: ipv4_acl
    type: ipv4
    state: delete
"""


RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def get_argument_spec():
    argument_spec = {
        "name": {"type": "str", "required": True},
        "type": {
            "type": "str",
            "required": True,
            "choices": ["ipv4", "ipv6", "mac"],
        },
        "acl_entries": {
            "type": "dict",
            "required": False,
            "default": None,
        },
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
    }
    return argument_spec


def main():
    module_args = get_argument_spec()

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    # Get playbook's arguments
    state = ansible_module.params["state"]
    name = ansible_module.params["name"]
    list_type = ansible_module.params["type"]
    acl_entries = ansible_module.params["acl_entries"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    acl = session.api.get_module(session, "ACL", name, list_type=list_type)

    try:
        acl.get()
        acl_exists = True
    except Exception:
        acl_exists = False

    modified_op = False
    if state == "delete" and acl_exists:
        #  If there are entries in configuration, delete them
        if acl_entries:
            for seq_num, acl_entry in acl.cfg_aces.items():
                if seq_num in acl_entries:
                    acl_entry.delete()
                    modified_op = True
        else:
            # Delete ACL
            acl.delete()
            modified_op = True
    elif state in ["create", "update"]:
        if not acl_exists:
            acl.create()
            modified_op = True

        if acl_entries:
            AclEntry = session.api.get_module_class(session, "AclEntry")
            sw_acl_entries = acl.cfg_aces.copy()
            valid_tcp_flags = [
                "ack",
                "cwr",
                "ece",
                "established",
                "fin",
                "psh",
                "rst",
                "syn",
                "urg",
            ]
            for sequence_number, config_cls in acl_entries.items():
                sequence_number = int(sequence_number)
                config = config_cls.copy()
                # Need to convert tcp_flags list in {tcp_flag: True}
                if "tcp_flags" in config:
                    for flag in config["tcp_flags"]:
                        if flag in valid_tcp_flags:
                            config["tcp_" + flag] = True
                        else:
                            ansible_module.fail_json(
                                msg=(
                                    "Invalid TCP Flag {0}, "
                                    "valid flags are: {1}"
                                ).format(flag, ", ".join(valid_tcp_flags))
                            )
                    del config["tcp_flags"]
                ObjectGroup = session.api.get_module_class(
                    session, "ObjectGroup"
                )
                for l4_port in ["src_l4_port", "dst_l4_port"]:
                    l4_port_grp_name = l4_port + "_group"
                    if l4_port_grp_name in config:
                        group_name = config[l4_port_grp_name]
                        l4_port_group = ObjectGroup(
                            session, group_name, "l4port"
                        )
                        try:
                            l4_port_group.get()
                        except Exception:
                            ansible_module.fail_json(
                                msg="{0} does not exist".format(
                                    str(l4_port_group)
                                )
                            )
                        config[l4_port_grp_name] = l4_port_group
                        config.pop(l4_port, None)
                        config.pop(l4_port + "_min", None)
                        config.pop(l4_port + "_max", None)
                for ip_param in ["src_ip", "dst_ip"]:
                    ip_grp_name = ip_param + "_group"
                    if ip_grp_name in config:
                        group_name = config[ip_grp_name]
                        ip_group = ObjectGroup(
                            session, group_name, acl.list_type
                        )
                        try:
                            ip_group.get()
                        except Exception:
                            ansible_module.fail_json(
                                msg="{0} does not exist".format(str(ip_group))
                            )
                        config[ip_grp_name] = ip_group
                        config.pop(ip_param, None)
                # Need to translate L4 port name if any
                if "src_l4_port" in config:
                    l4_port = config["src_l4_port"]
                    if isinstance(l4_port, int):
                        config["src_l4_port_min"] = l4_port
                        config["src_l4_port_max"] = l4_port
                    elif "-" in l4_port:
                        try:
                            port_range = iter(l4_port.split("-"))
                            config["src_l4_port_min"] = int(next(port_range))
                            config["src_l4_port_max"] = int(next(port_range))
                        except Exception as e:
                            ansible_module.fail_json(
                                msg="Unable to parse range: {0} ({1})".format(
                                    l4_port, str(e)
                                )
                            )
                    else:
                        if l4_port.isnumeric():
                            l4_port = int(l4_port)
                        config["src_l4_port_min"] = l4_port
                        config["src_l4_port_max"] = l4_port
                    del config["src_l4_port"]
                if "dst_l4_port" in config:
                    l4_port = config["dst_l4_port"]
                    if isinstance(l4_port, int):
                        config["dst_l4_port_min"] = l4_port
                        config["dst_l4_port_max"] = l4_port
                    elif "-" in l4_port:
                        try:
                            port_range = iter(l4_port.split("-"))
                            config["dst_l4_port_min"] = int(next(port_range))
                            config["dst_l4_port_max"] = int(next(port_range))
                        except Exception as e:
                            ansible_module.fail_json(
                                msg="Unable to parse range: {0} ({1})".format(
                                    l4_port, str(e)
                                )
                            )
                    else:
                        if l4_port.isnumeric():
                            l4_port = int(l4_port)
                        config["dst_l4_port_min"] = l4_port
                        config["dst_l4_port_max"] = l4_port
                    del config["dst_l4_port"]

                try:
                    if sequence_number in sw_acl_entries:
                        acl_entry = sw_acl_entries[sequence_number]
                        for attr, value in config.items():
                            setattr(acl_entry, attr, value)
                    else:
                        acl_entry = AclEntry(
                            session,
                            sequence_number=int(sequence_number),
                            parent_acl=acl,
                            **config
                        )
                    modified_op |= acl_entry.apply()
                except Exception as e:
                    ansible_module.fail_json(msg=str(e))

    # Changed
    if modified_op:
        result["changed"] = modified_op

    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
