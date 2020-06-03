
AOSCX Ansible Collection
=========

This Ansible Network collection provides a set of platform dependent configuration
management modules specifically designed for the AOS-CX network device.

Requirements
------------

* Python 2.7 or 3.5+
* Ansible 2.9.0 or later
* Minimum supported AOS-CX firmware version 10.03
* Enable REST on your AOS-CX device with the following commands:
    ```
    switch(config)# https-server rest access-mode read-write
    switch(config)# https-server vrf mgmt
    ```

SSH/CLI Modules
---------------
* To use the SSH/CLI modules `aoscx_config` and `aoscx_command`, SSH access must
  be enabled on your AOS-CX device. It is enabled by default.
    * If necessary, re-enable SSH access on the device with the following command:
    ```
    switch(config)# ssh server vrf mgmt
    ```
* The control machine's `known_hosts` file must contain the target device's public key.
    * Alternatively, host key checking by the control machine may be disabled, although this is not recommended.
    * To disable host key checking modify the ansible.cfg file (default /etc/ansible/ansible.cfg) to include:
      `host_key_checking = false`

#### Limitations and Notes
* The default command timeout is 30 seconds. If a command takes more than 30
 seconds to execute, the task will time out.
	* If you regularly encounter the `command timeout triggered, timeout value
	  is 30 secs` error, consider setting the environment variable
	  `ANSIBLE_PERSISTENT_COMMAND_TIMEOUT` to a greater value. See Ansible documentation [here](https://docs.ansible.com/ansible/latest/network/user_guide/network_debug_troubleshooting.html).

Installation
------------

Through Galaxy:

```
ansible-galaxy collection install arubanetworks.aoscx
```

Inventory Variables
-------------------

The variables that should be defined in your inventory for your AOS-CX host are:

* `ansible_host`: IP address of switch in `A.B.C.D` format. For IPv6 hosts use a string and enclose in square brackets E.G. `'[2001::1]'`.
* `ansible_user`: Username for switch in `plaintext` format  
* `ansible_password`: Password for switch in `plaintext` format
* `ansible_network_os`: Must always be set to `arubanetworks.aoscx.aoscx`
* `ansible_connection`: Set to `httpapi` to use REST API modules, and to `network_cli` to use SSH/CLI modules
  * See [below](#using-both-rest-api-and-sshcli-modules-on-a-host) for info on using both REST API modules and SSH/CLI modules on a host
* `ansible_httpapi_use_ssl`: (Only required for REST API modules) Must always be `True` as AOS-CX uses port 443 for REST
* `ansible_httpapi_validate_certs`: (Only required for REST API modules) Set `True` or `False` depending on if Ansible should attempt to validate certificates
* `ansible_acx_no_proxy`: Set to `True` or `False` depending if Ansible should bypass environment proxies to connect to AOS-CX

### Sample Inventories:

#### REST API Modules Only:

##### INI

```INI
aoscx_1 ansible_host=10.0.0.1 ansible_user=admin ansible_password=password ansible_network_os=arubanetworks.aoscx.aoscx ansible_connection=httpapi ansible_httpapi_validate_certs=False ansible_httpapi_use_ssl=True ansible_acx_no_proxy=True
```

##### YAML

```yaml
all:
  hosts:
    aoscx_1:
      ansible_host: 10.0.0.1
      ansible_user: admin
      ansible_password: password
      ansible_network_os: arubanetworks.aoscx.aoscx
      ansible_connection: httpapi  # REST API connection method
      ansible_httpapi_validate_certs: False
      ansible_httpapi_use_ssl: True
      ansible_acx_no_proxy: True
```

#### SSH/CLI Modules Only:

##### INI

```INI
aoscx_1 ansible_host=10.0.0.1 ansible_user=admin ansible_password=password ansible_network_os=arubanetworks.aoscx.aoscx ansible_connection=network_cli
```

##### YAML

```yaml
all:
  hosts:
    aoscx_1:
      ansible_host: 10.0.0.1
      ansible_user: admin
      ansible_password: password
      ansible_network_os: arubanetworks.aoscx.aoscx
      ansible_connection: network_cli  # SSH connection method
```

Example Playbooks
-----------------

### Including the Collection

If collection installed through Galaxy add `arubanetworks.aoscx` to your list of collections:

```yaml
-  hosts: all
 collections:
  - arubanetworks.aoscx
 tasks:
  - name: Create L3 Interface 1/1/3
    aoscx_l3_interface:
      interface: 1/1/3
      description: Uplink_Interface
      ipv4: ['10.20.1.3/24']
      ipv6: ['2001:db8::1234/64']
```


Using Both REST API and SSH/CLI Modules on a Host
-------------------------------------------------

To use both REST API and SSH/CLI modules on the same host,
you must create separate plays such
that each play uses either only REST API modules or only SSH/CLI modules.
A play cannot mix and match REST API and SSH/CLI module calls.
In each play, `ansible_connection` must possess the appropriate value
according to the modules used.
If the play uses REST API modules, the value should be `httpapi`.
If the play uses SSH/CLI modules, the value should be `network_cli`.

A recommended approach to successfully using both types of modules for a host
is as follows:
1. Set the host variables such that Ansible will connect to the host using REST API,
like seen [above](#rest-api-modules-only).
2. In the playbook, in each play wherein the SSH/CLI
modules are used, set the `ansible_connection` to `network_cli`.

The inventory should look something like this:

```yaml
all:
  hosts:
    aoscx_1:
      ansible_host: 10.0.0.1
      ansible_user: admin
      ansible_password: password
      ansible_network_os: arubanetworks.aoscx.aoscx
      ansible_connection: httpapi  # REST API connection method
      ansible_httpapi_validate_certs: False
      ansible_httpapi_use_ssl: True
      ansible_acx_no_proxy: True
```

and the playbook like this (note how the second play, which uses the SSH/CLI module `aoscx_command`,
sets the `ansible_connection` value accordingly):

```yaml
- hosts: all
  collections:
    - arubanetworks.aoscx
  tasks:
    - name: Adding or Updating Banner
      aoscx_banner:
        banner_type: banner
        banner: "Hi!"

- hosts: all
  collections:
    - arubanetworks.aoscx
  vars:
    ansible_connection: network_cli
  tasks:
    - name: Execute show run on the switch
      aoscx_command:
        commands: ['show run']
```

Contribution
-------
At Aruba Networks we're dedicated to ensuring the quality of our products, so if you find any
issues at all please open an issue on our [Github](https://github.com/aruba/aoscx-ansible-collection) and we'll be sure to respond promptly!

License
-------

Apache 2.0

Author Information
------------------
 - Madhusudan Pranav Venugopal (@madhusudan-pranav-venugopal)
 - Yang Liu (@yliu-aruba)
 - Tiffany Chiapuzio-Wong (@tchiapuziowong)
 - Derek Wang (@derekwangHPEAruba)
 - Melvin Gutierrez (@melvin-gutierrez)
 - Rodrigo Jose Hernandez (@rodrigo-j-hernandez)
