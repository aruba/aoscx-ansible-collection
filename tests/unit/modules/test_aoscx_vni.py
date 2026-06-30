# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_vni module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover input validation, check mode, idempotency, create, update, delete and
error handling.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_vni.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_vni,
)

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_vni"


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


def build_vni(exists, vlan_id=None, vrf_name=None, routing=False):
    vni = MagicMock()
    vni.routing = routing
    if vlan_id is not None:
        vlan = MagicMock()
        vlan.id = vlan_id
        vni.vlan = vlan
    else:
        vni.vlan = None
    if vrf_name is not None:
        vrf = MagicMock()
        vrf.name = vrf_name
        vni.vrf = vrf
    else:
        vni.vrf = None
    if exists:
        vni.get.return_value = True
    else:
        vni.get.side_effect = Exception("not found")
    return vni


def build_session(existing, new_vni=None, interface_type="vxlan"):
    session = MagicMock()
    create_kwargs = ("vlan", "vrf", "routing")

    def get_module(sess, module, index=None, **kwargs):
        if module == "Interface":
            intf = MagicMock()
            intf.type = interface_type
            return intf
        if module == "Vlan":
            vlan = MagicMock()
            vlan.id = index
            return vlan
        if module == "Vrf":
            vrf = MagicMock()
            vrf.name = index
            return vrf
        if module == "Vni":
            if any(k in kwargs for k in create_kwargs) and new_vni is not None:
                return new_vni
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_vni.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_vni_id_rejected():
    session = build_session(build_vni(False))
    result = run_module({"vni_id": 0, "interface": "vxlan1"}, session)
    assert result["failed"] is True
    assert "vni_id must be between" in result["msg"]


def test_invalid_interface_rejected():
    session = build_session(build_vni(False))
    result = run_module({"vni_id": 40000, "interface": "a,b"}, session)
    assert result["failed"] is True
    assert "Invalid interface" in result["msg"]


def test_invalid_vrf_rejected():
    session = build_session(build_vni(False))
    result = run_module(
        {"vni_id": 40000, "interface": "vxlan1", "vrf": "a/b"}, session
    )
    assert result["failed"] is True
    assert "Invalid vrf" in result["msg"]


def test_vlan_vrf_mutually_exclusive():
    session = build_session(build_vni(False))
    result = run_module(
        {
            "vni_id": 40000,
            "interface": "vxlan1",
            "vlan": 4000,
            "vrf": "red",
        },
        session,
    )
    assert result["failed"] is True


def test_non_vxlan_interface_rejected():
    session = build_session(build_vni(False), interface_type="system")
    result = run_module(
        {"vni_id": 40000, "interface": "1/1/1", "vlan": 4000}, session
    )
    assert result["failed"] is True
    assert "not a VXLAN interface" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_l2_vni():
    existing = build_vni(False)
    new = build_vni(False)
    session = build_session(existing, new_vni=new)
    result = run_module(
        {"vni_id": 40000, "interface": "vxlan1", "vlan": 4000},
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_l3_vni():
    existing = build_vni(False)
    new = build_vni(False)
    session = build_session(existing, new_vni=new)
    result = run_module(
        {
            "vni_id": 50000,
            "interface": "vxlan1",
            "vrf": "red",
            "routing": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode_does_not_write():
    existing = build_vni(False)
    new = build_vni(False)
    session = build_session(existing, new_vni=new)
    result = run_module(
        {
            "vni_id": 40000,
            "interface": "vxlan1",
            "vlan": 4000,
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
    existing = build_vni(True, vlan_id=4000)
    session = build_session(existing)
    result = run_module(
        {
            "vni_id": 40000,
            "interface": "vxlan1",
            "state": "update",
            "vlan": 4000,
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_changes_vlan():
    existing = build_vni(True, vlan_id=4000)
    session = build_session(existing)
    result = run_module(
        {
            "vni_id": 40000,
            "interface": "vxlan1",
            "state": "update",
            "vlan": 4001,
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_changes_routing():
    existing = build_vni(True, vrf_name="red", routing=False)
    session = build_session(existing)
    result = run_module(
        {
            "vni_id": 50000,
            "interface": "vxlan1",
            "state": "update",
            "routing": True,
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_unspecified_attrs_left_untouched():
    existing = build_vni(True, vlan_id=4000)
    session = build_session(existing)
    result = run_module(
        {"vni_id": 40000, "interface": "vxlan1", "state": "update"},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    existing = build_vni(True, vlan_id=4000)
    session = build_session(existing)
    result = run_module(
        {"vni_id": 40000, "interface": "vxlan1", "state": "delete"},
        session,
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_no_change():
    existing = build_vni(False)
    session = build_session(existing)
    result = run_module(
        {"vni_id": 40000, "interface": "vxlan1", "state": "delete"},
        session,
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_create_error_is_reported():
    existing = build_vni(False)
    new = build_vni(False)
    new.create.side_effect = Exception("boom")
    session = build_session(existing, new_vni=new)
    result = run_module(
        {"vni_id": 40000, "interface": "vxlan1", "vlan": 4000},
        session,
    )
    assert result["failed"] is True
    assert "Could not create VNI" in result["msg"]


# --------------------------------------------------------------------------
# VTEP peers (static head-end replication)
# --------------------------------------------------------------------------
VNI_KEY = "vxlan_vni,206"


def build_tep(destination, vni_keys, vrf_name="default", origin="static"):
    tep = MagicMock()
    tep.destination = destination
    tep.origin = origin
    tep.vrf_name = vrf_name
    tep.network_id = {k: "/rest/uri/" + k for k in vni_keys}
    return tep


def build_vtep_session(
    exists, existing_teps, new_vni=None, interface_type="vxlan"
):
    session = MagicMock()
    existing = build_vni(exists, vlan_id=206)
    created_teps = []

    def get_index(obj):
        return {VNI_KEY: "/rest/latest/system/virtual_network_ids/" + VNI_KEY}

    def get_module(sess, module, index=None, **kwargs):
        if module == "Interface":
            intf = MagicMock()
            intf.type = interface_type
            return intf
        if module == "Vlan":
            vlan = MagicMock()
            vlan.id = index
            return vlan
        if module == "Vrf":
            vrf = MagicMock()
            vrf.name = index
            return vrf
        if module == "Vni":
            if new_vni is not None and any(
                k in kwargs for k in ("vlan", "vrf", "routing")
            ):
                return new_vni
            return existing
        if module == "TunnelEndpoint":
            tep = MagicMock()
            tep.destination = kwargs.get("destination")
            tep.origin = "static"
            tep.vrf_name = "default"
            tep.network_id = {}
            created_teps.append(tep)
            return tep
        raise AssertionError("unexpected module {0}".format(module))

    tep_class = MagicMock()
    tep_class.get_all.return_value = {
        "{0},{1},{2}".format(t.vrf_name, t.origin, t.destination): t
        for t in existing_teps
    }

    session.api.get_module.side_effect = get_module
    session.api.get_module_class.return_value = tep_class
    session.api.get_index.side_effect = get_index
    session._created_teps = created_teps
    return session


def test_invalid_vtep_peer_rejected():
    session = build_session(build_vni(False))
    result = run_module(
        {"vni_id": 206, "interface": "vxlan1", "vtep_peers": ["a,b"]},
        session,
    )
    assert result["failed"] is True
    assert "Invalid VTEP peer" in result["msg"]


def test_vtep_peers_create_adds_endpoint():
    session = build_vtep_session(False, [], new_vni=build_vni(False))
    result = run_module(
        {
            "vni_id": 206,
            "interface": "vxlan1",
            "vlan": 206,
            "vtep_peers": ["9.9.9.9"],
        },
        session,
    )
    assert result["changed"] is True
    created = session._created_teps
    assert len(created) == 1
    assert created[0].destination == "9.9.9.9"
    created[0].create.assert_called_once()


def test_vtep_peers_idempotent():
    tep = build_tep("9.9.9.9", [VNI_KEY])
    session = build_vtep_session(True, [tep])
    result = run_module(
        {
            "vni_id": 206,
            "interface": "vxlan1",
            "state": "update",
            "vtep_peers": ["9.9.9.9"],
        },
        session,
    )
    assert result["changed"] is False
    tep.update.assert_not_called()
    tep.delete.assert_not_called()


def test_vtep_peers_remove_deletes_unreferenced_endpoint():
    tep = build_tep("9.9.9.9", [VNI_KEY])
    session = build_vtep_session(True, [tep])
    result = run_module(
        {
            "vni_id": 206,
            "interface": "vxlan1",
            "state": "update",
            "vtep_peers": [],
        },
        session,
    )
    assert result["changed"] is True
    tep.delete.assert_called_once()


def test_vtep_peers_remove_keeps_shared_endpoint():
    # Endpoint floods this VNI plus another one: removing this VNI must keep
    # the endpoint (update), not delete it.
    tep = build_tep("9.9.9.9", [VNI_KEY, "vxlan_vni,207"])
    session = build_vtep_session(True, [tep])
    result = run_module(
        {
            "vni_id": 206,
            "interface": "vxlan1",
            "state": "update",
            "vtep_peers": [],
        },
        session,
    )
    assert result["changed"] is True
    tep.update.assert_called_once()
    tep.delete.assert_not_called()


def test_vtep_peers_unsupported_pyaoscx_reports_error():
    session = build_vtep_session(True, [])
    session.api.get_module_class.side_effect = Exception("no TunnelEndpoint")
    result = run_module(
        {
            "vni_id": 206,
            "interface": "vxlan1",
            "state": "update",
            "vtep_peers": ["9.9.9.9"],
        },
        session,
    )
    assert result["failed"] is True
    assert "does not support VTEP peers" in result["msg"]
