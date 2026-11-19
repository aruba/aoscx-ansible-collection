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
module: aoscx_nae_script
version_added: "4.6.0"
short_description: Upload, update or delete NAE scripts on AOS-CX
description: >
  This module uploads, updates and deletes Network Analytics Engine (NAE)
  scripts on AOS-CX devices, and returns their validation status and the
  parameters they define. The agents running a script are managed with the
  aoscx_nae_agent module. NAE-Lite agents, and the scripts the switch
  generates for them, are managed with the aoscx_nae_lite_agent module.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the NAE script, 3 to 80 letters, digits, underscores or dots.
      It should match the Name of the script Manifest.
    required: true
    type: str
  script:
    description: >
      Python source of the NAE script. Mutually exclusive with I(src) and
      I(script_base64). One of them is required to upload a new script.
    required: false
    type: str
  script_base64:
    description: >
      Content of the NAE script encoded in Base64, as sent to the switch.
      Line breaks are ignored. Mutually exclusive with I(script) and
      I(src).
    required: false
    type: str
  src:
    description: >
      Path of a file holding the Python source of the NAE script, on the
      Ansible controller. A relative path is resolved from the directory
      ansible-playbook is run from: use for example
      C({{ playbook_dir }}/files/monitor.py). Mutually exclusive with
      I(script) and I(script_base64).
    required: false
    type: path
  expert_only:
    description: Whether the script requires expert level knowledge.
    required: false
    type: bool
  wait_for_validation:
    description: >
      Wait until the switch has validated an uploaded or updated script, and
      fail when the validation fails or when the script is in error. Agents
      cannot be created before the script is validated.
    required: false
    default: true
    type: bool
  timeout:
    description: Maximum time to wait for the validation, in seconds.
    required: false
    default: 60
    type: int
  state:
    description: >
      Upload or update the script, or delete it with its agents. Scripts
      provided by the system or generated for NAE-Lite agents cannot be
      changed or deleted.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Upload a NAE script from a local file
  aoscx_nae_script:
    name: interface_link_monitor
    src: "{{ playbook_dir }}/files/interface_link_monitor.py"

- name: Upload a NAE script already encoded in Base64
  aoscx_nae_script:
    name: interface_link_monitor
    script_base64: "{{ interface_link_monitor_b64 }}"

- name: Upload a NAE script from a template
  aoscx_nae_script:
    name: bgp_monitor
    script: "{{ lookup('ansible.builtin.template', 'bgp_monitor.py.j2') }}"

- name: Delete a NAE script and its agents
  aoscx_nae_script:
    name: bgp_monitor
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the script was uploaded, updated or deleted.
  returned: always
  type: bool
script:
  description: >
    Information and validation status of the script (origin, version,
    author, description, state, error_description...). Not returned when
    the script does not exist.
  returned: when the script exists
  type: dict
  sample:
    name: bgp_monitor
    origin: user
    version: "1.0"
    state: VALIDATED
    error_description: null
parameters:
  description: >
    Parameters defined by the script, keyed by name, with their type,
    default_value, required and encrypt flags and descriptions.
  returned: when the script exists
  type: dict
"""

import base64
import binascii
import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
    pyaoscx_error_message,
)

NAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,80}$")


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        script=dict(type="str"),
        script_base64=dict(type="str"),
        src=dict(type="path"),
        expert_only=dict(type="bool"),
        wait_for_validation=dict(type="bool", default=True),
        timeout=dict(type="int", default=60),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[("script", "script_base64", "src")],
        supports_check_mode=True,
    )
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    result = dict(changed=False)

    if not NAME_RE.match(name):
        ansible_module.fail_json(
            msg=(
                "Invalid NAE script name {0}: use 3 to 80 letters, digits, "
                "underscores or dots.".format(name)
            )
        )

    content = None
    if params["src"]:
        try:
            with open(params["src"], "rb") as script_file:
                content = script_file.read()
        except (IOError, OSError) as e:
            ansible_module.fail_json(
                msg="Could not read {0}: {1}".format(params["src"], str(e))
            )
    elif params["script"] is not None:
        content = params["script"].encode("utf-8")
    elif params["script_base64"] is not None:
        content = _decode_base64(ansible_module, params["script_base64"])

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        script = session.api.get_module(session, "NaeScript", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support NAE scripts. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        script.get()
        exists = True
    except Exception:
        exists = False

    origin = None
    if exists:
        try:
            origin = script.get_status().get("origin")
        except Exception as e:
            ansible_module.fail_json(
                msg=pyaoscx_error_message(
                    session, "Could not read NAE script {0}".format(name), e
                )
            )
        if origin in ("system", "generated") and (
            state == "delete"
            or content is not None
            or params["expert_only"] is not None
        ):
            hint = (
                " Use the aoscx_nae_lite_agent module to manage it."
                if origin == "generated"
                else ""
            )
            ansible_module.fail_json(
                msg=(
                    "NAE script {0} is a {1} script, it cannot be changed or "
                    "deleted.{2}".format(name, origin, hint)
                )
            )

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                script.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg=pyaoscx_error_message(
                        session,
                        "Could not delete NAE script {0}".format(name),
                        e,
                    )
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        if content is None:
            ansible_module.fail_json(
                msg=(
                    "NAE script {0} does not exist: script, script_base64 "
                    "or src is required to upload it.".format(name)
                )
            )
        result["changed"] = True
        if ansible_module.check_mode:
            ansible_module.exit_json(**result)
        create_kwargs = {"script": base64.b64encode(content).decode("ascii")}
        if params["expert_only"] is not None:
            create_kwargs["expert_only"] = params["expert_only"]
        script = session.api.get_module(
            session, "NaeScript", name, **create_kwargs
        )
        try:
            script.create()
        except Exception as e:
            ansible_module.fail_json(
                msg=pyaoscx_error_message(
                    session, "Could not upload NAE script {0}".format(name), e
                )
            )
    else:
        desired = {}
        if content is not None:
            desired["script"] = base64.b64encode(content).decode("ascii")
        if params["expert_only"] is not None:
            desired["expert_only"] = params["expert_only"]
        for key, value in desired.items():
            if getattr(script, key, None) != value:
                result["changed"] = True
            setattr(script, key, value)
            if key not in script.config_attrs:
                script.config_attrs.append(key)
        if result["changed"] and not ansible_module.check_mode:
            try:
                script.update()
            except Exception as e:
                ansible_module.fail_json(
                    msg=pyaoscx_error_message(
                        session,
                        "Could not update NAE script {0}".format(name),
                        e,
                    )
                )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    try:
        if result["changed"] and params["wait_for_validation"]:
            status = script.wait_for_validation(timeout=params["timeout"])
        else:
            status = script.get_status()
        result["script"] = status
        result["parameters"] = script.get_parameters()
    except Exception as e:
        ansible_module.fail_json(
            msg=pyaoscx_error_message(
                session, "Could not read NAE script {0}".format(name), e
            ),
            **result
        )

    if params["wait_for_validation"]:
        # An unchanged script can still hold the content of a failed upload
        if status["state"] == "ERROR":
            ansible_module.fail_json(
                msg="NAE script {0} is not valid: {1}".format(
                    name, status["error_description"]
                ),
                **result
            )
        if result["changed"] and status["state"] != "VALIDATED":
            ansible_module.fail_json(
                msg=(
                    "NAE script {0} is not validated after {1} seconds "
                    "(state {2}).".format(
                        name, params["timeout"], status["state"]
                    )
                ),
                **result
            )

    ansible_module.exit_json(**result)


def _decode_base64(ansible_module, value):
    """
    Decode the Base64 script content, so that it is sent in the canonical
    form compared with the content returned by the switch.
    """
    try:
        content = base64.b64decode("".join(value.split()), validate=True)
    except (binascii.Error, ValueError) as e:
        ansible_module.fail_json(
            msg="Invalid Base64 content in script_base64: {0}".format(e)
        )
    if not content:
        ansible_module.fail_json(msg="script_base64 is empty.")
    return content


if __name__ == "__main__":
    main()
