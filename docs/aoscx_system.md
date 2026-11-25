# module: aoscx_system

description: This module provides configuration management of the global
(system wide) settings of AOS-CX devices: global QoS trust mode, queue and
schedule profiles, global virtual MAC address, Group Based Policy enforcement,
internal VLAN range and interface group speeds. Options that are omitted are
left unchanged. Check mode is supported but does not report changes.

##### ARGUMENTS

```YAML
  global_qos_trust_mode:
    description: >
      Trust mode to be set as global for an AOS-CX device. Use "default" to set
      the factory-default global trust mode.
    type: str
    required: false
    choices:
      - cos
      - dscp
      - none
      - default

  global_queue_profile:
    description: >
      Queue Profile to set as the global one for an AOS-CX device. This option
      is mutually exclusive with the use_default_global_queue_profile option.
    type: str
    required: false

  use_default_global_queue_profile:
    description: >
      Set the global queue profile for an AOS-CX device to its factory
      default global queue profile, this option is mutually exclusive with the
      global_queue_profile option.
    type: bool
    default: false
    required: false

  global_schedule_profile:
    description: >
      Schedule Profile to set as the global one for an AOS-CX device. This
      option is mutually exclusive with the use_default_global_schedule_profile
      option.
    type: str
    required: false

  use_default_global_schedule_profile:
    description: >
      Set the global schedule profile for an AOS-CX device to its factory
      default global schedule profile, this option is mutually exclusive with
      the global_schedule_profile option.
    type: bool
    default: false
    required: false

  virtual_mac:
    description: >
      Global virtual MAC address (virtual-mac command), in the
      xx:xx:xx:xx:xx:xx format. EVPN advertises it as the router MAC of the
      symmetric IRB routes. This option is mutually exclusive with the
      use_default_virtual_mac option.
    type: str
    required: false

  use_default_virtual_mac:
    description: >
      Remove the global virtual MAC address (no virtual-mac), this option is
      mutually exclusive with the virtual_mac option.
    type: bool
    default: false
    required: false

  gbp_enable:
    description: >
      Enable (gbp enable) or disable (no gbp enable) Group Based Policy
      enforcement. Requires a pyaoscx release that ships
      Device.set_gbp_enable().
    type: bool
    required: false

  internal_vlan_range:
    description: >
      VLAN range reserved for internal use (system internal-vlan-range start
      <start> end <end>). Platforms such as the 6200 reserve no internal VLAN
      by default and refuse to enable routing on a port ("Configure system
      internal VLAN range before enabling routing") until a range is
      configured. The task fails on platforms where the range is not
      configurable (6300, 6400, 8360, ...). Requires a pyaoscx release that
      ships Device.set_internal_vlan_range().
    type: dict
    required: false
    suboptions:
      start:
        description: First VLAN ID of the range (2-4094).
        type: int
        required: true
      end:
        description: >
          Last VLAN ID of the range (2-4094), not lower than start.
        type: int
        required: true

  interface_groups:
    description: >
      Permitted transceiver speed of interface groups (system interface-group
      <group> [line-module <line_module>] speed <speed>). An interface group is
      a set of ports of a chassis or line module sharing the same permitted
      transceiver speed, for example on the 8360 or on some 6400 line modules.
      Changing the speed of a group resets all its ports. The groups and their
      ports are listed by "show system interface-group"; the group and speed
      are checked against the values supported by the switch before any
      change. Requires a pyaoscx release that ships
      Device.set_interface_group_speed().
    type: list
    elements: dict
    required: false
    suboptions:
      group:
        description: Interface group number.
        type: int
        required: true
      speed:
        description: >
          Permitted speed of the group, for example 10g, 25g or 50g depending
          on the group, or "default" to restore the default speed of the group.
        type: str
        required: true
      line_module:
        description: >
          Line module of the group, for example "1/3". Required on modular
          switches where several line modules have the group.
        type: str
        required: false
```

##### EXAMPLES

```YAML
- name: Set the global qos trust mode to dscp
  aoscx_system:
    global_qos_trust_mode: dscp

- name: Set the global qos trust mode to the switch's factory default
  aoscx_system:
    global_qos_trust_mode: default

- name: >
    Set the switch's global Queue Profile to a Queue Profile named
    STRICT-PROFILE
  aoscx_system:
    global_queue_profile: STRICT-PROFILE

- name: Set the global Queue Profile to the switch's factory default
  aoscx_system:
    use_default_global_queue_profile: true

- name: >
    Set the switch's global Schedule Profile to a Schedule Profile named
    STRICT-PROFILE
  aoscx_system:
    global_schedule_profile: STRICT-PROFILE

- name: Set the global Schedule Profile to the switch's factory default
  aoscx_system:
    use_default_global_schedule_profile: true

- name: Set the global virtual MAC address used by EVPN symmetric IRB
  aoscx_system:
    virtual_mac: "02:00:00:00:00:01"

- name: Remove the global virtual MAC address
  aoscx_system:
    use_default_virtual_mac: true

- name: Enable Group Based Policy enforcement
  aoscx_system:
    gbp_enable: true

- name: Reserve VLANs 3000-3999 for internal use (required on a 6200)
  aoscx_system:
    internal_vlan_range:
      start: 3000
      end: 3999

- name: Allow 10G transceivers in interface group 1 of an 8360
  aoscx_system:
    interface_groups:
      - group: 1
        speed: 10g

- name: Restore the default speed of interface group 2 of line module 1/3
  aoscx_system:
    interface_groups:
      - group: 2
        line_module: "1/3"
        speed: default
```
