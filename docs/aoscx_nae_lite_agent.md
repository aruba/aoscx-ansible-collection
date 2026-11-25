# module: aoscx_nae_lite_agent

description: This module manages NAE-Lite agents (CLI nae-agent lite) on AOS-CX
devices: the monitored resources or watched event logs, the condition and clear
condition, and the actions executed when they are met. Once activated, the
switch generates a NAE script and a NAE agent with the name of the NAE-Lite
agent. The module returns the generation status and the status and alert
information of the generated agent.

##### NOTES

- The REST API does not accept the alert description of the CLI status <level>
  description command in a form the switch can use. The module does not set it,
  and keeps a description set with the CLI.
- Requires AOS-CX 10.10 or later.

##### ARGUMENTS

```YAML
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
      watches. When provided, this is the full list of monitors.
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
          Monitored resource, as in the CLI monitor <name> resource
          command, for example system cpu, system memory,
          system storage or system cpu vsf.
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
          5 minutes. Not supported by every firmware.
        required: false
        type: str
  watches:
    description: >
      Event logs watched by the agent, at most two. Mutually exclusive with
      monitors. When provided, this is the full list of watches.
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
      Condition of the agent (CLI set-condition) and the actions executed
      when it is met. When provided, condition and clear_condition
      describe the full rule: an existing clear condition is removed when
      clear_condition is omitted.
    required: false
    type: dict
    suboptions:
      source:
        description: Name of the monitor or watch the condition applies to.
        required: true
        type: str
      expression:
        description: >
          Condition expression, as stored by the switch. On a monitor, an
          operator (lt, le, eq, ne, gt, ge) and a value
          with an optional duration, for example gt 90 or
          gt 90 for 2 minutes, or a transition, for example
          transition from "up" to "down","error". On a watch, for
          example count 5, include any "error,fail" count 2 or
          exclude "Ok".
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
          example schedule s1, 10 job j1 and
          trigger every minutes 30.
        required: false
        type: list
        elements: str
      snmp_trap:
        description: SNMP trap message sent when the condition is met.
        required: false
        type: str
  clear_condition:
    description: >
      Optional clear condition (CLI clear-condition): once the condition
      is met, it is suspended until the clear condition is met. Requires
      condition.
    required: false
    type: dict
    suboptions: Same suboptions as condition.
  activate:
    description: >
      Activate the agent (CLI nae-agent lite <name> activate), so that the
      switch generates it. An activated agent is generated again when the
      module changes it. false deactivates the agent.
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
```

##### EXAMPLES

```YAML
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
```
