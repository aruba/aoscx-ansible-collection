# module: aoscx_captive_portal_profile

description: This module provides configuration management of Captive Portal
Profiles on AOS-CX devices (system/captive_portal_profiles). A captive portal
profile defines the redirect URL used to onboard clients, and can be referenced
by a port access role. This module requires REST API version 10.16 (set
ansible_aoscx_rest_version to 10.16).

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the captive portal profile. This is the index of the resource
      under system/captive_portal_profiles.
    required: true
    type: str
  url:
    description: Captive portal redirect URL.
    required: false
    type: str
  url_hash_key:
    description: >
      Key used to compute the hash appended to the captive portal URL.
    required: false
    type: str
  state:
    description: Create, update or delete the captive portal profile.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
```

##### EXAMPLES

```YAML
- name: Create a captive portal profile
  aoscx_captive_portal_profile:
    name: guest-portal
    url: https://cp.example.com/guest

- name: Update the captive portal URL
  aoscx_captive_portal_profile:
    name: guest-portal
    url: https://cp.example.com/guest2
    state: update

- name: Delete a captive portal profile
  aoscx_captive_portal_profile:
    name: guest-portal
    state: delete
```
