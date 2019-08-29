
AOSCX Ansible Collection
=========

This Ansible Network collection provides a set of platform dependent configuration
 management modules specifically designed for the AOS-CX network device.

Requirements
------------

* Python 2.7 or 3.5+
* Ansible 2.8.4 or later  
* Minimum supported AOS-CX firmware version 10.03
* Enable REST on your AOS-CX device with the following commands:
    ```
    switch(config)# https-server rest access-mode read-write
    switch(config)# https-server vrf mgmt
    ```

Installation
------------

Through Github, use the following command. Use option `-f` to overwrite current collection version:

```
WORK IN PROGRESS
```

Through Galaxy:

```
WORK IN PROGRESS
```

Inventory Variables
--------------

The variables that should be defined in your inventory for your AOS-CX host are:

* `ansible_host`: IP address of switch in `A.B.C.D` format  
* `ansible_user`: Username for switch in `plaintext` format  
* `ansible_password`: Password for switch in `plaintext` format  
* `ansible_connection`: Must always be set to `httpapi`  
* `ansible_network_os`: Must always be set to `arubanetworks.aoscx.aoscx`  
* `ansible_httpapi_use_ssl`: Must always be `True` as AOS-CX uses port 443 for REST  
* `ansible_httpapi_validate_certs`: Set `True` or `False` depending on if Ansible should attempt to validate certificates  
* `ansible_acx_no_proxy`: Set `True` or `False` depending if Ansible should bypass environment proxies to connect to AOS-CX  

Sample `inventory.ini`:

```ini
aoscx_1 ansible_host=10.0.0.1 ansible_user=admin ansible_password=password ansible_connection=httpapi ansible_network_os=arubanetworks.aoscx.aoscx ansible_httpapi_validate_certs=False ansible_httpapi_use_ssl=True ansible_acx_no_proxy=True
```

Example Playbook
----------------

If collection installed through [Github](https://github.com/aruba/aoscx-ansible-collection)
set collection to `arubanetworks.aoscx`:

```yaml
    ---
    -  hosts: all
       collections:
         - arubanetworks.aoscx
       tasks:
         - name: Create L3 Interface 1/1/3
           aoscx_l3_interface:
            interface: 1/1/3
            description: Uplink_Interface
            ipv4: ['10.20.1.3/24']
            ipv6: ['2000:db8::1234/32']
```

If collection installed through [Galaxy](https://galaxy.ansible.com/arubanetworks/aoscx)
set collection to `arubanetworks.aoscx`:

```yaml
    ---
    -  hosts: all
       collections:
         - arubanetworks.aoscx
       tasks:
         - name: Create L3 Interface 1/1/3
           aoscx_l3_interface:
            interface: 1/1/3
            description: Uplink_Interface
            ipv4: ['10.20.1.3/24']
            ipv6: ['2000:db8::1234/32']
```

Contribution
-------
At Aruba Networks we're dedicated to ensuring the quality of our products, if you find any
issues at all please open an issue on our [Github](https://github.com/aruba/aoscx-ansible-collection) and we'll be sure to respond promptly!


License
-------

Apache-2.0

Author Information
------------------
 - Madhusudan Pranav Venugopal (@madhusudan-pranav-venugopal)  
 - Yang Liu (@yliu-aruba)  
 - Tiffany Chiapuzio-Wong (@tchiapuziowong)  

