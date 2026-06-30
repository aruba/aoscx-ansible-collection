# module: aoscx_vxlan_interface

description: This module provides configuration management of the VXLAN tunnel
interface (for example vxlan1) on AOS-CX devices: its source IPv4 address, the
destination UDP port, the administrative state and the description. The
VNI-to-VLAN and VNI-to-VRF mappings carried by the interface are managed with
the aoscx_vni module.

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the VXLAN tunnel interface, in the format vxlanN, for example
      vxlan1.
    required: true
    type: str
  source_ip:
    description: >
      Source IPv4 address used for VXLAN encapsulation, for example 10.0.0.1.
      Equivalent to the CLI source ip command.
    required: false
    type: str
  dest_udp_port:
    description: >
      Destination UDP port used by the VXLAN tunnel. When omitted the switch
      default (4789) is kept.
    required: false
    type: int
  description:
    description: Description of the VXLAN interface.
    required: false
    type: str
  enabled:
    description: >
      Administrative state of the interface. true brings the interface up
      (no shutdown), false shuts it down. When omitted, a newly created
      interface is brought up and an existing interface is left unchanged.
    required: false
    type: bool
  state:
    description: Create, update or delete the VXLAN interface.
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
- name: Create VXLAN interface vxlan1 with a source IP and bring it up
  aoscx_vxlan_interface:
    name: vxlan1
    source_ip: 10.141.254.11
    enabled: true
    state: create

- name: Update the destination UDP port and description of vxlan1
  aoscx_vxlan_interface:
    name: vxlan1
    dest_udp_port: 4789
    description: EVPN-VXLAN overlay
    state: update

- name: Shut down the VXLAN interface
  aoscx_vxlan_interface:
    name: vxlan1
    enabled: false
    state: update

- name: Delete the VXLAN interface
  aoscx_vxlan_interface:
    name: vxlan1
    state: delete
```
