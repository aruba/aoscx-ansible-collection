# module: aoscx_mka_policy

description: This module provides configuration management of MKA (MACsec Key
Agreement) policies on AOS-CX devices (system/mka_policies). An MKA policy
references a keychain and defines the pre-shared CAK/CKN and EAPOL parameters
used to establish MACsec sessions. This module requires REST API version 10.16
(set ansible_aoscx_rest_version to 10.16). The cak and ckn values are write-only
on the switch and cannot be read back, so a change to cak or ckn alone (without
any other field change) is not detected.

##### ARGUMENTS

```YAML
  name:
    description: Name of the MKA policy (index under system/mka_policies).
    required: true
    type: str
  mode:
    description: Key agreement mode of the policy.
    required: false
    type: str
    choices:
      - psk
      - eap-tls
  keychain:
    description: >
      Name of the keychain referenced by the policy. The keychain must already
      exist on the device.
    required: false
    type: str
  cak:
    description: >
      Connectivity Association Key. This value is write-only on the switch and
      cannot be read back; a change to cak alone is not detected.
    required: false
    type: str
  ckn:
    description: >
      Connectivity Association Key Name. This value is write-only on the switch
      and cannot be read back; a change to ckn alone is not detected.
    required: false
    type: str
  key_server_priority:
    description: Priority of the key server.
    required: false
    type: int
  transmit_interval:
    description: MKA hello transmit interval in seconds.
    required: false
    type: int
  eapol_destination_mac:
    description: Destination MAC address used for EAPOL frames.
    required: false
    type: str
  eapol_dot1q_tagged:
    description: Whether EAPOL frames are 802.1Q tagged.
    required: false
    type: bool
  eapol_eth_type:
    description: Ethertype used for EAPOL frames.
    required: false
    type: str
  state:
    description: Create, update or delete the MKA policy.
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
- name: Create an MKA policy referencing a keychain
  aoscx_mka_policy:
    name: mka1
    mode: psk
    keychain: mka_keys
    cak: "00112233445566778899aabbccddeeff"
    ckn: "11"
    key_server_priority: 5
    transmit_interval: 2

- name: Update the transmit interval of an MKA policy
  aoscx_mka_policy:
    name: mka1
    transmit_interval: 6

- name: Delete an MKA policy
  aoscx_mka_policy:
    name: mka1
    state: delete
```
