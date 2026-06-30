# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_evpn_vlan_aware_bundle module.

The pyaoscx session is fully mocked, so no switch is required. The tests cover
input validation, check mode, create, idempotency, update, member VLAN
reconciliation, delete and error handling.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_evpn_vlan_aware_bundle,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_evpn_vlan_aware_bundle"
)

PREFIX = "/rest/latest/"


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


def build_bundle(exists, **attrs):
    bundle = MagicMock()
    for key, value in attrs.items():
        setattr(bundle, key, value)
    if exists:
        bundle.get.return_value = True
    else:
        # The first get (existence check) fails; a later get (after create)
        # succeeds.
        bundle.get.side_effect = [Exception("not found"), True]
    return bundle


def build_session(bundle, vlan_exists=True):
    session = MagicMock()
    session.resource_prefix = PREFIX

    def get_module(sess, module, index=None, **kwargs):
        if module == "EvpnVlanAwareBundle":
            return bundle
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
            aoscx_evpn_vlan_aware_bundle.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_bundle_name_rejected():
    session = build_session(build_bundle(False))
    result = run_module({"bundle_name": "a/b"}, session)
    assert result["failed"] is True
    assert "Invalid bundle name" in result["msg"]


def test_missing_vlan_rejected():
    bundle = build_bundle(False)
    session = build_session(bundle, vlan_exists=False)
    result = run_module(
        {"bundle_name": "blue", "vlans": [{"id": 206}]}, session
    )
    assert result["failed"] is True
    assert "Could not find VLAN" in result["msg"]


# --------------------------------------------------------------------------
# Check mode
# --------------------------------------------------------------------------
def test_check_mode_create_reports_change():
    bundle = build_bundle(False)
    session = build_session(bundle)
    result = run_module(
        {"bundle_name": "blue", "rd": "65000:1", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    bundle.create.assert_not_called()


# --------------------------------------------------------------------------
# Create / idempotency / update
# --------------------------------------------------------------------------
def test_create():
    bundle = build_bundle(
        False,
        rd=None,
        import_route_targets=[],
        export_route_targets=[],
        redistribute={},
        disable=False,
        vlan_ethernet_tags={},
    )
    session = build_session(bundle)
    result = run_module(
        {
            "bundle_name": "blue",
            "rd": "65000:1",
            "vlans": [{"id": 206}, {"id": 207, "ethernet_tag": 100}],
        },
        session,
    )
    assert result["changed"] is True
    bundle.create.assert_called_once()
    bundle.update.assert_called_once()
    assert bundle.rd == "65000:1"
    assert bundle.vlan_ethernet_tags == {
        PREFIX + "system/vlans/206": 206,
        PREFIX + "system/vlans/207": 100,
    }


def test_idempotent():
    bundle = build_bundle(
        True,
        rd="65000:1",
        import_route_targets=["65000:1"],
        export_route_targets=["65000:1"],
        redistribute={"host-route": False},
        disable=False,
        vlan_ethernet_tags={PREFIX + "system/vlans/206": 206},
    )
    session = build_session(bundle)
    result = run_module(
        {
            "bundle_name": "blue",
            "rd": "65000:1",
            "import_route_targets": ["65000:1"],
            "export_route_targets": ["65000:1"],
            "vlans": [{"id": 206}],
            "state": "update",
        },
        session,
    )
    assert result["changed"] is False
    bundle.update.assert_not_called()


def test_update_replaces_vlans():
    bundle = build_bundle(
        True,
        rd="65000:1",
        import_route_targets=["65000:1"],
        export_route_targets=["65000:1"],
        redistribute={},
        disable=False,
        vlan_ethernet_tags={
            PREFIX + "system/vlans/206": 206,
            PREFIX + "system/vlans/207": 207,
        },
    )
    session = build_session(bundle)
    result = run_module(
        {"bundle_name": "blue", "vlans": [{"id": 206}], "state": "update"},
        session,
    )
    assert result["changed"] is True
    bundle.update.assert_called_once()
    assert bundle.vlan_ethernet_tags == {PREFIX + "system/vlans/206": 206}


def test_clear_vlans():
    bundle = build_bundle(
        True,
        rd="65000:1",
        import_route_targets=[],
        export_route_targets=[],
        redistribute={},
        disable=False,
        vlan_ethernet_tags={PREFIX + "system/vlans/206": 206},
    )
    session = build_session(bundle)
    result = run_module(
        {"bundle_name": "blue", "vlans": [], "state": "update"}, session
    )
    assert result["changed"] is True
    assert bundle.vlan_ethernet_tags == {}


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    bundle = build_bundle(True)
    session = build_session(bundle)
    result = run_module(
        {"bundle_name": "blue", "state": "delete"}, session
    )
    assert result["changed"] is True
    bundle.delete.assert_called_once()


def test_delete_idempotent():
    bundle = build_bundle(False)
    session = build_session(bundle)
    result = run_module(
        {"bundle_name": "blue", "state": "delete"}, session
    )
    assert result["changed"] is False
    bundle.delete.assert_not_called()
