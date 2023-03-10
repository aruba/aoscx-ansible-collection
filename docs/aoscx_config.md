# Config

Config module for Ansible.

Version added: 4.1.0

 - [Synopsis](#synopsis)
 - [Parameters](#parameters)
 - [Examples](#examples)

## Synopsis

This module allows configuration of running-configs on AOS-CX devices via SSH
connection.

## Parameters

| Parameter           | Type | Choices/Defaults                                     | Required | Comments                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|:--------------------|:-----|:-----------------------------------------------------|:--------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `lines`             | list |                                                      | [ ]      | List of configuration commands to be executed. If `parents` is specified, these are the child lines contained under/within the parent entry. If `parents` is not specified, these lines will be checked and/or placed under the global config level. These commands must correspond with what would be found in the device's running-config.                                                                                                                                                                                                                                                                                                                                                                     |
| `parents`           | list |                                                      | [ ]      | Parent lines that identify the configuration section or context under which the `lines` lines should be checked and/or placed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `src`               | path |                                                      | [ ]      | Path to the file containing the configuration to load into the device. The path can be either a full system path to the configuration file if the value starts with "/" or a path relative to the directory containing the playbook. This argument is mutually exclusive with the `lines` and `parents` arguments. This src file must have same indentation as a live switch config. The operation is purely additive, as it doesn't remove any lines that are present in the existing running-config, but not in the source config.                                                                                                                                                                             |
| `before`            | list |                                                      | [ ]      | Commands to be executed prior to execution of the parent and child lines. This option can be used to guarantee idempotency.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `after`             | list |                                                      | [ ]      | Commands to be executed following the execution of the parent and child lines. This option can be used to guarantee idempotency.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `match`             | str  | [`line`, `strict`, `exact`, `none`] / `line`         | [ ]      | Specifies the method of matching. Matching is the comparison against the existing running-config to determine whether changes need to be applied. If `match` is set to `line`, commands are matched line by line. If `match` is set to `strict`, command lines are matched with respect to position. If `match` is set to `exact`, command lines must be an equal match. If `match` is set to `none`, the module will not attempt to compare the source configuration with the running-config on the remote device.                                                                                                                                                                                              |
| `replace`           | str  | [`line`, `block`] / `line`                           | [ ]      | Specifies the approach the module will take when performing configuration on the device. If `replace` is set to `line`, then only the differing and missing configuration lines are pushed to the device. If `replace` is set to `block`, then the entire command block is pushed to the device if there is any differing or missing line at all.                                                                                                                                                                                                                                                                                                                                                                |
| `backup`            | bool | `false`                                              | [ ]      | Specifies whether a full backup of the existing running-config on the device will be performed before any changes are potentially made. If the `backup_options` value is not specified, the backup file is written to the `backup` folder in the playbook root directory. If the directory does not exist, it is created.                                                                                                                                                                                                                                                                                                                                                                                        |
| `backup_options`    | dict |                                                      | [ ]      | File path and name options for backing up the existing running-config. To be used with `backup`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `running_config`    | str  |                                                      | [ ]      | Specifies an alternative running-config to be used as the base config for matching. The module, by default, will connect to the device and retrieve the current running-config to use as the basis for comparison against the source. This argument is handy for times when it is not desirable to have the task get the current running-config, and instead use another config for matching.                                                                                                                                                                                                                                                                                                                    |
| `save_when`         | str  | [`always`, `never`, `modified`, `changed`] / `never` | [ ]      | Specifies when to copy the running-config to the startup-config. When changes are made to the device running-configuration, the changes are not copied to non-volatile storage by default. If `save_when` is set to `always`, the running-config will unconditionally be copied to startup-config. If `save_when` is set to `never`, the running-config will never be copied to startup-config. If `save_when` is set to `modified`, the running-config will be copied to startup-config if the two differ. If `save_when` is set to `changed`, the running-config will be copied to startup-config if the task modified the running-config.                                                                     |
| `diff_against`      | str  | [`startup`, `intended`, `running`]                   | [ ]      | When using the "ansible-playbook --diff" command line argument this module can generate diffs against different sources. This argument specifies the particular config against which a diff of the running-config will be performed. If `diff_against` is set to `startup`, the module will return the diff of the running-config against the startup configuration. If `diff_against` is set to `intended`, the module will return the diff of the running-config against the configuration provided in the `intended_config` argument. If `diff_against` is set to `running`, the module will return before and after diff of the running-config with respect to any changes made to the device configuration. |
| `diff_ignore_lines` | list |                                                      | [ ]      | Specifies one or more lines that should be ignored during the diff. This is used to ignore lines in the configuration that are automatically updated by the system. This argument takes a list of regular expressions or exact commands.                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `intended_config`   | str  |                                                      | [ ]      | Path to file containing the intended configuration that the device should conform to, and that is used to check the final running-config against. To be used with `diff_against`, which should be set to `intended`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `provider`          | dict |                                                      | [ ]      | A dict object containing connection details.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |

### `backup_options` dictionary parameters:

| Parameters | Type | Choices/Defaults | Required | Comments                                                  |
|:-----------|:-----|:-----------------|:--------:|:----------------------------------------------------------|
| `filename` | str  |                  | [ ]      | Name of file in which the running-config will be saved.   |
| `dir_path` | path |                  | [ ]      | Path to directory in which the backup file should reside. |

### `provider` dictionary parameters:

| Parameters    | Type | Choices/Defaults | Required | Comments                                                                                                                                                                                                                                                                                                           |
|:--------------|:-----|:-----------------|:--------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `auth_pass`   | str  |                  | [ ]      | Specifies the password to use if required to enter privileged mode on the remote device. If authorize is false, then this argument does nothing. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_AUTH_PASS will be used instead.                                          |
| `authorize`   | bool |                  | [ ]      | Instructs the module to enter privileged mode on the remote device before sending any commands. If not specified, the device will attempt to execute all commands in non-privileged mode. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_AUTHORIZE will be used instead. |
| `host`        | str  |                  | [x]      | Specifies the DNS host name or address for connecting to the remote device over the specified transport. The value of host is used as the destination address for the transport.                                                                                                                                   |
| `password`    | str  |                  | [ ]      | Specifies the password to use to authenticate the connection to the remote device. This value is used to authenticate the SSH session. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_PASSWORD will be used instead.                                                     |
| `port`        | int  |                  | [ ]      | Specifies the port to use when building the connection to the remote device.                                                                                                                                                                                                                                       |
| `ssh_keyfile` | path |                  | [ ]      | Specifies the SSH key to use to authenticate the connection to the remote device. This value is the path to the key used to authenticate the SSH session. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_SSH_KEYFILE will be used instead.                               |
| `timeout`     | int  |                  | [ ]      | Specifies the timeout in seconds for communicating with the network device for either connecting or sending commands. If the timeout is exceeded before the operation is completed, the module will error.                                                                                                         |
| `username`    | str  |                  | [ ]      | Configures the username to use to authenticate the connection to the remote device. This value is used to authenticate the SSH session. If the value is not specified in the task, the value of environment variable ANSIBLE_NET_USERNAME will be used instead.                                                    |

## Examples

Below you can find task examples of this module's implementation:

### Delete PoE assigned-class configuration

Before Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
    power-over-ethernet assigned-class 3
```

```YAML
- name: Delete PoE assigned-class configuration.
  aoscx_config:
    parents:
      - interface 1/1/4
    lines:
      - no power-over-ethernet assigned-class 3
```

After Device Configuration:
```
interface 1/1/4
    no shutdown
    vlan access 1
```

### Configure VLAN

```YAML
- name: First delete VLAN 44, then configure VLAN 45, and lastly create VLAN 46
  aoscx_config:
    before:
      - no vlan 44
    parents:
      - vlan 45
    lines:
      - name testvlan
      - description test_vlan
    after:
      - vlan 46
```

### Back up configuration

```YAML
- name: >
    Back up running-config, then create VLAN 100, and save running-config to
    startup-config if change was made.
  aoscx_config:
    backup: True
    lines:
      - vlan 100
    backup_options:
      filename: backup.cfg
      dir_path: /users/Home/
    save_when: changed
```

### Compare configurations

```YAML
- name: Compare running-config with saved config
  aoscx_config:
    diff_against: intended
    intended_config: /users/Home/backup.cfg
```

### Compare running-configs

```YAML
- name: >
    Configure VLAN 2345 and compare resulting running-config with previous
    running-config.
  aoscx_config:
    lines:
      - vlan 2345
    diff_against: running
```

### Upload configuration

```YAML
- name: Upload a config from local system file onto device
  aoscx_config:
    src: /users/Home/golden.cfg
```

### Update interface

```YAML
- name: >
    Update interface 1/1/4, matching only if both "parents" and "lines" are
    present.
  aoscx_config:
    lines:
      - ip address 4.4.4.5/24
    parents: interface 1/1/4
    match: strict
```

### Configure a multi-line banner

```YAML
- name: Configure a multi-line banner
  aoscx_config:
    lines:
      - hello this is a banner_motd
      - this is banner line 2 banner_motd
      - this is banner line 3 banner_motd
    before: "banner motd `"
    after: "`"
```
