# module: aoscx_nae_agent

description: This module creates, updates, enables, disables and deletes the
Network Analytics Engine (NAE) agents of a NAE script on AOS-CX devices, and
returns their status and alert information. The script is uploaded with the
aoscx_nae_script module.

##### ARGUMENTS

```YAML
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
      encrypted_parameters.
    required: false
    type: dict
  encrypted_parameters:
    description: >
      Values of the encrypted script parameters, keyed by parameter name.
      The switch only returns their encrypted form, see
      update_encrypted_parameters.
    required: false
    type: dict
  update_encrypted_parameters:
    description: >
      on_create only sets the encrypted parameters that have no value yet,
      so that the module stays idempotent. always sets them on every run
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
```

##### EXAMPLES

```YAML
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
```
