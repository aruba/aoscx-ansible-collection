# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_evpn module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover idempotency, scalar and dictionary reconciliation, check mode and
error handling.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_evpn.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_evpn,
)

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_evpn"


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


def build_evpn(
    arp_suppression_enable=True,
    nd_suppression_enable=False,
    mac_move_count=5,
    mac_move_timer=180,
    redistribute=None,
):
    evpn = MagicMock()
    evpn.arp_suppression_enable = arp_suppression_enable
    evpn.nd_suppression_enable = nd_suppression_enable
    evpn.mac_move_count = mac_move_count
    evpn.mac_move_timer = mac_move_timer
    evpn.redistribute = (
        redistribute
        if redistribute is not None
        else {"local-mac": False, "local-svi": False}
    )
    evpn.get.return_value = True
    return evpn


def build_session(evpn):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if module == "Evpn":
            return evpn
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_evpn.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Idempotency
# --------------------------------------------------------------------------
def test_no_params_no_change():
    evpn = build_evpn()
    session = build_session(evpn)
    result = run_module({}, session)
    assert result["changed"] is False
    evpn.update.assert_not_called()


def test_same_value_no_change():
    evpn = build_evpn(mac_move_timer=180)
    session = build_session(evpn)
    result = run_module({"mac_move_timer": 180}, session)
    assert result["changed"] is False
    evpn.update.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_change_scalar():
    evpn = build_evpn(mac_move_timer=180)
    session = build_session(evpn)
    result = run_module({"mac_move_timer": 181}, session)
    assert result["changed"] is True
    assert evpn.mac_move_timer == 181
    evpn.update.assert_called_once()


def test_change_bool():
    evpn = build_evpn(nd_suppression_enable=False)
    session = build_session(evpn)
    result = run_module({"nd_suppression_enable": True}, session)
    assert result["changed"] is True
    assert evpn.nd_suppression_enable is True
    evpn.update.assert_called_once()


def test_redistribute_merge():
    evpn = build_evpn(redistribute={"local-mac": False, "local-svi": False})
    session = build_session(evpn)
    result = run_module({"redistribute": {"local-mac": True}}, session)
    assert result["changed"] is True
    assert evpn.redistribute == {"local-mac": True, "local-svi": False}
    evpn.update.assert_called_once()


def test_redistribute_no_change():
    evpn = build_evpn(redistribute={"local-mac": True, "local-svi": False})
    session = build_session(evpn)
    result = run_module({"redistribute": {"local-mac": True}}, session)
    assert result["changed"] is False
    evpn.update.assert_not_called()


# --------------------------------------------------------------------------
# Check mode
# --------------------------------------------------------------------------
def test_check_mode_no_update():
    evpn = build_evpn(mac_move_timer=180)
    session = build_session(evpn)
    result = run_module(
        {"mac_move_timer": 181, "_ansible_check_mode": True}, session
    )
    assert result["changed"] is True
    evpn.update.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_get_failure():
    evpn = build_evpn()
    evpn.get.side_effect = Exception("boom")
    session = build_session(evpn)
    result = run_module({"mac_move_timer": 181}, session)
    assert result["failed"] is True
    assert "Could not retrieve EVPN configuration" in result["msg"]
