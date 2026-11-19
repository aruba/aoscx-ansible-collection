# module: aoscx_upload_config

description: This module uploads a configuration onto the switch stored locally
or it can also upload the configuration from a TFTP server. A local configuration
in CLI format can also be pushed directly in the REST payload, without TFTP.

##### ARGUMENTS

```YAML
  config_name:
    description: >
      Switch config file to be uploaded to, only running-config or startup-config can be used
    type: str
    default: 'running-config'
    required: false
  config_json:
    description: >
      JSON file name and path for locally uploading configuration, only JSON version of configuration can be uploaded
    type: str
    required: false
  config_file:
    description: >
      File name and path  of JSON formatted config for locally
      uploading configuration, will be converted to JSON, CLI NOT SUPPORTED
    type: str
    required: false
  remote_config_file_tftp_path:
    description: >
      TFTP server address and path for uploading configuration,
      can be JSON or CLI format, must be reachable through provided vrf ex) tftp://192.168.1.2/config.txt
    type: str
    required: false
  vrf:
    description: >
      VRF to be used to contact TFTP server, required if
      remote_output_file_tftp_path is provided.
    type: str
    required: false
  config_cli:
    description: >
      Local file name and path of a configuration in CLI format. Its content
      is sent directly to the switch in the REST request payload, no TFTP
      server is needed. Requires a pyaoscx version providing
      Configuration.upload_switch_config_cli_from_local.
      If the switch refuses the CLI format upload itself (HTTP 400, 404, 405
      or 415), the task fails stating it is probably not supported by the
      switch platform or firmware version.
    type: str
    required: false
  operation:
    description: >
      Operation to perform when uploading a CLI configuration with config_cli.
      replace replaces the whole configuration, merge merges the CLI
      configuration into the existing one. Only used with config_cli.
      If the switch rejects commands, the task fails and the errors are
      returned (errors). With replace nothing is applied, with merge the
      valid lines are applied.
    type: str
    choices:
      - replace
      - merge
    default: replace
    required: false
```

##### EXAMPLES

```YAML
- name: Copy Running Config from local JSON file as JSON
  aoscx_upload_config:
    config_name: 'running-config'
    config_file: '/user/admin/running.json'

- name: Copy Running Config from TFTP server as JSON
  aoscx_upload_config:
    config_name: 'running-config'
    remote_config_file_tftp_path: 'tftp://192.168.1.2/running.json'
    vrf: 'mgmt'

- name: Copy CLI from TFTP Server to Running Config
  aoscx_upload_config:
    config_name: 'running-config'
    remote_config_file_tftp_path: 'tftp://192.168.1.2/running.cli'
    vrf: 'mgmt'

- name: Copy CLI from TFTP Server to Startup Config
  aoscx_upload_config:
    config_name: 'startup-config'
    remote_config_file_tftp_path: 'tftp://192.168.1.2/startup.cli'
    vrf: 'mgmt'

- name: Replace Running Config with a local CLI file (no TFTP)
  aoscx_upload_config:
    config_name: 'running-config'
    config_cli: '/user/admin/running.cli'

- name: Merge a local CLI file into the Running Config (no TFTP)
  aoscx_upload_config:
    config_name: 'running-config'
    config_cli: '/user/admin/vlans.cli'
    operation: merge

- name: Upload a local CLI file and show the commands rejected by the switch
  aoscx_upload_config:
    config_cli: '/user/admin/running.cli'
  register: upload
  ignore_errors: true

- name: Display the switch errors
  debug:
    var: upload.errors
  when: upload is failed
```

##### RETURN VALUES

```YAML
errors:
  description: >
    Errors returned by the switch when a CLI configuration (config_cli) is
    rejected. Each error gives the line number in the file, the configuration
    context, the command and the error message.
  returned: failure with config_cli
  type: list
  elements: dict
  sample:
    - line: 34
      context: ["configure terminal", "interface 1/1/2"]
      command: "    vlan acess 10"
      message: "Invalid input: acess"
```
