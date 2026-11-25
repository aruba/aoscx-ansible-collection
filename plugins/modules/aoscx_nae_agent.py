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
module: aoscx_nae_agent
version_added: "4.6.0"
short_description: Create, update or delete NAE agents on AOS-CX
description: >
  This module creates, updates, enables, disables and deletes the Network
  Analytics Engine (NAE) agents of a NAE script on AOS-CX devices, and
  returns their status and alert information. The script is uploaded with
  the aoscx_nae_script module.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the NAE agent, 3 to 80 letters, digits, underscores or dots.
    required: true
    type: str
  script_name:
    description: Name of the NAE script run by the agent.
    required: true
    type: str
  parameters:
    description: >
      Values of the script parameters, keyed by parameter name. Only the
      given parameters are changed, the others keep their current value. A
      parameter not set when the agent is created takes the default value
      defined by the script. Encrypted parameters are set with
      I(encrypted_parameters).
    required: false
    type: dict
  encrypted_parameters:
    description: >
      Values of the encrypted script parameters, keyed by parameter name.
      The switch only returns their encrypted form, see
      I(update_encrypted_parameters).
    required: false
    type: dict
  update_encrypted_parameters:
    description: >
      C(on_create) only sets the encrypted parameters that have no value yet,
      so that the module stays idempotent. C(always) sets them on every run
      and always reports a change.
    required: false
    default: on_create
    choices:
      - on_create
      - always
    type: str
  disabled:
    description: Whether the agent is disabled.
    required: false
    type: bool
  vrf:
    description: >
      Name of the VRF the agent runs on. It can only be set when the agent is
      created. Defaults to the default VRF.
    required: false
    type: str
  state:
    description: Create, update or delete the agent.
    required: false
    default: create
    choices:
      - create
      - update
      - delete
    type: str
"""

EXAMPLES = """
- name: Create an agent of the interface_link_monitor script
  aoscx_nae_agent:
    name: link_monitor_uplinks
    script_name: interface_link_monitor
    parameters:
      interface_id: 1/1/49
      threshold: 5

- name: Create an agent with an encrypted parameter
  aoscx_nae_agent:
    name: api_poller
    script_name: api_poller
    vrf: mgmt
    parameters:
      server: 192.0.2.10
    encrypted_parameters:
      token: "{{ vault_api_token }}"

- name: Disable an agent
  aoscx_nae_agent:
    name: link_monitor_uplinks
    script_name: interface_link_monitor
    disabled: true
    state: update

- name: Delete an agent
  aoscx_nae_agent:
    name: link_monitor_uplinks
    script_name: interface_link_monitor
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the agent was created, updated or deleted.
  returned: always
  type: bool
agent:
  description: >
    Status and alert information of the agent: state, alert_level
    (CRITICAL, MAJOR, MINOR or NORMAL), alert_description, alerts_count,
    error_description, disabled, vrf and counters.
  returned: when the agent exists
  type: dict
  sample:
    name: link_monitor_uplinks
    script: interface_link_monitor
    state: SLEEPING
    alert_level: MAJOR
    alert_description: Link flapping on 1/1/49
    alerts_count: 3
    error_description: null
"""

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
    pyaoscx_error_message,
)

NAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,80}$")


def _to_switch_value(value):
    # The switch stores every parameter value as a string
    if isinstance(value, bool):
        return str(value).lower()
    return value if isinstance(value, str) else str(value)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        script_name=dict(type="str", required=True),
        parameters=dict(type="dict"),
        encrypted_parameters=dict(type="dict", no_log=True),
        update_encrypted_parameters=dict(
            type="str",
            default="on_create",
            choices=["on_create", "always"],
        ),
        disabled=dict(type="bool"),
        vrf=dict(type="str"),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )
    params = ansible_module.params
    name = params["name"]
    script_name = params["script_name"]
    state = params["state"]
    parameters = {
        key: _to_switch_value(value)
        for key, value in (params["parameters"] or {}).items()
    }
    encrypted = {
        key: _to_switch_value(value)
        for key, value in (params["encrypted_parameters"] or {}).items()
    }
    result = dict(changed=False)

    for label, value in (("agent", name), ("script", script_name)):
        if not NAME_RE.match(value):
            ansible_module.fail_json(
                msg=(
                    "Invalid NAE {0} name {1}: use 3 to 80 letters, digits, "
                    "underscores or dots.".format(label, value)
                )
            )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        script = session.api.get_module(session, "NaeScript", script_name)
        agent = session.api.get_module(
            session, "NaeAgent", name, parent_nae_script=script
        )
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support NAE agents. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        agent.get()
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                agent.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg=pyaoscx_error_message(
                        session,
                        "Could not delete NAE agent {0}".format(name),
                        e,
                    )
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    definitions = _check_script(ansible_module, session, script)
    _validate_parameters(ansible_module, definitions, parameters, encrypted)

    if not exists:
        result["changed"] = True
        if ansible_module.check_mode:
            ansible_module.exit_json(**result)
        create_kwargs = {}
        if parameters:
            create_kwargs["parameters_values"] = parameters
        if encrypted:
            create_kwargs["encrypted_parameters_values"] = encrypted
        if params["disabled"] is not None:
            create_kwargs["disabled"] = params["disabled"]
        if params["vrf"] is not None:
            create_kwargs["vrf"] = params["vrf"]
        agent = session.api.get_module(
            session,
            "NaeAgent",
            name,
            parent_nae_script=script,
            **create_kwargs
        )
        try:
            agent.create()
        except Exception as e:
            ansible_module.fail_json(
                msg=pyaoscx_error_message(
                    session, "Could not create NAE agent {0}".format(name), e
                )
            )
    else:
        current_vrf = getattr(agent, "vrf", None)
        if params["vrf"] is not None and params["vrf"] != current_vrf:
            ansible_module.fail_json(
                msg=(
                    "vrf cannot be changed on an existing NAE agent (current: "
                    "{0}). Delete and recreate it.".format(current_vrf)
                )
            )

        current = dict(getattr(agent, "parameters_values", None) or {})
        merged = dict(current)
        merged.update(parameters)
        if merged != current:
            result["changed"] = True
            agent.parameters_values = merged
            if "parameters_values" not in agent.config_attrs:
                agent.config_attrs.append("parameters_values")

        disabled = params["disabled"]
        if (
            disabled is not None
            and bool(getattr(agent, "disabled", False)) != disabled
        ):
            result["changed"] = True
            agent.disabled = disabled
            if "disabled" not in agent.config_attrs:
                agent.config_attrs.append("disabled")

        if params["update_encrypted_parameters"] == "on_create":
            encrypted = {
                key: value
                for key, value in encrypted.items()
                if key not in agent.encrypted_parameters_names
            }
        if encrypted:
            result["changed"] = True
            agent.encrypted_parameters_values = encrypted

        if result["changed"] and not ansible_module.check_mode:
            try:
                agent.update()
            except Exception as e:
                ansible_module.fail_json(
                    msg=pyaoscx_error_message(
                        session,
                        "Could not update NAE agent {0}".format(name),
                        e,
                    )
                )

    if not ansible_module.check_mode:
        try:
            result["agent"] = agent.get_status()
        except Exception as e:
            ansible_module.fail_json(
                msg=pyaoscx_error_message(
                    session, "Could not read NAE agent {0}".format(name), e
                ),
                **result
            )
    ansible_module.exit_json(**result)


def _check_script(ansible_module, session, script):
    """
    Check that the script exists and is validated, and return its parameter
    definitions.
    """
    try:
        status = script.get_status()
        definitions = script.get_parameters()
    except Exception as e:
        if getattr(e, "response_code", None) == 404:
            ansible_module.fail_json(
                msg="NAE script {0} does not exist.".format(script.name)
            )
        ansible_module.fail_json(
            msg=pyaoscx_error_message(
                session,
                "Could not read NAE script {0}".format(script.name),
                e,
            )
        )
    if status.get("state") != "VALIDATED":
        detail = status.get("error_description")
        ansible_module.fail_json(
            msg="NAE script {0} is not validated (state {1}){2}".format(
                script.name,
                status.get("state"),
                ": {0}".format(detail) if detail else ".",
            )
        )
    return definitions


def _validate_parameters(ansible_module, definitions, parameters, encrypted):
    """
    Check the parameter names against the script definitions, so that the
    user gets a clear error instead of a switch rejection.
    """
    for option, values, expect_encrypted in (
        ("parameters", parameters, False),
        ("encrypted_parameters", encrypted, True),
    ):
        for key in values:
            definition = definitions.get(key)
            if definition is None:
                ansible_module.fail_json(
                    msg=(
                        "Unknown parameter {0} in {1}. Parameters of the "
                        "script: {2}.".format(
                            key,
                            option,
                            ", ".join(sorted(definitions)) or "none",
                        )
                    )
                )
            if bool(definition.get("encrypt")) != expect_encrypted:
                is_encrypted = bool(definition.get("encrypt"))
                expected_option = (
                    "encrypted_parameters" if is_encrypted else "parameters"
                )
                ansible_module.fail_json(
                    msg="Parameter {0} is {1}encrypted: set it with "
                    "{2}.".format(
                        key, "" if is_encrypted else "not ", expected_option
                    )
                )


if __name__ == "__main__":
    main()
