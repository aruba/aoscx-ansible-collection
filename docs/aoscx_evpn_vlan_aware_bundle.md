# module: aoscx_evpn_vlan_aware_bundle

description: This module provides configuration management of EVPN VLAN-aware
bundles on AOS-CX devices. A bundle groups several VLANs under a single EVPN
instance that shares the same route distinguisher and route targets. The
member VLANs are mapped through their Ethernet tags. The bundle lives under
system/evpn/evpn_vlan_aware_bundles and is indexed by its name.

##### ARGUMENTS

```YAML
  bundle_name:
    description: Name of the EVPN VLAN-aware bundle.
    required: true
    type: str
  rd:
    description: >
      Route distinguisher of the bundle, for example 65000:1 or 1.1.1.1:1.
      When omitted it is left unchanged.
    required: false
    type: str
  import_route_targets:
    description: >
      List of import route targets for the bundle. The supplied list fully
      replaces the existing import route targets. When omitted they are left
      unchanged.
    required: false
    type: list
    elements: str
  export_route_targets:
    description: >
      List of export route targets for the bundle. The supplied list fully
      replaces the existing export route targets. When omitted they are left
      unchanged.
    required: false
    type: list
    elements: str
  redistribute:
    description: >
      Redistribution settings of the bundle, for example {host-route: true}.
      Only the supplied keys are reconciled; existing keys that are not
      mentioned are preserved. When omitted it is left unchanged.
    required: false
    type: dict
  disable:
    description: >
      Whether the bundle is administratively disabled. When omitted it is left
      unchanged.
    required: false
    type: bool
  vlans:
    description: >
      Member VLANs of the bundle with their Ethernet tags. The supplied list
      fully replaces the set of member VLANs. When omitted the VLANs are left
      unchanged; an empty list removes all member VLANs. The VLANs must already
      exist on the device. Ignored when state is delete.
    required: false
    type: list
    elements: dict
    suboptions:
      id:
        description: VLAN ID of the member VLAN.
        required: true
        type: int
      ethernet_tag:
        description: >
          Ethernet tag mapped to the VLAN. When omitted it defaults to the
          VLAN ID.
        required: false
        type: int
  state:
    description: Create, update or delete the EVPN VLAN-aware bundle.
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
- name: Create an EVPN VLAN-aware bundle with two member VLANs
  aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    rd: "65000:1"
    import_route_targets:
      - "65000:1"
    export_route_targets:
      - "65000:1"
    vlans:
      - id: 206
      - id: 207
        ethernet_tag: 100

- name: Replace the member VLANs of a bundle
  aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    state: update
    vlans:
      - id: 206

- name: Remove all member VLANs from a bundle
  aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    state: update
    vlans: []

- name: Delete an EVPN VLAN-aware bundle
  aoscx_evpn_vlan_aware_bundle:
    bundle_name: tenant-blue
    state: delete
```
