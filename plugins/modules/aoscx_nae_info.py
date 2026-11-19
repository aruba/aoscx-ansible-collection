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
module: aoscx_nae_info
version_added: "4.6.0"
short_description: Collect the status and alerts of NAE on AOS-CX
description: >
  This module collects the Network Analytics Engine (NAE) information of an
  AOS-CX device: the highest alert level of the switch, the scripts and
  their validation status, the agents with their status and alert
  information, the NAE-Lite agents with their generation status, and the
  list of agents with an alert. It does not change the switch
  configuration.
author: Aruba Networks (@ArubaNetworks)
options:
  script_name:
    description: >
      Only collect this script, its agents and the NAE-Lite agent with this
      name.
    required: false
    type: str
  agent_name:
    description: >
      Only collect the agents and the NAE-Lite agent with this name.
    required: false
    type: str
  include_conditions:
    description: >
      Add to each collected agent its rules and conditions, with the number
      of times each condition was met and the condition events not yet
      processed by the agent. This needs several requests per agent.
    required: false
    default: false
    type: bool
"""

EXAMPLES = """
- name: Collect the NAE status and alerts
  aoscx_nae_info:
  register: nae_info

- name: Show the agents with an alert
  ansible.builtin.debug:
    msg: >-
      {{ item.agent }}: {{ item.alert_level }} {{ item.alert_description }}
  loop: "{{ nae_info.nae.alerts }}"

- name: Fail when an agent has a critical alert
  ansible.builtin.assert:
    that: nae_info.nae.aggregated_alert_level != 'CRITICAL'

- name: Collect the conditions and events of an agent
  aoscx_nae_info:
    agent_name: high_cpu
    include_conditions: true
"""

RETURN = r"""
nae:
  description: NAE information of the switch.
  returned: always
  type: dict
  contains:
    aggregated_alert_level:
      description: >
        Highest alert level of all agents: CRITICAL, MAJOR, MINOR or NORMAL.
      type: str
    scripts:
      description: >
        Scripts keyed by name, with their information (origin, version,
        author, description...) and validation state and
        error_description.
      type: dict
    agents:
      description: >
        Agents keyed by name, with their script, origin, disabled, vrf,
        state, alert_level, alert_description, alert_level_updated_at,
        alerts_count, error_description, error_at, executed_at and
        counters, and conditions when I(include_conditions) is set.
      type: dict
    lite_agents:
      description: >
        NAE-Lite agents keyed by name, with their configuration (description,
        disabled, tags, monitors, watches), ready, and generation state and
        error_description.
      type: dict
    alerts:
      description: >
        Agents with an alert level other than NORMAL, from the most to the
        least severe.
      type: list
      elements: dict
      sample:
        - agent: high_cpu
          script: high_cpu
          alert_level: CRITICAL
          alert_description: critical - High CPU
          alert_level_updated_at: 1795105680
          alerts_count: 1
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
    pyaoscx_error_message,
)

ALERT_ORDER = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}


def main():
    module_args = dict(
        script_name=dict(type="str"),
        agent_name=dict(type="str"),
        include_conditions=dict(type="bool", default=False),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )
    params = ansible_module.params
    script_name = params["script_name"]
    agent_name = params["agent_name"]

    for value in (script_name, agent_name):
        if value is not None and ("/" in value or value in ("", ".", "..")):
            ansible_module.fail_json(msg="Invalid name: {0}".format(value))

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        script_class = session.api.get_module_class(session, "NaeScript")
        agent_class = session.api.get_module_class(session, "NaeAgent")
        lite_class = session.api.get_module_class(session, "NaeLiteAgent")
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support NAE. Upgrade pyaoscx. "
                "Details: {0}".format(str(e))
            )
        )

    nae = {}
    try:
        nae["aggregated_alert_level"] = agent_class.get_aggregated_alert_level(
            session
        )

        scripts = script_class.get_facts(session)
        if script_name is not None:
            scripts = {
                name: info
                for name, info in scripts.items()
                if name == script_name
            }
        nae["scripts"] = scripts

        if script_name is not None and script_name not in scripts:
            agents = {}
        else:
            agents = agent_class.get_facts(session, script_name)
        if agent_name is not None:
            agents = {
                name: info
                for name, info in agents.items()
                if name == agent_name
            }
        nae["agents"] = agents

        nae["lite_agents"] = _lite_agents(
            session, lite_class, script_name, agent_name
        )

        if params["include_conditions"]:
            for name, info in agents.items():
                agent = session.api.get_module(
                    session, "NaeAgent", name, parent_nae_script=info["script"]
                )
                info["conditions"] = agent.get_conditions()
    except Exception as e:
        ansible_module.fail_json(
            msg=pyaoscx_error_message(
                session, "Could not collect the NAE information", e
            )
        )

    nae["alerts"] = sorted(
        (
            {
                "agent": name,
                "script": info["script"],
                "alert_level": info["alert_level"],
                "alert_description": info["alert_description"],
                "alert_level_updated_at": info["alert_level_updated_at"],
                "alerts_count": info["alerts_count"],
            }
            for name, info in nae["agents"].items()
            if info["alert_level"] in ALERT_ORDER
        ),
        key=lambda alert: (ALERT_ORDER[alert["alert_level"]], alert["agent"]),
    )

    ansible_module.exit_json(changed=False, nae=nae)


def _lite_agents(session, lite_class, script_name, agent_name):
    try:
        data = lite_class.get_facts(session)
    except Exception as e:
        # Firmware versions before 10.10 do not support NAE-Lite
        if getattr(e, "response_code", None) == 404:
            return {}
        raise
    agents = {}
    for name, agent in data.items():
        if name != (script_name or name) or name != (agent_name or name):
            continue
        status = agent.pop("status", None) or {}
        agent.pop("name", None)
        agent["state"] = status.get("state")
        agent["error_description"] = status.get("error_description") or None
        agent["error_at"] = status.get("error_at") or None
        agents[name] = agent
    return agents


if __name__ == "__main__":
    main()
