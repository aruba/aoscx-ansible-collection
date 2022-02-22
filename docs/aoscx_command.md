# module: aoscx_command

description: This module allows execution of CLI commands on AOS-CX devices via
SSH connection.

Although this module can execute configuration commands, there is another
module designed to execute just configuration commands, `aoscx_config`.

##### NOTES

* `aoscx_command` will not handle commands that repeat forever such as `repeat`
* Besides simple "yes/no" prompts, `aoscx_command` is unable to process
  commands which require user input
	* This includes operations such as password entry
    * If a command requires a "yes/no" confirmation, include the line
      `auto-confirm` at the beginning of the task, like in the below example
        * `auto-confirm` does not allow copying AOS-CX images with TFTP
```yaml
- hosts: all
    roles:
      - role: aoscx-ansible-role
    tasks:
      - name: VSF Renumber-To with Autoconfirm
        aoscx_command:
          lines:
            - auto-confirm
            - configure
            - vsf renumber-to 2
```

##### ARGUMENTS

```YAML
  commands:
    description: >
      List of commands to be executed in sequence on the switch. Every command
      will attempt to be executed regardless of the success or failure of the
      previous command in the list. To execute commands in the 'configure'
      context, you must include the 'configure terminal' command or one of its
      variations before the configuration commands. 'Show' commands are valid
      and their output will be printed to the screen, returned by the module,
      and optionally saved to a file. The default module timeout is 30 seconds.
      To change the command timeout, set the variable 'ansible_command_timeout'
      to the desired time in seconds.
    required: true
    type: list
  wait_for:
    description: >
      A list of conditions to wait to be satisfied before continuing execution.
      Each condition must include a test of the 'result' variable, which
      contains the output results of each already-executed command in the
      'commands' list. 'result' is a list such that result[0] contains the
      output from commands[0], results[1] contains the output from commands[1],
      and so on.
    required: false
    type: list
    elements: str
    aliases:
      - waitfor
  match:
    description: >
      Specifies whether all conditions in 'wait_for' must be satisfied or if
      just any one condition can be satisfied. To be used with 'wait_for'.
    choices:
      - any
      - all
    default: 'all'
    required: false
    type: str
  retries:
    description: Maximum number of retries to check for the expected prompt.
    default: 10
    required: false
    type: int
  interval:
    description: Interval between retries, in seconds.
    default: 1
    required: false
    type: int
  output_file:
    description: >
      Full path of the local system file to which commands' results will be
      output. The directory must exist, but if the file doesn't exist, it will
      be created.
    required: false
    type: str
  output_file_format:
    description: Format to output the file in, either JSON or plain text.
      To be used with 'output_file'.
    default: json
    choices:
      - json
      - plain-text
    required: false
    type: str
```

##### EXAMPLES

```YAML
- name: >
    Execute show commands and configure commands, and output results to file in
    plaintext.
  aoscx_command:
    commands:
      - show run
      - show vsf
      - show interface 1/1/1
      - config
      - interface 1/1/2
      - no shut
      - ip address 10.10.10.10/24
      - routing
      - ip address 10.10.10.11/24
      - exit
      - vlan 2
      - end
    output_file: /users/Home/configure.cfg
    output_file_format: plain-text

- name: >
    Show running-config and show interface mgmt, and pass only if all (both)
    results match.
  aoscx_command:
    commands:
      - show run
      - show int mgmt
    wait_for:
      - result[0] contains "vlan "
      - result[1] contains "127.0.0.1"
    match: all
    retries: 5
    interval: 5

- name: Show all available commands and output them to a file (as JSON)
  aoscx_command:
    commands:
      - list
    output_file: /users/Home/config_list.cfg

- name: Run ping command with increased command timeout
  vars:
    - ansible_command_timeout: 60
  aoscx_command:
    commands:
      - ping 10.80.2.120 vrf mgmt repetitions 100
```
