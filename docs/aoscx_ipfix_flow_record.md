# module: aoscx_ipfix_flow_record

description: This module provides configuration management of IPFIX flow
records on AOS-CX devices. A flow record defines the key fields (match) and
non-key fields (collect) included in exported IPFIX flows. IPFIX requires REST
API version 10.13 or later (set ansible_aoscx_rest_version to 10.13).

##### ARGUMENTS

```YAML
  name:
    description: >
      Name of the flow record. This is the index of the resource under
      system/ipfix_flow_records.
    required: true
    type: str
  description:
    description: Free form description of the flow record.
    required: false
    type: str
  match:
    description: >
      Key fields for the flow record, as a dictionary mapping a field name to
      a boolean. Valid keys are ipv4_source_address, ipv4_destination_address,
      ipv4_protocol, ipv4_version, ipv6_source_address,
      ipv6_destination_address, ipv6_protocol, ipv6_version,
      transport_source_port and transport_destination_port. The supplied
      dictionary fully replaces the current key fields.
    required: false
    type: dict
  collect:
    description: >
      Non-key fields for the flow record, as a dictionary mapping a field name
      to a boolean (for example counter_bytes, counter_packets,
      application_name, egress_interface). The supplied dictionary fully
      replaces the current non-key fields.
    required: false
    type: dict
  state:
    description: Create, update or delete the flow record.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
```

##### EXAMPLES

```YAML
- name: Create an IPFIX flow record for IPv4 flows
  aoscx_ipfix_flow_record:
    name: ipv4-record
    description: Record ipv4 flows
    match:
      ipv4_source_address: true
      ipv4_destination_address: true
      ipv4_protocol: true
    collect:
      counter_bytes: true
      counter_packets: true

- name: Update the collected fields of a flow record
  aoscx_ipfix_flow_record:
    name: ipv4-record
    state: update
    collect:
      counter_bytes: true
      counter_packets: true
      application_name: true

- name: Delete a flow record
  aoscx_ipfix_flow_record:
    name: ipv4-record
    state: delete
```
