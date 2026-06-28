# module: aoscx_vni

description: This module provides configuration management of Virtual Network
Identifiers (VNIs) on AOS-CX devices. A VNI maps a network segment onto a
VXLAN tunnel interface. A Layer 2 VNI maps the segment to a VLAN, while a
Layer 3 VNI maps it to a VRF with routing enabled. A VNI is identified by the
compound index (vni_type, vni_id).

##### ARGUMENTS

```YAML
  vni_id:
    description: >
      Numeric identifier of the VNI (VXLAN Network Identifier), in the range
      1 to 16777215.
    required: true
    type: int
  interface:
    description: >
      Name of the VXLAN tunnel interface the VNI is attached to, for example
      vxlan1. The interface must already exist and be of type VXLAN.
    required: true
    type: str
  vni_type:
    description: Type of the VNI. Only VXLAN VNIs are supported.
    required: false
    default: vxlan_vni
    choices:
      - vxlan_vni
    type: str
  vlan:
    description: >
      VLAN ID mapped to the VNI for a Layer 2 VNI. Mutually exclusive with
      vrf. The VLAN must already exist on the device. When omitted it is left
      unchanged. Ignored when state is delete.
    required: false
    type: int
  vrf:
    description: >
      Name of the VRF mapped to the VNI for a Layer 3 VNI. Mutually exclusive
      with vlan. The VRF must already exist on the device. When omitted it is
      left unchanged. Ignored when state is delete.
    required: false
    type: str
  routing:
    description: >
      Whether routing is enabled for the VNI. Enable it for a Layer 3 (VRF)
      VNI. When omitted it is left unchanged. Ignored when state is delete.
    required: false
    type: bool
  state:
    description: Create, update or delete the VNI.
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
- name: Create a Layer 2 VNI mapping VLAN 4000
  aoscx_vni:
    vni_id: 40000
    interface: vxlan1
    vlan: 4000

- name: Create a Layer 3 VNI mapping a VRF
  aoscx_vni:
    vni_id: 50000
    interface: vxlan1
    vrf: red
    routing: true

- name: Update the VLAN mapped to an existing VNI
  aoscx_vni:
    vni_id: 40000
    interface: vxlan1
    state: update
    vlan: 4001

- name: Delete a VNI
  aoscx_vni:
    vni_id: 40000
    interface: vxlan1
    state: delete
```
