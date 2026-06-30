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
module: aoscx_port_access_vlan_group
version_added: "4.6.0"
short_description: Create, update or delete a Port Access VLAN Group
description: >
  This module provides configuration management of Port Access VLAN Groups on
  AOS-CX devices (system/port_access_vlan_groups). A VLAN group bundles a set
  of VLAN IDs that can be referenced by port access roles. This module requires
  REST API version 10.16 (set ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the port access VLAN group. This is the index of the resource
      under system/port_access_vlan_groups.
    required: true
    type: str
  vlans:
    description: >
      List of VLAN IDs that belong to the group. The list fully replaces the
      VLANs configured on the group.
    required: false
    type: list
    elements: int
  state:
    description: Create, update or delete the port access VLAN group.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a port access VLAN group
  aoscx_port_access_vlan_group:
    name: guest-vlans
    vlans:
      - 10
      - 20

- name: Update the VLAN membership
  aoscx_port_access_vlan_group:
    name: guest-vlans
    vlans:
      - 10
      - 20
      - 30
    state: update

- name: Delete a port access VLAN group
  aoscx_port_access_vlan_group:
    name: guest-vlans
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        vlans=dict(type="list", elements="int", required=False, default=None),
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

    name = ansible_module.params["name"]
    vlans = ansible_module.params["vlans"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        group = session.api.get_module(session, "PortAccessVlanGroup", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support port access VLAN "
                "groups. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        group.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                group.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete port access VLAN group: "
                    "{0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- create
    if not exists:
        kwargs = {}
        if vlans is not None:
            kwargs["vlans"] = sorted(vlans)
        group = session.api.get_module(
            session, "PortAccessVlanGroup", name, **kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                group.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create port access VLAN group: "
                    "{0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # --------------------------------------------------------------- update
    changed = False
    if vlans is not None:
        desired = sorted(vlans)
        current = sorted(getattr(group, "vlans", None) or [])
        if current != desired:
            changed = True
            group.vlans = desired
            if "vlans" not in group.config_attrs:
                group.config_attrs.append("vlans")

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            group.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update port access VLAN group: {0}".format(
                    str(e)
                )
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
