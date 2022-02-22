# module: aoscx_upload_config

description: This module uploads a configuration onto the switch stored locally
or it can also upload the configuration from a TFTP server.

##### ARGUMENTS

```YAML
  config_name:
    description: "Config file or checkpoint to be uploaded to. When using TFTP
      only running-config or startup-config can be used"
    type: str
    default: 'running-config'
    required: false
  config_json:
    description: "JSON file name and path for locally uploading configuration,
      only JSON version of configuration can be uploaded"
    type: str
    required: false
  config_file:
    description: "File name and path for locally uploading configuration,
      will be converted to JSON,
      only JSON version of configuration can be uploaded"
    type: str
    required: false
  remote_config_file_tftp_path:
    description: "TFTP server address and path for uploading configuration,
      can be JSON or CLI format, must be reachable through provided vrf
      ex) tftp://192.168.1.2/config.txt"
    type: str
    required: false
  vrf:
    description: >
      VRF to be used to contact TFTP server, required if
      remote_output_file_tftp_path is provided.
    type: str
    required: false
```

##### EXAMPLES

```YAML
- name: Copy Running Config from local JSON file as JSON
  aoscx_upload_config:
    config_name: 'running-config'
    remote_config_file_tftp_path: '/user/admin/running.json'

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
```
