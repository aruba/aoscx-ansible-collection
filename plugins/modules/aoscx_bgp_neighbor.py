#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_bgp_neighbor
version_added: "4.6.0"
short_description: Create, Update or Delete BGP neighbors on AOS-CX
description: >
  This module provides configuration management of BGP neighbors or peer
  groups (C(neighbor) commands of the C(router bgp) context) on AOS-CX
  devices, including their per address family settings. The same settings
  are applied to every neighbor given in I(neighbor) or I(neighbors). Other
  neighbors of the BGP router are never modified or deleted. The BGP router
  must exist, see M(arubanetworks.aoscx.aoscx_bgp_router).
author: Aruba Networks (@ArubaNetworks)
notes:
  - Requires pyaoscx 2.7.1 or later, which fixes the BGP neighbor handling
    of earlier releases.
  - Tested on a switch with REST API version 10.09 (firmware 10.19).
  - In check mode, a missing VRF or BGP router is reported as a change instead of an
    error, because it may be created by a previous task of the playbook.
options:
  asn:
    description: Autonomous System Number of the BGP router.
    required: true
    type: int
  vrf:
    description: Name of the VRF of the BGP router.
    required: false
    default: default
    type: str
  neighbor:
    description: >
      IPv4/IPv6 address of the neighbor, or name of the peer group. Mutually
      exclusive with I(neighbors), one of them is required.
    required: false
    type: str
  neighbors:
    description: >
      List of neighbors (IPv4/IPv6 addresses or peer group names) that get
      the same settings. Neighbors of the BGP router that are not listed are
      not modified. All the neighbors are checked before the first change is
      applied. Mutually exclusive with I(neighbor).
    required: false
    type: list
    elements: str
  is_peer_group:
    description: >
      Whether the neighbors are peer groups (C(neighbor <name> peer-group)).
      Only used on creation, it cannot be changed on an existing neighbor.
    required: false
    default: false
    type: bool
  peer_group:
    description: >
      Name of the peer group the neighbor belongs to
      (C(neighbor <ip> peer-group <name>)). The peer group must exist. Use an
      empty string to remove the neighbor from its peer group. Not supported
      when I(is_peer_group) is C(true).
    required: false
    type: str
  remote_as:
    description: ASN of the neighbor (C(remote-as)).
    required: false
    type: int
  description:
    description: Description of the neighbor (C(description)).
    required: false
    type: str
  update_source:
    description: >
      Source of the BGP session (C(update-source)): either an IP address, or
      the name of a loopback interface such as C(loopback0) (C(loopback 0)
      is also accepted). Use an empty string to remove it.
    required: false
    type: str
  ebgp_multihop:
    description: >
      Maximum number of hops to an external neighbor (C(ebgp-multihop)),
      between 1 and 255. Required for eBGP sessions between loopbacks. Use
      C(255) for the CLI C(ebgp-multihop) command without value, and C(1) to
      remove it (C(no neighbor ... ebgp-multihop)).
    required: false
    type: int
  shutdown:
    description: Administratively shut down the neighbor (C(shutdown)).
    required: false
    type: bool
  address_families:
    description: >
      Per address family settings (C(neighbor) commands of the
      C(address-family) contexts). Only the listed address families, and
      within them only the given settings, are changed. Ignored when
      I(state) is C(delete).
    required: false
    type: list
    elements: dict
    suboptions:
      address_family:
        description: Address family of the settings.
        required: true
        type: str
        choices:
          - ipv4_unicast
          - ipv6_unicast
          - l2vpn_evpn
      activate:
        description: Activate the neighbor in the address family (C(activate)).
        required: false
        type: bool
      send_community:
        description: >
          Communities sent to the neighbor (C(send-community)). C(none)
          disables it.
        required: false
        type: str
        choices:
          - both
          - extended
          - standard
          - none
      route_reflector_client:
        description: >
          Configure the neighbor as route reflector client
          (C(route-reflector-client)).
        required: false
        type: bool
      next_hop_self:
        description: >
          Advertise this router as next hop (C(next-hop-self)). Not supported
          for C(l2vpn_evpn).
        required: false
        type: bool
      next_hop_unchanged:
        description: >
          Keep the next hop unchanged (C(next-hop-unchanged)). Only supported
          for C(l2vpn_evpn).
        required: false
        type: bool
      inbound_soft_reconfiguration:
        description: >
          Enable inbound soft reconfiguration
          (C(soft-reconfiguration inbound)). Not supported for C(l2vpn_evpn).
        required: false
        type: bool
  state:
    description: >
      Create or update (C(create)) or delete (C(delete)) the given
      neighbors. Other neighbors are never deleted. A peer group cannot be
      deleted while neighbors belong to it.
    required: false
    default: create
    choices:
      - create
      - delete
    type: str
"""

EXAMPLES = """
# Equivalent CLI configuration:
#   router bgp 65000
#       neighbor spine-RR peer-group
#       neighbor spine-RR remote-as 65000
#       neighbor spine-RR description Spine and RR peer-group
#       neighbor spine-RR update-source loopback 0
#       neighbor spine-RR ebgp-multihop 255
#       neighbor 10.147.253.132 peer-group spine-RR
#       neighbor 10.147.253.165 peer-group spine-RR
#       address-family l2vpn evpn
#           neighbor spine-RR send-community both
#           neighbor 10.147.253.132 activate
#           neighbor 10.147.253.165 activate
#       exit-address-family
- name: Configure the spine-RR peer group
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: spine-RR
    is_peer_group: true
    remote_as: 65000
    description: Spine and RR peer-group
    update_source: loopback0
    ebgp_multihop: 255
    address_families:
      - address_family: l2vpn_evpn
        send_community: both

- name: Configure the spine neighbors
  aoscx_bgp_neighbor:
    asn: 65000
    neighbors:
      - 10.147.253.132
      - 10.147.253.165
    peer_group: spine-RR
    address_families:
      - address_family: l2vpn_evpn
        activate: true

# Equivalent CLI configuration:
#   router bgp 65000
#       address-family l2vpn evpn
#           neighbor leaf route-reflector-client
#           neighbor leaf send-community both
#       exit-address-family
- name: Configure the leaf peer group as route reflector clients
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: leaf
    is_peer_group: true
    remote_as: 65000
    address_families:
      - address_family: l2vpn_evpn
        route_reflector_client: true
        send_community: both

- name: Add the leafs to the leaf peer group
  aoscx_bgp_neighbor:
    asn: 65000
    neighbors:
      - 10.147.253.170
      - 10.147.253.171
    peer_group: leaf
    address_families:
      - address_family: l2vpn_evpn
        activate: true

- name: Delete a neighbor
  aoscx_bgp_neighbor:
    asn: 65000
    neighbor: 10.147.253.165
    state: delete
"""

RETURN = r"""
changed:
  description: Whether a neighbor was created, modified or deleted.
  returned: always
  type: bool
"""

import ipaddress

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves.urllib.parse import unquote
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

AF_SETTINGS = (
    "activate",
    "send_community",
    "route_reflector_client",
    "next_hop_self",
    "next_hop_unchanged",
    "inbound_soft_reconfiguration",
)

# Settings that do not exist in some address families
UNSUPPORTED_AF_SETTINGS = {
    "l2vpn_evpn": ("next_hop_self", "inbound_soft_reconfiguration"),
    "ipv4_unicast": ("next_hop_unchanged",),
    "ipv6_unicast": ("next_hop_unchanged",),
}


def get_argument_spec():
    af_options = {
        "address_family": {
            "type": "str",
            "required": True,
            "choices": list(UNSUPPORTED_AF_SETTINGS),
        },
        "send_community": {
            "type": "str",
            "choices": ["both", "extended", "standard", "none"],
        },
    }
    for setting in AF_SETTINGS:
        af_options.setdefault(setting, {"type": "bool"})
    return {
        "asn": {"type": "int", "required": True},
        "vrf": {"type": "str", "default": "default"},
        "neighbor": {"type": "str"},
        "neighbors": {"type": "list", "elements": "str"},
        "is_peer_group": {"type": "bool", "default": False},
        "peer_group": {"type": "str"},
        "remote_as": {"type": "int"},
        "description": {"type": "str"},
        "update_source": {"type": "str"},
        "ebgp_multihop": {"type": "int"},
        "shutdown": {"type": "bool"},
        "address_families": {
            "type": "list",
            "elements": "dict",
            "options": af_options,
        },
        "state": {
            "type": "str",
            "default": "create",
            "choices": ["create", "delete"],
        },
    }


def get_neighbor_names(params):
    if params["neighbor"] is not None:
        return [params["neighbor"]]
    return params["neighbors"]


def validate_params(ansible_module):
    params = ansible_module.params
    names = get_neighbor_names(params)
    if not 1 <= params["asn"] <= 4294967295:
        ansible_module.fail_json(msg="asn must be between 1 and 4294967295")
    if params["remote_as"] is not None and not (
        1 <= params["remote_as"] <= 4294967295
    ):
        ansible_module.fail_json(
            msg="remote_as must be between 1 and 4294967295"
        )
    if params["ebgp_multihop"] is not None and not (
        1 <= params["ebgp_multihop"] <= 255
    ):
        ansible_module.fail_json(msg="ebgp_multihop must be between 1 and 255")
    if not names:
        ansible_module.fail_json(msg="neighbors must not be empty")
    if len(set(names)) != len(names):
        ansible_module.fail_json(msg="Duplicate entries in neighbors")
    for name in names:
        # The name is interpolated into the REST URI
        if "/" in name or name in ("", ".", ".."):
            ansible_module.fail_json(msg="Invalid neighbor: {0}".format(name))
    if params["peer_group"] and params["peer_group"] in names:
        ansible_module.fail_json(
            msg="A neighbor cannot belong to itself as peer group"
        )
    if params["is_peer_group"] and params["peer_group"]:
        ansible_module.fail_json(
            msg="peer_group is not supported when is_peer_group is true"
        )
    seen = set()
    for entry in params["address_families"] or []:
        family = entry["address_family"]
        if family in seen:
            ansible_module.fail_json(msg="Duplicate address family: " + family)
        seen.add(family)
        for setting in UNSUPPORTED_AF_SETTINGS[family]:
            if entry[setting] is not None:
                ansible_module.fail_json(
                    msg="{0} is not supported for {1}".format(setting, family)
                )


def is_ip_address(value):
    try:
        ipaddress.ip_address("{0}".format(value))
    except ValueError:
        return False
    return True


def reference_name(reference):
    """Name of a referenced resource, given as {name: uri} or as an uri."""
    if not reference:
        return None
    if isinstance(reference, dict):
        return next(iter(reference))
    if isinstance(reference, str):
        return unquote(reference.rstrip("/").rsplit("/", 1)[-1])
    # pyaoscx object
    return getattr(reference, "name", None) or getattr(
        reference, "ip_or_ifname_or_group_name", None
    )


def read_is_peer_group(neighbor):
    """
    is_peer_group can only be set on creation, so the switch does not return
    it with the writable selector used by pyaoscx: read it separately.
    """
    import json

    from pyaoscx.exceptions.generic_op_error import GenericOperationError

    uri = "{0}/{1}".format(
        neighbor.base_uri, neighbor.ip_or_ifname_or_group_name
    )
    response = neighbor.session.request(
        "GET",
        uri,
        params={"selector": "configuration", "attributes": "is_peer_group"},
    )
    if response.status_code != 200:
        raise GenericOperationError(response.text, response.status_code)
    return bool(json.loads(response.text).get("is_peer_group", False))


class NeighborConfig(object):
    """Compute and apply the changes of a BGP neighbor."""

    def __init__(self, ansible_module, session, bgp_router, neighbor):
        self.module = ansible_module
        self.params = ansible_module.params
        self.session = session
        self.bgp_router = bgp_router
        self.neighbor = neighbor
        self.changes = {}

    def set(self, key, value, current):
        if current != value:
            self.changes[key] = value

    def compute(self):
        params = self.params
        neighbor = self.neighbor
        for key in ("remote_as", "description", "shutdown"):
            if params[key] is not None:
                self.set(key, params[key], getattr(neighbor, key, None))
        if params["ebgp_multihop"] is not None:
            # The switch reports 1 when ebgp-multihop is not configured
            current = getattr(neighbor, "ebgp_hop_count", None) or 1
            self.set("ebgp_hop_count", params["ebgp_multihop"], current)

        if params["peer_group"] is not None:
            self.compute_peer_group(params["peer_group"])
        if params["update_source"] is not None:
            self.compute_update_source(params["update_source"].strip())

        for entry in params["address_families"] or []:
            family = entry["address_family"].replace("_", "-")
            for setting in AF_SETTINGS:
                if entry[setting] is None:
                    continue
                current = dict(getattr(neighbor, setting, None) or {})
                if current.get(family) != entry[setting]:
                    merged = self.changes.get(setting, current)
                    merged[family] = entry[setting]
                    self.changes[setting] = merged

    def compute_peer_group(self, name):
        current = reference_name(
            getattr(self.neighbor, "bgp_peer_group", None)
        )
        if name == "":
            if current is not None:
                self.changes["bgp_peer_group"] = None
            return
        if current == name:
            return
        BgpNeighbor = self.session.api.get_module_class(
            self.session, "BgpNeighbor"
        )
        peer_group = BgpNeighbor(
            self.session, name, parent_bgp_router=self.bgp_router
        )
        if not self.module.check_mode:
            # Fails if the peer group does not exist
            self.read(peer_group, "peer group {0}".format(name))
            if not read_is_peer_group(peer_group):
                self.module.fail_json(
                    msg="{0} is not a peer group".format(name)
                )
        self.changes["bgp_peer_group"] = self.session.api.get_index(peer_group)

    def compute_update_source(self, source):
        current_ip = getattr(self.neighbor, "update_source", None) or None
        current_interface = reference_name(
            getattr(self.neighbor, "local_interface", None)
        )
        ip_source = None
        interface = None
        if is_ip_address(source):
            ip_source = source
        elif source:
            interface = source.replace(" ", "")

        if current_ip != ip_source:
            self.changes["update_source"] = ip_source
        if current_interface != interface:
            if interface is None:
                self.changes["local_interface"] = None
                return
            Interface = self.session.api.get_module_class(
                self.session, "Interface"
            )
            port = Interface(self.session, interface)
            if not self.module.check_mode:
                self.read(port, "interface {0}".format(interface))
            self.changes["local_interface"] = port

    def read(self, resource, label):
        from pyaoscx.exceptions.generic_op_error import GenericOperationError

        try:
            resource.get()
        except GenericOperationError as e:
            if e.response_code == 404:
                self.module.fail_json(msg="Could not find " + label)
            raise

    def apply(self):
        neighbor = self.neighbor
        if neighbor.materialized and not self.changes:
            return False
        if self.module.check_mode:
            return True
        if not neighbor.materialized:
            neighbor.is_peer_group = self.params["is_peer_group"]
            self.changes.setdefault("is_peer_group", neighbor.is_peer_group)
        for key, value in self.changes.items():
            setattr(neighbor, key, value)
            if key not in neighbor.config_attrs:
                neighbor.config_attrs.append(key)
        neighbor.apply()
        return True


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        mutually_exclusive=[["neighbor", "neighbors"]],
        required_one_of=[["neighbor", "neighbors"]],
        supports_check_mode=True,
    )
    validate_params(ansible_module)

    params = ansible_module.params
    vrf_name = params["vrf"]
    asn = params["asn"]
    names = get_neighbor_names(params)
    state = params["state"]

    result = dict(changed=False)

    try:
        from pyaoscx.exceptions.generic_op_error import GenericOperationError
        from pyaoscx.exceptions.pyaoscx_error import PyaoscxError
    except ImportError as e:
        ansible_module.fail_json(msg=str(e))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    def get_or_fail(resource, missing_msg):
        try:
            resource.get()
        except GenericOperationError as e:
            if e.response_code != 404 or resource.materialized:
                ansible_module.fail_json(msg=str(e))
            if missing_msg:
                ansible_module.fail_json(msg=missing_msg)
        except PyaoscxError as e:
            ansible_module.fail_json(msg=str(e))

    def require_parent(resource, missing_msg):
        get_or_fail(resource, None)
        if resource.materialized:
            return
        if state == "delete":
            # No parent, so no neighbor to delete
            ansible_module.exit_json(**result)
        if ansible_module.check_mode:
            # The parent may be created by a previous task of the playbook
            result["changed"] = True
            ansible_module.exit_json(**result)
        ansible_module.fail_json(msg=missing_msg)

    Vrf = session.api.get_module_class(session, "Vrf")
    vrf = Vrf(session, vrf_name)
    require_parent(vrf, "VRF {0} does not exist".format(vrf_name))

    BgpRouter = session.api.get_module_class(session, "BgpRouter")
    bgp_router = BgpRouter(session, asn, parent_vrf=vrf)
    require_parent(
        bgp_router,
        "BGP router {0} does not exist in VRF {1}, create it with "
        "aoscx_bgp_router first".format(asn, vrf_name),
    )

    BgpNeighbor = session.api.get_module_class(session, "BgpNeighbor")
    neighbors = []
    for name in names:
        neighbor = BgpNeighbor(session, name, parent_bgp_router=bgp_router)
        get_or_fail(neighbor, None)
        neighbors.append(neighbor)

    try:
        if state == "delete":
            for neighbor in neighbors:
                if neighbor.materialized:
                    if not ansible_module.check_mode:
                        neighbor.delete()
                    result["changed"] = True
        else:
            # Read and validate every neighbor before the first write
            configs = []
            for neighbor in neighbors:
                if neighbor.materialized and params[
                    "is_peer_group"
                ] != read_is_peer_group(neighbor):
                    ansible_module.fail_json(
                        msg="is_peer_group cannot be changed on an existing "
                        "neighbor, delete {0} first".format(
                            neighbor.ip_or_ifname_or_group_name
                        )
                    )
                config = NeighborConfig(
                    ansible_module, session, bgp_router, neighbor
                )
                config.compute()
                configs.append(config)
            for config in configs:
                if config.apply():
                    result["changed"] = True
    except PyaoscxError as e:
        ansible_module.fail_json(msg=str(e), **result)

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
