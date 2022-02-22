# module: aoscx_dns

description: This modules provides configuration management of DNS on AOS-CX
devices.

##### ARGUMENTS

```YAML
  mgmt_nameservers:
    description: >
      Primary and secondary nameservers on mgmt interface. The key of the
      dictionary is primary or secondary and value is the respective IP
      address.
    type: dict
  dns_domain_name:
    description: >
      Domain name used for name resolution by the DNS client, if
      'dns_domain_list' is not configured.
    type: str
  dns_domain_list:
    description: >
      Domain list names to be used for address resolution, keyed by the
      resolution priority order.
    type: dict
  dns_name_servers:
    description: >
      Name servers to be used for address resolution, keyed by the resolution
      priority order.
    type: dict
  vrf:
    description: VRF name where DNS configuration is added.
    type: str
    required: false
  dns_host_v4_address_mapping:
    description: >
      List of static host address configurations and the IPv4 address
      associated with them.
    type: dict
  state:
    description: Create or Update or Delete DNS configuration on the switch.
    default: create
    choices:
      - create
      - update
      - delete
    required: false
    type: str
```

##### EXAMPLES

```YAML
- name: DNS configuration creation
  aoscx_dns:
    mgmt_nameservers:
     "Primary": "10.10.2.10"
     "Secondary": "10.10.2.10"
    dns_domain_name: "hpe.com"
    dns_domain_list:
      0: "hp.com"
      1: "aru.com"
      2: "sea.com"
    dns_name_servers:
      0: "4.4.4.8"
      1: "4.4.4.10"
    dns_host_v4_address_mapping:
      "host1": "5.5.44.5"
      "host2": "2.2.44.2"
    vrf: "green"

- name: DNS configuration update
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    dns_domain_name: "hpe.com"
    dns_domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    dns_name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    dns_host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: update

- name: DNS configuration deletion
  aoscx_dns:
    mgmt_nameservers:
      "Primary": "10.10.2.15"
      "Secondary": "10.10.2.25"
    dns_domain_name: "hp.com"
    dns_domain_list:
      0: "hpe.com"
      1: "aruba.com"
      2: "seach.com"
    dns_name_servers:
      0: "4.4.4.10"
      1: "4.4.4.12"
    dns_host_v4_address_mapping:
      "host1": "5.5.5.5"
      "host2": "2.2.45.2"
    vrf: "green"
    state: delete
```
