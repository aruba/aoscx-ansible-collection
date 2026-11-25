#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
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
module: aoscx_vrf
version_added: "2.8.0"
short_description: Manage VRF configuration on AOS-CX
description: >
  This module provides configuration management of VRFs on AOS-CX devices.
  It can also manage the VRF route distinguisher and the import/export route
  targets per address family (EVPN, IPv4 unicast and IPv6 unicast).
author: Aruba Networks (@ArubaNetworks)
notes:
  - EVPN route targets are stored on the VRF itself, IPv4/IPv6 unicast route
    targets on the VRF address family sub-resource. The module hides this
    difference behind the O(address_families) option.
  - Route target order and duplicates are ignored when checking idempotency.
  - Updating IPv4/IPv6 unicast route targets on an existing address family
    requires a pyaoscx release that includes the VrfAddressFamily PUT fix.
options:
  name:
    description: The name of the VRF
    required: true
    type: str
  state:
    description: Create or update the VRF, or delete it.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
  rd:
    description:
      - Route distinguisher in ASN:nn or IPv4:nn format.
      - Applies to the entire VRF and is left unchanged when omitted.
      - Used only with O(state=create).
    type: str
  address_families:
    description:
      - Route targets to manage by address family. Omitted families are left unchanged.
      - Use ASN:nn for route targets. EVPN also accepts IPv4:nn and V(auto).
      - Used only with O(state=create).
    type: list
    elements: dict
    suboptions:
      address_family:
        description: Address family to configure. Specify each family at most once.
        required: true
        type: str
        choices: [evpn, ipv4_unicast, ipv6_unicast]
      import_route_targets:
        description:
          - Route targets to import. At least one of the import or export lists is required per family.
          - Replaces the import list for this family. Use an empty list to clear it or omit it to preserve it.
        type: list
        elements: str
      export_route_targets:
        description:
          - Route targets to export.
          - Replaces the export list for this family. Use an empty list to clear it or omit it to preserve it.
        type: list
        elements: str
"""

EXAMPLES = """
- name: Create a VRF
  aoscx_vrf:
    name: red
    state: create

# Equivalent CLI:
#   vrf CAMPUS
#       rd 10.140.253.13:20000
#       route-target export 1:1 evpn
#       route-target export 65001:20000 evpn
#       route-target import 1:1 evpn
#       route-target import 65001:20000 evpn
- name: Configure a VRF with an RD and EVPN route targets
  arubanetworks.aoscx.aoscx_vrf:
    name: CAMPUS
    rd: "10.140.253.13:20000"
    address_families:
      - address_family: evpn
        export_route_targets: ["1:1", "65001:20000"]
        import_route_targets: ["1:1", "65001:20000"]

- name: Use auto-generated EVPN route targets
  arubanetworks.aoscx.aoscx_vrf:
    name: CAMPUS
    address_families:
      - address_family: evpn
        import_route_targets: [auto]
        export_route_targets: [auto]

# Equivalent CLI:
#   vrf BLUE
#       rd 65001:100
#       address-family ipv4 unicast
#           route-target import 65001:100
#           route-target export 65001:100
#       address-family ipv6 unicast
#           route-target import 65001:100
- name: Configure IPv4 and IPv6 unicast route targets
  arubanetworks.aoscx.aoscx_vrf:
    name: BLUE
    rd: "65001:100"
    address_families:
      - address_family: ipv4_unicast
        import_route_targets: ["65001:100"]
        export_route_targets: ["65001:100"]
      - address_family: ipv6_unicast
        import_route_targets: ["65001:100"]

- name: Remove the EVPN export route targets, keep the import ones
  arubanetworks.aoscx.aoscx_vrf:
    name: CAMPUS
    address_families:
      - address_family: evpn
        export_route_targets: []

- name: Delete a VRF
  aoscx_vrf:
    name: red
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
    pyaoscx_error_message,
)


def get_argument_spec():
    argument_spec = {
        "name": {
            "type": "str",
            "required": True,
        },
        "state": {
            "type": "str",
            "default": "create",
            "choices": [
                "create",
                "delete",
            ],
        },
        "rd": {"type": "str"},
        "address_families": {
            "type": "list",
            "elements": "dict",
            "options": {
                "address_family": {
                    "type": "str",
                    "required": True,
                    "choices": ["evpn", "ipv4_unicast", "ipv6_unicast"],
                },
                "import_route_targets": {"type": "list", "elements": "str"},
                "export_route_targets": {"type": "list", "elements": "str"},
            },
            "required_one_of": [
                ["import_route_targets", "export_route_targets"],
            ],
        },
    }
    return argument_spec


RT_FIELDS = ("import_route_targets", "export_route_targets")


def family_targets(ansible_module):
    families = {}
    for entry in ansible_module.params["address_families"] or []:
        name = entry["address_family"]
        if name in families:
            ansible_module.fail_json(msg="Duplicate address family: " + name)
        families[name] = {
            key: sorted(set(entry[key]))
            for key in RT_FIELDS
            if entry[key] is not None
        }
    return families


def apply_configuration(resource, desired, check_mode):
    changes = {}
    for key, value in desired.items():
        current = getattr(resource, key, None)
        if isinstance(value, list):
            current = sorted(set(current or []))
        if current != value:
            changes[key] = value

    if resource.materialized and not changes:
        return False
    if check_mode:
        return True

    for key, value in changes.items():
        setattr(resource, key, value)
        if key not in resource.config_attrs:
            resource.config_attrs.append(key)
    return resource.apply()


def configure_vrf(vrf, rd, families, check_mode, result):
    desired = {} if rd is None else {"rd": rd}
    # EVPN is configured on the VRF; unicast targets are child resources.
    desired.update(
        ("evpn_" + key, value)
        for key, value in families.get("evpn", {}).items()
    )
    existing = {family.address_family: family for family in vrf.address_families}
    result["changed"] = apply_configuration(vrf, desired, check_mode)

    for name, targets in families.items():
        if name == "evpn":
            continue
        family = existing.get(name)
        if family is None:
            if not any(targets.values()):
                continue
            if check_mode:
                result["changed"] = True
                continue
            VrfAddressFamily = vrf.session.api.get_module_class(
                vrf.session, "VrfAddressFamily"
            )
            family = VrfAddressFamily(vrf.session, name, vrf)
        if apply_configuration(family, targets, check_mode):
            result["changed"] = True


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
    )

    # Get playbook's arguments
    vrf_name = ansible_module.params["name"]
    state = ansible_module.params["state"]
    families = family_targets(ansible_module) if state == "create" else {}

    result = dict(changed=False)

    try:
        from pyaoscx.device import Device
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
    Vrf = session.api.get_module_class(session, "Vrf")
    vrf = Vrf(session, vrf_name)

    try:
        vrf.get()
    except GenericOperationError as e:
        if e.response_code != 404 or vrf.materialized:
            ansible_module.fail_json(msg=str(e))
    except PyaoscxError as e:
        ansible_module.fail_json(msg=str(e))

    if state == "delete":
        if ansible_module.check_mode:
            ansible_module.exit_json(changed=vrf.materialized)
        if vrf.materialized:
            list_interfaces = vrf.get_interfaces()
            for interface in list_interfaces:
                try:
                    interface.get()
                except Exception as e:
                    ansible_module.fail_json(msg=str(e))

                if interface.type == "vlan":
                    interface.delete_vsx_configuration()
                    interface.configure_svi(
                        vlan=int(interface.name.split("n")[1]),
                        ipv4=[],
                        ipv6=[],
                        vrf="default",
                        description=None,
                    )
                    try:
                        dhcp_relay = Device(session).dhcp_relay(
                            vrf=vrf_name, port=interface.name
                        )
                        dhcp_relay.delete()
                    except Exception as e:
                        ansible_module.fail_json(msg=str(e))
                else:
                    interface.configure_l3(
                        ipv4=[],
                        ipv6=[],
                        vrf="default",
                    )
            try:
                vrf.delete()
                result["changed"] = True
            except Exception as e:
                ansible_module.fail_json(msg=str(e))

    if state == "create":
        try:
            configure_vrf(
                vrf,
                ansible_module.params["rd"],
                families,
                ansible_module.check_mode,
                result,
            )
        except PyaoscxError as e:
            ansible_module.fail_json(
                msg=pyaoscx_error_message(
                    session, "Could not configure VRF {0}".format(vrf_name), e
                ),
                **result
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
