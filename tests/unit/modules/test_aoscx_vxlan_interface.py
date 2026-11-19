# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_vxlan_interface module.

The pyaoscx session is fully mocked, so no switch is required. The tests cover
input validation, check mode, idempotency, create, update, delete and error
handling.

Run with:
    .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_vxlan_interface.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_vxlan_interface,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_vxlan_interface"
)


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


def set_module_args(args):
    serialized = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(serialized)


@pytest.fixture(autouse=True)
def patch_ansible_module():
    with patch.multiple(
        basic.AnsibleModule,
        exit_json=exit_json,
        fail_json=fail_json,
    ):
        yield


def build_interface(exists, interface_type="vxlan", apply_changed=False):
    interface = MagicMock()
    interface.type = interface_type
    interface.options = {}
    interface.apply.return_value = apply_changed
    if exists:
        interface.get.return_value = True
    else:
        interface.get.side_effect = Exception("not found")
    return interface


def build_session(interface):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if module == "Interface":
            return interface
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_vxlan_interface.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_name_rejected():
    session = build_session(build_interface(False))
    result = run_module({"name": "vxlan1,extra"}, session)
    assert result["failed"] is True
    assert "Invalid VXLAN interface name" in result["msg"]


# --------------------------------------------------------------------------
# Check mode
# --------------------------------------------------------------------------
def test_check_mode_create_reports_change():
    interface = build_interface(False)
    session = build_session(interface)
    result = run_module(
        {"name": "vxlan1", "source_ip": "10.0.0.1", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    interface.apply.assert_not_called()


# --------------------------------------------------------------------------
# Create / idempotency / update
# --------------------------------------------------------------------------
def test_create():
    interface = build_interface(False, apply_changed=True)
    session = build_session(interface)
    result = run_module(
        {"name": "vxlan1", "source_ip": "10.0.0.1", "enabled": True}, session
    )
    assert result["changed"] is True
    assert interface.type == "vxlan"
    assert interface.options["local_ip"] == "10.0.0.1"
    assert interface.admin_state == "up"


def test_idempotent_update():
    interface = build_interface(True, apply_changed=False)
    session = build_session(interface)
    result = run_module(
        {"name": "vxlan1", "source_ip": "10.0.0.1", "state": "update"}, session
    )
    assert result["changed"] is False


def test_update_changes():
    interface = build_interface(True, apply_changed=True)
    session = build_session(interface)
    result = run_module(
        {
            "name": "vxlan1",
            "description": "overlay",
            "dest_udp_port": 4789,
            "state": "update",
        },
        session,
    )
    assert result["changed"] is True
    assert interface.options["vxlan_dest_udp_port"] == "4789"
    assert interface.description == "overlay"


def test_create_on_existing_non_vxlan_rejected():
    interface = build_interface(True, interface_type="system")
    session = build_session(interface)
    result = run_module({"name": "vxlan1", "source_ip": "10.0.0.1"}, session)
    assert result["failed"] is True
    assert "not a VXLAN" in result["msg"]


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    interface = build_interface(True)
    session = build_session(interface)
    result = run_module({"name": "vxlan1", "state": "delete"}, session)
    assert result["changed"] is True
    interface.delete.assert_called_once()


def test_delete_idempotent():
    interface = build_interface(False)
    session = build_session(interface)
    result = run_module({"name": "vxlan1", "state": "delete"}, session)
    assert result["changed"] is False
    interface.delete.assert_not_called()


def test_delete_non_vxlan_rejected():
    interface = build_interface(True, interface_type="system")
    session = build_session(interface)
    result = run_module({"name": "vxlan1", "state": "delete"}, session)
    assert result["failed"] is True
    assert "not a VXLAN" in result["msg"]


# --------------------------------------------------------------------------
# Switch errors (unsupported feature)
# --------------------------------------------------------------------------
@pytest.mark.parametrize(
    "exists, text, code, unsupported",
    [
        # Firmware that does not know the attribute
        (True, "invalid attribute: inter_vxlan_bridging_mode\n", 400, True),
        # Resource unknown to the switch
        (False, "Not Found", 404, True),
        # Other validation error, not reported as unsupported
        (True, "unknown string: allow\n", 400, False),
    ],
)
def test_switch_error_reported(exists, text, code, unsupported):
    from pyaoscx.exceptions.generic_op_error import GenericOperationError

    interface = build_interface(exists)
    interface.apply.side_effect = GenericOperationError(text, code)
    session = build_session(interface)
    session.api.__str__.return_value = "10.09"

    def request(method, path, params=None):
        response = MagicMock()
        response.json.return_value = (
            {"current_version": "FL.10.08.1010"}
            if path == "firmware"
            else {"platform_name": "6300"}
        )
        return response

    session.request.side_effect = request
    result = run_module(
        {"name": "vxlan1", "inter_vxlan_bridging_mode": "static-all"}, session
    )
    assert result["failed"] is True
    assert result.get("changed", False) is False
    expected = (
        "Could not configure VXLAN interface vxlan1 "
        "(inter_vxlan_bridging_mode)"
        if exists
        else "Could not create VXLAN interface vxlan1"
    )
    assert result["msg"].startswith(expected + ": " + text.strip())
    assert "(HTTP {0})".format(code) in result["msg"]
    assert ("probably not supported" in result["msg"]) is unsupported
    context = "Switch: 6300, firmware FL.10.08.1010, REST API v10.09"
    assert (context in result["msg"]) is unsupported


def test_created_interface_removed_when_configuration_rejected():
    from pyaoscx.exceptions.generic_op_error import GenericOperationError

    interface = build_interface(False)
    interface.apply.side_effect = [
        True,
        GenericOperationError(
            "invalid attribute: inter_vxlan_bridging_mode\n", 400
        ),
    ]
    session = build_session(interface)
    result = run_module(
        {"name": "vxlan1", "inter_vxlan_bridging_mode": "static-all"}, session
    )
    assert result["failed"] is True
    assert result["changed"] is False
    interface.delete.assert_called_once()
    assert "probably not supported" in result["msg"]
    assert result["msg"].endswith(
        "The VXLAN interface created by this task was removed"
    )
