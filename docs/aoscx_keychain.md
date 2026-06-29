# module: aoscx_keychain

description: This module provides configuration management of keychains on AOS-CX
devices (system/keychains). A keychain is a named container of authentication
keys used by MKA policies and routing protocol authentication. This module
requires REST API version 10.16 (set ansible_aoscx_rest_version to 10.16). The
supplied keys fully replace the existing keys of the keychain. The fields of a
key cannot be modified in place; when they change the key is recreated. The
auth_key value is write-only on the switch and cannot be read back, so a change
to auth_key alone (without any other key field change) is not detected.

##### ARGUMENTS

```YAML
  name:
    description: Name of the keychain (index under system/keychains).
    required: true
    type: str
  keys:
    description: >
      List of keys of the keychain. The supplied list fully replaces the
      existing keys. When omitted, the keys are left untouched and only the
      existence of the keychain is reconciled.
    required: false
    type: list
    elements: dict
    suboptions:
      key_id:
        description: Identifier of the key within the keychain.
        required: true
        type: int
      auth_type:
        description: Authentication algorithm of the key.
        required: false
        type: str
        choices:
          - md5
          - sha1
          - sha256
          - sha384
          - sha512
          - aes_cmac128
      auth_key:
        description: >
          Authentication key value. This value is write-only on the switch and
          cannot be read back; a change to auth_key alone is not detected.
        required: false
        type: str
      name:
        description: Optional name of the key.
        required: false
        type: str
      accept_start:
        description: >
          Start of the period during which the key is accepted, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      accept_end:
        description: >
          End of the period during which the key is accepted, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      send_start:
        description: >
          Start of the period during which the key is used to send, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      send_end:
        description: >
          End of the period during which the key is used to send, as a Unix
          timestamp (between 1577836800 and 2556143999).
        required: false
        type: int
      recv_id:
        description: Receive identifier of the key.
        required: false
        type: int
      send_id:
        description: Send identifier of the key.
        required: false
        type: int
  state:
    description: Create, update or delete the keychain.
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
- name: Create a keychain with one SHA-256 key
  aoscx_keychain:
    name: mka_keys
    keys:
      - key_id: 1
        auth_type: sha256
        auth_key: "S3cretKey123"
        accept_start: 1577836800
        accept_end: 2556143999
        send_start: 1577836800
        send_end: 2556143999
        recv_id: 1
        send_id: 1

- name: Remove all keys but keep the keychain
  aoscx_keychain:
    name: mka_keys
    keys: []

- name: Delete a keychain
  aoscx_keychain:
    name: mka_keys
    state: delete
```
