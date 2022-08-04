# OSPF (version 3)

# Synopsis

OSPFv3 (Open Shortest Path First version 3) is a routing protocol which is
described in RFC5340 entitled OSPF for IPv6. It is a Link State-based IGP
(Interior Gateway Protocol) routing protocol. It is widely used with medium to
large-sized enterprise networks.

OSPFv3's characteristics are:

- Provides loop free topology using SPF algorithm
- Allows hierarchical routing using area 0 (backbone area) as the top of the
  hierarchy
- Supports load balancing with equal cost routes for same destination
- Is a classless protocol, and allows for hierarchical design with VLSM
  (Variable Length Subnet Masking) and route summarization
- Scales enterprise-sized network easily with area concept
- Provides fast convergence with triggered, incremental updates via Link State
  Advertisements (LSAs)

## Modules:

- [aoscx_ospfv3_router](#aoscx_ospfv3_router)
- [aoscx_ospfv3_area](#aoscx_ospfv3_area)
- [aoscx_ospfv3_vlink](#aoscx_ospfv3_vlink)

---
## aoscx_ospfv3_router

OSPFv3 Router module for Ansible.

Version added: 4.1.0

This module implements creation, and deletion of OSPF v3 Routers.

An OSPF Rotuer works as a logical entity for an OSPF process in the switch,
there is a maximum of eight OSPF processes allowed per VRF.

- ## Parameters

| Parameter      | Type | [Choices]/Defaults                                        | Required | Comments                                                  |
|:---------------|:-----|:----------------------------------------------------------|:--------:|:----------------------------------------------------------|
| `state`        | str  | [`create`, `delete`, `update`] / `create`                 | [ ]      | The action to be taken with the current Router.           |
| `vrf`          | str  |                                                           | [x]      | Name of the VRF where the router will be in.              |
| `instance_tag` | int  |                                                           | [x]      | OSPFv3 process ID (1-63).                                 |
| `redistribute` | list | [`connected`, `local_loopback`, `static`, `bgp`, `ripng`] | [ ]      | List with route sources to redistribute in this instance. |

---
## aoscx_ospfv3_area

OSPFv3 Area module for Ansible.

Version added: 4.1.0

This module implements creation, and deletion of OPSF Areas.

An OSPF Area is a logical collection of OSPF networks.

- ## Parameters

| Parameter      | Type | [Choices]/Defaults                        | Required | Comments                                                   |
|:---------------|:-----|:------------------------------------------|:--------:|:-----------------------------------------------------------|
| `vrf`          | str  |                                           | [x]      | Name of the VRF where the router wil be in.                |
| `ospf_id`      | int  |                                           | [x]      | OSPFv3 process ID/Instance Tag.                            |
| `area_id`      | str  |                                           | [x]      | OSPF Area Identifier.                                      |
| `state`        | str  | [`create`, `delete`, `update`] / `create` | [ ]      | The action to be taken with the current Router.            |
| `other_config` | dict |                                           | [ ]      | Explained in more detail [here](#other_config-dictionary). |

## `other_config` dictionary

| Parameter           | Type | Choices/Defaults                                                       | Comments                                                  |
|:--------------------|:-----|:-----------------------------------------------------------------------|:----------------------------------------------------------|
| `stub_default`      | int  |                                                                        | Cost for the default summary route sent to the stub area. |
| `stub_metric_type`  | str  | [`metric_standard`, `metric_comparable_cost`, `metric_non_comparable`] |                                                           |

---
# aoscx_ospfv3_vlink

OSPFv3 Virtual Link module for Ansible.

Version added: 4.1.0

This module implements creation, and deletion of OSPF Virtual Links.

An OSPF Virtual Link is a A link between areas that don't have a physical
connection to the backbone area.

- ## Parameters

| Parameter            | Type | [Choices]/Defaults                                                        | Required | Comments                                                                                |
|:---------------------|:-----|:--------------------------------------------------------------------------|:--------:|:----------------------------------------------------------------------------------------|
| `vrf`                | str  |                                                                           | [x]      | Name of the VRF where the router wil be in.                                             |
| `ospf_id`            | Int  |                                                                           | [x]      | OSPFv3 process ID/Instance Tag.                                                         |
| `area_id`            | str  |                                                                           | [x]      | OSPF Area Identifier, in X.X.X.X form.                                                  |
| `peer_router_id`     | str  |                                                                           | [x]      | Vlink's Peer Router Id.                                                                 |
| `state`              | str  | [`create`, `delete`, `update`] / `create`                                 | [ ]      | The action to be taken with the current Vlink.                                          |
| `ipsec_ah`           | dict |                                                                           | [ ]      | IPsec Authentication Header configuration. Preferred over `ipsec_esp` if both are used. |
| `ipsec_esp`          | dict |                                                                           | [ ]      | IPsec Encapsulating Security Payload configuration.                                     |
| `ospf_auth_md5_keys` | list |                                                                           | [ ]      | Authentication keys for OSPF authentication type md5.                                   |
| `ospf_auth_sha_keys` | list |                                                                           | [ ]      | Authentication keys for OSPF authentication type sha.                                   |
| `ospf_auth_text_key` | str  |                                                                           | [ ]      | Authentication keys for OSPF authentication type text.                                  |
| `ospf_auth_keychain` | str  |                                                                           | [ ]      | Authentication keys for OSPF authentication type keychain.                              |
| `ospf_auth_type`     | str  | [`none`, `text`, `md5`, `sha1`, `sha256`, `sha384`, `sha512`, `keychain`] | [ ]      | Authentication type to use.                                                             |
| `other_config`       | dict |                                                                           | [ ]      | Miscellaneous options.                                                                  |

## `ipsec_ah` dictionary

| Parameter   | Type | Choices/Defaults | Comments                                                                            |
|:------------|:-----|:-----------------|:------------------------------------------------------------------------------------|
| `auth_key`  | str  |                  | IPsec AH authentication key.                                                        |
| `auth_type` | str  | [`md5`, `sha1`]  | IPsec AH authentication algorithm.                                                  |
| `spi`       | str  |                  | Security Parameters Index. Must be unique per router, must be in [256, 4294967295]. |

## `ipsec_esp` dictionary

| Parameter         | Type | Choices/Defaults               | Comments                                                                            |
|:------------------|:-----|:-------------------------------|:------------------------------------------------------------------------------------|
| `auth_key`        | str  |                                | IPsec ESP authentication key.                                                       |
| `auth_type`       | str  | [`md5`, `sha1`]                | IPsec ESP authentication algorithm.                                                 |
| `encryption_key`  | str  |                                | IPsec ESP encryption key.                                                           |
| `encryption_type` | str  | [`des`, `3des`, `aes`, `none`] | IPsec ESP authentication algorithm.                                                 |
| `spi`             | str  |                                | Security Parameters Index. Must be unique per router, must be in [256, 4294967295]. |

## `ospf_auth_md5_keys` list's dictionary elements

| Parameter | Type | Choices/Defaults | Required | Comments                                      |
|:----------|:-----|:-----------------|:--------:|:----------------------------------------------|
| `id`      | int  |                  | [x]      | Key ID for security key. Must be in [1, 255]. |
| `key`     | str  |                  | [x]      | md5 Key to use.                               |

## `ospf_auth_sha_keys` list's dictionary elements

| Parameter | Type  | Choices/Defaults | Required | Comments                                      |
|:----------|:------|:-----------------|:--------:|:----------------------------------------------|
| `id`      | int   |                  | [x]      | Key ID for security key. Must be in [1, 255]. |
| `key`     | str   |                  | [x]      | sha Key to use.                               |

## `other_config` dictionary

| Parameter             | Type | Choices/Defaults | Comments                                                                      |
|:----------------------|:-----|:-----------------|:------------------------------------------------------------------------------|
| `dead_interval`       | str  |                  | Seconds to wait for hello packet from neighbor before tearing down adjacency. |
| `transmit_delay`      | str  |                  | Seconds estimated to transmit an LSA to a neighbor.                           |
| `virtual_ifindex`     | str  |                  | Virtual link index assigned to the OSPFv3 virtual interface.                  |
| `retransmit_interval` | str  |                  | Seconds estimated between successive LSAs.                                    |
| `hello_interval`      | str  |                  | Seconds between succesive hello packets.                                      |

---

## Examples

## Create new OSPFv3 Router

```YAML
- name: Create new OSPFv3 Router
  aoscx_ospfv3_router:
    vrf: default
    instance_tag: 1
```

## Create new OSPFv3 Router, with OSPF redistribution methods

```YAML
- name: >
    Create new OSPFv3 Router, with bgp, and static as OSPF
    redistribution methods.
  aoscx_ospfv3_router:
    state: update
    vrf: default
    instance_tag: 1
    redistribute:
      - bgp
      - static
```

## Update OSPFv3 Router

```YAML
- name: >
    Update OSPFv3 Router, add connected to the redistribute methods list.
  aoscx_ospfv3_router:
    state: update
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
```

## Update OSPFv3 Router

```YAML
- name: >
    Update OSPFv3 Router, set redistribute to connected, and static only. This
    deletes bgp from the list.
  aoscx_ospfv3_router:
    state: override
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
      - static
```

## Update OSPFv3 Router

```YAML
- name: >
    Update OSPFv3 Router, set redistribute to connected only. This deletes
    static from the list.
  aoscx_ospfv3_router:
    state: override
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
```

## Delete OSPFv3 Router

```YAML
- name: Delete OSPFv3 Router
  aoscx_ospfv3_router:
    vrf: default
    instance_tag: 1
    state: delete
```

## Create new OSPFv3 Area

```YAML
- name: Create new OSPFv3 Area
  aoscx_ospfv3_area:
    vrf: default
    ospf_id: 1
    area_id: 1
```

## Update OSPF Area's type to nssa

```YAML
- name: Update OSPFv3 Area type to nssa
  aoscx_ospfv3_area:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    area_type: nssa
    state: update
```

## Delete OSPF Area

```YAML
- name: Delete OSPFv3 Area type to nssa
  aoscx_ospfv3_area:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    state: delete
```

## Create new OSPFv3 Vlink

```YAML
- name: Create new OSPFv3 Vlink
  aoscx_ospfv3_vlink:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    peer_router_id: 0.0.0.1
```

## Delete new OSPFv3 Vlink

```YAML
- name: Delete OSPFv3 Interface
  aoscx_ospfv3_vlink:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    peer_router_id: 0.0.0.1
    state: delete
```
