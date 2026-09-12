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
module: aoscx_traffic_insight
version_added: "4.6.0"
short_description: Create, update or delete a Traffic Insight instance
description: >
  This module provides configuration management of the Traffic Insight
  instance on AOS-CX devices (system/traffic_insights). Traffic Insight
  requires REST API version 10.13 or later (set ansible_aoscx_rest_version to
  10.13). Note that the switch supports a single Traffic Insight instance at a
  time.
author: Aruba Networks (@ArubaNetworks)
notes:
  - Some platforms only expose a single built-in Traffic Insight instance and
    reject creation of additional instances; in that case the switch returns
    an error when a new name is created.
options:
  name:
    description: >
      Name of the Traffic Insight instance. This is the index of the resource
      under system/traffic_insights.
    required: true
    type: str
  enable:
    description: Enable or disable the Traffic Insight instance.
    required: false
    type: bool
  source:
    description: >
      List of data sources feeding the Traffic Insight instance. The only
      supported source is ipfix. The supplied list fully replaces the current
      sources.
    required: false
    type: list
    elements: str
    choices:
      - ipfix
  state:
    description: Create, update or delete the Traffic Insight instance.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create a Traffic Insight instance
  aoscx_traffic_insight:
    name: TI-01
    enable: true
    source:
      - ipfix

- name: Disable a Traffic Insight instance
  aoscx_traffic_insight:
    name: TI-01
    state: update
    enable: false

- name: Delete a Traffic Insight instance
  aoscx_traffic_insight:
    name: TI-01
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
        enable=dict(type="bool", required=False, default=None),
        source=dict(
            type="list",
            elements="str",
            required=False,
            default=None,
            choices=["ipfix"],
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

    name = ansible_module.params["name"]
    state = ansible_module.params["state"]

    scalar_attrs = ["enable", "source"]
    supplied = {
        attr: ansible_module.params[attr]
        for attr in scalar_attrs
        if ansible_module.params[attr] is not None
    }

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        instance = session.api.get_module(session, "TrafficInsight", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support Traffic Insight. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        instance.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                instance.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete Traffic Insight instance: "
                    "{0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        instance = session.api.get_module(
            session, "TrafficInsight", name, **supplied
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                instance.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create Traffic Insight instance: "
                    "{0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(instance, attr, None) != value:
            changed = True
            setattr(instance, attr, value)
            if attr not in instance.config_attrs:
                instance.config_attrs.append(attr)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            instance.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update Traffic Insight instance: "
                "{0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
