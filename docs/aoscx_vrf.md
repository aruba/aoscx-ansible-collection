# module: aoscx_vrf

description: This modules provides configuration management of VRFs on AOS-CX
devices.

##### ARGUMENTS

```YAML
  name:
    description: The name of the VRF
    required: true
    type: str
  state:
    description: Create or delete the VRF.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
```

##### EXAMPLES

```YAML
- name: Create a VRF
  aoscx_vrf:
    name: red
    state: create

- name: Delete a VRF
  aoscx_vrf:
    name: red
    state: delete
```
