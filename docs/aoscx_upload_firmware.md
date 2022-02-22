# module: aoscx_upload_firmware

description: This module uploads a firmware image onto the switch stored
locally or it can also upload the firmware from an HTTP server.

##### ARGUMENTS

```YAML
  partition_name:
    description: Name of the partition for the image to be uploaded.
    type: str
    default: primary
    choices:
      - primary
      - secondary
    required: false
  firmware_file_path:
    description: File name and path for locally uploading firmware image
    type: str
    required: false
  remote_firmware_file_path:
    description: >
      HTTP server address and path for uploading firmware image, must be
      reachable through provided vrf.
    type: str
    required: false
  vrf:
    description: >
      VRF to be used to contact HTTP server, required if
      remote_firmware_file_path is provided.
    type: str
    required: false
```

##### EXAMPLES

```YAML
- name: Upload firmware to primary through HTTP
  aoscx_upload_firmware:
    partition_name: 'primary'
    remote_firmware_file_path: 'http://192.168.1.2:8000/TL_10_04_0030P.swi'
    vrf: 'mgmt'

- name: Upload firmware to secondary through local
  aoscx_upload_firmware:
    partition_name: 'secondary'
    firmware_file_path: '/tftpboot/TL_10_04_0030A.swi'
```
