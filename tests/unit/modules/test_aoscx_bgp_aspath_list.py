# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_bgp_aspath_list module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover input validation, check mode, idempotency, create/update/delete and
error handling.

Run with:
    PYTHONPATH=/tmp/acoll2 .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_bgp_aspath_list.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_bgp_aspath_list,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_bgp_aspath_list"
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


def build_filter(exists):
    flt = MagicMock()
    flt.config_attrs = []
    if exists:
        flt.get.return_value = True
    else:
        flt.get.side_effect = Exception("not found")
    return flt


def build_session(aspath_filter, existing_entries=None, entry=None):
    session = MagicMock()
    existing_entries = existing_entries or {}

    def get_module(sess, module, index=None, **kwargs):
        if module == "BgpAspathFilter":
            return aspath_filter
        if module == "BgpAspathFilterEntry":
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
            aoscx_bgp_aspath_list.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_name_rejected():
    session = build_session(build_filter(False))
    result = run_module({"name": "bad/name"}, session)
    assert result["failed"] is True
    assert "Invalid AS-Path filter name" in result["msg"]


def test_duplicate_preference_rejected():
    session = build_session(build_filter(False))
    result = run_module(
        {
            "name": "F1",
            "entries": [
                {"preference": 10, "action": "permit", "regex": "a"},
                {"preference": 10, "action": "deny", "regex": "b"},
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "Duplicate entry preference" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_new_filter():
    aspath_filter = build_filter(False)
    session = build_session(aspath_filter)
    result = run_module({"name": "F1", "state": "create"}, session)
    assert result["changed"] is True
    aspath_filter.create.assert_called_once()


def test_create_check_mode_does_not_write():
    aspath_filter = build_filter(False)
    session = build_session(aspath_filter)
    result = run_module(
        {"name": "F1", "state": "create", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    aspath_filter.create.assert_not_called()


def test_create_entry():
    aspath_filter = build_filter(False)
    entry = MagicMock()
    entry.config_attrs = []
    entry.get.side_effect = Exception("not found")
    session = build_session(aspath_filter, entry=entry)
    result = run_module(
        {
            "name": "F1",
            "entries": [
                {"preference": 10, "action": "permit", "regex": "^65000_"}
            ],
        },
        session,
    )
    assert result["changed"] is True
    entry.create.assert_called_once()
    called = [
        c
        for c in session.api.get_module.call_args_list
        if c.args[1] == "BgpAspathFilterEntry"
    ][-1]
    assert called.kwargs["action"] == "permit"
    assert called.kwargs["regex"] == "^65000_"


# --------------------------------------------------------------------------
# Idempotency / update
# --------------------------------------------------------------------------
def test_idempotent_entry_no_change():
    aspath_filter = build_filter(True)
    entry = MagicMock()
    entry.config_attrs = []
    entry.get.return_value = True
    entry.action = "permit"
    entry.regex = "^65000_"
    session = build_session(aspath_filter, entry=entry)
    result = run_module(
        {
            "name": "F1",
            "state": "update",
            "entries": [
                {"preference": 10, "action": "permit", "regex": "^65000_"}
            ],
        },
        session,
    )
    assert result["changed"] is False
    entry.update.assert_not_called()


def test_update_entry_changes():
    aspath_filter = build_filter(True)
    entry = MagicMock()
    entry.config_attrs = []
    entry.get.return_value = True
    entry.action = "permit"
    entry.regex = "^65000_"
    session = build_session(aspath_filter, entry=entry)
    result = run_module(
        {
            "name": "F1",
            "state": "update",
            "entries": [
                {"preference": 10, "action": "permit", "regex": "^65002_"}
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
    aspath_filter = build_filter(True)
    stale = MagicMock()
    session = build_session(aspath_filter, existing_entries={"20": stale})
    result = run_module(
        {
            "name": "F1",
            "state": "update",
            "entries": [{"preference": 10, "action": "permit", "regex": "a"}],
        },
        session,
    )
    assert result["changed"] is True
    stale.delete.assert_called_once()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    aspath_filter = build_filter(True)
    session = build_session(aspath_filter)
    result = run_module({"name": "F1", "state": "delete"}, session)
    assert result["changed"] is True
    aspath_filter.delete.assert_called_once()


def test_delete_absent_no_change():
    aspath_filter = build_filter(False)
    session = build_session(aspath_filter)
    result = run_module({"name": "F1", "state": "delete"}, session)
    assert result["changed"] is False
    aspath_filter.delete.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_create_error_is_reported():
    aspath_filter = build_filter(False)
    aspath_filter.create.side_effect = Exception("boom")
    session = build_session(aspath_filter)
    result = run_module({"name": "F1", "state": "create"}, session)
    assert result["failed"] is True
    assert "Could not create AS-Path filter" in result["msg"]
