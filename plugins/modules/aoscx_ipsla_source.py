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
module: aoscx_ipsla_source
version_added: "4.6.0"
short_description: Create, update or delete an IP SLA source
description: >
  This module provides configuration management of IP SLA sources on AOS-CX
  devices (system/ipsla_sources). An IP SLA source originates probes used to
  measure reachability, latency and jitter. IP SLA requires REST API version
  10.16 (set ansible_aoscx_rest_version to 10.16). The type and vrf are set
  when the source is created and cannot be changed afterwards.
author: Aruba Networks (@ArubaNetworks)
options:
  name:
    description: >
      Name of the IP SLA source. This is the index of the resource under
      system/ipsla_sources.
    required: true
    type: str
  vrf:
    description: >
      Name of the VRF the IP SLA source belongs to. Set on creation only.
    required: false
    default: default
    type: str
  type:
    description: >
      Probe type of the IP SLA source. Required when the source is created
      and cannot be changed afterwards.
    required: false
    type: str
    choices:
      - icmp_echo
      - udp_echo
      - tcp_connect
      - udp_jitter_voip
      - http
      - https
      - dns
      - dhcp
  enable:
    description: Enable or disable the IP SLA source.
    required: false
    type: bool
  frequency:
    description: >
      Interval in seconds between two consecutive probes (5-604800).
    required: false
    type: int
  history_interval:
    description: >
      Number of probes whose statistics are kept in the history (10-7200).
    required: false
    type: int
  ipsla_timeout:
    description: >
      Time in seconds to wait for a probe response (5-604800).
    required: false
    type: int
  payload_size:
    description: Probe payload size in bytes (0-1440).
    required: false
    type: int
  source_ip:
    description: Source IP address used by the probes.
    required: false
    type: str
  source_port_number:
    description: Source UDP/TCP port used by the probes (1-65535).
    required: false
    type: int
  tos:
    description: Type of Service value carried by the probes (0-255).
    required: false
    type: int
  domain_name_server:
    description: DNS server used to resolve the probe destination.
    required: false
    type: str
  source_interface:
    description: >
      Name of the interface (for example 1/1/1) the probes are sourced from.
    required: false
    type: str
  http_sla:
    description: >
      HTTP probe settings, applicable to the http probe type. Supported keys
      are cache_disable (bool), type (get or raw) and version_number (str).
      The supplied dictionary fully replaces the current settings.
    required: false
    type: dict
  https_sla:
    description: >
      HTTPS probe settings, applicable to the https probe type. Supported keys
      are cache_disable (bool), type (get or raw) and version_number (str).
      The supplied dictionary fully replaces the current settings.
    required: false
    type: dict
  voip_jitter_sla:
    description: >
      VoIP jitter probe settings, applicable to the udp_jitter_voip probe
      type. Supported keys are advantage_factor (int) and codec_type (str).
      The supplied dictionary fully replaces the current settings.
    required: false
    type: dict
  responder:
    description: >
      IP SLA responder address. Required for all probe types except http and
      https (which use a URL instead). Supported keys are hostname (the
      hostname, FQDN or IPv4/IPv6 address of the responder) and port (the
      transport layer port number; not needed for icmp_echo). The supplied
      dictionary fully replaces the current settings.
    required: false
    type: dict
  state:
    description: Create, update or delete the IP SLA source.
    required: false
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Create an ICMP echo IP SLA source
  aoscx_ipsla_source:
    name: probe-gw
    type: icmp_echo
    vrf: default
    frequency: 30
    tos: 8

- name: Update the probe frequency
  aoscx_ipsla_source:
    name: probe-gw
    state: update
    frequency: 60

- name: Create an HTTP IP SLA source from a given interface
  aoscx_ipsla_source:
    name: probe-web
    type: http
    vrf: default
    source_interface: 1/1/1
    http_sla:
      cache_disable: true
      type: get
      version_number: "1.1"

- name: Create a VoIP jitter IP SLA source
  aoscx_ipsla_source:
    name: probe-voip
    type: udp_jitter_voip
    vrf: default
    voip_jitter_sla:
      advantage_factor: 5
      codec_type: g729a

- name: Delete an IP SLA source
  aoscx_ipsla_source:
    name: probe-gw
    state: delete
"""

RETURN = r""" # """

from urllib.parse import quote

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
    get_pyaoscx_session,
)


def interface_uri(session, ansible_module, name):
    """Validate an interface exists and return its URI for a request body."""
    interface = session.api.get_module(session, "Interface", name)
    try:
        interface.get()
    except Exception:
        ansible_module.fail_json(
            msg="Could not find interface {0}".format(name)
        )
    return "{0}system/interfaces/{1}".format(
        session.resource_prefix, quote(name, safe="")
    )


def main():
    module_args = dict(
        name=dict(type="str", required=True),
        vrf=dict(type="str", required=False, default="default"),
        type=dict(
            type="str",
            required=False,
            default=None,
            choices=[
                "icmp_echo",
                "udp_echo",
                "tcp_connect",
                "udp_jitter_voip",
                "http",
                "https",
                "dns",
                "dhcp",
            ],
        ),
        enable=dict(type="bool", required=False, default=None),
        frequency=dict(type="int", required=False, default=None),
        history_interval=dict(type="int", required=False, default=None),
        ipsla_timeout=dict(type="int", required=False, default=None),
        payload_size=dict(type="int", required=False, default=None),
        source_ip=dict(type="str", required=False, default=None),
        source_port_number=dict(type="int", required=False, default=None),
        tos=dict(type="int", required=False, default=None),
        domain_name_server=dict(type="str", required=False, default=None),
        source_interface=dict(type="str", required=False, default=None),
        http_sla=dict(type="dict", required=False, default=None),
        https_sla=dict(type="dict", required=False, default=None),
        voip_jitter_sla=dict(type="dict", required=False, default=None),
        responder=dict(type="dict", required=False, default=None),
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

    name = ansible_module.params["name"]
    vrf_name = ansible_module.params["vrf"]
    state = ansible_module.params["state"]
    source_interface = ansible_module.params["source_interface"]

    scalar_attrs = [
        "type",
        "enable",
        "frequency",
        "history_interval",
        "ipsla_timeout",
        "payload_size",
        "source_ip",
        "source_port_number",
        "tos",
        "domain_name_server",
        "http_sla",
        "https_sla",
        "voip_jitter_sla",
        "responder",
    ]
    supplied = {
        attr: ansible_module.params[attr]
        for attr in scalar_attrs
        if ansible_module.params[attr] is not None
    }

    result = dict(changed=False)

    try:
        session = get_pyaoscx_session(ansible_module)
    except Exception as e:
        ansible_module.fail_json(
            msg="Could not get PYAOSCX Session: {0}".format(str(e))
        )

    try:
        source = session.api.get_module(session, "IpslaSource", name)
    except Exception as e:
        ansible_module.fail_json(
            msg=(
                "This pyaoscx version does not support IP SLA. "
                "Upgrade pyaoscx. Details: {0}".format(str(e))
            )
        )

    try:
        source.get(selector="writable")
        exists = True
    except Exception:
        exists = False

    # --------------------------------------------------------------- delete
    if state == "delete":
        if exists and not ansible_module.check_mode:
            try:
                source.delete()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not delete IP SLA source: {0}".format(str(e))
                )
        result["changed"] = exists
        ansible_module.exit_json(**result)

    # ------------------------------------------------------- create / update
    if not exists:
        if "type" not in supplied:
            ansible_module.fail_json(
                msg="type is required to create an IP SLA source"
            )
        vrf = session.api.get_module(session, "Vrf", vrf_name)
        try:
            vrf.get()
        except Exception:
            ansible_module.fail_json(
                msg="Could not find VRF, make sure it exists"
            )
        create_kwargs = dict(supplied)
        if source_interface is not None:
            create_kwargs["source_interface"] = interface_uri(
                session, ansible_module, source_interface
            )
        source = session.api.get_module(
            session, "IpslaSource", name, vrf=vrf, **create_kwargs
        )
        result["changed"] = True
        if not ansible_module.check_mode:
            try:
                source.create()
            except Exception as e:
                ansible_module.fail_json(
                    msg="Could not create IP SLA source: {0}".format(str(e))
                )
        ansible_module.exit_json(**result)

    changed = False
    for attr, value in supplied.items():
        # type is set at creation time and cannot be changed.
        if attr == "type":
            continue
        if getattr(source, attr, None) != value:
            changed = True
            setattr(source, attr, value)
            if attr not in source.config_attrs:
                source.config_attrs.append(attr)

    if source_interface is not None:
        desired_uri = interface_uri(session, ansible_module, source_interface)
        current = getattr(source, "source_interface", None)
        if isinstance(current, dict) and current:
            current_uri = list(current.values())[0]
        else:
            current_uri = None
        if current_uri != desired_uri:
            changed = True
            source.source_interface = desired_uri
            if "source_interface" not in source.config_attrs:
                source.config_attrs.append("source_interface")

    result["changed"] = changed
    if changed and not ansible_module.check_mode:
        try:
            source.update()
        except Exception as e:
            ansible_module.fail_json(
                msg="Could not update IP SLA source: {0}".format(str(e))
            )

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
