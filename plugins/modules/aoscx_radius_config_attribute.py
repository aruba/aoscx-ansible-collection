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
module: aoscx_radius_config_attribute
version_added: "4.6.0"
short_description: >
  Manage the RADIUS configuration attributes of an AAA server group on AOS-CX.
description: >
  This module provides configuration management of the RADIUS configuration
  attributes attached to an AAA server group on AOS-CX devices. Each attribute
  controls whether a RADIUS attribute is included for the port-access service.
  The resource is identified by the AAA server group it applies to.
author: Aruba Networks (@ArubaNetworks)
options:
  server_group:
    description: >
      Name of the AAA server group the RADIUS configuration attributes apply
      to. The server group must already exist.
    type: str
    required: true
  server_group_type:
    description: Type of the referenced AAA server group.
    type: str
    required: false
    default: radius
    choices:
      - radius
      - tacacs
  framed_ip_addr:
    description: >
      Include the Framed-IP-Address attribute for the port-access service.
    type: bool
    required: false
  nas_id:
    description: >
      Include the NAS-Identifier attribute for the port-access service.
    type: bool
    required: false
  nas_ip_addr:
    description: >
      Include the NAS-IP-Address attribute for the port-access service.
    type: bool
    required: false
  tunnel_private_group_id:
    description: >
      Include the Tunnel-Private-Group-ID attribute for the port-access
      service.
    type: bool
    required: false
  state:
    description: Create, update or delete the RADIUS configuration attributes.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Enable NAS-Identifier and NAS-IP-Address for a server group
  arubanetworks.aoscx.aoscx_radius_config_attribute:
    server_group: my-radius-group
    nas_id: true
    nas_ip_addr: true
    state: create

- name: Disable the NAS-Identifier attribute
  arubanetworks.aoscx.aoscx_radius_config_attribute:
    server_group: my-radius-group
    nas_id: false
    state: update

- name: Delete the RADIUS configuration attributes of a server group
  arubanetworks.aoscx.aoscx_radius_config_attribute:
    server_group: my-radius-group
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the RADIUS configuration attributes were modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

# Each RADIUS configuration attribute is enabled for a single, fixed service
# type. The HPE-ANW-AVPair VSA uses a different schema and is not handled here.
ATTR_SERVICE_TYPE = {
    "framed_ip_addr": "port-access",
    "nas_id": "port-access",
    "nas_ip_addr": "user-management",
    "tunnel_private_group_id": "port-access",
}
ATTRIBUTES = tuple(ATTR_SERVICE_TYPE)


def main():
    module_args = dict(
        server_group=dict(type="str", required=True),
        server_group_type=dict(
            type="str", required=False, default="radius",
            choices=["radius", "tacacs"],
        ),
        framed_ip_addr=dict(type="bool", required=False, default=None),
        nas_id=dict(type="bool", required=False, default=None),
        nas_ip_addr=dict(type="bool", required=False, default=None),
        tunnel_private_group_id=dict(
            type="bool", required=False, default=None
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

    p = ansible_module.params
    server_group = p["server_group"]
    server_group_type = p["server_group_type"]
    state = p["state"]

    result = dict(changed=False)

    if server_group in ("", ".", "..") or "/" in server_group \
            or "," in server_group:
        ansible_module.fail_json(
            msg="Invalid server group: {0}".format(server_group)
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    rp = session.resource_prefix
    sep = session.api.compound_index_separator
    grp_index = "{0}{1}{2}".format(server_group, sep, server_group_type)
    grp_uri = "{0}system/aaa_server_groups/{1}".format(rp, grp_index)

    try:
        entry = session.api.get_module(
            session, "RadiusConfigAttribute", server_group,
            server_group_uri=grp_uri,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS configuration "
                "attributes. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        entry.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # ----------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                entry.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete config attributes: {0}".format(
                        str(e)
                    )
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # Validate the referenced AAA server group exists.
    grp = session.api.get_module(
        session, "AaaServerGroup", server_group,
        group_type=server_group_type,
    )
    try:
        grp.get()
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not find AAA server group {0}: {1}".format(
                server_group, str(e)
            )
        )

    # ----------------------------------------------------------- check mode
    if ansible_module.check_mode:
        result["changed"] = (not exists) or any(
            p[a] is not None for a in ATTRIBUTES
        )
        ansible_module.exit_json(**result)

    # ----------------------------------------------------------- create/update
    created = False
    if not exists:
        try:
            entry.create()
            entry.get(selector="writable")
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not create config attributes: {0}".format(str(e))
            )
        created = True

    needs_update = False
    for attr in ATTRIBUTES:
        value = p[attr]
        if value is None:
            continue
        desired = (
            {"service_type": ATTR_SERVICE_TYPE[attr]} if value else {}
        )
        current = getattr(entry, attr, None) or {}
        if current != desired:
            needs_update = True
            setattr(entry, attr, desired)

    if needs_update:
        try:
            entry.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update config attributes: {0}".format(str(e))
            )

    result["changed"] = created or needs_update
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
