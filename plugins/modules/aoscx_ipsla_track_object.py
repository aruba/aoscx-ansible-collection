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
module: aoscx_ipsla_track_object
version_added: "4.6.0"
short_description: Create, update or delete an IP SLA track object
description: >
  This module provides configuration management of IP SLA track objects on
  AOS-CX devices (system/ipsla_track_objects). A track object follows the
  state of one or more IP SLA sessions. IP SLA requires REST API version 10.16
  (set ansible_aoscx_rest_version to 10.16). The tracked IP SLA sessions are
  set when the track object is created and cannot be modified; changing them
  recreates the track object.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the IP SLA track object. This is the index of the resource
      under system/ipsla_track_objects.
    required: true
    type: str
  tracked_ipsla_session:
    description: >
      List of IP SLA source names tracked by this object. Set on creation;
      changing this list recreates the track object.
    required: false
    type: list
    elements: str
  track_list_operator:
    description: >
      Operator combining the tracked sessions to compute the overall state.
    required: false
    type: str
    choices:
      - and
      - or
  up_delay:
    description: >
      Delay in seconds before the track object is declared up (0-180).
    required: false
    type: int
  down_delay:
    description: >
      Delay in seconds before the track object is declared down (0-180).
    required: false
    type: int
  state:
    description: Create, update or delete the IP SLA track object.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an IP SLA track object
  aoscx_ipsla_track_object:
    name: track-gw
    tracked_ipsla_session:
      - probe-gw
    track_list_operator: or
    up_delay: 5

- name: Update the track object timers
  aoscx_ipsla_track_object:
    name: track-gw
    state: update
    up_delay: 10
    down_delay: 5

- name: Delete an IP SLA track object
  aoscx_ipsla_track_object:
    name: track-gw
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
        tracked_ipsla_session=dict(
            type="list",
            elements="str",
            required=False,
            default=None,
        ),
        track_list_operator=dict(
            type="str",
            required=False,
            default=None,
            choices=["and", "or"],
        ),
        up_delay=dict(type="int", required=False, default=None),
        down_delay=dict(type="int", required=False, default=None),
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
    tracked = ansible_module.params["tracked_ipsla_session"]
    state = ansible_module.params["state"]

    scalar_attrs = ["track_list_operator", "up_delay", "down_delay"]
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
        track = session.api.get_module(session, "IpslaTrackObject", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support IP SLA. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        track.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                track.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete IP SLA track object: "
                    "{0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    def materialize_sources():
        sources = []
        for source_name in tracked or []:
            source = session.api.get_module(
                session, "IpslaSource", source_name
            )
            try:
                source.get()
            except Exception:
                ansible_module.fail_json(
                    msg="Could not find IP SLA source {0}".format(source_name)
                )
            sources.append(source)
        return sources

    def build_track():
        return session.api.get_module(
            session,
            "IpslaTrackObject",
            name,
            tracked_ipsla_session=materialize_sources(),
            **supplied
        )

    # ------------------------------------------------------------ create
    if not exists:
        new_track = build_track()
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                new_track.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create IP SLA track object: "
                    "{0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    # ------------------------------------------------------------ update
    # The tracked sessions are set at creation time. If a different set is
    # requested, the track object must be recreated.
    recreate = False
    if tracked is not None:
        probe = session.api.get_module(session, "IpslaTrackObject", name)
        try:
            probe.get(selector="configuration")
        except Exception:
            probe = None
        current = set((getattr(probe, "tracked_ipsla_session", {}) or {}))
        if current != set(tracked):
            recreate = True

    if recreate:
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                track.delete()
                build_track().create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not update IP SLA track object: "
                    "{0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(track, attr, None) != value:
            changed = True
            setattr(track, attr, value)
            if attr not in track.config_attrs:
                track.config_attrs.append(attr)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            track.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update IP SLA track object: "
                "{0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
