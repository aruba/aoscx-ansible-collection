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
module: aoscx_snmp_community
version_added: "4.6.0"
short_description: Create, update or delete an SNMP community
description: >
  This module provides configuration management of SNMP communities on AOS-CX
  devices (system/snmp_community_attributes). Requires REST API v10.16
  (set ansible_aoscx_rest_version to 10.16).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: Name of the SNMP community.
    required: true
    type: str
  snmp_view:
    description: Name of the SNMP view associated to the community.
    required: false
    type: str
  state:
    description: Create, update or delete the SNMP community.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an SNMP community
  aoscx_snmp_community:
    name: anstest
    snmp_view: my_view

- name: Delete an SNMP community
  aoscx_snmp_community:
    name: anstest
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.snmp_community import SnmpCommunity
    from pyaoscx.snmp_view import SnmpView

    HAS_PYAOSCX_SNMP = True
except ImportError:
    HAS_PYAOSCX_SNMP = False

if HAS_PYAOSCX_SNMP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        snmp_view=dict(type="str", required=False),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_SNMP:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support SNMP. Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    name = ansible_module.params["name"]
    snmp_view = ansible_module.params["snmp_view"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    community = SnmpCommunity(session, name)
    try:
        community.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            community.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    kwargs = {}
    if snmp_view is not None:
        view = SnmpView(session, snmp_view)
        view.get()
        kwargs["snmp_view"] = view.get_uri()

    for key, value in kwargs.items():
        setattr(community, key, value)
    result["changed"] = community.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
