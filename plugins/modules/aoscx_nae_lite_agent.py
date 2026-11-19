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
module: aoscx_nae_lite_agent
version_added: "4.6.0"
short_description: Create, update or delete NAE-Lite agents on AOS-CX
description: >
  This module manages NAE-Lite agents (CLI C(nae-agent lite)) on AOS-CX
  devices: the monitored resources or watched event logs, the condition and
  clear condition, and the actions executed when they are met. Once
  activated, the switch generates a NAE script and a NAE agent with the name
  of the NAE-Lite agent. The module returns the generation status and the
  status and alert information of the generated agent.
author: Aruba Networks (@ArubaNetworks)
notes:
  - The REST API does not accept the alert description of the CLI
    C(status <level> description) command in a form the switch can use. The
    module does not set it, and keeps a description set with the CLI.
  - Requires AOS-CX 10.10 or later.
options:
  name:
    description: >
      Name of the NAE-Lite agent, 3 to 80 letters, digits or underscores.
    required: true
    type: str
  description:
    description: Description of the agent.
    required: false
    type: str
  disabled:
    description: Whether the agent is disabled.
    required: false
    type: bool
  tags:
    description: Tags of the agent, 3 to 32 characters each.
    required: false
    type: list
    elements: str
  monitors:
    description: >
      Resources monitored by the agent, at most two. Mutually exclusive with
      I(watches). When provided, this is the full list of monitors.
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description: Name of the monitor, 3 to 80 characters.
        required: true
        type: str
      resource:
        description: >
          Monitored resource, as in the CLI C(monitor <name> resource)
          command, for example C(system cpu), C(system memory),
          C(system storage) or C(system cpu vsf).
        required: true
        type: str
      aggregate_by:
        description: >
          Function used to aggregate the data of the monitored resource.
          Not supported by every firmware.
        required: false
        choices:
          - Rate
          - Count
          - CountOverTime
          - Sum
          - SumOverTime
          - Min
          - MinOverTime
          - Max
          - MaxOverTime
          - Average
          - AverageOverTime
        type: str
      time_interval:
        description: >
          Time interval of the aggregation function, for example
          C(5 minutes). Not supported by every firmware.
        required: false
        type: str
  watches:
    description: >
      Event logs watched by the agent, at most two. Mutually exclusive with
      I(monitors). When provided, this is the full list of watches.
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description: Name of the watch, 3 to 80 characters.
        required: true
        type: str
      event_ids:
        description: Event log IDs watched, from 101 to 32767.
        required: true
        type: list
        elements: int
  condition:
    description: >
      Condition of the agent (CLI C(set-condition)) and the actions executed
      when it is met. When provided, I(condition) and I(clear_condition)
      describe the full rule: an existing clear condition is removed when
      I(clear_condition) is omitted.
    required: false
    type: dict
    suboptions: &condition_options
      source:
        description: Name of the monitor or watch the condition applies to.
        required: true
        type: str
      expression:
        description: >
          Condition expression, as stored by the switch. On a monitor, an
          operator (C(lt), C(le), C(eq), C(ne), C(gt), C(ge)) and a value
          with an optional duration, for example C(gt 90) or
          C(gt 90 for 2 minutes), or a transition, for example
          C(transition from "up" to "down","error"). On a watch, for
          example C(count 5), C(include any "error,fail" count 2) or
          C(exclude "Ok").
        required: true
        type: str
      alert_level:
        description: Alert level set on the agent when the condition is met.
        required: false
        default: normal
        choices:
          - critical
          - major
          - minor
          - normal
        type: str
      syslog:
        description: Syslog message sent when the condition is met.
        required: false
        type: dict
        suboptions:
          text:
            description: Syslog message, 3 to 255 characters.
            required: true
            type: str
          severity:
            description: Syslog severity.
            required: false
            default: info
            choices:
              - debug
              - info
              - notice
              - warning
              - err
              - crit
              - alert
              - emer
            type: str
          facility:
            description: Syslog facility.
            required: false
            default: daemon
            choices:
              - kern
              - user
              - mail
              - daemon
              - auth
              - syslog
              - lpr
              - news
              - uucp
              - authpriv
              - cron
              - ftp
            type: str
      cli_commands:
        description: CLI commands executed when the condition is met.
        required: false
        type: list
        elements: str
      schedule:
        description: >
          Job schedule CLI commands executed when the condition is met, for
          example C(schedule s1), C(10 job j1) and
          C(trigger every minutes 30).
        required: false
        type: list
        elements: str
      snmp_trap:
        description: SNMP trap message sent when the condition is met.
        required: false
        type: str
  clear_condition:
    description: >
      Optional clear condition (CLI C(clear-condition)): once the condition
      is met, it is suspended until the clear condition is met. Requires
      I(condition).
    required: false
    type: dict
    suboptions: *condition_options
  activate:
    description: >
      Activate the agent (CLI C(nae-agent lite <name> activate)), so that the
      switch generates it. An activated agent is generated again when the
      module changes it. C(false) deactivates the agent.
    required: false
    default: true
    type: bool
  wait:
    description: >
      Wait until the generated agent has run after an activation, and fail
      when the generation or the agent fails.
    required: false
    default: true
    type: bool
  timeout:
    description: Maximum time to wait for the activation, in seconds.
    required: false
    default: 60
    type: int
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
- name: Raise a critical alert when the CPU utilization is high
  aoscx_nae_lite_agent:
    name: high_cpu
    description: CPU utilization above 90 percent
    monitors:
      - name: cpu
        resource: system cpu
    condition:
      source: cpu
      expression: gt 90 for 2 minutes
      alert_level: critical
      syslog:
        text: High CPU utilization
        severity: warning
      cli_commands:
        - show system resource-utilization
    clear_condition:
      source: cpu
      expression: lt 50
      alert_level: normal

- name: Send a trap when a power supply event is logged
  aoscx_nae_lite_agent:
    name: psu_events
    watches:
      - name: psu_logs
        event_ids:
          - 1201
          - 1202
    condition:
      source: psu_logs
      expression: count 1
      alert_level: major
      snmp_trap: Power supply event

- name: Deactivate an agent
  aoscx_nae_lite_agent:
    name: high_cpu
    activate: false
    state: update

- name: Delete an agent
  aoscx_nae_lite_agent:
    name: high_cpu
    state: delete
"""

RETURN = r"""
changed:
  description: Whether the agent was created, updated, activated or deleted.
  returned: always
  type: bool
nae_lite_agent:
  description: >
    Generation status of the agent (ready, state, error_description) and,
    in agent, the status and alert information of the generated NAE agent
    (state, alert_level, alert_description, alerts_count,
    error_description...), null when it is not generated.
  returned: when the agent exists
  type: dict
  sample:
    name: high_cpu
    ready: true
    state: AGENT_CREATED
    error_description: null
    agent:
      name: high_cpu
      alert_level: CRITICAL
      alerts_count: 1
"""

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
    pyaoscx_error_message,
)

NAME_RE = re.compile(r"^[A-Za-z0-9_]{3,80}$")
RULE_NAME = "Default"
CONDITION_TYPES = (
    ("condition", "active_condition"),
    ("clear_condition", "clear_condition"),
)
# The switch inserts the CLI commands in the generated script, they are
# separated with a literal "\n"
CLI_SEPARATOR = "\\n"
SYSLOG_SEVERITIES = [
    "debug",
    "info",
    "notice",
    "warning",
    "err",
    "crit",
    "alert",
    "emer",
]
SYSLOG_FACILITIES = [
    "kern",
    "user",
    "mail",
    "daemon",
    "auth",
    "syslog",
    "lpr",
    "news",
    "uucp",
    "authpriv",
    "cron",
    "ftp",
]
AGGREGATE_FUNCTIONS = [
    "Rate",
    "Count",
    "CountOverTime",
    "Sum",
    "SumOverTime",
    "Min",
    "MinOverTime",
    "Max",
    "MaxOverTime",
    "Average",
    "AverageOverTime",
]


def main():
    condition_spec = dict(
        source=dict(type="str", required=True),
        expression=dict(type="str", required=True),
        alert_level=dict(
            type="str",
            default="normal",
            choices=["critical", "major", "minor", "normal"],
        ),
        syslog=dict(
            type="dict",
            options=dict(
                text=dict(type="str", required=True),
                severity=dict(
                    type="str", default="info", choices=SYSLOG_SEVERITIES
                ),
                facility=dict(
                    type="str", default="daemon", choices=SYSLOG_FACILITIES
                ),
            ),
        ),
        cli_commands=dict(type="list", elements="str"),
        schedule=dict(type="list", elements="str"),
        snmp_trap=dict(type="str"),
    )
    module_args = dict(
        name=dict(type="str", required=True),
        description=dict(type="str"),
        disabled=dict(type="bool"),
        tags=dict(type="list", elements="str"),
        monitors=dict(
            type="list",
            elements="dict",
            options=dict(
                name=dict(type="str", required=True),
                resource=dict(type="str", required=True),
                aggregate_by=dict(type="str", choices=AGGREGATE_FUNCTIONS),
                time_interval=dict(type="str"),
            ),
        ),
        watches=dict(
            type="list",
            elements="dict",
            options=dict(
                name=dict(type="str", required=True),
                event_ids=dict(type="list", elements="int", required=True),
            ),
        ),
        condition=dict(type="dict", options=condition_spec),
        clear_condition=dict(type="dict", options=condition_spec),
        activate=dict(type="bool", default=True),
        wait=dict(type="bool", default=True),
        timeout=dict(type="int", default=60),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[("monitors", "watches")],
        required_by={"clear_condition": "condition"},
        supports_check_mode=True,
    )
    params = ansible_module.params
    name = params["name"]
    state = params["state"]
    result = dict(changed=False)

    if not NAME_RE.match(name):
        ansible_module.fail_json(
            msg=(
                "Invalid NAE-Lite agent name {0}: use 3 to 80 letters, "
                "digits or underscores.".format(name)
            )
        )

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        agent = session.api.get_module(session, "NaeLiteAgent", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support NAE-Lite agents. "
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
                        "Could not delete NAE-Lite agent {0}".format(name),
                        e,
                    )
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    desired = _desired_agent(ansible_module, params)
    sources = _sources(desired, agent if exists else None)
    _validate_conditions(ansible_module, params, sources)

    if not exists:
        if not desired.get("monitors") and not desired.get("watches"):
            ansible_module.fail_json(
                msg=(
                    "NAE-Lite agent {0} does not exist: monitors or watches "
                    "are required to create it.".format(name)
                )
            )
        result["changed"] = True
        if ansible_module.check_mode:
            ansible_module.exit_json(**result)
        agent = session.api.get_module(
            session, "NaeLiteAgent", name, **desired
        )
        _call(ansible_module, session, agent.create, "create", name)
        ready = False
    else:
        ready = bool(getattr(agent, "ready", False))
        for key, value in desired.items():
            if _normalize_agent_value(
                key, getattr(agent, key, None)
            ) != _normalize_agent_value(key, value):
                result["changed"] = True
                setattr(agent, key, value)
                if key not in agent.config_attrs:
                    agent.config_attrs.append(key)
        if result["changed"] and not ansible_module.check_mode:
            _call(ansible_module, session, agent.update, "update", name)

    if params["condition"] is not None:
        if _apply_conditions(ansible_module, session, agent, params, sources):
            result["changed"] = True

    # ----------------------------------------------------------- activation
    if params["activate"]:
        activate = result["changed"] or not ready
    else:
        activate = False
        if ready:
            result["changed"] = True
            if not ansible_module.check_mode:
                _call(
                    ansible_module,
                    session,
                    agent.deactivate,
                    "deactivate",
                    name,
                )
    if activate:
        result["changed"] = True

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if activate:
        _call(ansible_module, session, agent.activate, "activate", name)

    try:
        if activate and params["wait"]:
            status = agent.wait_for_activation(timeout=params["timeout"])
        else:
            status = agent.get_status()
    except Exception as e:
        ansible_module.fail_json(
            msg=pyaoscx_error_message(
                session, "Could not read NAE-Lite agent {0}".format(name), e
            ),
            **result
        )
    result["nae_lite_agent"] = status

    if activate and params["wait"]:
        if status["state"] == "ERROR":
            ansible_module.fail_json(
                msg="NAE-Lite agent {0} failed: {1}".format(
                    name, status["error_description"]
                ),
                **result
            )
        if status["state"] != "AGENT_CREATED":
            ansible_module.fail_json(
                msg=(
                    "NAE-Lite agent {0} is not generated after {1} seconds "
                    "(state {2}).".format(
                        name, params["timeout"], status["state"]
                    )
                ),
                **result
            )

    ansible_module.exit_json(**result)


def _call(ansible_module, session, method, action, name):
    try:
        method()
    except Exception as e:
        ansible_module.fail_json(
            msg=pyaoscx_error_message(
                session,
                "Could not {0} NAE-Lite agent {1}".format(action, name),
                e,
            )
        )


def _desired_agent(ansible_module, params):
    """Build the requested agent attributes, in the switch format."""
    desired = {}
    for key in ("description", "disabled", "tags"):
        if params[key] is not None:
            desired[key] = params[key]

    if params["monitors"] is not None:
        _check_items(ansible_module, "monitors", params["monitors"])
        monitors = {}
        for monitor in params["monitors"]:
            entry = {"resource": monitor["resource"]}
            for key in ("aggregate_by", "time_interval"):
                if monitor[key] is not None:
                    entry[key] = monitor[key]
            monitors[monitor["name"]] = entry
        desired["monitors"] = monitors
        desired["watches"] = {}

    if params["watches"] is not None:
        _check_items(ansible_module, "watches", params["watches"])
        watches = {}
        for watch in params["watches"]:
            for event_id in watch["event_ids"]:
                if not 101 <= event_id <= 32767:
                    ansible_module.fail_json(
                        msg=(
                            "Invalid event ID {0} in watch {1}: must be "
                            "between 101 and 32767.".format(
                                event_id, watch["name"]
                            )
                        )
                    )
            watches[watch["name"]] = {
                "type": "event_log",
                "event_id": ",".join(str(i) for i in watch["event_ids"]),
            }
        desired["watches"] = watches
        desired["monitors"] = {}

    return desired


def _check_items(ansible_module, option, items):
    if len(items) > 2:
        ansible_module.fail_json(
            msg="A NAE-Lite agent supports at most two {0}.".format(option)
        )
    names = [item["name"] for item in items]
    if len(set(names)) != len(names):
        ansible_module.fail_json(
            msg="Duplicate names in {0}: {1}.".format(option, ", ".join(names))
        )
    for item_name in names:
        if not 3 <= len(item_name) <= 80:
            ansible_module.fail_json(
                msg=(
                    "Invalid name {0} in {1}: use 3 to 80 characters.".format(
                        item_name, option
                    )
                )
            )


def _sources(desired, agent):
    """Return the monitors and watches the conditions can use."""
    if "monitors" in desired:
        return {
            "monitor_resource": set(desired["monitors"]),
            "watch_event_log": set(desired["watches"]),
        }
    return {
        "monitor_resource": set(getattr(agent, "monitors", None) or {}),
        "watch_event_log": set(getattr(agent, "watches", None) or {}),
    }


def _validate_conditions(ansible_module, params, sources):
    known = sources["monitor_resource"] | sources["watch_event_log"]
    for option, dummy in CONDITION_TYPES:
        condition = params[option]
        if condition is not None and condition["source"] not in known:
            ansible_module.fail_json(
                msg=(
                    "The source {0} of {1} is not a monitor or watch of the "
                    "agent ({2}).".format(
                        condition["source"],
                        option,
                        ", ".join(sorted(known)) or "none",
                    )
                )
            )


def _normalize_agent_value(key, value):
    if key == "watches":
        return {
            watch_name: sorted(
                int(i) for i in str(watch.get("event_id", "")).split(",") if i
            )
            for watch_name, watch in (value or {}).items()
        }
    if key == "monitors":
        return {
            monitor_name: {k: v for k, v in monitor.items() if v is not None}
            for monitor_name, monitor in (value or {}).items()
        }
    if key == "tags":
        return value or []
    return value


def _unquote(value):
    # The CLI stores the messages between double quotes
    if (
        isinstance(value, str)
        and len(value) >= 2
        and value[0] == value[-1] == '"'
    ):
        return value[1:-1]
    return value


def _condition_body(condition, sources, current=None):
    """Build the full PUT/POST body of a condition."""
    expression_type = (
        "monitor_resource"
        if condition["source"] in sources["monitor_resource"]
        else "watch_event_log"
    )
    syslog = condition["syslog"]
    return {
        "expression": condition["expression"],
        "expression_type": expression_type,
        "resource_name": {"0": condition["source"]},
        "action_alert_state": condition["alert_level"],
        # Kept as set with the CLI, see the module notes
        "action_alert_description": (current or {}).get(
            "action_alert_description"
        ),
        "action_cli_commands": (
            CLI_SEPARATOR.join(condition["cli_commands"])
            if condition["cli_commands"]
            else None
        ),
        "action_schedule": (
            CLI_SEPARATOR.join(condition["schedule"])
            if condition["schedule"]
            else None
        ),
        "action_snmp": condition["snmp_trap"] or None,
        "action_syslog": (
            {
                "message": syslog["text"],
                "severity": syslog["severity"],
                "facility": syslog["facility"],
            }
            if syslog
            else None
        ),
    }


def _normalize_condition(body):
    syslog = body.get("action_syslog") or {}
    message = _unquote(syslog.get("message"))
    return {
        "expression": body.get("expression"),
        "expression_type": body.get("expression_type"),
        "resource_name": {
            str(k): v for k, v in (body.get("resource_name") or {}).items()
        },
        "action_alert_state": body.get("action_alert_state") or "normal",
        "action_cli_commands": body.get("action_cli_commands") or None,
        "action_schedule": body.get("action_schedule") or None,
        "action_snmp": body.get("action_snmp") or None,
        "action_syslog": (
            {
                "message": message,
                "severity": syslog.get("severity") or "info",
                "facility": syslog.get("facility") or "daemon",
            }
            if message
            else None
        ),
    }


def _apply_conditions(ansible_module, session, agent, params, sources):
    """Create, update or remove the condition and the clear condition."""
    changed = False
    for option, condition_type in CONDITION_TYPES:
        desired = params[option]
        condition = session.api.get_module(
            session,
            "NaeLiteCondition",
            RULE_NAME,
            condition_type=condition_type,
            parent_nae_lite_agent=agent,
        )
        try:
            condition.get()
            exists = True
        except Exception:
            exists = False

        if desired is None:
            if exists:
                changed = True
                if not ansible_module.check_mode:
                    _call_condition(ansible_module, session, condition.delete)
            continue

        current = (
            {
                key: getattr(condition, key, None)
                for key in condition.config_attrs
            }
            if exists
            else None
        )
        body = _condition_body(desired, sources, current)
        if exists and _normalize_condition(current) == _normalize_condition(
            body
        ):
            continue

        changed = True
        if ansible_module.check_mode:
            continue
        if exists:
            for key, value in body.items():
                setattr(condition, key, value)
                if key not in condition.config_attrs:
                    condition.config_attrs.append(key)
            _call_condition(ansible_module, session, condition.update)
        else:
            condition = session.api.get_module(
                session,
                "NaeLiteCondition",
                RULE_NAME,
                condition_type=condition_type,
                parent_nae_lite_agent=agent,
                **body
            )
            _call_condition(ansible_module, session, condition.create)
    return changed


def _call_condition(ansible_module, session, method):
    try:
        method()
    except Exception as e:
        ansible_module.fail_json(
            msg=pyaoscx_error_message(
                session, "Could not configure the NAE-Lite condition", e
            )
        )


if __name__ == "__main__":
    main()
