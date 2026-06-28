# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_route_map module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover input validation, check mode, idempotency, create/update/delete and
error handling.

Run with:
    PYTHONPATH=/tmp/acoll2 .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_route_map.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_route_map,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_route_map"
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


def build_route_map(exists):
    rmap = MagicMock()
    rmap.config_attrs = []
    if exists:
        rmap.get.return_value = True
    else:
        rmap.get.side_effect = Exception("not found")
    return rmap


def build_session(route_map, existing_entries=None, entry=None):
    session = MagicMock()
    existing_entries = existing_entries or {}

    def get_module(sess, module, index=None, **kwargs):
        if module == "RouteMap":
            return route_map
        if module == "RouteMapEntry":
            if entry is not None:
                return entry
            new_entry = MagicMock()
            new_entry.config_attrs = []
            new_entry.get.side_effect = Exception("not found")
            return new_entry
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module

    entry_class = MagicMock()
    entry_class.get_all.return_value = existing_entries
    session.api.get_module_class.return_value = entry_class
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_route_map.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_name_rejected():
    session = build_session(build_route_map(False))
    result = run_module({"name": "bad/name"}, session)
    assert result["failed"] is True
    assert "Invalid route map name" in result["msg"]


def test_duplicate_preference_rejected():
    session = build_session(build_route_map(False))
    result = run_module(
        {
            "name": "RM1",
            "entries": [
                {"preference": 10, "action": "permit"},
                {"preference": 10, "action": "deny"},
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "Duplicate entry preference" in result["msg"]


def test_goto_requires_continue():
    session = build_session(build_route_map(False))
    result = run_module(
        {
            "name": "RM1",
            "entries": [
                {
                    "preference": 10,
                    "action": "permit",
                    "exitpolicy": "goto",
                }
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "route_map_continue is required" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_new_route_map():
    route_map = build_route_map(False)
    session = build_session(route_map)
    result = run_module({"name": "RM1", "state": "create"}, session)
    assert result["changed"] is True
    route_map.create.assert_called_once()


def test_create_check_mode_does_not_write():
    route_map = build_route_map(False)
    session = build_session(route_map)
    result = run_module(
        {"name": "RM1", "state": "create", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    route_map.create.assert_not_called()


def test_create_entry_with_match_set():
    route_map = build_route_map(False)
    entry = MagicMock()
    entry.config_attrs = []
    entry.get.side_effect = Exception("not found")
    session = build_session(route_map, entry=entry)
    result = run_module(
        {
            "name": "RM1",
            "entries": [
                {
                    "preference": 10,
                    "action": "permit",
                    "match": {"source_protocol": "bgp"},
                    "set": {
                        "local_preference": 200,
                        "atomic_aggregate": True,
                    },
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    entry.create.assert_called_once()
    # The set clause must be built with the REST key names.
    called = [
        c
        for c in session.api.get_module.call_args_list
        if c.args[1] == "RouteMapEntry"
    ][-1]
    assert called.kwargs["set"] == {
        "local_preference": 200,
        "atomic-aggregate": True,
    }
    assert called.kwargs["match"] == {"source_protocol": "bgp"}


# --------------------------------------------------------------------------
# Idempotency / update
# --------------------------------------------------------------------------
def test_idempotent_entry_no_change():
    route_map = build_route_map(True)
    entry = MagicMock()
    entry.config_attrs = []
    entry.get.return_value = True
    entry.action = "permit"
    entry.match = {"source_protocol": "bgp"}
    session = build_session(route_map, entry=entry)
    result = run_module(
        {
            "name": "RM1",
            "state": "update",
            "entries": [
                {
                    "preference": 10,
                    "action": "permit",
                    "match": {"source_protocol": "bgp"},
                }
            ],
        },
        session,
    )
    assert result["changed"] is False
    entry.update.assert_not_called()


def test_update_entry_changes():
    route_map = build_route_map(True)
    entry = MagicMock()
    entry.config_attrs = []
    entry.get.return_value = True
    entry.action = "permit"
    entry.match = {"source_protocol": "ospf"}
    session = build_session(route_map, entry=entry)
    result = run_module(
        {
            "name": "RM1",
            "state": "update",
            "entries": [
                {
                    "preference": 10,
                    "action": "permit",
                    "match": {"source_protocol": "bgp"},
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    entry.update.assert_called_once()


# --------------------------------------------------------------------------
# Prune
# --------------------------------------------------------------------------
def test_prune_removes_stale_entry():
    route_map = build_route_map(True)
    stale = MagicMock()
    session = build_session(route_map, existing_entries={"20": stale})
    result = run_module(
        {
            "name": "RM1",
            "state": "update",
            "entries": [{"preference": 10, "action": "permit"}],
        },
        session,
    )
    assert result["changed"] is True
    stale.delete.assert_called_once()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    route_map = build_route_map(True)
    session = build_session(route_map)
    result = run_module({"name": "RM1", "state": "delete"}, session)
    assert result["changed"] is True
    route_map.delete.assert_called_once()


def test_delete_absent_no_change():
    route_map = build_route_map(False)
    session = build_session(route_map)
    result = run_module({"name": "RM1", "state": "delete"}, session)
    assert result["changed"] is False
    route_map.delete.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_create_error_is_reported():
    route_map = build_route_map(False)
    route_map.create.side_effect = Exception("boom")
    session = build_session(route_map)
    result = run_module({"name": "RM1", "state": "create"}, session)
    assert result["failed"] is True
    assert "Could not create route map" in result["msg"]
