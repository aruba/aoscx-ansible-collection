# module: aoscx_acl

description: This modules provides configuration management and creation of Access Classifier Lists on AOS-CX devices.  

##### ARGUMENTS
```YAML
  name:
    description: Name of the Access Classifier List
    type: str
    required: true
  type:
    description: Type of the Access Classifier List
    type: str
    choices: ['ipv4', 'ipv6', 'mac']
    required: true
  acl_entries:
    description: "Dictionary of dictionaries of Access Classifier Entries
      configured in Access Classifier List. Each entry key of the dictionary
      should be the sequence number of the ACL entry. Each ACL entry dictionary
      should have the minimum following keys - action , src_ip, dst_ip. See
      below for examples of options and values."
    type: dict
    required: false
  state:
    description: Create, Update, or Delete Access Classifier List
    type: str
    choices: ['create', 'delete', 'update']
    default: 'create'
    required: false
```

##### EXAMPLES
```YAML
- name: Configure IPv4 ACL with entry - 1 deny tcp 10.10.12.12 10.10.12.11 count
  aoscx_acl:
    name: ipv4_acl_example
    type: ipv4
    acl_entries: {
      '1': {action: deny, # ACL Entry Action - choices: ['permit', 'deny']
            count: true, # Enable 'count' on the ACL Entry - choices: ['permit', 'deny']
            dst_ip: 10.10.12.11/255.255.255.255,  # Matching Destination IPv4 address, format IP/MASK
            protocol: tcp,  # Matching protocol
            src_ip: 10.10.12.12/255.255.255.255 # Matching Source IPv4 address, format IP/MASK
            }
      }

- name: Configure IPv6 ACL with entry - 809 permit icmpv6 2001:db8::11 2001:db8::12
  aoscx_acl:
    name: ipv6_acl_example
    type: ipv6
    acl_entries: {
      '809': {action: permit, # ACL Entry Action - choices: ['permit', 'deny']
              count: false, # Enable 'count' on the ACL Entry - choices: ['permit', 'deny']
              dst_ip: 2001:db8::11/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff,  # Matching Destination IPv6 address, format IP/MASK
              protocol: icmpv6,  # Matching protocol
              src_ip: 2001:db8::12/ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff # Matching Source IPv6 address, format IP/MASK
              }
      }

- name: Change existing IPv4 ACL Entry - 1 permit tcp 10.10.12.12 10.10.12.11 count
  aoscx_acl:
    name: ipv4_acl_example
    type: ipv4
    acl_entries: {
      '1': {action: permit, # ACL Entry Action - choices: ['permit', 'deny']
            count: true, # Enable 'count' on the ACL Entry - choices: ['permit', 'deny']
            dst_ip: 10.10.12.11/255.255.255.255,  # Matching Destination IPv4 address, format IP/MASK
            protocol: tcp,  # Matching protocol
            src_ip: 10.10.12.12/255.255.255.255 # Matching Source IPv4 address, format IP/MASK
            }
      }
    state: update

- name: Delete ipv4 ACL from config
  aoscx_acl:
    name: ipv4_acl
    type: ipv4
    state: delete
```