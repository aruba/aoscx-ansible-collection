# module: aoscx_vrf

description: This module provides configuration management of VRFs on AOS-CX
devices. It can also manage the VRF route distinguisher (RD) and the
import/export route targets (RT) per address family (EVPN, IPv4 unicast and
IPv6 unicast).

##### ARGUMENTS

```YAML
  name:
    description: The name of the VRF
    required: true
    type: str
  state:
    description: Create or update the VRF, or delete it.
    required: false
    choices:
      - create
      - delete
    default: create
    type: str
  rd:
    description:
      - Route distinguisher in ASN:nn or IPv4:nn format.
      - Applies to the entire VRF and is left unchanged when omitted.
      - Used only with O(state=create).
    type: str
  address_families:
    description:
      - Route targets to manage by address family. Omitted families are left unchanged.
      - Use ASN:nn for route targets. EVPN also accepts IPv4:nn and V(auto).
      - Used only with O(state=create).
    type: list
    elements: dict
    suboptions:
      address_family:
        description: Address family to configure. Specify each family at most once.
        required: true
        type: str
        choices: [evpn, ipv4_unicast, ipv6_unicast]
      import_route_targets:
        description:
          - Route targets to import. At least one of the import or export lists is required per family.
          - Replaces the import list for this family. Use an empty list to clear it or omit it to preserve it.
        type: list
        elements: str
      export_route_targets:
        description:
          - Route targets to export.
          - Replaces the export list for this family. Use an empty list to clear it or omit it to preserve it.
        type: list
        elements: str
```

##### NOTES

- `rd` and `address_families` are used with `state: create` (create or update).
- Each supplied route target list replaces the corresponding list on the
  switch; use `[]` to clear it. An omitted RD, address family or route target
  list is left unchanged.
- At least one of `import_route_targets` / `export_route_targets` is required
  per address family, and each family can be listed only once.
- Route targets use `ASN:nn`; EVPN also accepts `IPv4:nn` and `auto`.
- Route target order and duplicates are ignored when checking idempotency.
- EVPN route targets are stored on the VRF itself (`evpn_import_route_targets`
  / `evpn_export_route_targets`), IPv4/IPv6 unicast route targets on the
  `vrf_address_families` sub-resource. The module hides this difference.
- Updating IPv4/IPv6 unicast route targets on an existing address family
  requires a pyaoscx release that includes the `VrfAddressFamily` PUT fix.
- Check mode is supported.

##### EXAMPLES

```YAML
- name: Create a VRF
  aoscx_vrf:
    name: red
    state: create

# Equivalent CLI:
#   vrf CAMPUS
#       rd 10.140.253.13:20000
#       route-target export 1:1 evpn
#       route-target export 65001:20000 evpn
#       route-target import 1:1 evpn
#       route-target import 65001:20000 evpn
- name: Configure a VRF with an RD and EVPN route targets
  arubanetworks.aoscx.aoscx_vrf:
    name: CAMPUS
    rd: "10.140.253.13:20000"
    address_families:
      - address_family: evpn
        export_route_targets: ["1:1", "65001:20000"]
        import_route_targets: ["1:1", "65001:20000"]

- name: Use auto-generated EVPN route targets
  arubanetworks.aoscx.aoscx_vrf:
    name: CAMPUS
    address_families:
      - address_family: evpn
        import_route_targets: [auto]
        export_route_targets: [auto]

# Equivalent CLI:
#   vrf BLUE
#       rd 65001:100
#       address-family ipv4 unicast
#           route-target import 65001:100
#           route-target export 65001:100
#       address-family ipv6 unicast
#           route-target import 65001:100
- name: Configure IPv4 and IPv6 unicast route targets
  arubanetworks.aoscx.aoscx_vrf:
    name: BLUE
    rd: "65001:100"
    address_families:
      - address_family: ipv4_unicast
        import_route_targets: ["65001:100"]
        export_route_targets: ["65001:100"]
      - address_family: ipv6_unicast
        import_route_targets: ["65001:100"]

- name: Remove the EVPN export route targets, keep the import ones
  arubanetworks.aoscx.aoscx_vrf:
    name: CAMPUS
    address_families:
      - address_family: evpn
        export_route_targets: []

- name: Delete a VRF
  aoscx_vrf:
    name: red
    state: delete
```
