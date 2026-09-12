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
module: aoscx_radius_dynauth_proxy_server
version_added: "4.6.0"
short_description: >
  Create, update or delete a RADIUS dynamic authorization proxy server on
  AOS-CX.
description: >
  This module provides configuration management of RADIUS dynamic
  authorization (Change of Authorization) proxy servers on AOS-CX devices. A
  proxy server lives under a VRF and is identified by the combination of its
  address, port and port type.
author: Aruba Networks (@ArubaNetworks)
options:
  vrf:
    description: VRF the proxy server belongs to.
    type: str
    required: false
    default: default
  address:
    description: IPv4 address or hostname of the proxy server.
    type: str
    required: true
  port:
    description: UDP/TCP port of the proxy server.
    type: int
    required: false
    default: 3799
  port_type:
    description: Transport used by the proxy server.
    type: str
    required: false
    default: udp
    choices:
      - udp
      - tcp
  secret_key:
    description: >
      Shared secret used with the proxy server. It is write-only; the switch
      only ever returns it encrypted, so when C(secret_key) is supplied the
      module reports changed on every run.
    type: str
    required: false
  state:
    description: Create, update or delete the proxy server.
    choices:
      - create
      - update
      - delete
    default: create
    required: false
    type: str
"""

EXAMPLES = """
- name: Create a RADIUS dynamic authorization proxy server
  arubanetworks.aoscx.aoscx_radius_dynauth_proxy_server:
    vrf: default
    address: 192.0.2.30
    port: 3799
    port_type: udp
    secret_key: my-secret
    state: create

- name: Delete a RADIUS dynamic authorization proxy server
  arubanetworks.aoscx.aoscx_radius_dynauth_proxy_server:
    vrf: default
    address: 192.0.2.30
    port: 3799
    port_type: udp
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the proxy server was modified.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        vrf=dict(type="str", required=False, default="default"),
        address=dict(type="str", required=True),
        port=dict(type="int", required=False, default=3799),
        port_type=dict(
            type="str", required=False, default="udp",
            choices=["udp", "tcp"],
        ),
        secret_key=dict(type="str", required=False, default=None,
                        no_log=True),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    vrf = ansible_module.params["vrf"]
    address = ansible_module.params["address"]
    port = ansible_module.params["port"]
    port_type = ansible_module.params["port_type"]
    secret_key = ansible_module.params["secret_key"]
    state = ansible_module.params["state"]

    result = dict(changed=False)

    if "," in vrf or "/" in vrf or "," in address:
        ansible_module.fail_json(
            msg="Invalid vrf or address: {0} {1}".format(vrf, address)
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        server = session.api.get_module(
            session,
            "RadiusDynauthProxyServer",
            vrf,
            address=address,
            port=port,
            port_type=port_type,
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support RADIUS dynamic "
                "authorization proxy servers. Upgrade pyaoscx. Details: "
                "{0}".format(str(e))
            )
        )

    try:
        server.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # ----------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                server.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete proxy server: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ----------------------------------------------------------- check mode
    if ansible_module.check_mode:
        result["changed"] = (not exists) or secret_key is not None
        ansible_module.exit_json(**result)

    # ----------------------------------------------------------- create/update
    created = False
    if not exists:
        try:
            server.create()
            server.get(selector="writable")
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not create proxy server: {0}".format(str(e))
            )
        created = True

    needs_update = False
    if secret_key is not None:
        # The secret is write-only and salted; always re-apply when supplied.
        server.secret_key = secret_key
        needs_update = True

    if needs_update:
        try:
            server.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update proxy server: {0}".format(str(e))
            )

    result["changed"] = created or needs_update
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
