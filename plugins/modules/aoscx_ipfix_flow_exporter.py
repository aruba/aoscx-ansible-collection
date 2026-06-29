#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
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
module: aoscx_ipfix_flow_exporter
version_added: "4.6.0"
short_description: Create, update or delete an IPFIX flow exporter on AOS-CX
description: >
  This module provides configuration management of IPFIX flow exporters on
  AOS-CX devices. A flow exporter defines the destination to which IPFIX flow
  data is exported, either a collector reachable by hostname or IP address
  through a VRF, or a local Traffic Insight instance. IPFIX requires REST API
  version 10.13 or later (set ansible_aoscx_rest_version to 10.13).
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the flow exporter. This is the index of the resource under
      system/ipfix_flow_exporters.
    required: true
    type: str
  description:
    description: Free form description of the flow exporter.
    required: false
    type: str
  destination_type:
    description: >
      Type of the export destination. Use hostname-or-ip-addr to export to a
      collector, or traffic-insight to export to a local Traffic Insight
      instance.
    required: false
    choices:
      - hostname-or-ip-addr
      - traffic-insight
    type: str
  destination:
    description: >
      Hostname or IP address of the collector. Used when destination_type is
      hostname-or-ip-addr.
    required: false
    type: str
  vrf:
    description: >
      Name of the VRF used to reach the collector. Used together with
      destination.
    required: false
    default: default
    type: str
  traffic_insight:
    description: >
      Name of the Traffic Insight instance to export to. Used when
      destination_type is traffic-insight.
    required: false
    type: str
  template_data_timeout:
    description: >
      Interval, in seconds, between transmissions of the IPFIX template and
      options data (0-86400).
    required: false
    type: int
  transport_port:
    description: >
      UDP destination port used to export flow data (1-65535).
    required: false
    type: int
  transport_protocol:
    description: Transport protocol used to export flow data.
    required: false
    default: udp
    choices:
      - udp
    type: str
  state:
    description: Create, update or delete the flow exporter.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an IPFIX flow exporter to a collector
  aoscx_ipfix_flow_exporter:
    name: collector-1
    description: Export to collector 1
    destination_type: hostname-or-ip-addr
    destination: 10.0.0.5
    vrf: default
    transport_port: 4739
    template_data_timeout: 600

- name: Create an IPFIX flow exporter to a Traffic Insight instance
  aoscx_ipfix_flow_exporter:
    name: ti-exporter
    destination_type: traffic-insight
    traffic_insight: TI-01

- name: Delete a flow exporter
  aoscx_ipfix_flow_exporter:
    name: collector-1
    state: delete
"""

RETURN = r""" # """

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        description=dict(type="str", required=False, default=None),
        destination_type=dict(
            type="str",
            required=False,
            default=None,
            choices=["hostname-or-ip-addr", "traffic-insight"],
        ),
        destination=dict(type="str", required=False, default=None),
        vrf=dict(type="str", required=False, default="default"),
        traffic_insight=dict(type="str", required=False, default=None),
        template_data_timeout=dict(type="int", required=False, default=None),
        transport_port=dict(type="int", required=False, default=None),
        transport_protocol=dict(
            type="str", required=False, default="udp", choices=["udp"]
        ),
        state=dict(
            type="str",
            default="create",
            choices=["create", "update", "delete"],
        ),
    )
    ansible_module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    params = ansible_module.params
    name = params["name"]
    state = params["state"]

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    # Build the supplied attribute set from the user-friendly parameters.
    supplied = {}
    if params["description"] is not None:
        supplied["description"] = params["description"]
    if params["destination_type"] is not None:
        supplied["destination_type"] = params["destination_type"]
    if params["destination"] is not None:
        vrf_uri = "{0}system/vrfs/{1}".format(
            session.resource_prefix, params["vrf"]
        )
        supplied["destination_hostname_or_ip_addr"] = {
            params["destination"]: vrf_uri
        }
    if params["traffic_insight"] is not None:
        supplied["destination_traffic_insight"] = params["traffic_insight"]
    if params["template_data_timeout"] is not None:
        supplied["template_data_timeout"] = params["template_data_timeout"]
    if params["transport_port"] is not None:
        supplied["transport"] = {
            "port": params["transport_port"],
            "protocol": params["transport_protocol"],
        }

    try:
        exporter = session.api.get_module(session, "IpfixFlowExporter", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support IPFIX. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        exporter.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                exporter.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete flow exporter: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        exporter = session.api.get_module(
            session, "IpfixFlowExporter", name, **supplied
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                exporter.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create flow exporter: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        if getattr(exporter, attr, None) != value:
            changed = True
            setattr(exporter, attr, value)
            if attr not in exporter.config_attrs:
                exporter.config_attrs.append(attr)

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            exporter.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update flow exporter: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
