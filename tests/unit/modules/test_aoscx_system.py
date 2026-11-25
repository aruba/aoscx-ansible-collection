# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the virtual_mac, gbp_enable, internal_vlan_range and
interface_groups options of the aoscx_system module.

The pyaoscx session and Device are fully mocked, so no switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from pyaoscx.exceptions.parameter_error import ParameterError
from pyaoscx.exceptions.unsupported_capability_error import (
    UnsupportedCapabilityError,
)
from ansible.module_utils.common.text.converters import to_bytes

try:
    from ansible.module_utils.testing import patch_module_args
except ImportError:  # ansible-core < 2.19
    patch_module_args = None

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_system,
)

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_system"


class AnsibleExitJson(Exception):
    """Raised by the mocked exit_json to stop module execution."""


class AnsibleFailJson(Exception):
    """Raised by the mocked fail_json to stop module execution."""


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


def run_module(args, changed=True, device=None):
    if patch_module_args is None:
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({"ANSIBLE_MODULE_ARGS": args})
        )
        args_context = nullcontext()
    else:
        args_context = patch_module_args(args)
    if device is None:
        device = MagicMock()
        device.set_virtual_mac.return_value = changed
        device.set_gbp_enable.return_value = changed
        device.set_internal_vlan_range.return_value = changed
        device.delete_internal_vlan_range.return_value = changed
        device.set_interface_group_speed.return_value = changed
    with args_context:
        with patch(MODULE + ".get_pyaoscx_session", return_value=MagicMock()):
            with patch(MODULE + ".Device", return_value=device):
                with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
                    aoscx_system.main()
    return exc.value.args[0], device


def test_set_virtual_mac():
    result, device = run_module({"virtual_mac": "02:00:00:00:00:01"})
    assert result["changed"] is True
    device.set_virtual_mac.assert_called_once_with("02:00:00:00:00:01")


def test_set_virtual_mac_unchanged():
    result, _ = run_module({"virtual_mac": "02:00:00:00:00:01"}, changed=False)
    assert result["changed"] is False


def test_remove_virtual_mac():
    result, device = run_module({"use_default_virtual_mac": True})
    assert result["changed"] is True
    device.set_virtual_mac.assert_called_once_with(None)


def test_invalid_virtual_mac_rejected():
    result, device = run_module({"virtual_mac": "0200.0000.0001"})
    assert result["failed"] is True
    assert "xx:xx:xx:xx:xx:xx" in result["msg"]
    device.set_virtual_mac.assert_not_called()


def test_virtual_mac_options_are_mutually_exclusive():
    result, _ = run_module(
        {"virtual_mac": "02:00:00:00:00:01", "use_default_virtual_mac": True}
    )
    assert result["failed"] is True


@pytest.mark.parametrize("enable", [True, False])
def test_set_gbp_enable(enable):
    result, device = run_module({"gbp_enable": enable})
    assert result["changed"] is True
    device.set_gbp_enable.assert_called_once_with(enable)


def test_gbp_enable_unchanged():
    result, _ = run_module({"gbp_enable": True}, changed=False)
    assert result["changed"] is False


def test_gbp_enable_omitted_is_not_applied():
    _, device = run_module({"virtual_mac": "02:00:00:00:00:01"})
    device.set_gbp_enable.assert_not_called()


def test_gbp_enable_unsupported_pyaoscx_reports_error():
    device = MagicMock(spec=["set_virtual_mac"])
    result, _ = run_module({"gbp_enable": True}, device=device)
    assert result["failed"] is True
    assert "Upgrade pyaoscx" in result["msg"]


def test_set_internal_vlan_range():
    result, device = run_module(
        {"internal_vlan_range": {"start": 3000, "end": 3999}}
    )
    assert result["changed"] is True
    device.set_internal_vlan_range.assert_called_once_with(3000, 3999)


def test_internal_vlan_range_unchanged():
    result, _ = run_module(
        {"internal_vlan_range": {"start": 3000, "end": 3999}}, changed=False
    )
    assert result["changed"] is False


def test_internal_vlan_range_unsupported_platform_fails():
    device = MagicMock()
    device.set_internal_vlan_range.side_effect = UnsupportedCapabilityError(
        "The internal VLAN range is not supported on this platform"
    )
    result, _ = run_module(
        {"internal_vlan_range": {"start": 3000, "end": 3999}}, device=device
    )
    assert result["failed"] is True
    assert "internal VLAN range" in result["msg"]


def test_internal_vlan_range_unsupported_pyaoscx_reports_error():
    device = MagicMock(spec=["set_virtual_mac"])
    result, _ = run_module(
        {"internal_vlan_range": {"start": 3000, "end": 3999}}, device=device
    )
    assert result["failed"] is True
    assert "Upgrade pyaoscx" in result["msg"]


def test_remove_internal_vlan_range():
    result, device = run_module({"use_default_internal_vlan_range": True})
    assert result["changed"] is True
    device.delete_internal_vlan_range.assert_called_once_with()


def test_remove_internal_vlan_range_refused_fails():
    device = MagicMock()
    device.delete_internal_vlan_range.side_effect = ParameterError(
        "routing is enabled on: 1/1/23"
    )
    result, _ = run_module(
        {"use_default_internal_vlan_range": True}, device=device
    )
    assert result["failed"] is True
    assert "1/1/23" in result["msg"]


def test_internal_vlan_range_options_are_mutually_exclusive():
    result, _ = run_module(
        {
            "internal_vlan_range": {"start": 3000, "end": 3999},
            "use_default_internal_vlan_range": True,
        }
    )
    assert result["failed"] is True


def test_set_interface_groups():
    result, device = run_module(
        {
            "interface_groups": [
                {"group": 1, "speed": "10g"},
                {"group": 2, "speed": "default", "line_module": "1/3"},
            ]
        }
    )
    assert result["changed"] is True
    assert device.set_interface_group_speed.call_args_list == [
        ((1, "10g"), {"line_module": None}),
        ((2, None), {"line_module": "1/3"}),
    ]


def test_interface_groups_unchanged():
    result, _ = run_module(
        {"interface_groups": [{"group": 1, "speed": "10g"}]}, changed=False
    )
    assert result["changed"] is False


def test_interface_groups_invalid_speed_fails():
    device = MagicMock()
    device.set_interface_group_speed.side_effect = ParameterError(
        "Invalid speed 40g for interface group 1"
    )
    result, _ = run_module(
        {"interface_groups": [{"group": 1, "speed": "40g"}]}, device=device
    )
    assert result["failed"] is True
    assert "interface group 1" in result["msg"]
