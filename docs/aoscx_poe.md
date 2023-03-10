# Power over Ethernet

Power over Ethernet module for Ansible.

Version added: 4.0.0

 - [Synopsis](#Synopsis)
 - [Parameters](#Parameters)
 - [Examples](#Examples)

## Synopsis

Power-over-ethernet (PoE) manages power supplied to devices using standard
Ethernet data cables by managing an Interface's Configuration. You can find
additional information online about how PoE is structured at the [Aruba Portal
](https://developer.arubanetworks.com/aruba-aoscx/reference/get_system-interfaces-name-poe-interface)

## Parameters

| Parameter             | Type | Choices/Defaults                                                                                 | Required | Comments                                                                                                                                                                                                   |
|:----------------------|:-----|:-------------------------------------------------------------------------------------------------|:--------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `interface`           | str  |                                                                                                  | [x]      | The name of an interface available inside a switch.                                                                                                                                                        |
| `enable`              | bool |                                                                                                  | [ ]      | Configurable flag to control PoE power delivery on this Interface. A value of true would enable PoE power delivery on this Interface. By default, the flag is set to false for all PoE capable Interfaces. |
| `priority`            | str  | [`low`, `high`, `critical`]                                                                      | [ ]      | Power criticality level for the PoE Interface.                                                                                                                                                             |
| `allocate_by_method`  | str  | [`usage`, `class`]                                                                               | [ ]      | Configure the power allocation method for the PoE Interface.                                                                                                                                               |
| `assigned_class`      | int  | [3, 4, 6, 8]                                                                                     | [ ]      | Assigned class (power limit) for the PoE Interface.                                                                                                                                                        |
| `pd_class_override`   | bool |                                                                                                  | [ ]      | Enable PD requested class override by user assigned class.                                                                                                                                                 |
| `pre_standard_detect` | bool |                                                                                                  | [ ]      | Enable detection of pre-standard PoE devices.                                                                                                                                                              |
| `state`               | str  | [`create`, `delete`, `update`]/`create`                                                          | [ ]      | Create, Update, or Delete PoE Interface.                                                                                                                                                                   |

## Examples

### Enable Power over Ethernet

The following example enables PoE on the 1/1/5 and 1/1/10 interfaces.

Before Device Configuration:
```
interface 1/1/5
    no shutdown
    vlan access 1
    no power-over-ethernet
```

Playbook:
```YAML
- name: Enable Power over Ethernet on Interface 1/1/5
  aoscx_poe:
    interface: 1/1/5
    enable: True
```

After Device Configuration:
```
interface 1/1/5
    no shutdown
    vlan access 1
```

Before Device Configuration:
```
interface 1/1/10
    no shutdown
    vlan access 1
    no power-over-ethernet
```

Playbook:
```YAML
- name: Enable Power Over Ethernet on Interface 1/1/10
  aoscx_poe:
    interface: 1/1/10
    enable: True
```

After Device Configuration:
```
interface 1/1/10
    no shutdown
    vlan access 1
```

### Disable Power over Ethernet

The following example disables PoE on the 1/1/7 interface.

Before Device Configuration:
```
interface 1/1/7
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Disable Power Over Ethernet on Interface 1/1/7
  aoscx_poe:
    interface: 1/1/7
    enable: False
```

After Device Configuration:
```
interface 1/1/7
    no shutdown
    vlan access 1
    no power-over-ethernet
```

### Set priority levels

The following examples set different priority levels to different interfaces.

Before Device Configuration:
```
interface 1/1/23
    no shutdown
    vlan access 1
    power-over-ethernet priority high
```

Playbook:
```YAML
- name: Configure PoE on Interface 1/1/23
  aoscx_poe:
    interface: 1/1/23
    priority: low
```

After Device Configuration:
```
interface 1/1/23
    no shutdown
    vlan access 1
```

Before Device Configuration:
```
interface 1/1/24
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure and enable PoE on Interface 1/1/24
  aoscx_poe:
    interface: 1/1/24
    enable: True
    priority: high
```

After Device Configuration:
```
interface 1/1/24
    no shutdown
    vlan access 1
    power-over-ethernet priority high
```

Before Device Configuration:
```
interface 1/1/25
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Configure PoE on Interface 1/1/25
  aoscx_poe:
    interface: 1/1/25
    priority: critical
```

After Device Configuration:
```
interface 1/1/25
    no shutdown
    vlan access 1
    power-over-ethernet priority critical
```

### Set allocate method

The following examples set different allocate methods to different interfaces.

Before Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Set allocate method for PoE on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    allocate_by_method: class
```

After Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
    power-over-ethernet allocate-by class
```

Before Device Configuration:
```
interface 1/1/5
    no shutdown
    vlan access 1
    power-over-ethernet allocate-by class
```

Playbook:
```YAML
- name: Set allocate method for PoE on Interface 1/1/5
  aoscx_poe:
    interface: 1/1/5
    allocate_by_method: usage
```

After Device Configuration:
```
interface 1/1/5
    no shutdown
    vlan access 1
```

### Set assigned class

The following examples assigned different classes to different interfaces.

Before Device Configuration:
```
interface 1/1/9
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Set class for PoE on Interface 1/1/9
  aoscx_poe:
    interface: 1/1/9
    assigned_class: 3
```

After Device Configuration:
```
interface 1/1/9
    no shutdown
    vlan access 1
    power-over-ethernet assigned-class 3
```

Before Device Configuration:
```
interface 1/1/7
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Set class for PoE on Interface 1/1/7
  aoscx_poe:
    interface: 1/1/7
    assigned_class: 8
```

After Device Configuration:
```
interface 1/1/7
    no shutdown
    vlan access 1
    power-over-ethernet assigned-class 8
```

### Enable PD class override

The following example enables PD class override to an interface.

Before Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Enable PD requested class override on Interface 1/1/3
  aoscx_poe:
    interface: 1/1/3
    pd_class_override: true
```

After Device Configuration:
```
interface 1/1/3
    no shutdown
    vlan access 1
    power-over-ethernet pd-class-override
    power-over-ethernet allocate-by class
```

### Enable detection of pre-standard

The following example enables detection of pre-standard to an interface.

Before Device Configuration:
```
interface 1/1/2
    no shutdown
    vlan access 1
```

Playbook:
```YAML
- name: Enable detection of pre-standard on Interface 1/1/2
  aoscx_poe:
    interface: 1/1/2
    pre_standard_detect: true
```

After Device Configuration:
```
interface 1/1/2
    no shutdown
    vlan access 1
    power-over-ethernet pre-std-detect
```

### Delete configuration

The following example deletes the current configuration.

Before Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
    power-over-ethernet allocate-by class
```

Playbook:
```YAML
- name: Delete current configuration on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    allocate_by_method: class
    state: delete
```

After Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
```

Before Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
    power-over-ethernet pd-class-override
    power-over-ethernet allocate-by class
```

Playbook:
```YAML
- name: Delete current configuration on Interface 1/1/4
  aoscx_poe:
    interface: 1/1/4
    pd_class_override: true
    state: delete
```

After Device Configuration:

```
interface 1/1/4
    no shutdown
    vlan access 1
    power-over-ethernet allocate-by class
```
