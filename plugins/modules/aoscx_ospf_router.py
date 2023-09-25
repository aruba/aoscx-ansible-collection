#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_ospf_router
version_added: "4.1.0"
short_description: Create, Update or Delete OSPF configuration on AOS-CX
description: >
  This modules provides configuration management of OSPF Routers on AOS-CX
  devices.
author: Aruba Networks (@ArubaNetworks)
options:
  state:
    description: Create, update, or delete the OSPF Router.
    required: false
    choices:
      - create
      - update
      - delete
      - override
    default: create
    type: str
  vrf:
    description: >
      The VRF the OSPF Router will belong to once created. If none provided,
      it will be in the Default VRF. If the OSPF Router is created and the
      user wants to change its VRF, the user must first delete the OSPF
      Router, and then recreate it in the desired VRF.
    type: str
    required: true
  instance_tag:
    description: OSPF Process ID, in [0, 63]
    required: true
    type: int
  active_interfaces:
    description: >
      The list of the active-interfaces. If "passive_interface_default" is set
      to "false", then this list should be empty.
    type: list
    required: false
    elements: str
  admin_router_id:
    description: >
      The router identifier configured for the OSPF instance. The router ID
      MUST be unique within the entire Autonomous System. If admin_router_id is
      present, the same will be elected as active_router_id. The router ID is
      in IPv4 address format.
    type: str
    required: false
  auto_cost_ref_bw:
    description: >
      The reference bandwidth, Mbits/second, for interface cost calculations.
      Must be in [1, 4000000].
    required: false
    type: int
  bfd_all_interfaces_enable:
    description: Enables BFD on all interfaces involved in this OSPF Router
    required: false
    type: bool
  default_originate:
    description: >
      Criteria for redistribution of the default routes into the OSPF domain:
      disable: no default route should be advertised.
      originate: advertise default route if it exists in the routing table.
      always_originate: always advertise default route, regardless of its
      presence in the routing table.
    required: false
    type: str
    choices:
      - disable
      - originate
      - always_originate
  distance:
    description: Administrative distances.
    required: false
    type: dict
    suboptions:
      all:
        description: >
          The administrative distance applies to all types of routes if not
          configured specifically for certain types. Must be in [1, 255].
        required: false
        type: int
      external:
        description: >
          The administrative distance applies to routes of type external. Must
          be in [1, 255].
        required: false
        type: int
      inter_area:
        description: >
          The administrative distance applies to routes of type inter-area.
          Must be in [1, 255].
        required: false
        type: int
      intra_area:
        description: >
          The administrative distance applies to routes of type intra-area.
          Must be in [1, 255].
        required: false
        type: int
  gr_ignore_lost_interface:
    description: >
      Specifies whether to ignore OSPF interfaces that have gone down just
      prior to the restart event.
    required: false
    type: bool
  helper_disable:
    description: >
      Indicates whether OSPF will help a neighbor undergoing hitless restart on
      this interface.
    required: false
    type: bool
  lsa_arrival:
    description: >
      Minimum wait time in milliseconds before same LSAs received from a peer
      are processed. Must be in [0, 600000]
    required: false
    type: int
  lsa_throttle:
    description: Timers related to LSA throttling.
    type: dict
    required: false
    suboptions:
      hold_time:
        description: >
          The base value of hold_time in milliseconds until when a next
          instance of the same LSA generation will be delayed. This will double
          each time the same LSA needs to be generated until it reaches the
          max_wait_time after which it will start with the base time again.
          When set to 0, the minimum time between same LSA regeneration is not
          increased.
        required: false
        type: int
      max_wait_time:
        description: >
          Maximum time until when next instance of same LSA generation will be
          delayed. When set to 0, the maximum time between same LSA
          regeneration is not increased.
        required: false
        type: int
      start_time:
        description: >
          The initial wait time in milliseconds after which LSAs will be
          generated. When set to 0, the LSAs are generated without any delay.
        required: false
        type: int
  maximum_paths:
    description: >
      Maximum number of equal cost paths that are stored for each destination
      in the routing table.
    required: false
    type: int
  other_config:
    description: Miscellaneous configuration
    required: false
    type: dict
    suboptions:
      default_metric:
        description: The default cost metric for the distributed routes.
        required: false
        type: int
      ospf_rfc1583_compatible:
        description: >
          This determines whether RFC1583 compatibility mode is enabled or not.
          If value is false then the path preference algorithm is calculated as
          defined by RFC2328.
        required: false
        type: bool
  passive_interfaces:
    description: >
      List of passive interfaces. If "passive_interface_default" is set to
      true, then this list should be empty.
    required: false
    type: list
    elements: str
  passive_interface_default:
    description: >
      This determines whether all interfaces should be set to passive by
      default.
    required: false
    type: bool
  protocol_disable:
    description: Disable this OSPF instance
    required: false
    type: bool
  redistribute:
    description: >
      From where to redistribute routes from other sources into this OSPF
      instance, if the same source also has a route map based filter
      associated with it, only the filtered routes will be redistributed
      into this instance.
    type: list
    elements: str
    choices:
      - connected
      - local_loopback
      - static
      - bgp
      - rip
  redistribute_ospf:
    description: >
      Redistribute routes from other OSPF instances into this OSPF instance. If
      the same instance also has a route map based filter associated with it,
      only the filtered routes will be redistributed into this instance.
    required: false
    type: list
    elements: str
  restart_interval:
    description: >
      If OSPF is attempting to undergo a graceful restart, this field specifies
      the length in seconds of grace period that should be requested from
      adjacent routers in grace LSAs. Must be in [5, 1800].
    required: false
    type: int
  snmp_traps:
    description: The configurations related to the OSPF SNMP traps.
    type: dict
    required: false
    suboptions:
      base:
        description: Enable all the base (non LSA) traps.
        type: bool
        required: true
      lsa:
        description: Enable all LSA traps.
        type: bool
        required: true
      throttle_num_traps:
        description: >
          Maximum number of traps to be generated per throttle window, must
          be in [0, 255].
        type: int
        required: true
      throttle_time_window:
        description: Maximum number of traps to be generated per throttle
          window, must be in [2, 60].
        type: int
        required: true
  spf_throttle:
    description: Timers related to SPF throttling.
    type: dict
    required: false
    suboptions:
      hold_time:
        description: >
          Exponential backoff time in milliseconds before the next SPF
          calculation can be scheduled, must be in [0, 600000].
        type: int
        required: false
      max_wait_time:
        description: Maximum duration of the exponential backoff time in
          milliseconds until when an SPF calculation can be delayed, must
          be in [0, 600000].
        type: int
        required: false
      start_time:
        description: Initial delay in milliseconds after which an SPF
          calculation will be triggered, must be in [0, 600000].
        type: int
        required: false
  strict_lsa_check_disable:
    description: >
      Specifies whether strict LSA checking is disabled for this OSPF router
      instance.
    type: bool
    required: false
  stub_router_adv:
    description: >
      Configurations related to stub router and router_lsa advertisements.
    type: dict
    required: false
    suboptions:
      admin_set:
        description: >
          This determines whether the stub router router_lsa advertisement is
          set administratively.
        required: false
        type: bool
      include_stub:
        description: >
          Determines whether the router should advertise maximum metric for
          stub links in router_lsa.
        type: bool
        required: true
      startup:
        description: >
          Determines whether the router should advertise stub router
          router_lsa on start-up. The delay, in seconds, is the duration
          for how long, after the reboot, stub router router_lsa should be
          advertised.
        type: int
        required: true
"""

EXAMPLES = """
---
- name: Create new OSPF Router
  aoscx_ospf_router:
    vrf: default
    instance_tag: 1

- name: >
    Create new OSPF Router, with bgp, and static as OSPF redistribution
    methods. Also set passive interfaces.
  aoscx_ospf_router:
    state: update
    vrf: default
    instance_tag: 1
    redistribute:
      - bgp
      - static
    passive_interface_default: false
    passive_interfaces:
      - 1/1/5
      - 1/1/6

- name: >
    Update OSPF Router, add connected to the redistribute methods list.
  aoscx_ospf_router:
    state: update
    vrf: default
    instance_tag: 1
    redistribute:
      - connected

- name: >
    Update OSPF Router, set redistribute to connected, and static only. This
    deletes bgp from the list and remove a previously configured passive
    interface (1/1/5).
  aoscx_ospf_router:
    state: override
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
      - static
    passive_interface_default: false
    passive_interfaces:
      - 1/1/6

- name: >
    Update OSPF Router, set redistribute to connected only. This deletes static
    from the list. Set an active interfaces and remove all passive interfaces.
  aoscx_ospf_router:
    state: override
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
    passive_interface_default: true
    passive_interfaces: []
    active_interfaces:
      - 1/1/6

- name: >
    Update OS

- name: Delete OSPF Router
  aoscx_ospf_router:
    state: delete
    vrf: default
    instance_tag: 1
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.ospf_router import OspfRouter
    from pyaoscx.vrf import Vrf

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def get_argument_spec():
    argument_spec = {
        "vrf": {
            "type": "str",
            "required": True,
        },
        "state": {
            "type": "str",
            "required": False,
            "choices": ["create", "update", "delete", "override"],
            "default": "create",
        },
        "instance_tag": {
            "required": True,
            "type": "int",
        },
        "active_interfaces": {
            "type": "list",
            "elements": "str",
            "required": False,
            "default": None,
        },
        "admin_router_id": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "auto_cost_ref_bw": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "bfd_all_interfaces_enable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "default_originate": {
            "type": "str",
            "required": False,
            "default": None,
            "choices": ["disable", "originate", "always_originate"],
        },
        "distance": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "all": {
                    "type": "int",
                    "required": False,
                },
                "external": {
                    "type": "int",
                    "required": False,
                },
                "inter_area": {
                    "type": "int",
                    "required": False,
                },
                "intra_area": {
                    "type": "int",
                    "required": False,
                },
            },
        },
        "gr_ignore_lost_interface": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "helper_disable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "lsa_arrival": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "lsa_throttle": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "hold_time": {
                    "type": "int",
                    "required": False,
                },
                "max_wait_time": {
                    "type": "int",
                    "required": False,
                },
                "start_time": {
                    "type": "int",
                    "required": False,
                },
            },
        },
        "maximum_paths": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "other_config": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "default_metric": {
                    "type": "int",
                    "required": False,
                },
                "ospf_rfc1583_compatible": {"type": "bool", "required": False},
            },
        },
        "passive_interfaces": {
            "type": "list",
            "required": False,
            "default": None,
            "elements": "str",
        },
        "passive_interface_default": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "protocol_disable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "redistribute": {
            "type": "list",
            "required": False,
            "default": None,
            "elements": "str",
            "choices": [
                "connected",
                "local_loopback",
                "static",
                "bgp",
                "rip",
            ],
        },
        "redistribute_ospf": {
            "type": "list",
            "required": False,
            "default": None,
            "elements": "str",
        },
        "restart_interval": {
            "required": False,
            "default": None,
            "type": "int",
        },
        "snmp_traps": {
            "required": False,
            "default": None,
            "type": "dict",
            "options": {
                "base": {"required": True, "type": "bool"},
                "lsa": {"required": True, "type": "bool"},
                "throttle_num_traps": {
                    "required": True,
                    "type": "int",
                },
                "throttle_time_window": {
                    "required": True,
                    "type": "int",
                },
            },
        },
        "spf_throttle": {
            "required": False,
            "default": None,
            "type": "dict",
            "options": {
                "hold_time": {
                    "type": "int",
                    "required": False,
                },
                "max_wait_time": {
                    "type": "int",
                    "required": False,
                },
                "start_time": {
                    "type": "int",
                    "required": False,
                },
            },
        },
        "strict_lsa_check_disable": {
            "required": False,
            "default": None,
            "type": "bool",
        },
        "stub_router_adv": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "admin_set": {"type": "bool", "required": False},
                "include_stub": {"type": "bool", "required": True},
                "startup": {"type": "int", "required": True},
            },
        },
    }
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(), supports_check_mode=True
    )

    result = {"changed": False}

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    # Get playbook's arguments
    params = ansible_module.params.copy()

    # Remove what is not a direct parameter for the router
    instance_tag = params.pop("instance_tag")
    vrf = params.pop("vrf")
    state = params.pop("state")

    session = get_pyaoscx_session(ansible_module)

    vrf = Vrf(session, vrf)
    try:
        vrf.get()
    except Exception:
        ansible_module.fail_json(msg="Could not find VRF, make sure it exists")

    # Avoid passing None, as it could delete config
    for key in list(params):
        if params[key] is None:
            del params[key]

    ospf_router = OspfRouter(session, instance_tag, vrf, **params)
    try:
        ospf_router.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            ospf_router.delete()
        result["changed"] = exists
        ansible_module.exit_json(**result)

    if not exists:
        ospf_router.create()
        result["changed"] = True
        ansible_module.exit_json(**result)

    overridable_lists = [
        "active_interfaces",
        "passive_interfaces",
        "redistribute",
    ]

    warnings = []

    passive_interface_default = params.get("passive_interface_default")
    passive_as_default = (
        passive_interface_default
        if passive_interface_default is not None
        else ospf_router.passive_interface_default
    )
    if passive_as_default:
        passive_interfaces = params.get("passive_interfaces")
        if passive_interfaces is not None and passive_interfaces != []:
            warnings.append(
                "Interfaces are passive by default, "
                "'passive_interfaces' should be empty"
            )
            params.pop("passive_interfaces")
            ospf_router.passive_interfaces = None
    else:
        active_interfaces = params.get("active_interfaces")
        if active_interfaces is not None and active_interfaces != []:
            warnings.append(
                "Interfaces are active by default, "
                "'active_interfaces' should be empty"
            )
            params.pop("active_interfaces")
            ospf_router.active_interfaces = None

    for olist in overridable_lists:
        if olist not in params:
            continue
        _olist = params.pop(olist)
        present = getattr(ospf_router, olist)
        if olist != "redistribute":
            present = [i.name for i in present]
        if state in ["override"]:
            result["changed"] |= set(_olist) != set(present)
        else:
            _olist = list(set(_olist) | set(present))
            result["changed"] |= bool(set(_olist) - set(present))
        setattr(ospf_router, olist, _olist)

    for key, value in params.items():
        present = getattr(ospf_router, key)
        if present != value:
            result["changed"] = True
        setattr(ospf_router, key, value)
    if result["changed"]:
        ospf_router.apply()
    if warnings:
        result["warnings"] = warnings
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
