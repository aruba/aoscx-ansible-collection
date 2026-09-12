# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_evpn_vlan module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover input validation, check mode, idempotency, create, update, delete and
error handling.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_evpn_vlan.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_evpn_vlan,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules"
    ".aoscx_evpn_vlan"
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


def build_evpn_vlan(
    exists,
    rd="65000:204",
    import_route_targets=None,
    export_route_targets=None,
    redistribute=None,
):
    ev = MagicMock()
    ev.rd = rd
    ev.import_route_targets = (
        import_route_targets
        if import_route_targets is not None
        else ["65000:204"]
    )
    ev.export_route_targets = (
        export_route_targets
        if export_route_targets is not None
        else ["65000:204"]
    )
    ev.redistribute = (
        redistribute if redistribute is not None else {"host-route": True}
    )
    if exists:
        ev.get.return_value = True
    else:
        ev.get.side_effect = Exception("not found")
    return ev


def build_session(existing, new_ev=None, vlan_exists=True):
    session = MagicMock()
    create_kwargs = (
        "rd",
        "import_route_targets",
        "export_route_targets",
        "redistribute",
    )

    def get_module(sess, module, index=None, **kwargs):
        if module == "EvpnVlan":
            if any(k in kwargs for k in create_kwargs) and new_ev is not None:
                return new_ev
            return existing
        if module == "Vlan":
            vlan = MagicMock()
            if vlan_exists:
                vlan.get.return_value = True
            else:
                vlan.get.side_effect = Exception("no vlan")
            return vlan
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_evpn_vlan.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_vlan_rejected():
    session = build_session(build_evpn_vlan(False))
    result = run_module({"vlan": 0}, session)
    assert result["failed"] is True
    assert "vlan must be between" in result["msg"]


def test_vlan_not_found_rejected():
    session = build_session(build_evpn_vlan(False), vlan_exists=False)
    result = run_module({"vlan": 204, "rd": "65000:204"}, session)
    assert result["failed"] is True
    assert "Could not find VLAN" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    existing = build_evpn_vlan(False)
    new = build_evpn_vlan(False)
    session = build_session(existing, new_ev=new)
    result = run_module(
        {
            "vlan": 204,
            "rd": "65000:204",
            "import_route_targets": ["65000:204"],
            "export_route_targets": ["65000:204"],
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_evpn_vlan(False)
    new = build_evpn_vlan(False)
    session = build_session(existing, new_ev=new)
    result = run_module(
        {"vlan": 204, "rd": "65000:204", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_rd():
    existing = build_evpn_vlan(True, rd="65000:204")
    session = build_session(existing)
    result = run_module(
        {"vlan": 204, "state": "update", "rd": "65001:204"}, session
    )
    assert result["changed"] is True
    assert existing.rd == "65001:204"
    existing.update.assert_called_once()


def test_update_route_targets_order_insensitive():
    existing = build_evpn_vlan(
        True, import_route_targets=["65000:204", "65000:205"]
    )
    session = build_session(existing)
    result = run_module(
        {
            "vlan": 204,
            "state": "update",
            "import_route_targets": ["65000:205", "65000:204"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_route_targets_change():
    existing = build_evpn_vlan(True, export_route_targets=["65000:204"])
    session = build_session(existing)
    result = run_module(
        {
            "vlan": 204,
            "state": "update",
            "export_route_targets": ["65000:204", "65000:999"],
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_redistribute_merge():
    existing = build_evpn_vlan(True, redistribute={"host-route": False})
    session = build_session(existing)
    result = run_module(
        {
            "vlan": 204,
            "state": "update",
            "redistribute": {"host-route": True},
        },
        session,
    )
    assert result["changed"] is True
    assert existing.redistribute == {"host-route": True}
    existing.update.assert_called_once()


def test_update_no_change():
    existing = build_evpn_vlan(True, rd="65000:204")
    session = build_session(existing)
    result = run_module(
        {"vlan": 204, "state": "update", "rd": "65000:204"}, session
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    existing = build_evpn_vlan(True)
    session = build_session(existing)
    result = run_module({"vlan": 204, "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent():
    existing = build_evpn_vlan(False)
    session = build_session(existing)
    result = run_module({"vlan": 204, "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
