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
module: aoscx_evpn_vlan
version_added: "4.6.0"
short_description: Create, Update or Delete a per-VLAN EVPN entry on AOS-CX
description: >
  This module provides configuration management of per-VLAN EVPN (Ethernet
  VPN) settings on AOS-CX devices. Each entry binds a VLAN to its EVPN
  instance and configures its route distinguisher, import and export route
  targets, and redistribution. The VLAN must already exist on the device.
author: Aruba Networks (@ArubaNetworks)
options:
  vlan:
    description: >
      ID of the VLAN the EVPN instance is bound to. The VLAN must already
      exist on the device.
    required: true
    type: int
  rd:
    description: >
      Route distinguisher for the VLAN's EVPN instance, for example
      C(65000:204) or C(auto). When omitted it is left unchanged. Ignored
      when I(state) is C(delete).
    required: false
    type: str
  import_route_targets:
    description: >
      List of import route targets for the VLAN's EVPN instance. The list is
      compared regardless of order. When omitted it is left unchanged.
      Ignored when I(state) is C(delete).
    required: false
    type: list
    elements: str
  export_route_targets:
    description: >
      List of export route targets for the VLAN's EVPN instance. The list is
      compared regardless of order. When omitted it is left unchanged.
      Ignored when I(state) is C(delete).
    required: false
    type: list
    elements: str
  redistribute:
    description: >
      Dictionary controlling redistribution for the VLAN's EVPN instance,
      for example C({"host-route": true}). Only the keys you provide are
      reconciled; other keys are preserved. When omitted it is left
      unchanged. Ignored when I(state) is C(delete).
    required: false
    type: dict
  arp_suppression:
    description: >
      ARP suppression for this VLAN (CLI C(arp-suppression enable|disable) in
      the C(evpn) / C(vlan) context). C(enable) and C(disable) override the
      global C(arp_suppression_enable) of M(arubanetworks.aoscx.aoscx_evpn),
      C(global) removes the override so that the VLAN follows the global
      setting again. Cannot be enabled together with
      I(arp_suppression_extended). When omitted it is left unchanged. Ignored
      when I(state) is C(delete). Requires a pyaoscx version providing
      C(EvpnVlan.set_suppression()).
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  arp_suppression_extended:
    description: >
      ARP suppression extended for this VLAN (CLI
      C(arp-suppression-extended enable|disable)). It also suppresses on L2
      VLANs and not only on active gateway SVIs. Same values and behavior as
      I(arp_suppression), the global setting is
      C(arp_suppression_extended_enable) of
      M(arubanetworks.aoscx.aoscx_evpn). Cannot be enabled together with
      I(arp_suppression). When omitted it is left unchanged. Ignored when
      I(state) is C(delete).
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  nd_suppression:
    description: >
      Neighbor Discovery (ND) suppression for this VLAN (CLI
      C(nd-suppression enable|disable)). Same values and behavior as
      I(arp_suppression), the global setting is C(nd_suppression_enable) of
      M(arubanetworks.aoscx.aoscx_evpn). Cannot be enabled together with
      I(nd_suppression_extended). When omitted it is left unchanged. Ignored
      when I(state) is C(delete).
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  nd_suppression_extended:
    description: >
      ND suppression extended for this VLAN (CLI
      C(nd-suppression-extended enable|disable)). Same values and behavior
      as I(arp_suppression_extended), the global setting is
      C(nd_suppression_extended_enable) of
      M(arubanetworks.aoscx.aoscx_evpn). Cannot be enabled together with
      I(nd_suppression). When omitted it is left unchanged. Ignored when
      I(state) is C(delete).
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  arp_suppression_exclude:
    description: >
      IPv4 addresses excluded from ARP suppression, whose ARP requests are
      flooded in the fabric (CLI C(arp-suppression exclude <ip>)). The list
      replaces the current one and is compared regardless of order, an empty
      list removes all the exclusions. At most 256 addresses. When omitted it
      is left unchanged. Ignored when I(state) is C(delete).
    required: false
    type: list
    elements: str
  arp_suppression_extended_exclude:
    description: >
      IPv4 addresses excluded from ARP suppression extended. Same behavior as
      I(arp_suppression_exclude).
    required: false
    type: list
    elements: str
  nd_suppression_exclude:
    description: >
      IPv6 addresses excluded from ND suppression (CLI
      C(nd-suppression exclude <ip>)). Same behavior as
      I(arp_suppression_exclude).
    required: false
    type: list
    elements: str
  nd_suppression_extended_exclude:
    description: >
      IPv6 addresses excluded from ND suppression extended. Same behavior as
      I(arp_suppression_exclude).
    required: false
    type: list
    elements: str
  state:
    description: Create, update or delete the per-VLAN EVPN entry.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create an EVPN instance for VLAN 204
  aoscx_evpn_vlan:
    vlan: 204
    rd: "65000:204"
    import_route_targets:
      - "65000:204"
    export_route_targets:
      - "65000:204"

- name: Update the route distinguisher of an EVPN VLAN
  aoscx_evpn_vlan:
    vlan: 204
    state: update
    rd: "65001:204"

- name: Configure redistribution for an EVPN VLAN
  aoscx_evpn_vlan:
    vlan: 204
    redistribute:
      host-route: true

- name: Delete an EVPN VLAN entry
  aoscx_evpn_vlan:
    vlan: 204
    state: delete

- name: Enable ARP suppression on VLAN 204 whatever the global setting is
  aoscx_evpn_vlan:
    vlan: 204
    arp_suppression: enable
    arp_suppression_exclude:
      - 10.204.0.1
      - 10.204.0.2

- name: Migrate VLAN 204 to ARP and ND suppression extended
  aoscx_evpn_vlan:
    vlan: 204
    arp_suppression: disable
    arp_suppression_extended: enable
    nd_suppression_extended: enable
    nd_suppression_extended_exclude:
      - "fd00:204::1"

- name: Follow the global ARP suppression again and remove the exclusions
  aoscx_evpn_vlan:
    vlan: 204
    arp_suppression: global
    arp_suppression_exclude: []
"""

RETURN = r"""
changed:
  description: Whether the per-VLAN EVPN entry was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

# VLAN IDs are 12-bit values, 1 to 4094 are usable.
MIN_VLAN_ID = 1
MAX_VLAN_ID = 4094

# SDK suppression feature -> (mode option, exclusion list option)
SUPPRESSION_OPTIONS = {
    "arp": ("arp_suppression", "arp_suppression_exclude"),
    "arp_extended": (
        "arp_suppression_extended",
        "arp_suppression_extended_exclude",
    ),
    "nd": ("nd_suppression", "nd_suppression_exclude"),
    "nd_extended": (
        "nd_suppression_extended",
        "nd_suppression_extended_exclude",
    ),
}


def apply_suppression(evpn_vlan, params):
    """
    Set the suppression modes and exclusion lists supplied by the user on the
    EvpnVlan object, nothing is sent to the switch.

    :return: True if one of them differs from the current configuration.
    """
    changed = False
    for feature, (mode_option, exclude_option) in SUPPRESSION_OPTIONS.items():
        mode = params[mode_option]
        if mode is not None:
            # "global" removes the override of the global setting
            value = None if mode == "global" else mode
            if evpn_vlan.set_suppression(feature, value):
                changed = True
        addresses = params[exclude_option]
        if addresses is not None:
            if evpn_vlan.set_suppression_ip_exemption(feature, addresses):
                changed = True
    return changed


def main():
    module_args = dict(
        vlan=dict(type="int", required=True),
        rd=dict(type="str", default=None),
        import_route_targets=dict(type="list", elements="str", default=None),
        export_route_targets=dict(type="list", elements="str", default=None),
        redistribute=dict(type="dict", default=None),
        arp_suppression=dict(
            type="str", default=None, choices=["enable", "disable", "global"]
        ),
        arp_suppression_extended=dict(
            type="str", default=None, choices=["enable", "disable", "global"]
        ),
        nd_suppression=dict(
            type="str", default=None, choices=["enable", "disable", "global"]
        ),
        nd_suppression_extended=dict(
            type="str", default=None, choices=["enable", "disable", "global"]
        ),
        arp_suppression_exclude=dict(
            type="list", elements="str", default=None
        ),
        arp_suppression_extended_exclude=dict(
            type="list", elements="str", default=None
        ),
        nd_suppression_exclude=dict(type="list", elements="str", default=None),
        nd_suppression_extended_exclude=dict(
            type="list", elements="str", default=None
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    vlan = ansible_module.params["vlan"]
    rd = ansible_module.params["rd"]
    import_route_targets = ansible_module.params["import_route_targets"]
    export_route_targets = ansible_module.params["export_route_targets"]
    redistribute = ansible_module.params["redistribute"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    suppression_requested = any(
        ansible_module.params[option] is not None
        for options in SUPPRESSION_OPTIONS.values()
        for option in options
    )
    if not MIN_VLAN_ID <= vlan <= MAX_VLAN_ID:
        ansible_module.fail_json(
            msg="vlan must be between {0} and {1}.".format(
                MIN_VLAN_ID, MAX_VLAN_ID
            )
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        evpn_vlan = session.api.get_module(session, "EvpnVlan", vlan)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support EVPN. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        evpn_vlan.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                evpn_vlan.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete EVPN VLAN: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # The per-VLAN EVPN entry references the VLAN resource, so it must exist.
    try:
        vlan_obj = session.api.get_module(session, "Vlan", vlan)
        vlan_obj.get()
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not find VLAN {0}: {1}".format(vlan, str(e))
        )

    # ------------------------------------------------------- create / update
    if suppression_requested and not hasattr(
        evpn_vlan, "set_suppression_ip_exemption"
    ):
        ansible_module.fail_json(
            msg=(
                "The suppression options require a pyaoscx version "
                "providing EvpnVlan.set_suppression() and "
                "EvpnVlan.set_suppression_ip_exemption(). Upgrade pyaoscx."
            )
        )

    if not exists:
        kwargs = {}
        if rd is not None:
            kwargs["rd"] = rd
        if import_route_targets is not None:
            kwargs["import_route_targets"] = import_route_targets
        if export_route_targets is not None:
            kwargs["export_route_targets"] = export_route_targets
        if redistribute is not None:
            kwargs["redistribute"] = redistribute
        evpn_vlan = session.api.get_module(session, "EvpnVlan", vlan, **kwargs)
        try:
            if suppression_requested:
                apply_suppression(evpn_vlan, ansible_module.params)
                evpn_vlan.check_suppression()
        except Exception as e:
            ansible_module.fail_json(
                msg="Invalid suppression configuration: {0}".format(str(e))
            )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                evpn_vlan.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create EVPN VLAN: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False

    if rd is not None and getattr(evpn_vlan, "rd", None) != rd:
        changed = True
        evpn_vlan.rd = rd

    # Route targets are unordered, compare them regardless of order.
    if import_route_targets is not None:
        current = getattr(evpn_vlan, "import_route_targets", None) or []
        if sorted(current) != sorted(import_route_targets):
            changed = True
            evpn_vlan.import_route_targets = import_route_targets

    if export_route_targets is not None:
        current = getattr(evpn_vlan, "export_route_targets", None) or []
        if sorted(current) != sorted(export_route_targets):
            changed = True
            evpn_vlan.export_route_targets = export_route_targets

    # redistribute is a dictionary; only reconcile the keys provided and
    # preserve any existing keys the user did not mention.
    if redistribute is not None:
        current = dict(getattr(evpn_vlan, "redistribute", None) or {})
        merged = dict(current)
        merged.update(redistribute)
        if merged != current:
            changed = True
            evpn_vlan.redistribute = merged

    if suppression_requested:
        try:
            if apply_suppression(evpn_vlan, ansible_module.params):
                changed = True
            evpn_vlan.check_suppression()
        except Exception as e:
            ansible_module.fail_json(
                msg="Invalid suppression configuration: {0}".format(str(e))
            )

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            evpn_vlan.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update EVPN VLAN: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
