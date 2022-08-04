# OSPF (version 2)

## Synopsis

OSPF (Open Shortest Path First version 2) is a routing protocol which is
described in RFC2328 entitled OSPF version 2. It is a Link State-based IGP
(Interior Gateway Protocol) routing protocol. It is widely used with medium to
large-sized enterprise networks.

OSPF's characteristics are:

- Provides loop free topology using SPF algorithm
- Allows hierarchical routing using area 0 (backbone area) as the top of the
  hierarchy
- Supports load balancing with equal cost routes for same destination
- Is a classless protocol, and allows for hierarchical design with VLSM
  (Variable Length Subnet Masking) and route summarization
- Provides authentication of routing messages.
- Scales enterprise-sized network easily with area concept
- Provides fast convergence with triggered, incremental updates via Link State
  Advertisements (LSAs)

## Modules:

- [aoscx_ospf_router](#aoscx_ospf_router)
- [aoscx_ospf_area](#aoscx_ospf_area)
- [aoscx_ospf_vlink](#aoscx_ospf_vlink)

---
## aoscx_ospf_router

OSPF Router module for Ansible.

Version added: 4.1.0

This module implements creation, and deletion of OSPF Routers.

An OSPF Rotuer works as a logical entity for an OSPF process in the switch,
there is a maximum of eight OSPF processes allowed per VRF.

- ## Parameters

| Parameter      | Type | [Choices]/Defaults                                        | Required | Comments                                                  |
|:---------------|:-----|:----------------------------------------------------------|:--------:|:----------------------------------------------------------|
| `state`        | str  | [`create`, `delete`, `update`] / `create`                 | [ ]      | The action to be taken with the current Router.           |
| `vrf`          | str  |                                                           | [x]      | Name of the VRF where the router will be in.              |
| `instance_tag` | int  |                                                           | [x]      | OSPF process ID (1-63).                                   |
| `redistribute` | list | [`connected`, `local_loopback`, `static`, `bgp`, `ripng`] | [ ]      | List with route sources to redistribute in this instance. |

---
## aoscx_ospf_area

OSPF Area module for Ansible.

Version added: 4.1.0

This module implements creation, and deletion of OPSF Areas.

An OSPF Area is a logical collection of OSPF networks.

- ## Parameters

| Parameter      | Type | [Choices]/Defaults                        | Required | Comments                                                   |
|:---------------|:-----|:------------------------------------------|:--------:|:-----------------------------------------------------------|
| `vrf`          | str  |                                           | [x]      | Name of the VRF where the router will be in.               |
| `ospf_id`      | int  |                                           | [x]      | OSPF process ID/Instance Tag.                              |
| `area_id`      | str  |                                           | [x]      | OSPF Area Identifier.                                      |
| `state`        | str  | [`create`, `delete`, `update`] / `create` | [ ]      | The action to be taken with the current Router.            |
| `other_config` | dict |                                           | [ ]      | Explained in more detail [here](#other_config-dictionary). |

## `other_config` dictionary

| Parameter           | Type | Choices/Defaults                                                       | Comments                                                  |
|:--------------------|:-----|:-----------------------------------------------------------------------|:----------------------------------------------------------|
| `stub_default`      | int  |                                                                        | Cost for the default summary route sent to the stub area. |
| `stub_metric_type`  | str  | [`metric_standard`, `metric_comparable_cost`, `metric_non_comparable`] |                                                           |

---
# aoscx_ospf_vlink

OSPF Virtual Link module for Ansible.

Version added: 4.1.0

This module implements creation, and deletion of OSPF Virtual Links.

An OSPF Virtual Link is a A link between areas that don't have a physical
connection to the backbone area.

- ## Parameters

| Parameter            | Type | [Choices]/Defaults                                                        | Required | Comments                                                                                |
|:---------------------|:-----|:--------------------------------------------------------------------------|:--------:|:----------------------------------------------------------------------------------------|
| `vrf`                | str  |                                                                           | [x]      | Name of the VRF where the router will be in.                                            |
| `ospf_id`            | Int  |                                                                           | [x]      | OSPF process ID/Instance Tag.                                                           |
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

| Parameter | Type | Choices/Defaults | Required | Comments                                      |
|:----------|:-----|:-----------------|:--------:|:----------------------------------------------|
| `id`      | int  |                  | [x]      | Key ID for security key. Must be in [1, 255]. |
| `key`     | str  |                  | [x]      | sha Key to use.                               |

## `other_config` dictionary

| Parameter             | Type | Choices/Defaults | Comments                                                                      |
|:----------------------|:-----|:-----------------|:------------------------------------------------------------------------------|
| `dead_interval`       | int  |                  | Seconds to wait for hello packet from neighbor before tearing down adjacency. |
| `transmit_delay`      | int  |                  | Seconds estimated to transmit an LSA to a neighbor.                           |
| `virtual_ifindex`     | int  |                  | Virtual link index assigned to the OSPF virtual interface.                    |
| `retransmit_interval` | int  |                  | Seconds estimated between successive LSAs.                                    |
| `hello_interval`      | int  |                  | Seconds between succesive hello packets.                                      |

---

## Examples

## Create new OSPF Router

```YAML
- name: Create new OSPF Router
  aoscx_ospf_router:
    vrf: default
    instance_tag: 1
```

## Create new OSPF Router, with OSPF redistribution methods

```YAML
- name: >
    Create new OSPF Router, with bgp, and static as OSPF redistribution methods
  aoscx_ospf_router:
    state: update
    vrf: default
    instance_tag: 1
    redistribute:
      - bgp
      - static
```

## Update OSPF Router

```YAML
- name: >
    Update OSPF Router, add connected to the redistribute methods list.
  aoscx_ospf_router:
    state: update
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
```

## Update OSPF Router

```YAML
- name: >
    Update OSPF Router, set redistribute to connected, and static only. This
    deletes bgp from the list.
  aoscx_ospf_router:
    state: override
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
      - static
```

## Update OSPF Router

```YAML
- name: >
    Update OSPF Router, set redistribute to connected only. This deletes static
    from the list.
  aoscx_ospf_router:
    state: override
    vrf: default
    instance_tag: 1
    redistribute:
      - connected
```

## Delete OSPF Router

```YAML
- name: Delete OSPF Router
  aoscx_ospf_router:
    state: delete
    vrf: default
    instance_tag: 1
```

## Create new OSPF Area

```YAML
- name: Create new OSPF Area
  aoscx_ospf_area:
    vrf: default
    ospf_id: 1
    area_id: 1
```

## Update OSPF Area's type to nssa

```YAML
- name: Update OSPF Area type to nssa
  aoscx_ospf_area:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    area_type: nssa
    state: update
```

## Delete OSPF Area

```YAML
- name: Delete OSPF Area type to nssa
  aoscx_ospf_area:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    state: delete
```

## Create new OSPF Vlink

```YAML
- name: Create new OSPF Vlink
  aoscx_ospf_vlink:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    peer_router_id: 0.0.0.1
```

## Delete new OSPF Vlink

```YAML
- name: Delete OSPF Interface
  aoscx_ospf_vlink:
    vrf: default
    ospf_id: 1
    area_id: 1.1.1.1
    peer_router_id: 0.0.0.1
    state: delete
```
