# module: aoscx_nae_script

description: This module uploads, updates and deletes Network Analytics Engine
(NAE) scripts on AOS-CX devices, and returns their validation status and the
parameters they define. The agents running a script are managed with the
aoscx_nae_agent module. NAE-Lite agents, and the scripts the switch generates
for them, are managed with the aoscx_nae_lite_agent module.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the NAE script, 3 to 80 letters, digits, underscores or dots.
      It should match the Name of the script Manifest.
    required: true
    type: str
  script:
    description: >
      Python source of the NAE script. Mutually exclusive with src and
      script_base64. One of them is required to upload a new script.
    required: false
    type: str
  script_base64:
    description: >
      Content of the NAE script encoded in Base64, as sent to the switch.
      Line breaks are ignored. Mutually exclusive with script and
      src.
    required: false
    type: str
  src:
    description: >
      Path of a file holding the Python source of the NAE script, on the
      Ansible controller. A relative path is resolved from the directory
      ansible-playbook is run from: use for example
      {{ playbook_dir }}/files/monitor.py. Mutually exclusive with
      script and script_base64.
    required: false
    type: path
  expert_only:
    description: Whether the script requires expert level knowledge.
    required: false
    type: bool
  wait_for_validation:
    description: >
      Wait until the switch has validated an uploaded or updated script, and
      fail when the validation fails or when the script is in error. Agents
      cannot be created before the script is validated.
    required: false
    default: true
    type: bool
  timeout:
    description: Maximum time to wait for the validation, in seconds.
    required: false
    default: 60
    type: int
  state:
    description: >
      Upload or update the script, or delete it with its agents. Scripts
      provided by the system or generated for NAE-Lite agents cannot be
      changed or deleted.
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
- name: Upload a NAE script from a local file
  aoscx_nae_script:
    name: interface_link_monitor
    src: "{{ playbook_dir }}/files/interface_link_monitor.py"

- name: Upload a NAE script already encoded in Base64
  aoscx_nae_script:
    name: interface_link_monitor
    script_base64: "{{ interface_link_monitor_b64 }}"

- name: Upload a NAE script from a template
  aoscx_nae_script:
    name: bgp_monitor
    script: "{{ lookup('ansible.builtin.template', 'bgp_monitor.py.j2') }}"

- name: Delete a NAE script and its agents
  aoscx_nae_script:
    name: bgp_monitor
    state: delete
```
