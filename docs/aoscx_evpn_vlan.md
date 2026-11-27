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
  arp_suppression:
    description: >
      ARP suppression for this VLAN (CLI arp-suppression enable|disable in
      the evpn / vlan context). enable and disable override the global
      arp_suppression_enable of aoscx_evpn, global removes the override so
      that the VLAN follows the global setting again. Cannot be enabled
      together with arp_suppression_extended. When omitted it is left
      unchanged. Ignored when state is delete. Requires a pyaoscx version
      providing EvpnVlan.set_suppression().
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  arp_suppression_extended:
    description: >
      ARP suppression extended for this VLAN. Same behavior as
      arp_suppression.
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  nd_suppression:
    description: Neighbor Discovery suppression for this VLAN. Same behavior as arp_suppression.
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  nd_suppression_extended:
    description: Neighbor Discovery suppression extended for this VLAN. Same behavior as arp_suppression.
    required: false
    type: str
    choices:
      - enable
      - disable
      - global
  arp_suppression_exclude:
    description: >
      IPv4 addresses excluded from ARP suppression, whose ARP requests are
      flooded in the fabric (CLI arp-suppression exclude <ip>). The list
      replaces the current one and is compared regardless of order, an empty
      list removes all the exclusions. At most 256 addresses. When omitted it
      is left unchanged. Ignored when state is delete.
    required: false
    type: list
    elements: str
  arp_suppression_extended_exclude:
    description: >
      IPv4 addresses excluded from ARP suppression extended. Same behavior as
      arp_suppression_exclude.
    required: false
    type: list
    elements: str
  nd_suppression_exclude:
    description: >
      IPv6 addresses excluded from ND suppression. Same behavior as
      arp_suppression_exclude.
    required: false
    type: list
    elements: str
  nd_suppression_extended_exclude:
    description: >
      IPv6 addresses excluded from ND suppression extended. Same behavior as
      arp_suppression_exclude.
    required: false
    type: list
    elements: str
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

- name: Enable ARP suppression on VLAN 204 whatever the global setting is
  aoscx_evpn_vlan:
    vlan: 204
    arp_suppression: enable
    arp_suppression_exclude:
      - 10.204.0.1
      - 10.204.0.2

- name: Migrate VLAN 204 to ARP and ND suppression extended
  aoscx_evpn_vlan:
    vlan: 204
    arp_suppression: disable
    arp_suppression_extended: enable
    nd_suppression_extended: enable
    nd_suppression_extended_exclude:
      - "fd00:204::1"

- name: Follow the global ARP suppression again and remove the exclusions
  aoscx_evpn_vlan:
    vlan: 204
    arp_suppression: global
    arp_suppression_exclude: []
```
