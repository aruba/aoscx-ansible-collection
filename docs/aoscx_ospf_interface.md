# module: aoscx_ospf_interface

OSPF Interface module for Ansible.

Version added: 4.1.0

- [Synopsis](#Synopsis)
- [Parameters](#Parameters)
- [Examples](#Examples)

# Synopsis

This modules provides application management of OSPF on Interfaces on AOS-CX
devices.

### NOTE

if IPSec is configured, IPSec parameters must be provided in each playbook,
using the aoscx_ospf_interface module, not doing so results in an error,
unless disabling IPSec for OSPFv3

additionally, if configuring an interface with other modules in this
collection, if the OSPF IPSec is configured in the interface, the idempotency
of the modules is not guaranteed, and aoscx_ospf_interface module must be
used again to set the intended IPSec configuration

# Parameters

| Parameter              | Type | [Choices]/Defaults                                                                                 | Required | Comments                                                                                                                                                           |
|:-----------------------|:-----|:---------------------------------------------------------------------------------------------------|:--------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `state`                | str  | [`create`, `delete`, `update`] / `create`                                                          | [ ]      | The action to be taken with the current OSPF Interface. `delete` will remove all OSPF configuration from the interface.                                            |
| `vrf`                  | str  |                                                                                                    | [x]      | Name of the VRF where the router wil be in.                                                                                                                        |
| `version`              | str  | [`v2`, `v3`]                                                                                       | [x]      | OSPF version. `v2` for OSPFv2, and `v3` for OSPFv3.                                                                                                                |
| `ospf_id`              | int  |                                                                                                    | [x]      | OSPFv3 process ID/Instance Tag.                                                                                                                                    |
| `area_id`              | str  |                                                                                                    | [x]      | OSPF Area Identifier, in X.X.X.X form.                                                                                                                             |
| `interface_name`       | str  |                                                                                                    | [x]      | Name of the Interface in which the OSPF process must be attached.                                                                                                  |
| `cost`                 | int  |                                                                                                    | [ ]      | Output cost configured for the interface.                                                                                                                          |
| `type`                 | str  | [`none`, `broadcast`, `nbma`, `point_to_point`, `point_to_multipoint`, `virtual_link`, `loopback`] | [ ]      | The type of the OSPF network interface.                                                                                                                            |
| `shutdown`             | bool |                                                                                                    | [ ]      | Shutdown OSPF functionalities on this interface.                                                                                                                   |
| `priority`             | int  |                                                                                                    | [ ]      | The router with the highest priority will be more eligible to become the designated router. Setting 0 makes the router ineligible to become the designated router. |
| `bfd`                  | str  |                                                                                                    | [ ]      | Specifies whether the router global Bidirectional Forwarding Detection (BFD) should be overriden for this particular interface.                                    |
| `transmit_delay`       | int  |                                                                                                    | [ ]      | Estimated time in seconds to trasmit an LSA to a neighbor.                                                                                                         |
| `retransmit_interval`  | int  |                                                                                                    | [ ]      | Time in seconds between LSA retransmissions.                                                                                                                       |
| `hello_interval`       | int  |                                                                                                    | [ ]      | The hello packet will be sent every hello_interval seconds.                                                                                                        |
| `dead_interval`        | int  |                                                                                                    | [ ]      | The time, in seconds, that a neighbor should wait for a hello packet before tearing down adjacencies with the local router.                                        |
| `ospfv2_auth_type`     | str  | [`none`, `text`, `md5`, `sha1`, `sha256`, `sha384`, `sha512`, `keychain`]                          | [ ]      | Authentication type to use.                                                                                                                                        |
| `ospfv2_auth_sha_keys` | dict |                                                                                                    | [ ]      | Authentication keys for OSPF authentication type sha.                                                                                                              |
| `ospfv2_auth_md5_keys` | dict |                                                                                                    | [ ]      | Authentication keys for OSPF authentication type md5.                                                                                                              |
| `ospfv2_auth_text_key` | str  |                                                                                                    | [ ]      | Authentication keys for OSPF authentication type text.                                                                                                             |
| `ospfv2_auth_keychain` | str  |                                                                                                    | [ ]      | Authentication keys for OSPF authentication type keychain.                                                                                                         |
| `ospfv3_ipsec_ah`      | dict |                                                                                                    | [ ]      | IPsec Authentication Header configuration. Preferred over `ipsec_esp` if both are used.                                                                            |
| `no_ospfv3_ipsec_ah`   | bool |                                                                                                    | [ ]      | Option to delete ospfv3 IPsec AH configuration. This option is mutually exclusive with the `ospfv3_ipsec_ah` option.                                               |
| `ospfv3_ipsec_esp`     | dict |                                                                                                    | [ ]      | IPsec Encapsulating Security Payload configuration.                                                                                                                |

## `ospf_auth_sha_keys` list's dictionary elements

| Parameter | Type | [Choices]/Defaults | Required | Comments                                      |
|:----------|:-----|:-------------------|:--------:|:----------------------------------------------|
| `id`      | int  |                    | [x]      | Key ID for security key. Must be in [1, 255]. |
| `key`     | str  |                    | [x]      | sha Key to use.                               |

## `ospf_auth_md5_keys` list's dictionary elements

| Parameter | Type | [Choices]/Defaults | Required | Comments                                      |
|:----------|:-----|:-------------------|:--------:|:----------------------------------------------|
| `id`      | int  |                    | [x]      | Key ID for security key. Must be in [1, 255]. |
| `key`     | str  |                    | [x]      | md5 Key to use.                               |

## `ospfv3_ipsec_ah` dictionary

| Parameter   | Type | [Choices]/Defaults | Required | Comments                                                                                                                           |
|:------------|:-----|:-------------------|:--------:|:-----------------------------------------------------------------------------------------------------------------------------------|
| `auth_key`  | str  |                    | [ ]      | IPsec AH authentication key.  This parameter is required if auth_type and spi are set.                                             |
| `auth_type` | str  | [`md5`, `sha1`]    | [ ]      | IPsec AH authentication algorithm. This parameter is required if auth_key is set.                                                  |
| `spi`       | str  |                    | [ ]      | Security Parameters Index. Must be unique per router, must be in [256, 4294967295]. This parameter is required if auth_key is set. |
| `ah_null`   | bool |                    | [ ]      | Disable OSPF IPsec AH authentication on this interface.                                                                            |

## `ospfv3_ipsec_esp` dictionary

| Parameter         | Type | [Choices]/Defaults             | Required | Comments                                                                            |
|:------------------|:-----|:-------------------------------|:--------:|:------------------------------------------------------------------------------------|
| `auth_key`        | str  |                                | [x]      | IPsec ESP authentication key.                                                       |
| `auth_type`       | str  | [`md5`, `sha1`]                | [x]      | IPsec ESP authentication algorithm.                                                 |
| `encryption_key`  | str  |                                | [x]      | IPsec ESP encryption key.                                                           |
| `encryption_type` | str  | [`des`, `3des`, `aes`, `none`] | [x]      | IPsec ESP authentication algorithm.                                                 |
| `spi`             | str  |                                | [x]      | Security Parameters Index. Must be unique per router, must be in [256, 4294967295]. |
| `esp_null`        | str  |                                | [x]      | Disable OSPF IPsec ESP encryption and authentication on this interface.             |

---

## Examples

```YAML
- name: Attach an OSPF router and area to interface 1/1/1
  aoscx_ospf_interface:
    vrf: RED
    version: v3
    ospf_id: 5
    area_id: 1.1.1.1
    interface_name: 1/1/1
    state: create
```

```YAML
- name: Remove interface 1/1/3 from OSPFv3 Area 1.1.1.1
  aoscx_ospf_interface:
    vrf: RED
    version: v3
    ospf_id: 5
    area_id: 1.1.1.1
    interface_name: 1/1/3
    state: delete
```

```YAML
- name: Set the OSPFv3 transmit delay in interface 1/1/13
  aoscx_ospf_interface:
    vrf: default
    version: v3
    ospf_id: 4
    area_id: 1.1.1.2
    interface_name: 1/1/13
    transmit_delay: 20
```

```YAML
- name: Enable OSPF authentication
  aoscx_ospf_interface:
    vrf: default
    version: v2
    ospf_id: 5
    area_id: 1.1.1.1
    interface_name: 1/1/4
    ospfv2_auth_type: sha1
    ospfv2_auth_sha_keys:
      - id: 1
        key: sha_key_1
      - id: 2
        key: sha_key_2
```

```YAML
- name: Configure OSPFv3 IPSec authentication header
  aoscx_ospf_interface:
    vrf: default
    version: v3
    ospf_id: 5
    area_id: 0.0.0.1
    interface_name: 1/1/3
    ospfv3_ipsec_ah:
      auth_key: 12345678
      auth_type: sha1
      spi: 257
```

```YAML
- name: Disable OSPFv3 IPSec authentication header
  aoscx_ospf_interface:
    vrf: default
    version: v3
    ospf_id: 5
    area_id: 0.0.0.1
    interface_name: 1/1/3
    ospfv3_ipsec_ah:
      ah_null: true
```

```YAML
- name: Disable OSPFv3 IPSec authentication header
  aoscx_ospf_interface:
    vrf: default
    version: v3
    ospf_id: 5
    area_id: 0.0.0.1
    interface_name: 1/1/3
    no_ospfv3_ipsec_ah: true
```
