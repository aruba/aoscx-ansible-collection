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
module: aoscx_evpn_vlan_aware_bundle
version_added: "4.6.0"
short_description: Create, update or delete an EVPN VLAN-aware bundle on AOS-CX.
description: >
  This module provides configuration management of EVPN VLAN-aware bundles on
  AOS-CX devices. A bundle groups several VLANs under a single EVPN instance
  that shares the same route distinguisher and route targets. The member VLANs
  are mapped through their Ethernet tags. The bundle lives under
  system/evpn/evpn_vlan_aware_bundles and is indexed by its name.
author: Aruba Networks (@ArubaNetworks)
options:
  bundle_name:
    description: Name of the EVPN VLAN-aware bundle.
    type: str
    required: true
  rd:
    description: >
      Route distinguisher of the bundle, for example C(65000:1) or
      C(1.1.1.1:1). When omitted it is left unchanged.
    type: str
    required: false
  import_route_targets:
    description: >
      List of import route targets for the bundle. The supplied list fully
      replaces the existing import route targets. When omitted they are left
      unchanged.
    type: list
    elements: str
    required: false
  export_route_targets:
    description: >
      List of export route targets for the bundle. The supplied list fully
      replaces the existing export route targets. When omitted they are left
      unchanged.
    type: list
    elements: str
    required: false
  redistribute:
    description: >
      Redistribution settings of the bundle, for example
      C({host-route: true}). Only the supplied keys are reconciled; existing
      keys that are not mentioned are preserved. When omitted it is left
      unchanged.
    type: dict
    required: false
  disable:
    description: >
      Whether the bundle is administratively disabled. When omitted it is left
      unchanged.
    type: bool
    required: false
  vlans:
    description: >
      Member VLANs of the bundle with their Ethernet tags. The supplied list
      fully replaces the set of member VLANs. When omitted the VLANs are left
      unchanged; an empty list removes all member VLANs. The VLANs must already
      exist on the device. Ignored when I(state) is C(delete).
    type: list
    elements: dict
    required: false
    suboptions:
      id:
        description: VLAN ID of the member VLAN.
        type: int
        required: true
      ethernet_tag:
        description: >
          Ethernet tag mapped to the VLAN. When omitted it defaults to the
          VLAN ID.
        type: int
        required: false
  state:
    description: Create, update or delete the EVPN VLAN-aware bundle.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Create an EVPN VLAN-aware bundle with two member VLANs
  arubanetworks.aoscx.aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    rd: "65000:1"
    import_route_targets:
      - "65000:1"
    export_route_targets:
      - "65000:1"
    vlans:
      - id: 206
      - id: 207
        ethernet_tag: 100
    state: create

- name: Replace the member VLANs of a bundle
  arubanetworks.aoscx.aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    vlans:
      - id: 206
    state: update

- name: Remove all member VLANs from a bundle
  arubanetworks.aoscx.aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    vlans: []
    state: update

- name: Delete an EVPN VLAN-aware bundle
  arubanetworks.aoscx.aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the EVPN VLAN-aware bundle was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def build_vlan_tags(session, ansible_module, vlans):
    """Resolve the desired vlan_ethernet_tags {vlan_uri: ethernet_tag} map.

    Validates that every member VLAN exists and builds the URI-keyed map the
    REST API expects.
    """
    tags = {}
    for entry in vlans:
        vlan_id = entry["id"]
        ethernet_tag = entry.get("ethernet_tag")
        if ethernet_tag is None:
            ethernet_tag = vlan_id
        vlan_obj = session.api.get_module(session, "Vlan", vlan_id)
        try:
            vlan_obj.get()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not find VLAN {0}: {1}".format(vlan_id, str(e))
            )
        uri = "{0}system/vlans/{1}".format(
            session.resource_prefix, vlan_id
        )
        tags[uri] = ethernet_tag
    return tags


def normalize_tags(tags):
    """Reduce a {vlan_uri: tag} map to a comparable {vlan_id: tag} dict."""
    normalized = {}
    for uri, tag in (tags or {}).items():
        vlan_id = str(uri).rstrip("/").rsplit("/", 1)[-1]
        normalized[vlan_id] = tag
    return normalized


def main():
    module_args = dict(
        bundle_name=dict(type="str", required=True),
        rd=dict(type="str", required=False, default=None),
        import_route_targets=dict(
            type="list", elements="str", required=False, default=None
        ),
        export_route_targets=dict(
            type="list", elements="str", required=False, default=None
        ),
        redistribute=dict(type="dict", required=False, default=None),
        disable=dict(type="bool", required=False, default=None),
        vlans=dict(
            type="list",
            elements="dict",
            required=False,
            default=None,
            options=dict(
                id=dict(type="int", required=True),
                ethernet_tag=dict(type="int", required=False, default=None),
            ),
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    bundle_name = ansible_module.params["bundle_name"]
    rd = ansible_module.params["rd"]
    import_route_targets = ansible_module.params["import_route_targets"]
    export_route_targets = ansible_module.params["export_route_targets"]
    redistribute = ansible_module.params["redistribute"]
    disable = ansible_module.params["disable"]
    vlans = ansible_module.params["vlans"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    if bundle_name in ("", ".", "..") or "/" in bundle_name:
        ansible_module.fail_json(
            msg="Invalid bundle name: {0}".format(bundle_name)
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        bundle = session.api.get_module(
            session, "EvpnVlanAwareBundle", bundle_name
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support EVPN VLAN-aware "
                "bundles. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        bundle.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # ----------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                bundle.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete bundle: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # Resolve the desired member VLANs before mutating anything.
    desired_tags = None
    if vlans is not None:
        desired_tags = build_vlan_tags(session, ansible_module, vlans)

    # ----------------------------------------------------------- check mode
    if ansible_module.check_mode:
        result["changed"] = (not exists) or any(
            value is not None
            for value in (
                rd,
                import_route_targets,
                export_route_targets,
                redistribute,
                disable,
                vlans,
            )
        )
        ansible_module.exit_json(**result)

    # ----------------------------------------------------------- create/update
    created = False
    if not exists:
        try:
            bundle.create()
            bundle.get(selector="writable")
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not create bundle: {0}".format(str(e))
            )
        created = True

    needs_update = False

    if rd is not None and getattr(bundle, "rd", None) != rd:
        needs_update = True
        bundle.rd = rd

    if import_route_targets is not None:
        current = getattr(bundle, "import_route_targets", None) or []
        if sorted(current) != sorted(import_route_targets):
            needs_update = True
            bundle.import_route_targets = import_route_targets

    if export_route_targets is not None:
        current = getattr(bundle, "export_route_targets", None) or []
        if sorted(current) != sorted(export_route_targets):
            needs_update = True
            bundle.export_route_targets = export_route_targets

    if redistribute is not None:
        current = dict(getattr(bundle, "redistribute", None) or {})
        merged = dict(current)
        merged.update(redistribute)
        if merged != current:
            needs_update = True
            bundle.redistribute = merged

    if disable is not None and getattr(bundle, "disable", None) != disable:
        needs_update = True
        bundle.disable = disable

    if desired_tags is not None:
        current_tags = getattr(bundle, "vlan_ethernet_tags", None) or {}
        if normalize_tags(current_tags) != normalize_tags(desired_tags):
            needs_update = True
            bundle.vlan_ethernet_tags = desired_tags

    if needs_update:
        try:
            bundle.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update bundle: {0}".format(str(e))
            )

    result["changed"] = created or needs_update
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
