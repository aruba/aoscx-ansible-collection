# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_udp_bcast_forwarder module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover input validation, check mode, idempotency, create, update, delete and
error handling.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_udp_bcast_forwarder.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_udp_bcast_forwarder,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_udp_bcast_forwarder"
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


def build_forwarder(exists, ipv4=None):
    fwd = MagicMock()
    fwd.config_attrs = []
    fwd.ipv4_ucast_server = ipv4 if ipv4 is not None else []
    if exists:
        fwd.get.return_value = True
    else:
        fwd.get.side_effect = Exception("not found")
    return fwd


def build_session(existing, new_forwarder=None):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if module in ("Vrf", "Interface"):
            return MagicMock(name=module)
        if module == "UdpBcastForwarderServer":
            if "ipv4_ucast_server" in kwargs and new_forwarder is not None:
                return new_forwarder
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_udp_bcast_forwarder.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_src_port_rejected():
    session = build_session(build_forwarder(False))
    result = run_module({"src_port": "a,b", "udp_dport": 53}, session)
    assert result["failed"] is True
    assert "Invalid src_port" in result["msg"]


def test_invalid_dest_vrf_rejected():
    session = build_session(build_forwarder(False))
    result = run_module(
        {"src_port": "1/1/1", "udp_dport": 53, "dest_vrf": "a/b"},
        session,
    )
    assert result["failed"] is True
    assert "Invalid dest_vrf" in result["msg"]


def test_udp_dport_out_of_range_rejected():
    session = build_session(build_forwarder(False))
    result = run_module({"src_port": "1/1/1", "udp_dport": 70000}, session)
    assert result["failed"] is True
    assert "udp_dport must be between 0 and 65535" in result["msg"]


def test_too_many_servers_rejected():
    session = build_session(build_forwarder(False))
    result = run_module(
        {
            "src_port": "1/1/1",
            "udp_dport": 53,
            "ipv4_ucast_server": ["10.0.0.{0}".format(i) for i in range(9)],
        },
        session,
    )
    assert result["failed"] is True
    assert "at most 8" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_new_forwarder():
    existing = build_forwarder(False)
    new = build_forwarder(False)
    session = build_session(existing, new_forwarder=new)
    result = run_module(
        {
            "src_port": "1/1/1",
            "udp_dport": 53,
            "ipv4_ucast_server": ["10.0.0.1"],
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode_does_not_write():
    existing = build_forwarder(False)
    new = build_forwarder(False)
    session = build_session(existing, new_forwarder=new)
    result = run_module(
        {
            "src_port": "1/1/1",
            "udp_dport": 53,
            "ipv4_ucast_server": ["10.0.0.1"],
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
    existing = build_forwarder(True, ipv4=["10.0.0.2", "10.0.0.1"])
    session = build_session(existing)
    result = run_module(
        {
            "src_port": "1/1/1",
            "udp_dport": 53,
            "state": "update",
            "ipv4_ucast_server": ["10.0.0.1", "10.0.0.2"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_changes_server_list():
    existing = build_forwarder(True, ipv4=["10.0.0.1"])
    session = build_session(existing)
    result = run_module(
        {
            "src_port": "1/1/1",
            "udp_dport": 53,
            "state": "update",
            "ipv4_ucast_server": ["10.0.0.1", "10.0.0.2"],
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    existing = build_forwarder(True)
    session = build_session(existing)
    result = run_module(
        {"src_port": "1/1/1", "udp_dport": 53, "state": "delete"},
        session,
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_no_change():
    existing = build_forwarder(False)
    session = build_session(existing)
    result = run_module(
        {"src_port": "1/1/1", "udp_dport": 53, "state": "delete"},
        session,
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_create_error_is_reported():
    existing = build_forwarder(False)
    new = build_forwarder(False)
    new.create.side_effect = Exception("boom")
    session = build_session(existing, new_forwarder=new)
    result = run_module(
        {
            "src_port": "1/1/1",
            "udp_dport": 53,
            "ipv4_ucast_server": ["10.0.0.1"],
        },
        session,
    )
    assert result["failed"] is True
    assert "Could not create UDP forwarder" in result["msg"]
