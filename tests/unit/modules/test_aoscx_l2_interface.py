# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the spanning tree handling of the aoscx_l2_interface module.

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
    aoscx_l2_interface,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_l2_interface"
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


def build_interface(l2_changed=False, with_stp_method=True):
    attrs = [
        "configure_l2",
        "port_security_disable",
        "modified",
        "was_modified",
        "type",
    ]
    if with_stp_method:
        attrs.append("configure_spanning_tree")
    interface = MagicMock(spec=attrs)
    interface.modified = False
    interface.was_modified.return_value = False
    interface.type = "system"
    interface.configure_l2.return_value = l2_changed
    interface.port_security_disable.return_value = False
    if with_stp_method:
        interface.configure_spanning_tree.return_value = False
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
                    aoscx_l2_interface.main()
    return exc.value.args[0]


ACCESS_ARGS = {"interface": "1/1/2", "vlan_mode": "access", "vlan_access": 1}


def test_spanning_tree_not_configured_without_stp_options():
    interface = build_interface()
    result = run_module(ACCESS_ARGS, interface)
    assert result["changed"] is False
    interface.configure_spanning_tree.assert_not_called()


def test_layer2_change_is_not_overwritten_by_spanning_tree():
    interface = build_interface(l2_changed=True)
    result = run_module(
        dict(ACCESS_ARGS, stp_bpdu_guard_enable=True), interface
    )
    assert result["changed"] is True
    interface.configure_spanning_tree.assert_called_once()


def test_stp_options_with_unsupported_pyaoscx_report_error():
    interface = build_interface(with_stp_method=False)
    result = run_module(
        dict(ACCESS_ARGS, stp_bpdu_guard_enable=True), interface
    )
    assert result["failed"] is True
    assert "aoscx_interface_stp" in result["msg"]
