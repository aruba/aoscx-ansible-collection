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
    if patch_module_args is not None:
        return patch_module_args(args)
    serialized = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(serialized)
    return nullcontext()


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
    dyn_vxlan_tunnel_bridging_mode="no-bridging",
):
    evpn = MagicMock()
    evpn.dyn_vxlan_tunnel_bridging_mode = dyn_vxlan_tunnel_bridging_mode
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
    with set_module_args(args):
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


@pytest.mark.parametrize(
    "current, wanted, changed",
    [
        ("no-bridging", "ibgp-ebgp", True),
        ("ibgp-ebgp", "no-bridging", True),
        ("ibgp-ebgp", "ibgp-ebgp", False),
        # Attribute absent: firmware not supporting it, sent to fail
        (None, "no-bridging", True),
    ],
)
def test_dyn_vxlan_tunnel_bridging_mode(current, wanted, changed):
    evpn = build_evpn(dyn_vxlan_tunnel_bridging_mode=current)
    session = build_session(evpn)
    result = run_module({"dyn_vxlan_tunnel_bridging_mode": wanted}, session)
    assert result["changed"] is changed
    if changed:
        evpn.set_dyn_vxlan_tunnel_bridging_mode.assert_called_once_with(wanted)
        evpn.update.assert_called_once()
    else:
        evpn.set_dyn_vxlan_tunnel_bridging_mode.assert_not_called()
        evpn.update.assert_not_called()


def test_dyn_vxlan_tunnel_bridging_mode_old_pyaoscx():
    evpn = build_evpn()
    del evpn.set_dyn_vxlan_tunnel_bridging_mode
    session = build_session(evpn)
    result = run_module(
        {"dyn_vxlan_tunnel_bridging_mode": "ibgp-ebgp"}, session
    )
    assert result["failed"] is True
    assert "Upgrade pyaoscx" in result["msg"]
    evpn.update.assert_not_called()


def test_dyn_vxlan_tunnel_bridging_mode_unsupported_by_switch():
    evpn = build_evpn(dyn_vxlan_tunnel_bridging_mode=None)
    evpn.update.side_effect = Exception(
        "cannot modify the attribute: dyn_vxlan_tunnel_bridging_mode "
        "(attribute probably not supported by this switch platform or "
        "firmware version)"
    )
    session = build_session(evpn)
    result = run_module(
        {"dyn_vxlan_tunnel_bridging_mode": "ibgp-ebgp"}, session
    )
    assert result["failed"] is True
    assert "probably not supported" in result["msg"]


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
