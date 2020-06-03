# module: aoscx_boot_firmware

description: This module boots the AOS-CX switch with the image present to the specified partition.  

##### ARGUMENTS
```YAML
  partition_name:
    description: Name of the partition for device to boot to.
    type: str
    default: 'primary'
    choices: ['primary', 'secondary']
    required: false
```

##### EXAMPLES
```YAML
- name: Boot to primary
  aoscx_boot_firmware:
    partition_name: 'primary'

- name: Boot to secondary
  aoscx_boot_firmware:
    partition_name: 'secondary'
```