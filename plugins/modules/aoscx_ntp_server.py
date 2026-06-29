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
module: aoscx_ntp_server
version_added: "4.6.0"
short_description: Create, update or delete an NTP server association
description: >
  This module provides configuration management of NTP server associations on
  AOS-CX devices (system/vrfs/{vrf}/ntp_associations). A server is identified
  by its address within a VRF. Optionally the association may reference an
  existing NTP key for authentication.
author: Aruba Networks (@ArubaNetworks)
options:
  address:
    description: >
      Hostname or IP address of the NTP server. This is the index of the
      resource under the VRF's ntp_associations.
    required: true
    type: str
  vrf:
    description: VRF the NTP association belongs to.
    required: false
    type: str
    default: default
  key_id:
    description: >
      key_id of an existing NTP authentication key used for this association.
    required: false
    type: int
  prefer:
    description: Mark this server as preferred.
    required: false
    type: bool
  ntp_version:
    description: NTP protocol version used for this association.
    required: false
    type: int
    choices:
      - 3
      - 4
  burst_mode:
    description: Burst mode used when polling this server.
    required: false
    type: str
    choices:
      - none
      - burst
      - iburst
  minpoll:
    description: Minimum poll interval (power of two seconds).
    required: false
    type: int
  maxpoll:
    description: Maximum poll interval (power of two seconds).
    required: false
    type: int
  state:
    description: Create, update or delete the NTP server association.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an NTP server association
  aoscx_ntp_server:
    address: 198.51.100.1
    vrf: default
    prefer: true
    ntp_version: 4
    burst_mode: iburst

- name: Create an authenticated NTP server association
  aoscx_ntp_server:
    address: 198.51.100.2
    key_id: 60001

- name: Delete an NTP server association
  aoscx_ntp_server:
    address: 198.51.100.1
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.ntp_association import NtpAssociation
    from pyaoscx.ntp_key import NtpKey
    from pyaoscx.vrf import Vrf

    HAS_PYAOSCX_NTP = True
except ImportError:
    HAS_PYAOSCX_NTP = False

if HAS_PYAOSCX_NTP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        address=dict(type="str", required=True),
        vrf=dict(type="str", required=False, default="default"),
        key_id=dict(type="int", required=False),
        prefer=dict(type="bool", required=False),
        ntp_version=dict(type="int", required=False, choices=[3, 4]),
        burst_mode=dict(
            type="str",
            required=False,
            choices=["none", "burst", "iburst"],
        ),
        minpoll=dict(type="int", required=False),
        maxpoll=dict(type="int", required=False),
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

    if not HAS_PYAOSCX_NTP:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support NTP associations. "
                "Upgrade pyaoscx."
            )
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    address = ansible_module.params["address"]
    vrf_name = ansible_module.params["vrf"]
    key_id = ansible_module.params["key_id"]
    prefer = ansible_module.params["prefer"]
    ntp_version = ansible_module.params["ntp_version"]
    burst_mode = ansible_module.params["burst_mode"]
    minpoll = ansible_module.params["minpoll"]
    maxpoll = ansible_module.params["maxpoll"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    vrf = Vrf(session, vrf_name)

    assoc = NtpAssociation(session, vrf, address)
    try:
        assoc.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            assoc.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    kwargs = {}
    if key_id is not None:
        kwargs["key_id"] = NtpKey(session, key_id).get_uri()

    association_attributes = {}
    if prefer is not None:
        association_attributes["prefer"] = prefer
    if ntp_version is not None:
        association_attributes["ntp_version"] = ntp_version
    if burst_mode is not None:
        association_attributes["burst_mode"] = burst_mode
    if minpoll is not None:
        association_attributes["minpoll"] = minpoll
    if maxpoll is not None:
        association_attributes["maxpoll"] = maxpoll
    if association_attributes:
        kwargs["association_attributes"] = association_attributes

    assoc = NtpAssociation(session, vrf, address, **kwargs)
    if exists:
        assoc.get()
        for key, value in kwargs.items():
            setattr(assoc, key, value)
    result["changed"] = assoc.apply()

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
