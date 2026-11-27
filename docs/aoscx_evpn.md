# module: aoscx_evpn

description: This module provides configuration management of the global EVPN
(Ethernet VPN) settings on AOS-CX devices. EVPN is a singleton resource, so
this module only updates the existing configuration; it never creates or
deletes the resource. Only the parameters you supply are reconciled; any
parameter left unset is preserved.

##### ARGUMENTS

```YAML
  arp_suppression_enable:
    description: >
      Whether ARP suppression is globally enabled. When omitted it is left
      unchanged.
    required: false
    type: bool
  nd_suppression_enable:
    description: >
      Whether Neighbor Discovery (ND) suppression is globally enabled. When
      omitted it is left unchanged.
    required: false
    type: bool
  arp_suppression_extended_enable:
    description: >
      Whether ARP suppression extended is globally enabled (CLI
      arp-suppression-extended). It cannot be enabled together with
      arp_suppression_enable: to migrate, disable the latter in the same
      task. When omitted it is left unchanged. Requires a pyaoscx version
      providing Evpn.check_suppression().
    required: false
    type: bool
  nd_suppression_extended_enable:
    description: >
      Whether ND suppression extended is globally enabled (CLI
      nd-suppression-extended). Same behavior as
      arp_suppression_extended_enable, and cannot be enabled together with
      nd_suppression_enable. When omitted it is left unchanged.
    required: false
    type: bool
  mac_move_count:
    description: >
      Maximum number of MAC moves allowed within the MAC move interval before
      the MAC address is frozen. When omitted it is left unchanged.
    required: false
    type: int
  mac_move_timer:
    description: >
      Length of the MAC move detection interval, in seconds. When omitted it
      is left unchanged.
    required: false
    type: int
  redistribute:
    description: >
      Dictionary controlling which local address types are redistributed into
      EVPN, for example {"local-mac": true, "local-svi": false}. Only the keys
      you provide are reconciled; other keys are preserved. When omitted it is
      left unchanged.
    required: false
    type: dict
  dyn_vxlan_tunnel_bridging_mode:
    description: >
      Bridging mode between dynamic (EVPN) VXLAN tunnels. ibgp-ebgp (CLI
      dyn-vxlan-tunnel-bridging-mode ibgp-ebgp) puts the iBGP and eBGP tunnels
      in different broadcast groups and permits bridging between them, for
      example between two fabrics interconnected by border leaves.
      no-bridging (default of the switch, CLI no dyn-vxlan-tunnel-bridging-mode
      ibgp-ebgp) puts all EVPN tunnels in the same broadcast group. The module
      fails if the switch platform or firmware does not support it. When
      omitted it is left unchanged.
    required: false
    type: str
    choices:
      - no-bridging
      - ibgp-ebgp
  state:
    description: >
      Use create or update to apply the configuration. Both behave the same
      because EVPN is a singleton that always exists.
    required: false
    default: update
    choices:
      - create
      - update
    type: str
```

##### EXAMPLES

```YAML
- name: Enable ARP and ND suppression globally
  aoscx_evpn:
    arp_suppression_enable: true
    nd_suppression_enable: true

- name: Tune the MAC move detection
  aoscx_evpn:
    mac_move_count: 5
    mac_move_timer: 180

- name: Configure EVPN redistribution
  aoscx_evpn:
    redistribute:
      local-mac: true
      local-svi: true

- name: Permit bridging between iBGP and eBGP EVPN tunnels on a border leaf
  aoscx_evpn:
    dyn_vxlan_tunnel_bridging_mode: ibgp-ebgp

- name: Put back all EVPN tunnels in the same broadcast group (default)
  aoscx_evpn:
    dyn_vxlan_tunnel_bridging_mode: no-bridging

- name: Migrate the global ARP and ND suppression to the extended versions
  aoscx_evpn:
    arp_suppression_enable: false
    arp_suppression_extended_enable: true
```
