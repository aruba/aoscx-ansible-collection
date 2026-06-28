# module: aoscx_evpn_vlan

description: This module provides configuration management of per-VLAN EVPN
(Ethernet VPN) settings on AOS-CX devices. Each entry binds a VLAN to its
EVPN instance and configures its route distinguisher, import and export route
targets, and redistribution. The VLAN must already exist on the device.

##### ARGUMENTS

```YAML
  vlan:
    description: >
      ID of the VLAN the EVPN instance is bound to. The VLAN must already
      exist on the device.
    required: true
    type: int
  rd:
    description: >
      Route distinguisher for the VLAN's EVPN instance, for example 65000:204
      or auto. When omitted it is left unchanged. Ignored when state is
      delete.
    required: false
    type: str
  import_route_targets:
    description: >
      List of import route targets for the VLAN's EVPN instance. The list is
      compared regardless of order. When omitted it is left unchanged. Ignored
      when state is delete.
    required: false
    type: list
    elements: str
  export_route_targets:
    description: >
      List of export route targets for the VLAN's EVPN instance. The list is
      compared regardless of order. When omitted it is left unchanged. Ignored
      when state is delete.
    required: false
    type: list
    elements: str
  redistribute:
    description: >
      Dictionary controlling redistribution for the VLAN's EVPN instance, for
      example {"host-route": true}. Only the keys you provide are reconciled;
      other keys are preserved. When omitted it is left unchanged. Ignored
      when state is delete.
    required: false
    type: dict
  state:
    description: Create, update or delete the per-VLAN EVPN entry.
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
- name: Create an EVPN instance for VLAN 204
  aoscx_evpn_vlan:
    vlan: 204
    rd: "65000:204"
    import_route_targets:
      - "65000:204"
    export_route_targets:
      - "65000:204"

- name: Update the route distinguisher of an EVPN VLAN
  aoscx_evpn_vlan:
    vlan: 204
    state: update
    rd: "65001:204"

- name: Configure redistribution for an EVPN VLAN
  aoscx_evpn_vlan:
    vlan: 204
    redistribute:
      host-route: true

- name: Delete an EVPN VLAN entry
  aoscx_evpn_vlan:
    vlan: 204
    state: delete
```
