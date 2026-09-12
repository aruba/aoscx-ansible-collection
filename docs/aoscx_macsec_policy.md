# module: aoscx_macsec_policy

description: This module provides configuration management of MACsec policies on
AOS-CX devices (system/macsec_policies). A MACsec policy defines the
confidentiality, replay protection and cipher suite behaviour applied to a
MACsec protected channel; it is referenced by MKA policies and port access
roles. This module requires REST API version 10.16 (set
ansible_aoscx_rest_version to 10.16).

##### ARGUMENTS

```YAML
  name:
    description: Name of the MACsec policy, index under system/macsec_policies.
    required: true
    type: str
  clear_tag_mode:
    description: >
      Ethernet data that must precede the MACsec SecTAG in clear text. With
      dot1q the 802.1q tag is sent in clear and untagged traffic is not allowed
      on the MACsec channel.
    required: false
    type: str
    choices:
      - none
      - dot1q
  confidentiality_disable:
    description: Disable encryption on the MACsec interface.
    required: false
    type: bool
  confidentiality_offset:
    description: >
      Number of leading octets of an Ethernet frame that are left unencrypted.
      Only applicable when confidentiality is enabled.
    required: false
    type: str
    choices:
      - byte_0
      - byte_30
      - byte_50
  data_delay_protection_enable:
    description: >
      Enable data delay protection so that MACsec frames delayed by more than
      two seconds are dropped.
    required: false
    type: bool
  include_sci_disable:
    description: >
      Disable inclusion of the Secure Channel Identifier (SCI) in MACsec
      frames.
    required: false
    type: bool
  replay_protect_disable:
    description: Disable replay protection on the MACsec interface.
    required: false
    type: bool
  replay_window:
    description: >
      Replay protection window. A received packet is processed only if its
      packet number is within this window. Only applicable when replay
      protection is enabled.
    required: false
    type: int
  secure_mode:
    description: >
      Forwarding behaviour of the interface when the MKA session is not
      established. should-secure opens the data plane without MACsec
      protection; must-secure blocks the interface.
    required: false
    type: str
    choices:
      - should-secure
      - must-secure
  bypass:
    description: Features that bypass MACsec processing on the channel.
    required: false
    type: dict
    suboptions:
      ieee_bpdu_enabled:
        description: >
          Bypass MACsec protection for IEEE BPDU frames (destination MAC in
          01:80:c2:00:00:0*) in both directions.
        required: false
        type: bool
  cipher_suites:
    description: >
      MACsec cipher suites used to protect the frames. When more than one is
      enabled the most secure one is used to generate the SAK when the switch
      is the key server.
    required: false
    type: dict
    suboptions:
      gcm_aes_128_enabled:
        description: Enable GCM with the AES-128 cipher.
        required: false
        type: bool
      gcm_aes_256_enabled:
        description: Enable GCM with the AES-256 cipher.
        required: false
        type: bool
      gcm_aes_xpn_128_enabled:
        description: >
          Enable GCM with the AES-128 cipher and extended packet numbering.
        required: false
        type: bool
      gcm_aes_xpn_256_enabled:
        description: >
          Enable GCM with the AES-256 cipher and extended packet numbering.
        required: false
        type: bool
  state:
    description: Create, update or delete the MACsec policy.
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
- name: Create a MACsec policy that must secure with AES-256
  aoscx_macsec_policy:
    name: secure_uplinks
    secure_mode: must-secure
    confidentiality_offset: byte_0
    cipher_suites:
      gcm_aes_256_enabled: true

- name: Relax a MACsec policy to should-secure and bypass BPDUs
  aoscx_macsec_policy:
    name: secure_uplinks
    state: update
    secure_mode: should-secure
    bypass:
      ieee_bpdu_enabled: true

- name: Delete a MACsec policy
  aoscx_macsec_policy:
    name: secure_uplinks
    state: delete
```
