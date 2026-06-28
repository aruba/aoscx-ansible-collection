# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_dhcp_relay module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover input validation, check mode, idempotency, create, update, delete and
error handling.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_dhcp_relay.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_dhcp_relay,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_dhcp_relay"
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


def build_relay(exists, ipv4=None, ipv6=None, other_config=None):
    relay = MagicMock()
    relay.config_attrs = []
    relay.ipv4_ucast_server = ipv4 if ipv4 is not None else []
    relay.ipv6_ucast_server = ipv6 if ipv6 is not None else []
    relay.other_config = other_config if other_config is not None else {}
    if exists:
        relay.get.return_value = True
    else:
        relay.get.side_effect = Exception("not found")
    return relay


def build_session(existing, new_relay=None):
    session = MagicMock()
    create_kwargs = (
        "ipv4_ucast_server",
        "ipv6_ucast_server",
        "other_config",
    )

    def get_module(sess, module, index=None, **kwargs):
        if module in ("Vrf", "Interface"):
            return MagicMock(name=module)
        if module == "DhcpRelay":
            if (
                any(k in kwargs for k in create_kwargs)
                and new_relay is not None
            ):
                return new_relay
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_dhcp_relay.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_port_rejected():
    session = build_session(build_relay(False))
    result = run_module({"port": "a,b"}, session)
    assert result["failed"] is True
    assert "Invalid port" in result["msg"]


def test_invalid_vrf_rejected():
    session = build_session(build_relay(False))
    result = run_module({"port": "1/1/3", "vrf": "a/b"}, session)
    assert result["failed"] is True
    assert "Invalid vrf" in result["msg"]


def test_too_many_ipv4_servers_rejected():
    session = build_session(build_relay(False))
    result = run_module(
        {
            "port": "1/1/3",
            "ipv4_ucast_server": ["10.0.0.{0}".format(i) for i in range(9)],
        },
        session,
    )
    assert result["failed"] is True
    assert "ipv4_ucast_server accepts at most 8" in result["msg"]


def test_too_many_ipv6_servers_rejected():
    session = build_session(build_relay(False))
    result = run_module(
        {
            "port": "1/1/3",
            "ipv6_ucast_server": ["2001:db8::{0}".format(i) for i in range(9)],
        },
        session,
    )
    assert result["failed"] is True
    assert "ipv6_ucast_server accepts at most 8" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_new_relay():
    existing = build_relay(False)
    new = build_relay(False)
    session = build_session(existing, new_relay=new)
    result = run_module(
        {"port": "1/1/3", "ipv4_ucast_server": ["10.1.1.1"]},
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_with_bootp_gateway():
    existing = build_relay(False)
    new = build_relay(False)
    session = build_session(existing, new_relay=new)
    result = run_module(
        {
            "port": "1/1/3",
            "ipv4_ucast_server": ["10.1.1.1"],
            "bootp_gateway": "10.1.1.254",
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode_does_not_write():
    existing = build_relay(False)
    new = build_relay(False)
    session = build_session(existing, new_relay=new)
    result = run_module(
        {
            "port": "1/1/3",
            "ipv4_ucast_server": ["10.1.1.1"],
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Idempotency / update
# --------------------------------------------------------------------------
def test_idempotent_no_change():
    existing = build_relay(True, ipv4=["10.1.1.2", "10.1.1.1"])
    session = build_session(existing)
    result = run_module(
        {
            "port": "1/1/3",
            "state": "update",
            "ipv4_ucast_server": ["10.1.1.1", "10.1.1.2"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_changes_ipv4_list():
    existing = build_relay(True, ipv4=["10.1.1.1"])
    session = build_session(existing)
    result = run_module(
        {
            "port": "1/1/3",
            "state": "update",
            "ipv4_ucast_server": ["10.1.1.1", "10.1.1.2"],
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_changes_bootp_gateway():
    existing = build_relay(True, other_config={"bootp_gateway": "10.1.1.1"})
    session = build_session(existing)
    result = run_module(
        {
            "port": "1/1/3",
            "state": "update",
            "bootp_gateway": "10.1.1.254",
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_unspecified_attrs_left_untouched():
    existing = build_relay(True, ipv4=["10.1.1.1"])
    session = build_session(existing)
    result = run_module(
        {"port": "1/1/3", "state": "update"},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    existing = build_relay(True)
    session = build_session(existing)
    result = run_module(
        {"port": "1/1/3", "state": "delete"},
        session,
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_no_change():
    existing = build_relay(False)
    session = build_session(existing)
    result = run_module(
        {"port": "1/1/3", "state": "delete"},
        session,
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_create_error_is_reported():
    existing = build_relay(False)
    new = build_relay(False)
    new.create.side_effect = Exception("boom")
    session = build_session(existing, new_relay=new)
    result = run_module(
        {"port": "1/1/3", "ipv4_ucast_server": ["10.1.1.1"]},
        session,
    )
    assert result["failed"] is True
    assert "Could not create DHCP relay" in result["msg"]
