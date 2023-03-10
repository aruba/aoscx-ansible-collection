# MAC

MAC module for Ansible.

Version added: 4.1.0

 - [Synopsis](#Synopsis)
 - [Parameters](#Parameters)
 - [Examples](#Examples)

## Synopsis

The MAC module allows a user to fetch and print the MAC addresses of an AOSCX device. The output is concatenated to the Ansible's playbook output. You can find additional information online about how MAC is structured at the [Aruba Portal](https://developer.arubanetworks.com/aruba-aoscx/reference/mac)

## Parameters

| Parameter  | Type | Choices/Defaults                                                                                                                                        | Required | Comments                                                                                                                       |
|:-----------|:----:|:--------------------------------------------------------------------------------------------------------------------------------------------------------|:--------:|:-------------------------------------------------------------------------------------------------------------------------------|
| all        | bool | [`true`, `false`]/`false`                                                                                                                               | [ ]      | Boolean to specify if the module will fetch all the VLANs in a device. This option is mutually exclusive with the vlan option. |
| vlan       | int  |                                                                                                                                                         | [ ]      | VLAN ID the MAC addresses are attached to. This option is mutually exclusive with the `all_vlans` option.                      |
| sources    | list | [`dynamic`, `evpn`, `hsc`, `static`, `port-access-security`, `vrrp`, `vsx`]/[`dynamic`, `evpn`, `hsc`, `static`, `port-access-security`, `vrrp`, `vsx`] | [ ]      | List of sources of the MAC addresses which acts as a filter on which MAC addresses will be included in the output.             |

## Examples

### Retrieve MAC addresses using the sources filter

```YAML
- name: Fetch MAC addresses from VLAN 3 from 'static' source
  aoscx_mac:
    vlan: 3
    sources:
      - static

- name: Fetch MAC addresses from VLAN 12 from 'static' and 'dynamic' sources
  aoscx_mac:
    vlan: 12
    sources:
      - static
      - dynamic
```

### Retrieve all MAC addresses from the device.

```YAML
- name: Fetch all MAC addresses from all VLANs
  aoscx_mac:
    all_vlans: true
```

### Retrieve all MAC addresses from one vlan

```YAML
- name: Fetch all MAC addresses from VLAN 4
  aoscx_mac:
    vlan: 4

- name: Fetch all MAC addresses from VLAN 10
  aoscx_mac:
    vlan: 10
```