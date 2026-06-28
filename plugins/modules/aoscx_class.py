#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
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
---
module: aoscx_class
version_added: "4.6.0"
short_description: Create, update or delete a traffic class
description: >
  This module provides configuration management of traffic classes on AOS-CX
  devices (system/classes). A traffic class is identified by the compound index
  of its name and type, and contains an ordered list of match/ignore entries
  that classify traffic in a similar way to access control lists. Traffic
  classes are referenced by port access group based policies, application based
  policies and port access policies (their gbp-, abp- and ipv4/ipv6/mac
  variants). This module requires REST API version 10.16 (set
  ansible_aoscx_rest_version to 10.16). The supplied entries fully replace the
  existing entries of the class. The match fields of an entry cannot be
  modified in place; when they change the entry is recreated.
author: Aruba Networks (@ArubaNetworks)
options:
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
"""

EXAMPLES = """
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
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

COLLECTION = "system/classes"

CLASS_TYPES = [
    "ipv4",
    "ipv6",
    "mac",
    "gbp-ipv4",
    "gbp-ipv6",
    "gbp-mac",
    "abp-ipv4",
    "abp-ipv6",
]

# Match fields of an entry. They cannot be modified in place: when any of them
# changes the entry is deleted and recreated. ``count`` is grouped here because
# it shares the same immutable behaviour. ``comment`` is handled separately as
# it is the only modifiable attribute.
MATCH_FIELDS = [
    {"name": "count", "type": "bool"},
    {"name": "src_ip", "type": "str"},
    {"name": "dst_ip", "type": "str"},
    {"name": "src_mac", "type": "str"},
    {"name": "dst_mac", "type": "str"},
    {"name": "src_role", "type": "str"},
    {"name": "dst_role", "type": "str"},
    {"name": "dst_fqdn_address", "type": "str"},
    {"name": "src_l4_port_min", "type": "int"},
    {"name": "src_l4_port_max", "type": "int"},
    {"name": "dst_l4_port_min", "type": "int"},
    {"name": "dst_l4_port_max", "type": "int"},
    {"name": "protocol", "type": "int"},
    {"name": "ethertype", "type": "int"},
    {"name": "icmp_type", "type": "int"},
    {"name": "icmp_code", "type": "int"},
    {"name": "dscp", "type": "int"},
    {"name": "ecn", "type": "int"},
    {"name": "ip_precedence", "type": "int"},
    {"name": "pcp", "type": "int"},
    {"name": "tos", "type": "int"},
    {"name": "ttl", "type": "int"},
    {"name": "vlan", "type": "int"},
    {"name": "fragment", "type": "bool"},
    {"name": "arc_app", "type": "str"},
    {"name": "arc_app_category", "type": "str"},
    {"name": "tcp_ack", "type": "bool"},
    {"name": "tcp_cwr", "type": "bool"},
    {"name": "tcp_ece", "type": "bool"},
    {"name": "tcp_established", "type": "bool"},
    {"name": "tcp_fin", "type": "bool"},
    {"name": "tcp_psh", "type": "bool"},
    {"name": "tcp_rst", "type": "bool"},
    {"name": "tcp_syn", "type": "bool"},
    {"name": "tcp_urg", "type": "bool"},
]

# Immutable fields compared to detect whether an existing entry must be
# recreated. ``type`` (the match/ignore action) is immutable as well.
IMMUTABLE_FIELDS = [{"name": "type", "type": "str"}] + MATCH_FIELDS


def ok(response):
    return response is not None and response.status_code < 400


def build_argument_spec():
    entry_spec = dict(
        sequence_number=dict(type="int", required=True),
        action=dict(
            type="str",
            required=False,
            default="match",
            choices=["match", "ignore"],
        ),
        comment=dict(type="str", required=False, default=None),
    )
    for field in MATCH_FIELDS:
        entry_spec[field["name"]] = dict(
            type=field["type"], required=False, default=None
        )

    return dict(
        name=dict(type="str", required=True),
        type=dict(type="str", required=True, choices=list(CLASS_TYPES)),
        entries=dict(
            type="list",
            elements="dict",
            options=entry_spec,
            required=False,
            default=None,
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )


def _build_desired(ansible_module, entries):
    desired = {}
    for entry in entries:
        seq = entry["sequence_number"]
        if seq in desired:
            ansible_module.fail_json(
                msg="Duplicate sequence_number {0}".format(seq)
            )
        body = {"sequence_number": seq, "type": entry["action"]}
        if entry["comment"] is not None:
            body["comment"] = entry["comment"]
        for field in MATCH_FIELDS:
            value = entry.get(field["name"])
            if value is not None:
                body[field["name"]] = value
        desired[seq] = body
    return desired


def _match_differs(want, current):
    for field in IMMUTABLE_FIELDS:
        name = field["name"]
        default = False if field["type"] == "bool" else None
        want_value = want.get(name, default)
        current_value = current.get(name, default)
        if current_value is None and field["type"] == "bool":
            current_value = False
        if want_value != current_value:
            return True
    return False


def _get_entries(session, container_path):
    response = session.request(
        "GET",
        "{0}/cfg_entries".format(container_path),
        params={"depth": 2, "selector": "configuration"},
    )
    if not ok(response):
        return {}
    return {int(seq): data for seq, data in response.json().items()}


def _reconcile_entries(
    ansible_module, session, container_path, desired, current, check_mode
):
    base = "{0}/cfg_entries".format(container_path)
    changed = False

    # Remove entries that are no longer desired (full replace).
    for seq in current:
        if seq not in desired:
            changed = True
            if not check_mode:
                session.request("DELETE", "{0}/{1}".format(base, seq))

    for seq, want in desired.items():
        cur = current.get(seq)
        # The match fields of an entry are immutable; recreate the entry when
        # it is missing or when any of its match fields changed.
        if cur is None or _match_differs(want, cur):
            changed = True
            if not check_mode:
                if cur is not None:
                    session.request("DELETE", "{0}/{1}".format(base, seq))
                response = session.request(
                    "POST", base, data=ansible_module.jsonify(want)
                )
                if not ok(response):
                    ansible_module.fail_json(
                        msg="Could not create entry {0}: {1}".format(
                            seq, response.text
                        )
                    )
            continue

        # Match fields are identical; reconcile the modifiable comment.
        want_comment = want.get("comment")
        if want_comment is not None and want_comment != cur.get("comment"):
            changed = True
            if not check_mode:
                session.request(
                    "PUT",
                    "{0}/{1}".format(base, seq),
                    data=ansible_module.jsonify({"comment": want_comment}),
                )

    return changed


def run_module(ansible_module, session):
    params = ansible_module.params
    name = params["name"]
    class_type = params["type"]
    state = params["state"]
    entries_param = params["entries"]
    manage_entries = entries_param is not None
    entries = entries_param or []
    check_mode = ansible_module.check_mode

    index = "{0}{1}{2}".format(
        name, session.api.compound_index_separator, class_type
    )
    container_path = "{0}/{1}".format(COLLECTION, index)

    result = dict(changed=False)
    exists = ok(session.request("GET", container_path))

    if state == "delete":
        if exists and not check_mode:
            response = session.request("DELETE", container_path)
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not delete {0}: {1}".format(name, response.text)
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    desired = {}
    if manage_entries:
        desired = _build_desired(ansible_module, entries)

    changed = False
    if not exists:
        changed = True
        if not check_mode:
            response = session.request(
                "POST",
                COLLECTION,
                data=ansible_module.jsonify(
                    {"name": name, "type": class_type}
                ),
            )
            if not ok(response):
                ansible_module.fail_json(
                    msg="Could not create {0}: {1}".format(name, response.text)
                )
        current = {}
    elif manage_entries:
        current = _get_entries(session, container_path)
    else:
        current = {}

    if manage_entries:
        changed = (
            _reconcile_entries(
                ansible_module,
                session,
                container_path,
                desired,
                current,
                check_mode,
            )
            or changed
        )

    result["changed"] = changed
    ansible_module.exit_json(**result)


def main():
    ansible_module = AnsibleModule(
        argument_spec=build_argument_spec(),
        supports_check_mode=True,
    )
    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )
    run_module(ansible_module, session)


if __name__ == "__main__":
    main()
