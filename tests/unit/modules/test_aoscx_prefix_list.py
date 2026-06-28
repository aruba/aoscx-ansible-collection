# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_prefix_list module.

These tests mock the pyaoscx session entirely, so no switch is required.
They cover input validation, check mode, idempotency, create/update/delete
flows and error handling.

Run with:
    PYTHONPATH=/tmp/acoll2 .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_prefix_list.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_prefix_list,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_prefix_list"
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


def build_prefix_list(exists, af="ipv4", description=None):
    plist = MagicMock()
    plist.config_attrs = []
    if exists:
        plist.get.return_value = True
        plist.address_family = af
        plist.description = description
    else:
        plist.get.side_effect = Exception("not found")
    return plist


def build_session(prefix_list, existing_entries=None, entry_exists=False):
    session = MagicMock()
    existing_entries = existing_entries or {}

    def get_module(sess, module, index=None, **kwargs):
        if module == "PrefixList":
            return prefix_list
        if module == "PrefixListEntry":
            entry = MagicMock()
            entry.config_attrs = []
            if entry_exists:
                entry.get.return_value = True
            else:
                entry.get.side_effect = Exception("not found")
            return entry
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
            aoscx_prefix_list.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Input validation (boundary, runs before any switch contact)
# --------------------------------------------------------------------------
def test_invalid_name_rejected():
    session = build_session(build_prefix_list(False))
    result = run_module({"name": "bad/name", "state": "create"}, session)
    assert result["failed"] is True
    assert "Invalid prefix list name" in result["msg"]


def test_ge_out_of_range_rejected():
    session = build_session(build_prefix_list(False))
    result = run_module(
        {
            "name": "L1",
            "entries": [
                {
                    "preference": 10,
                    "action": "permit",
                    "prefix": "10.0.0.0/8",
                    "ge": 200,
                }
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "between 0 and 128" in result["msg"]


def test_ge_greater_than_le_rejected():
    session = build_session(build_prefix_list(False))
    result = run_module(
        {
            "name": "L1",
            "entries": [
                {
                    "preference": 10,
                    "action": "permit",
                    "prefix": "10.0.0.0/8",
                    "ge": 30,
                    "le": 24,
                }
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "cannot be greater than" in result["msg"]


def test_duplicate_preference_rejected():
    session = build_session(build_prefix_list(False))
    result = run_module(
        {
            "name": "L1",
            "entries": [
                {"preference": 10, "action": "permit", "prefix": "10/8"},
                {"preference": 10, "action": "deny", "prefix": "11/8"},
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "Duplicate entry preference" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_new_list():
    prefix_list = build_prefix_list(False)
    session = build_session(prefix_list)
    result = run_module(
        {"name": "L1", "address_family": "ipv4", "state": "create"},
        session,
    )
    assert result["changed"] is True
    prefix_list.create.assert_called_once()


def test_create_check_mode_does_not_write():
    prefix_list = build_prefix_list(False)
    session = build_session(prefix_list)
    result = run_module(
        {
            "name": "L1",
            "address_family": "ipv4",
            "state": "create",
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    prefix_list.create.assert_not_called()


# --------------------------------------------------------------------------
# Update / idempotency
# --------------------------------------------------------------------------
def test_idempotent_description_no_change():
    prefix_list = build_prefix_list(True, af="ipv4", description="same")
    session = build_session(prefix_list)
    result = run_module(
        {"name": "L1", "description": "same", "state": "update"},
        session,
    )
    assert result["changed"] is False
    prefix_list.update.assert_not_called()


def test_update_description_changes():
    prefix_list = build_prefix_list(True, af="ipv4", description="old")
    session = build_session(prefix_list)
    result = run_module(
        {"name": "L1", "description": "new", "state": "update"},
        session,
    )
    assert result["changed"] is True
    prefix_list.update.assert_called_once()


def test_address_family_immutable():
    prefix_list = build_prefix_list(True, af="ipv4")
    session = build_session(prefix_list)
    result = run_module(
        {"name": "L1", "address_family": "ipv6", "state": "update"},
        session,
    )
    assert result["failed"] is True
    assert "address_family cannot be changed" in result["msg"]


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    prefix_list = build_prefix_list(True)
    session = build_session(prefix_list)
    result = run_module({"name": "L1", "state": "delete"}, session)
    assert result["changed"] is True
    prefix_list.delete.assert_called_once()


def test_delete_absent_no_change():
    prefix_list = build_prefix_list(False)
    session = build_session(prefix_list)
    result = run_module({"name": "L1", "state": "delete"}, session)
    assert result["changed"] is False
    prefix_list.delete.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_create_error_is_reported():
    prefix_list = build_prefix_list(False)
    prefix_list.create.side_effect = Exception("boom")
    session = build_session(prefix_list)
    result = run_module(
        {"name": "L1", "address_family": "ipv4", "state": "create"},
        session,
    )
    assert result["failed"] is True
    assert "Could not create prefix list" in result["msg"]
