# module: aoscx_nae_info

description: This module collects the Network Analytics Engine (NAE)
information of an AOS-CX device: the highest alert level of the switch, the
scripts and their validation status, the agents with their status and alert
information, the NAE-Lite agents with their generation status, and the list of
agents with an alert. It does not change the switch configuration.

##### ARGUMENTS

```YAML
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
```

##### EXAMPLES

```YAML
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
```
