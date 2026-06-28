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


def main():
    module_args = dict(
        vlan=dict(type="int", required=True),
        rd=dict(type="str", default=None),
        import_route_targets=dict(type="list", elements="str", default=None),
        export_route_targets=dict(type="list", elements="str", default=None),
        redistribute=dict(type="dict", default=None),
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
