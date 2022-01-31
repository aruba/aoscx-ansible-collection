#!/usr/bin/python
# -*- coding: utf-8 -*-

# (C) Copyright 2019-2022 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule

try:
    from pyaoscx.device import Device

    HAS_PYAOSCX = True
except ImportError:
    HAS_PYAOSCX = False

if HAS_PYAOSCX:
    from ansible_collections.arubanetworks.aoscx.plugins.module_utils.aoscx_pyaoscx import (  # NOQA
        get_pyaoscx_session,
    )

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "certified",
}

DOCUMENTATION = """
---
module: aoscx_vsx
version_added: "2.8.0"
short_description: Create or Delete VSX configuration on AOS-CX.
description: >
  This modules provides configuration management of VSX on AOS-CX devices. Note
  that if you require to remove configuration, you'll need to delete the VSX
  configuration, and recreate it without the attributes you wish to remove.
author: Aruba Networks (@ArubaNetworks)
options:
  system_mac:
    description: >
      System MAC address to be used by L2 control plane protocols like STP and
      LACP as their Bridge Identifier. A pair of VSX switches must have the
      same system MAC. If system_mac is not configured, L2 control plane
      protocols will use the VSX Primary device MAC address as their Bridge
      Identifier. MAC address must be in xx:xx:xx:xx:xx:xx format.
    type: str
    required: false
  keepalive_vrf:
    description: >
      VRF to be used for keepalive routing. If not configured, keepalive
      functionality is disabled.
    type: str
    required: false
  software_update_url:
    description: >
      URL for downloading software from a connected storage device or a remote
      host. TFTP and USB are the only download methods supported.
    type: str
    required: false
  keepalive_src_ip:
    description: >
      IPv4 address of the device. If not configured, keepalive functionality is
      disabled. MUST be together with keepalive_peer_ip.
    type: str
    required: false
  linkup_delay_timer:
    description: >
      Number of seconds that multi-chassis LAGs should be held down after the
      ISL is considered to be fully established and VSX switches are
      synchronized.
    type: int
    required: false
  software_update_vrf:
    description: >
      VRF that is used for downloading the image. If the VRF is not specified
      then the default VRF is used.
    type: str
    required: false
  isl_port:
    description: Port to be used as inter switch link.
    type: str
    required: false
  keepalive_udp_port:
    description: UDP port number of peer device.
    type: int
    required: false
  device_role:
    description: >
      Specifies whether the device will act as primary or secondary for vsx
      operation requires a switch to be primary and another to be
      secondary.
    type: str
    choices:
      - primary
      - secondary
    required: false
  isl_timers:
    description: Timing configuration for ISL functionality.
    type: dict
    timeout:
      description: Seconds to wait for hellos from peer.
      type: int
      required: true
    peer_detect_interval:
      description: >
        Configures the amount of time in seconds that the device waits for ISL
        interface to link up after a reboot. If the ISL link does not come up
        within this time window, the device declares itself as split from its
        peer.
      type: int
      required: true
    hold_time:
      description: Configures ISL port-flap hold time in seconds.
      type: int
      required: true
    hello_interval:
      description: ISLP hello interval in seconds.
      type: int
      required: true
  config_sync_features:
    description: >
      Feature configurations to be globally synchronized between VSX peers.
    type: list
    choices:
      - aaa
      - acl-log-timer
      - arp-security
      - bfd-global
      - bgp
      - control-plane-acls
      - copp-policy
      - dhcp-server
      - dns
      - dhcp-relay
      - dhcp-snooping
      - hardware-high-capacity-tcam
      - evpn
      - icmp-tcp
      - gbp
      - lldp
      - loop-protect-global
      - keychain
      - mac-lockout
      - mclag-interfaces
      - mgmd-global
      - macsec
      - neighbor
      - ospf
      - qos-global
      - nd-snooping
      - route-map
      - sflow-global
      - snmp
      - ssh
      - static-routes
      - stp-global
      - rip
      - time
      - vsx-global
      - udp-forwarder
      - vrrp
    required: false
  keepalive_timers:
    description: Timing configuration for keepalive functionality.
    required: false
    type: dict
    hello_interval:
      description: Keepalive hello interval in seconds.
      type: int
      required: true
    dead_interval:
      description: >
        Configures the amount of time in seconds to wait for keepalive packets
        from a peer.
      type: int
      required: true
  keepalive_peer_ip:
    description: >
      IPv4 address of the peer device. If not configured, keepalive
      functionality is disabled. MUST be together with keepalive_src_ip.
    type: str
    required: false
  config_sync_disable:
    description: >
      Specifies whether VSX configuration synchronization is enabled or not.
    type: bool
    required: false
  split_recovery_disable:
    description: Disables split brain recovery.
    type: bool
    required: false
  software_update_abort_request:
    description: >
      Number of times a software update process was requested to be aborted.
      The abort operation takes effect only when the update operation is in
      progress.
    type: int
    required: false
  software_update_schedule_time:
    description: >
      Time (in seconds from epoch) when the update should be performed.  When
      the software update parameters (URL, VRF, schedule_time[optional] are
      added/updated, the new image is downloaded to alternate bank of both,
      primary and secondary. Post download, the secondary is rebooted and then
      followed by the primary.
    type: int
    required: false
  state:
    description: Create or delete VSX configuration.
    required: true
    choices:
      - create
      - update
      - delete
    default: create
    type: str
"""

EXAMPLES = """
- name: Delete VSX configuration
  aoscx_vsx:
    state: delete
- name: Update VSX configuration for primary device, set ISL port
  aoscx_vsx:
    device_role: primary
    isl_port: 1/1/1
    state: update
- name: >
    Create simple VSX configuration with lag as ISL port for secondary device
  aoscx_vsx:
    device_role: secondary
    isl_port: lag1
    keepalive_vrf: red
    state: create
- name: Create detailed VSX configuration
  aoscx_vsx:
    config_sync_disable: false
    config_sync_features:
      - aaa
      - bgp
      - dns
      - vrrp
    device_role: primary
    isl_port: 1/1/8
    isl_timers:
      timeout: 20
      peer_detect_interval: 100
      hold_time: 3
      hello_interval: 5
    keepalive_peer_ip: 10.0.0.2
    keepalive_src_ip:  10.0.0.1
    keepalive_timers:
      hello_interval: 5
      dead_interval: 20
    keepalive_udp_port: 7678
    keepalive_vrf: default
    linkup_delay_timer: 90
    software_update_abort_request: 7
    software_update_schedule_time: 1635356306
    software_update_url: usb://boot_bank=primary
    software_update_vrf: default
    split_recovery_disable: false
    system_mac: 00:FF:11:EE:22:DD
"""

RETURN = r""" # """


def get_argument_spec():
    module_args = {
        "state": {
            "type": "str",
            "required": False,
            "default": "create",
            "choices": ["create", "update", "delete"],
        },
        "config_sync_disable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "config_sync_features": {
            "type": "list",
            "required": False,
            "default": None,
            "choices": [
                "aaa",
                "acl-log-timer",
                "arp-security",
                "bfd-global",
                "bgp",
                "control-plane-acls",
                "copp-policy",
                "dhcp-server",
                "dns",
                "dhcp-relay",
                "dhcp-snooping",
                "hardware-high-capacity-tcam",
                "evpn",
                "icmp-tcp",
                "gbp",
                "lldp",
                "loop-protect-global",
                "keychain",
                "mac-lockout",
                "mclag-interfaces",
                "mgmd-global",
                "macsec",
                "neighbor",
                "ospf",
                "qos-global",
                "nd-snooping",
                "route-map",
                "sflow-global",
                "snmp",
                "ssh",
                "static-routes",
                "stp-global",
                "rip",
                "time",
                "vsx-global",
                "udp-forwarder",
                "vrrp",
            ],
        },
        "device_role": {
            "type": "str",
            "required": False,
            "default": "primary",
            "choices": ["primary", "secondary"],
        },
        "isl_port": {"type": "str", "required": False, "default": None},
        "isl_timers": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "timeout": {
                    "type": "int",
                    "required": True,
                },
                "peer_detect_interval": {
                    "type": "int",
                    "required": True,
                },
                "hold_time": {
                    "type": "int",
                    "required": True,
                },
                "hello_interval": {
                    "type": "int",
                    "required": True,
                },
            },
        },
        "keepalive_peer_ip": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "keepalive_src_ip": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "keepalive_timers": {
            "type": "dict",
            "required": False,
            "default": None,
            "options": {
                "hello_interval": {
                    "type": "int",
                    "required": True,
                },
                "dead_interval": {"type": "int", "required": True},
            },
        },
        "keepalive_udp_port": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "keepalive_vrf": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "linkup_delay_timer": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "software_update_abort_request": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "software_update_schedule_time": {
            "type": "int",
            "required": False,
            "default": None,
        },
        "software_update_url": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "software_update_vrf": {
            "type": "str",
            "required": False,
            "default": None,
        },
        "split_recovery_disable": {
            "type": "bool",
            "required": False,
            "default": None,
        },
        "system_mac": {"type": "str", "required": False, "default": None},
    }
    return module_args


def main():
    ansible_module = AnsibleModule(
        argument_spec=get_argument_spec(),
        supports_check_mode=True,
        required_together=[("keepalive_src_ip", "keepalive_peer_ip")],
    )

    result = dict(changed=False)

    if ansible_module.check_mode:
        ansible_module.exit_json(**result)

    if not HAS_PYAOSCX:
        ansible_module.fail_json(
            msg="Could not find the PYAOSCX SDK. Make sure it is installed."
        )

    params = ansible_module.params.copy()
    state = params.pop("state")

    # NOTE: remove all values that are unspecified in playbook
    vsx_kw = {k: v for k, v in params.items() if v is not None}

    session = get_pyaoscx_session(ansible_module)

    # Get Pyaoscx device to handle switch configuration
    device = Device(session)

    vsx = device.vsx(**vsx_kw)
    result["changed"] = vsx.modified

    if state == "delete":
        vsx.delete()
        result["changed"] = not result["changed"]

    ansible_module.exit_json(**result)


if __name__ == "__main__":
    main()
