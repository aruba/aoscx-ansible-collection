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
module: aoscx_aaa_server_group_prio
version_added: "4.6.0"
short_description: Configure AAA server group priorities for a session type.
description:
  - This module configures the ordered list of AAA server groups used for
    accounting, authentication, authorization and RADIUS authorize-only for a
    management session type on AOS-CX switches.
author: Aruba Networks (@ArubaNetworks)
options:
  session_type:
    description: Management session type the priorities apply to.
    required: true
    choices:
      - console
      - ssh
      - telnet
      - https-server
      - gnmi
      - default
    type: str
  accounting_groups:
    description: Ordered list of AAA server group names used for accounting.
    required: false
    type: list
    elements: str
  authentication_groups:
    description: >
      Ordered list of AAA server group names used for authentication.
    required: false
    type: list
    elements: str
  authorization_groups:
    description: Ordered list of AAA server group names used for authorization.
    required: false
    type: list
    elements: str
  radius_authorize_only_groups:
    description: >
      Ordered list of AAA server group names used for RADIUS authorize-only.
    required: false
    type: list
    elements: str
  state:
    description: Configure or reset the server group priorities.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Set accounting server groups for SSH (clearpass then local)
  arubanetworks.aoscx.aoscx_aaa_server_group_prio:
    session_type: ssh
    accounting_groups:
      - clearpass
      - local
    state: create

- name: Reset accounting server groups for SSH
  arubanetworks.aoscx.aoscx_aaa_server_group_prio:
    session_type: ssh
    accounting_groups: []
    state: update
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)

ATTR_MAP = {
    "accounting_groups": "accounting_group_prios",
    "authentication_groups": "authentication_group_prios",
    "authorization_groups": "authorization_group_prios",
    "radius_authorize_only_groups": "radius_authorize_only_group_prios",
}


def _names(prio_map):
    # Return the ordered list of server group names from a {index: uri} map.
    if not isinstance(prio_map, dict):
        return []
    ordered = sorted(prio_map.items(), key=lambda kv: int(kv[0]))
    return [uri.rstrip("/").rsplit("/", 1)[-1] for idx, uri in ordered]


def main():
    module_args = dict(
        session_type=dict(
            type="str",
            required=True,
            choices=[
                "console",
                "ssh",
                "telnet",
                "https-server",
                "gnmi",
                "default",
            ],
        ),
        accounting_groups=dict(type="list", elements="str", default=None),
        authentication_groups=dict(type="list", elements="str", default=None),
        authorization_groups=dict(type="list", elements="str", default=None),
        radius_authorize_only_groups=dict(
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

    session_type = ansible_module.params["session_type"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        entry = session.api.get_module(
            session, "AaaServerGroupPrio", session_type
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support AAA server group "
                "priorities. Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    entry.get(selector="writable")

    supplied = {
        attr: ansible_module.params[attr]
        for attr in ATTR_MAP
        if ansible_module.params[attr] is not None
    }

    def build_map(groups):
        prio = {}
        for index, name in enumerate(groups):
            group = session.api.get_module(session, "AaaServerGroup", name)
            prio[str(index)] = group.get_uri()
        return prio

    changed = False
    for attr, groups in supplied.items():
        target = ATTR_MAP[attr]
        current = getattr(entry, target, None)
        if state == "delete":
            desired_names = []
        else:
            desired_names = list(groups)
        if _names(current) == desired_names:
            continue
        new_map = {} if state == "delete" else build_map(groups)
        setattr(entry, target, new_map)
        if target not in entry.config_attrs:
            entry.config_attrs.append(target)
        changed = True

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            entry.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update entry: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
