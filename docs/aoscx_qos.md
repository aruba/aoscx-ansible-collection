# Quality of Service (QoS)

## Synopsis

Quality of Service features:

- Allow network devices to customize how different kinds of traffic are served,
  so as to reflect each traffic type's unique characteristics and importance to
  your organization.
- Ensure uniform and efficient traffic-handling throughout the network, while
  keeping the most important traffic moving at an acceptable throughput,
  regardless of available bandwidth usage.
- Exercise control over the priority settings of inbound traffic arriving at
  each network device.

## Modules:

- [aoscx_qos](#aoscx_qos)
- [aoscx_qos_cos](#aoscx_qos_cos)
- [aoscx_qos_dscp](#aoscx_qos_dscp)
- [aoscx_queue](#aoscx_queue)
- [aoscx_queue_profile](#aoscx_queue_profile)
- [aoscx_queue_profile_entry](#aoscx_queue_profile_entry)

---
## aoscx_qos

QoS (Quality of Service) module for Ansible.

Version added: 4.0.0

This module implements creation or deletion of a Schedule Profiles for future
configuration through the related [Queue](#aoscx_queue) module.

You can find additional information online about how QoS is structured at the
[Aruba Portal](https://developer.arubanetworks.com/aruba-aoscx/reference#qos)

- ## Parameters
| Parameter       | Type | Choices/Defaults                          | Required | Comments                                                            |
|:----------------|:-----|:------------------------------------------|:--------:|:--------------------------------------------------------------------|
| `name`          | str  |                                           | [x]      | Name of the Schedule Profile.                                       |
| `vsx_sync`      | list | [`all_attributes_and_dependents`]         | [ ]      | Controls which attributes should be synchronized between VSX peers. |
| `state`         | str  | [`create`, `update`, `delete`] / `create` | [ ]      | The action to be taken with the current Schedule Profile.           |

---
## aoscx_qos_cos

QoS CoS Map Entry module for Ansible.

Version added: 4.0.0

This module implements update actions of the CoS _(Class of Service)_ Map to
determine which local-priority and color to assign to packets.

You can find additional information online about how the CoS Map is structured
at the [Aruba Portal
](https://developer.arubanetworks.com/aruba-aoscx/reference#qos_cos_map_entry)

- ## Parameters
| Parameter       | Type | Choices/Defaults           | Required | Comments                                                                                                                                                                                                             |
|:----------------|:-----|:---------------------------|:--------:|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `code_point`    | int  | [0-7]                      | [x]      | Integer to identify an entry a QoS COS trust mode object. The minimum code_point is 0 and the maximum is 7.                                                                                                          |
| `color`         | str  | [`red`, `yellow`, `green`] | [ ]      | String to identify the color which may be used later in the pipeline in packet-drop decision points.                                                                                                                 |
| `description`   | str  |                            | [ ]      | String used for customer documentation.                                                                                                                                                                              |
| `local_priority`| int  | [0-7]                      | [ ]      | Integer to represent an internal meta-data value that will be associated with the packet. This value will be used later to select the egress queue for the packet. The range of the local priority goes from 0 to 7. |

---
## aoscx_qos_dscp

QoS DSCP Map Entry module for Ansible.

Version added: 4.0.0

This module implements update actions of the DSCP _(Differentiated Services
Code Point)_ Map to determine which local-priority and color to assign to
packets.

You can find additional information online about how the DSCP Map is structured
at the [Aruba Portal
](https://developer.arubanetworks.com/aruba-aoscx/reference#qos_dscp_map_entry)

- ## Parameters
| Parameter             | Type | Choices/Defaults           | Required | Comments                                                                                                                                                                                 |
|:----------------------|:-----|:---------------------------|:--------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `code_point`          | int  | [0-63]                     | [x]      | Integer to identify an entry a DSCP QoS trust mode object. The minimum code_point is 0 and the maximum is 63.                                                                            |
| `color`               | str  | [`red`, `yellow`, `green`] | [ ]      | String to identify the color which may be used later in the pipeline in packet-drop decision points.                                                                                     |
| `description`         | str  |                            | [ ]      | String used for customer documentation.                                                                                                                                                  |
| `local_priority`      | int  | [0-7]                      | [ ]      | This integer value is used to select the egress queue for the packet.                                                                                                                    |
| `cos`                 | int  | [0-7]                      | [ ]      | Priority Code Point (PCP), assigned to any IP packet with the specified DSCP codepoint, transmitted out of a port or trunk with a VLAN tag. Used in 4100, 6000, and 6100 switches.       |
| `priority_code_point` | int  | [0-7]                      | [ ]      | Priority Code Point (PCP), assigned to any IP packet with the specified DSCP codepoint, transmitted out of a port or trunk with a VLAN tag. Used in 6200, 6300, 6400, and 8360 switches. |

---
## aoscx_queue

QoS Queues module for Ansible.

Version added: 4.0.0

This module implements creation or deletion of a Queues, in Schedule Profiles.

You can find additional information online about how Queues are structured at
the [Aruba Portal
](https://developer.arubanetworks.com/aruba-aoscx/reference#queues)

| Parameter        | Type | Choices/Defaults                          | Required | Comments                                                                                                                                                                                                                                                                                                                                                                            |
|:-----------------|:-----|:------------------------------------------|:--------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `qos_name`       | str  |                                           | [x]      | Schedule Profile configuration name.                                                                                                                                                                                                                                                                                                                                                |
| `queue_number`   | int  |                                           | [x]      | Number to identify a Queue.                                                                                                                                                                                                                                                                                                                                                         |
| `weight`         | int  |                                           | [ ]      | Weight value for a queue. Maximum number is hardware dependent.                                                                                                                                                                                                                                                                                                                     |
| `algorithm`      | str  | [`strict`, `dwrr`, `wfq`] / `strict`      | [ ]      | Scheduling behavior of the queue, strict will service packets in queue before packets in lower numbered queues, dwrr, or Deficit Weighted Round Robin will apportion available bandwidth among all non-empty dwrr queues in relation to their weight, wfq, or Weighted Fair Queueing will apportion available bandwidth among all non-empty wfq queues in relation to their weight. |
| `bandwidth`      | int  |                                           | [ ]      | Bandwidth limit in kilobits per second to apply to egress traffic, if not specified, bandwidth is not limited per queue.                                                                                                                                                                                                                                                            |
| `burst`          | int  |                                           | [ ]      | Burst size in kilobytes allowed per bandwidth-queue, if not specified the default 32KB will be applied.                                                                                                                                                                                                                                                                             |
| `gmb_percent`    | int  | [0-100]                                   | [ ]      | The Guaranteed Minimum Bandwidth as a percentage of line rate between 0 and 100. This option is mutually exclusive with the `no_gmb_percent` option.                                                                                                                                                                                                                                |
| `no_gmb_percent` | bool | false                                     | [ ]      | Option to remove the Guaranteed Minimum Bandwidth. This option is mutually exclusive with the `gmb_percent` option.                                                                                                                                                                                                                                                                 |
| `state`          | str  | [`create`, `update`, `delete`] / `create` | [ ]      | Create, update, or delete the Queue.                                                                                                                                                                                                                                                                                                                                                |

---
## aoscx_queue_profile

Queue Profile module for Ansible.

Version added: 4.0.0

This module implements creation, deletion or update of a Queue Profile.

You can find additional information online about how Queue Profiles are
structured at the [Aruba Portal
](https://developer.arubanetworks.com/aruba-aoscx/reference#q_profile)

| Parameter               | Type | Choices/Defaults                          | Required | Comments                                                            |
|:------------------------|:-----|:------------------------------------------|:--------:|:--------------------------------------------------------------------|
| `name`                  | str  |                                           | [x]      | Queue Profile Name.                                                 |
| `vsx_sync`              | list | [`all_attributes_and_dependents`]         | [ ]      | Controls which attributes should be synchronized between VSX peers. |
| `state`                 | str  | [`create`, `delete`, `update`] / `create` | [ ]      | Create or update or delete the Queue.                               |

## aoscx_queue_profile_entry

This module implements creation, deletion, or update for a Queue Profile Entry

You can find additional information online about how Queue Profile Entries are
structured at the [Aruba Portal
](https://developer.arubanetworks.com/aruba-aoscx/reference#q_profile_entry)

| Parameter          | Type | Choices/Defaults | Required | Comments                                                                                                   |
|:-------------------|:-----|:-----------------|:--------:|:-----------------------------------------------------------------------------------------------------------|
| `queue_number`     | int  | [0-7]            | [x]      | Number to identify a Queue Profile.                                                                        |
| `description`      | str  |                  | [ ]      | Used for documentation of these queue configuration parameters.                                            |
| `local_priorities` | list | [0-7]            | [ ]      | Specifies one or more local-priority(ies) (int) assigned to this queue. If missing, the queue is not used. |

You can find an [example](#example) below.

---

# Examples:

Below you can find an example of an implementation of the modules above:

## Configure Quality of Service profiles and queues.

```YAML
  - name: Create Schedule Profile named 'High-Traffic'
    aoscx_qos:
      name: High-Traffic
      state: create
      vsx_sync:
        - all_attributes_and_dependents

  - name: Create Queue 5 for 'High-Traffic' Schedule Profile
    aoscx_queue:
      qos_name: High-Traffic
      queue: 5
      state: create
      algorithm: dwrr
      bandwidth: 1024
      burst: 1024
      weight: 127
      gmb_percent: 89

  - name: Remove the Guaranteed Minimum Bandwidth from queue 4
    aoscx_queue:
      qos_name: High-Traffic
      queue_number: 4
      no_gmb_percent: true

  - name: Set a Guaranteed Minimum Bandwidth of 45% for queue 2
    aoscx_queue:
      qos_name: High-Traffic
      queue_number: 2
      gmb_percent: 45
      algorithm: min-bandwidth

  - name: Delete Queue 3 for 'High-Traffic' Schedule Profile
    aoscx_queue:
      qos_name: High-Traffic
      queue_number: 3
      state: delete
```
## Update QoS Entries

```YAML
  - name: Update color and local priority for QoS COS with code point 5.
    aoscx_qos_cos:
      code_point: 5
      color: yellow
      local_priority: 3

  - name: Update color of QoS COS trust type map entry with code point 2
    aoscx_qos_cos:
      code_point: 2
      color: yellow

  - name: Update QoS DSCP trust type 5
    aoscx_qos_dscp:
      code_point: 5
      color: yellow
      local_priority: 3
```

## Configure a Queue Profile with entries

Create a new Queue Profile and a Queue Profile Entry

```YAML
  - name: Create a new Queue Profile called Strict-Profile
    aoscx_queue_profile:
      name: Strict-Profile
      state: create
      vsx_sync:
        - all_attributes_and_dependents

  - name: Create Queue Profile Entry 1
    aoscx_queue_profile_entry:
      queue_number: 1
      description: Low-Queue-Prof entry
      local_priorities:
        - 1
        - 2
        - 3
```

## Configure QoS in an Interface or Global Context

```YAML
  - name: Set Schedule Profile for 1/1/5 interface
    aoscx_interface:
      name: 1/1/5
      qos: High-Traffic
      qos_trust_mode: dscp
      queue_profile: Strict-Profile

  - name: Create Queue Profile 'STRICT-PROFILE'
    aoscx_queue_profile:
      name: STRICT-PROFILE
      state: create

  - name: Set Queue Profile 'STRICT-PROFILE' as global
    aoscx_system:
      global_queue_profile: STRICT-PROFILE

  - name: Set default global Queue Profile
    aoscx_system:
      use_default_global_queue_profile: true

  - name: Delete 'STRICT-PROFILE' Queue Profile
    aoscx_queue_profile:
      name: STRICT-PROFILE
      state: delete

  - name: Create a new Queue Profile called STRICT-PROFILE2
    aoscx_queue_profile:
      name: STRICT-PROFILE2
      state: create

  - name: Set global Queue Profile
    aoscx_system:
      global_queue_profile: STRICT-PROFILE2

  - name: Use the default global Queue Profile
    aoscx_system:
      use_default_global_queue_profile: true

  - name: Create Schedule Profile 'MEDIUM-TRAFFIC'
    aoscx_qos:
      name: MEDIUM-TRAFFIC
      state: create

  - name: Set Schedule Profile 'MEDIUM-TRAFFIC' as global
    aoscx_system:
      global_schedule_profile: MEDIUM-TRAFFIC

  - name: Delete 'MEDIUM-TRAFFIC' Schedule Profile
    aoscx_qos:
      name: MEDIUM-TRAFFIC
      state: delete

  - name: Use default global Schedule Profile
    aoscx_system:
      use_default_global_schedule_profile: true

  - name: Delete 'MEDIUM-TRAFFIC' Schedule Profile
    aoscx_qos:
      name: MEDIUM-TRAFFIC
      state: delete

  - name: Create Schedule Profile 'MEDIUM-TRAFFIC2'
    aoscx_qos:
      name: MEDIUM-TRAFFIC2
      state: create

  - name: Set global Schedule Profile
    aoscx_system:
      global_schedule_profile: MEDIUM-TRAFFIC2

  - name: Use the default global Schedule Profile
    aoscx_system:
      use_default_global_schedule_profile: true
```

## Delete a Queue Profile

Delete a Queue Profile 'STRICT-PROFILE', this is ignored while it is
set as global

```YAML
  - name: Delete 'STRICT-PROFILE' Queue Profile
    aoscx_queue_profile:
      name: STRICT-PROFILE
      state: delete
```
