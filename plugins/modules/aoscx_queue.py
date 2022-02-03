#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_queue
version_added: "4.0.0"
short_description: Create, Update or Delete a Queue on AOS-CX devices.
description: >
  This module provides configuration management of Queues on AOS-CX devices.
author: Aruba Networks (@ArubaNetworks)
options:
  qos_name:
    description: Name to identify a QoS configuration.
    required: true
    type: str
  queue_number:
    description: Number to identify a Queue.
    required: true
    type: int
  state:
    description: Create, update or delete the Queue.
    required: false
    type: str
    choices:
      - create
      - update
      - delete
    default: create
  algorithm:
    description: >
      Scheduling behavior of the queue, strict will service packets in queue
      before packets in lower numbered queues, dwrr, or Deficit Weighted Round
      Robin will apportion available bandwidth among all non-empty dwrr queues
      in relation to their weight, wfq, or Weighted Fair Queueing will
      apportion available bandwidth among all non-empty wfq queues in relation
      to their weight.
    required: false
    choices:
      - dwrr
      - strict
      - wfq
      - min-bandwidth
    default: strict
    type: str
  bandwidth:
    description: >
      Bandwidth limit in kilobits per second to apply to egress traffic, if not
      specified, bandwidth is not limited per queue.
    required: false
    type: int
  gmb_percent:
    description: >
      The Guaranteed Minimum Bandwidth as a percentage of line rate. This
      option is mutually exclusive with the no_gmb_percent option.
    required: false
    type: int
    default: None
  no_gmb_percent:
    description: >
      Option to remove the Guaranteed Minimum Bandwidth. This option is
      mutually exclusive with the gmb_percent option.
    required: false
    type: bool
    default: false
  burst:
    description: >
      burst size in kilobytes allowed per bandwidth-queue, if not specified the
      default 32KB will be applied.
    required: false
    type: int
  weight:
    description: >
      Weight value for a queue. Maximum number is hardware dependent.
    required: false
    type: int
"""

EXAMPLES = """
---
- name: Create Queue 5 in 'High-Traffic' Schedule Profile
  aoscx_queue:
    qos_name: High-Traffic
    queue_number: 5

- name: Delete Queue 3 in 'High-Traffic' Schedule Profile
  aoscx_queue:
    qos_name: High-Traffic
    queue_number: 3
    state: delete

- name: Create queue 1 in 'High-Traffic' Schedule Profile
  aoscx_queue:
    qos_name: High-Traffic
    queue_number: 1
    algorithm: "dwrr"
    bandwidth: 1024
    burst: 1024
    weight: 127

- name: Set a Guaranteed Minimum Bandwidth of 46 percent for the queue 1
  aoscx_queue:
    qos_name: VOIP_Profile
    queue_number: 1
    gmb_percent: 46

- name: Remove the Guaranteed Minimum Bandwidth from the queue 4
  aoscx_queue:
    qos_name: VOIP_Profile
    queue_number: 4
    no_gmb_percent: true
"""

RETURN = r""" # """


try:
    from pyaoscx.queue import Queue
except ImportError as imp:
    raise ImportError(
        "Unable to find the PYAOSCX SDK. Make sure it is installed correctly."
    ) from imp

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx import (  # NOQA
    aoscx_http_argument_spec,
)


def get_argument_spec():
    argument_spec = {
        "qos_name": {
            "type": "str",
            "required": True,
        },
        "queue_number": {
            "type": "int",
            "required": True,
        },
        "algorithm": {
            "type": "str",
            "required": False,
            "choices": ["strict", "dwrr", "wfq", "min-bandwidth"],
            "default": "strict",
        },
        "bandwidth": {
            "type": "int",
            "required": False,
        },
        "gmb_percent": {
            "type": "int",
            "required": False,
            "default" : None,
        },
        "no_gmb_percent": {
            "type": "bool",
            "required": False,
            "default": False,
        },
        "burst": {
            "type": "int",
            "required": False,
        },
        "weight": {
            "type": "int",
            "required": False,
        },
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
    }
    argument_spec.update(aoscx_http_argument_spec)
    return argument_spec


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        mutually_exclusive=[
          ("gmb_percent", "no_gmb_percent")
        ],
        required_if=[
          ("algorithm", "min-bandwidth", ("gmb_percent",))
        ],
    )

    result = dict(
        changed=False
    )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    session = get_pyaoscx_session(ansible_module)

    # Get playbook's arguments
    qos_name = ansible_module.params["qos_name"]
    queue_number = ansible_module.params["queue_number"]
    state = ansible_module.params["state"]
    algorithm = ansible_module.params["algorithm"]
    bandwidth = ansible_module.params["bandwidth"]
    burst = ansible_module.params["burst"]
    weight = ansible_module.params["weight"]
    gmb_percent = ansible_module.params["gmb_percent"]
    no_gmb_percent = ansible_module.params["no_gmb_percent"]

    kwargs = {}
    if algorithm:
        kwargs["algorithm"] = algorithm
    if bandwidth:
        if bandwidth < 1:
            ansible_module.fail_json(msg="Bandwidth must be at least 1")
        kwargs["bandwidth"] = bandwidth
    if burst:
        if burst < 1:
            ansible_module.fail_json(msg="Burst must be at least 1")
        kwargs["burst"] = burst
    if weight:
        if weight < 1:
            ansible_module.fail_json(msg="Weight must be at least 1")
        kwargs["weight"] = weight
    if gmb_percent:
        if gmb_percent < 0 or gmb_percent > 100:
            ansible_module.fail_json(
                msg="gmb_percent must be an integer in the [0, 100] "
                "interval, that is, an integer no lower than 0, and no "
                "higher than 100"
            )
        kwargs["gmb_percent"] = int(gmb_percent)
    if no_gmb_percent:
        kwargs["gmb_percent"] = None

    queue = Queue(session, qos_name, queue_number)
    try:
        queue.get()
        present = True
    except Exception as exc:
        present = False

    if state == "delete":
        if present:
            queue.delete()
        result["changed"] = present
    else:
        if present:
            for k, v in kwargs.items():
                setattr(queue, k, v)
            queue.apply()
            result["changed"] = queue.was_modified()
        else:
            queue = Queue(session, qos_name, queue_number, **kwargs)
            queue.create()
            result["changed"] = True
    # Exit
    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
