#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_stp
version_added: "4.6.0"
short_description: Manage Spanning Tree instance settings
description: >
  This module provides configuration management of Spanning Tree on AOS-CX
  devices: the global settings (system/stp_config, e.g. enable, mode, bridge
  priority, MSTP region name and revision) and the per-instance settings
  (system/stp_instances, e.g. timers and topology change traps).
author: Aruba Networks (@ArubaNetworks)
options:
  instance:
    description: Spanning Tree instance identifier (for example "mstp,0").
    required: false
    type: str
    default: "mstp,0"
  enable:
    description: >
      Global knob to enable or disable Spanning Tree on the device
      (the C(spanning-tree) global command).
    required: false
    type: bool
  mode:
    description: Global spanning tree mode.
    required: false
    type: str
    choices:
      - mstp
      - rpvst
  config_name:
    description: >
      MSTP region configuration name (the C(spanning-tree config-name)
      command). Global setting.
    required: false
    type: str
  config_revision:
    description: >
      MSTP region configuration revision number (the
      C(spanning-tree config-revision) command). Global setting.
    required: false
    type: int
  max_hop_count:
    description: >
      Global MSTP maximum hop count (the C(spanning-tree max-hops) command).
    required: false
    type: int
  tx_hold_count:
    description: >
      Global transmit hold count, limiting how many BPDUs are sent per hello
      interval (the C(spanning-tree transmit-hold-count) command).
    required: false
    type: int
  path_cost_type:
    description: >
      Global path cost calculation method (the C(spanning-tree cost) style).
    required: false
    type: str
    choices:
      - long
      - short
  bpdu_guard_timeout:
    description: >
      Global BPDU guard error-disable recovery timeout in seconds (0 keeps the
      port disabled until it is re-enabled manually).
    required: false
    type: int
  extended_system_id_disable:
    description: Disable the use of the extended system-id in the bridge id.
    required: false
    type: bool
  ignore_pvid_inconsistency:
    description: Ignore PVID inconsistency for RPVST.
    required: false
    type: bool
  qinq_pbridge_mode:
    description: Enable MSTP QinQ provider-bridge mode.
    required: false
    type: bool
  rpvst_auto_vlan:
    description: Enable RPVST automatic VLAN handling.
    required: false
    type: bool
  rpvst_auto_vlan_no_vport_limit:
    description: Disable the virtual-port limit for RPVST automatic VLANs.
    required: false
    type: bool
  rpvst_auto_vlan_priority:
    description: Priority applied to RPVST automatic VLANs.
    required: false
    type: int
  rpvst_mstp_interconnect_vlan:
    description: VLAN used to interconnect RPVST and MSTP regions.
    required: false
    type: int
  trap_errant_bpdu_rx:
    description: Enable the SNMP trap for received errant BPDUs.
    required: false
    type: bool
  trap_loop_guard_inconsistency:
    description: Enable the SNMP trap for loop-guard inconsistencies.
    required: false
    type: bool
  trap_new_root:
    description: Enable the SNMP trap sent when the device becomes root.
    required: false
    type: bool
  trap_root_guard_inconsistency:
    description: Enable the SNMP trap for root-guard inconsistencies.
    required: false
    type: bool
  priority:
    description: Bridge priority multiplier (0-15).
    required: false
    type: int
  hello_time:
    description: Hello time in seconds.
    required: false
    type: int
  forward_delay:
    description: Forward delay in seconds.
    required: false
    type: int
  max_age:
    description: Maximum age in seconds.
    required: false
    type: int
  topology_change_trap_enable:
    description: Enable topology change traps for this instance.
    required: false
    type: bool
  vlan_ids:
    description: >
      List of VLAN ids joined into this Spanning Tree (MSTP) instance. The
      supplied list fully replaces the current set of VLANs.
    required: false
    type: list
    elements: int
  ports:
    description: >
      Per-instance, per-port Spanning Tree settings. Ports must already exist.
    required: false
    type: list
    elements: dict
    suboptions:
      port:
        description: Interface name (for example 1/1/5).
        required: true
        type: str
      admin_path_cost:
        description: Administrative path cost for the port in this instance.
        required: false
        type: int
      port_priority:
        description: Port priority for the port in this instance.
        required: false
        type: int
  state:
    description: Update or delete the Spanning Tree instance.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Set a low bridge priority on the default instance
  aoscx_stp:
    instance: "mstp,0"
    priority: 4

- name: Tune STP timers
  aoscx_stp:
    instance: "mstp,0"
    hello_time: 2
    forward_delay: 15
    max_age: 20
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule

import json
from urllib.parse import quote

try:
    from pyaoscx.stp import Stp

    HAS_PYAOSCX_STP = True
except ImportError:
    HAS_PYAOSCX_STP = False

if HAS_PYAOSCX_STP:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )


def main():
    module_args = dict(
        instance=dict(type="str", required=False, default="mstp,0"),
        enable=dict(type="bool", required=False),
        mode=dict(
            type="str", required=False, choices=["mstp", "rpvst"]
        ),
        config_name=dict(type="str", required=False),
        config_revision=dict(type="int", required=False),
        max_hop_count=dict(type="int", required=False),
        tx_hold_count=dict(type="int", required=False),
        path_cost_type=dict(
            type="str", required=False, choices=["long", "short"]
        ),
        bpdu_guard_timeout=dict(type="int", required=False),
        extended_system_id_disable=dict(type="bool", required=False),
        ignore_pvid_inconsistency=dict(type="bool", required=False),
        qinq_pbridge_mode=dict(type="bool", required=False),
        rpvst_auto_vlan=dict(type="bool", required=False),
        rpvst_auto_vlan_no_vport_limit=dict(type="bool", required=False),
        rpvst_auto_vlan_priority=dict(type="int", required=False),
        rpvst_mstp_interconnect_vlan=dict(type="int", required=False),
        trap_errant_bpdu_rx=dict(type="bool", required=False),
        trap_loop_guard_inconsistency=dict(type="bool", required=False),
        trap_new_root=dict(type="bool", required=False),
        trap_root_guard_inconsistency=dict(type="bool", required=False),
        priority=dict(type="int", required=False),
        hello_time=dict(type="int", required=False),
        forward_delay=dict(type="int", required=False),
        max_age=dict(type="int", required=False),
        topology_change_trap_enable=dict(type="bool", required=False),
        vlan_ids=dict(type="list", elements="int", required=False),
        ports=dict(
            type="list",
            elements="dict",
            required=False,
            options=dict(
                port=dict(type="str", required=True),
                admin_path_cost=dict(type="int", required=False),
                port_priority=dict(type="int", required=False),
            ),
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )

    ansible_module = AnsibleModule(
        argument_spec=module_args, supports_check_mode=True
    )

    result = dict(changed=False)

    if not HAS_PYAOSCX_STP:
        ansible_module.fail_json(
            msg="This pyaoscx version does not support STP instances. "
            "Upgrade pyaoscx."
        )

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    instance = ansible_module.params["instance"]
    state = ansible_module.params["state"]

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    stp = Stp(session, instance)
    try:
        stp.get()
        exists = True
    except Exception:
        exists = False

    if state == "delete":
        if exists:
            stp.delete()
            result["changed"] = True
        ansible_module.exit_json(**result)

    vlan_ids = ansible_module.params["vlan_ids"]

    changed = not exists
    # The pyaoscx Stp class cannot create a new instance (it posts a
    # non-configurable "instance" key), so create it directly through REST
    # with its compound index parts.
    if not exists:
        if "," not in instance:
            ansible_module.fail_json(
                msg="instance must be '<type>,<id>', for example 'mstp,1'"
            )
        instance_type, _sep, stp_instance_id = instance.partition(",")
        body = {"instance_type": instance_type}
        try:
            body["stp_instance_id"] = int(stp_instance_id)
        except ValueError:
            body["stp_instance_id"] = stp_instance_id
        if vlan_ids is not None:
            body["vlan_ids"] = vlan_ids
        post = session.request(
            "POST", "system/stp_instances", data=json.dumps(body)
        )
        if not 200 <= post.status_code < 300:
            ansible_module.fail_json(
                msg="Could not create STP instance {0}: {1}".format(
                    instance, post.text
                )
            )
        stp = Stp(session, instance)
        stp.get()
        exists = True

    for field in (
        "priority",
        "hello_time",
        "forward_delay",
        "max_age",
        "topology_change_trap_enable",
    ):
        value = ansible_module.params[field]
        if value is None:
            continue
        if getattr(stp, field, None) != value:
            setattr(stp, field, value)
            if field not in stp.config_attrs:
                stp.config_attrs.append(field)
            changed = True

    if vlan_ids is not None:
        current_vlans = getattr(stp, "vlan_ids", None) or []
        if sorted(current_vlans) != sorted(vlan_ids):
            stp.vlan_ids = vlan_ids
            if "vlan_ids" not in stp.config_attrs:
                stp.config_attrs.append("vlan_ids")
            changed = True

    if changed:
        stp.apply()

    # Global Spanning Tree settings live in system/stp_config.
    global_map = {
        "enable": "stp_enable",
        "mode": "stp_mode",
        "config_name": "mstp_config_name",
        "config_revision": "mstp_config_revision",
        "max_hop_count": "max_hop_count",
        "tx_hold_count": "tx_hold_count",
        "path_cost_type": "path_cost_type",
        "bpdu_guard_timeout": "bpdu_guard_timeout",
        "extended_system_id_disable": "extended_sysid_disable",
        "ignore_pvid_inconsistency": "ignore_pvid_inconsistency_enable",
        "qinq_pbridge_mode": "mstp_qinq_pbridge_mode_enable",
        "rpvst_auto_vlan": "rpvst_auto_vlan_enable",
        "rpvst_auto_vlan_no_vport_limit": "rpvst_auto_vlan_no_vport_limit",
        "rpvst_auto_vlan_priority": "rpvst_auto_vlan_priority",
        "rpvst_mstp_interconnect_vlan": "rpvst_mstp_interconnect_vlan",
        "trap_errant_bpdu_rx": "stp_errant_bpdu_rx_trap_enable",
        "trap_loop_guard_inconsistency": (
            "stp_loop_guard_inconsistency_trap_enable"
        ),
        "trap_new_root": "stp_new_root_trap_enable",
        "trap_root_guard_inconsistency": (
            "stp_root_guard_inconsistency_trap_enable"
        ),
    }
    global_supplied = {
        attr: ansible_module.params[param]
        for param, attr in global_map.items()
        if ansible_module.params[param] is not None
    }
    if global_supplied:
        response = session.request(
            "GET", "system", params={"selector": "writable", "depth": 1}
        )
        system_doc = json.loads(response.text)
        stp_cfg = dict(system_doc.get("stp_config") or {})
        if any(stp_cfg.get(k) != v for k, v in global_supplied.items()):
            stp_cfg.update(global_supplied)
            system_doc["stp_config"] = stp_cfg
            put = session.request(
                "PUT", "system", data=json.dumps(system_doc)
            )
            if not 200 <= put.status_code < 300:
                ansible_module.fail_json(
                    msg="Could not update global STP config: {0}".format(
                        put.text
                    )
                )
            changed = True

    # Per-instance, per-port settings (system/stp_instances/.../
    # stp_instance_ports/{port}); these entries are PUT-only.
    ports = ansible_module.params["ports"]
    if ports:
        for entry in ports:
            supplied = {
                key: entry[key]
                for key in ("admin_path_cost", "port_priority")
                if entry.get(key) is not None
            }
            if not supplied:
                continue
            port_uri = "{0}/stp_instance_ports/{1}".format(
                stp.path, quote(entry["port"], safe="")
            )
            get_resp = session.request(
                "GET", port_uri,
                params={"selector": "writable", "depth": 1},
            )
            port_doc = json.loads(get_resp.text)
            if any(port_doc.get(k) != v for k, v in supplied.items()):
                port_doc.update(supplied)
                put = session.request(
                    "PUT", port_uri, data=json.dumps(port_doc)
                )
                if not 200 <= put.status_code < 300:
                    ansible_module.fail_json(
                        msg=(
                            "Could not update STP instance port {0}: "
                            "{1}".format(entry["port"], put.text)
                        )
                    )
                changed = True

    result["changed"] = changed

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
