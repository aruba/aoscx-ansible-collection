# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the IP unnumbered handling of the aoscx_l3_interface module.

The pyaoscx Device and Interface are fully mocked, so no switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

try:
    from ansible.module_utils.testing import patch_module_args
except ImportError:  # ansible-core < 2.19
    patch_module_args = None

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_l3_interface,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_l3_interface"
)


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def exit_json(*args, **kwargs):
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


@pytest.fixture(autouse=True)
def patch_ansible_module():
    with patch.multiple(
        basic.AnsibleModule,
        exit_json=exit_json,
        fail_json=fail_json,
    ):
        yield


def build_interface(
    ip_unnumbered=None, ip4_address=None, vrf="default", with_method=True
):
    attrs = [
        "configure_l3",
        "modified",
        "was_modified",
        "type",
        "vrf",
        "ip4_address",
        "ip4_address_secondary",
        "ip6_addresses",
    ]
    if with_method:
        attrs += ["set_ip_unnumbered", "ip_unnumbered"]
    interface = MagicMock(spec=attrs)
    interface.modified = False
    interface.was_modified.return_value = False
    interface.type = "system"
    interface.vrf = MagicMock()
    interface.vrf.name = vrf
    interface.ip4_address = ip4_address
    interface.ip4_address_secondary = []
    interface.ip6_addresses = []
    if with_method:
        interface.ip_unnumbered = ip_unnumbered
    interface.configure_l3.return_value = False
    return interface


def run_module(args, interface):
    if patch_module_args is None:
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({"ANSIBLE_MODULE_ARGS": args})
        )
        args_context = nullcontext()
    else:
        args_context = patch_module_args(args)
    device = MagicMock()
    device.interface.return_value = interface
    with args_context:
        with patch(MODULE + ".get_pyaoscx_session", return_value=MagicMock()):
            with patch("pyaoscx.device.Device", return_value=device):
                with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
                    aoscx_l3_interface.main()
    return exc.value.args[0]


def l3_kwargs(interface):
    return interface.configure_l3.call_args.kwargs


def test_set_ip_unnumbered():
    interface = build_interface()
    result = run_module(
        {"interface": "1/1/25", "ip_unnumbered": "loopback0"}, interface
    )
    assert result["changed"] is True
    assert l3_kwargs(interface)["ip_unnumbered"] == "loopback0"


def test_same_ip_unnumbered_not_changed():
    interface = build_interface(ip_unnumbered="loopback0")
    result = run_module(
        {"interface": "1/1/25", "ip_unnumbered": "loopback0"}, interface
    )
    assert result["changed"] is False


def test_ip_unnumbered_omitted_left_unchanged():
    interface = build_interface(ip_unnumbered="loopback0")
    result = run_module(
        {"interface": "1/1/25", "description": "p2p"}, interface
    )
    assert result["changed"] is False
    assert "ip_unnumbered" not in l3_kwargs(interface)


def test_delete_configured_ip_unnumbered():
    interface = build_interface(ip_unnumbered="loopback0")
    result = run_module(
        {
            "interface": "1/1/25",
            "ip_unnumbered": "loopback0",
            "state": "delete",
        },
        interface,
    )
    assert result["changed"] is True
    assert l3_kwargs(interface)["ip_unnumbered"] == ""


def test_delete_other_ip_unnumbered_not_changed():
    interface = build_interface(ip_unnumbered="loopback0")
    result = run_module(
        {
            "interface": "1/1/25",
            "ip_unnumbered": "loopback1",
            "state": "delete",
        },
        interface,
    )
    assert result["changed"] is False
    assert "ip_unnumbered" not in l3_kwargs(interface)


def test_vrf_change_removes_ip_unnumbered():
    interface = build_interface(ip_unnumbered="loopback0")
    result = run_module({"interface": "1/1/25", "vrf": "red"}, interface)
    assert result["changed"] is True
    assert l3_kwargs(interface)["ip_unnumbered"] == ""


def test_ipv4_and_ip_unnumbered_mutually_exclusive():
    interface = build_interface()
    result = run_module(
        {
            "interface": "1/1/25",
            "ipv4": ["192.0.2.1/31"],
            "ip_unnumbered": "loopback0",
        },
        interface,
    )
    assert result["failed"] is True
    assert "mutually exclusive" in result["msg"]


def test_warn_when_static_ipv4_configured():
    interface = build_interface(ip4_address="192.0.2.1/31")
    with patch.object(basic.AnsibleModule, "warn") as warn:
        run_module(
            {"interface": "1/1/25", "ip_unnumbered": "loopback0"}, interface
        )
    warn.assert_called_once()


def test_pyaoscx_error_reported():
    interface = build_interface()
    interface.configure_l3.side_effect = Exception("not in the same VRF")
    result = run_module(
        {"interface": "1/1/25", "ip_unnumbered": "loopback0"}, interface
    )
    assert result["failed"] is True
    assert "same VRF" in result["msg"]


def test_unsupported_pyaoscx_reports_error():
    interface = build_interface(with_method=False)
    result = run_module(
        {"interface": "1/1/25", "ip_unnumbered": "loopback0"}, interface
    )
    assert result["failed"] is True
    assert "set_ip_unnumbered" in result["msg"]
