# module: aoscx_checkpoint

description: This module creates a new checkpoint or copies an existing
checkpoint to the running or startup config of an AOS-CX switch.

##### ARGUMENTS

```YAML
  source_config:
    description: >
      Name of the source configuration from which checkpoint needs to be
      created or copied.
    type: str
    required: false
    default: running-config
  destination_config:
    description: Name of the destination configuration or name of checkpoint.
    type: str
    required: false
    default: startup-config
```

##### EXAMPLES

```YAML
- name: Copy running-config to startup-config
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'startup-config'

- name: Copy startup-config to running-config
  aoscx_checkpoint:
    source_config: 'startup-config'
    destination_config: 'running-config'

- name: Copy running-config to backup checkpoint
  aoscx_checkpoint:
    source_config: 'running-config'
    destination_config: 'checkpoint_20200128'
```
