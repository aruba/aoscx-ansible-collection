# module: aoscx_banner

description: This modules provides configuration management of Banner on AOS-CX
devices.

##### ARGUMENTS

```YAML
  banner_type:
    description: Type of banner being configured on the switch.
    required: True
    choices:
      - banner
      - banner_exec
    type: str

  state:
    description: Create or Delete Banner on the switch.
    default: create
    choices:
      - create
      - delete
    required: False
    type: str

  banner:
    description : String to be configured as the banner.
    required: True
    type: str
```

##### EXAMPLES

```YAML
- name: Adding or Updating Banner
  aoscx_banner:
    banner_type: banner
    banner: "Aruba Rocks!"

- name: Delete Banner
  aoscx_banner:
    banner_type: banner
    state: delete

- name: Delete Exec Banner
  aoscx_banner:
    banner_type: banner_exec
    state: delete
```
