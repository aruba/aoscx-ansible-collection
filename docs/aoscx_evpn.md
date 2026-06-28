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
```
