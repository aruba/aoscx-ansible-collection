# module: aoscx_backup_config

description: This module downloads an existing configuration from AOS-CX devices.  

##### ARGUMENTS
```YAML
  config_name:
    description: "Config file or checkpoint to be downloaded. When using TFTP
      only running-config or startup-config can be used"
    type: str
    default: 'running-config'
    required: false
  output_file:
    description: "File name and path for locally downloading configuration,
      only JSON version of configuration will be downloaded"
    type: str
    required: false
  remote_output_file_tftp_path:
    description: "TFTP server address and path for copying off configuration,
      must be reachable through provided vrf
      ex) tftp://192.168.1.2/config.txt"
    type: str
    required: false
  config_type:
    description: Configuration type to be downloaded, JSON or CLI version of the config.
    type: str
    choices: ['json', 'cli']
    default: 'json'
    required: false
  vrf:
    description: VRF to be used to contact TFTP server, required if remote_output_file_tftp_path is provided
    type: str
    required: false
```

##### EXAMPLES
```YAML
 - name: Copy Running Config to local as JSON
   aoscx_backup_config:
     config_name: 'running-config'
     output_file: '/home/admin/running-config.json'

 - name: Copy Startup Config to local as JSON
   aoscx_backup_config:
     config_name: 'startup-config'
     output_file: '/home/admin/startup-config.json'

 - name: Copy Checkpoint Config to local as JSON
   aoscx_backup_config:
     config_name: 'checkpoint1'
     output_file: '/home/admin/checkpoint1.json'

 - name: Copy Running Config to TFTP server as JSON
   aoscx_backup_config:
     config_name: 'running-config'
     remote_output_file_tftp_path: 'tftp://192.168.1.2/running.json'
     config_type: 'json'
     vrf: 'mgmt'

 - name: Copy Running Config to TFTP server as CLI
   aoscx_backup_config:
     config_name: 'running-config'
     remote_output_file_tftp_path: 'tftp://192.168.1.2/running.cli'
     config_type: 'cli'
     vrf: 'mgmt'

 - name: Copy Startup Config to TFTP server as CLI
   aoscx_backup_config:
     config_name: 'startup-config'
     remote_output_file_tftp_path: 'tftp://192.168.1.2/startup.cli'
     config_type: 'cli'
     vrf: 'mgmt'
```