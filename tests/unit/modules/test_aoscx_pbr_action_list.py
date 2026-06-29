# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_pbr_action_list module.

The pyaoscx session is fully mocked, so no switch is required. The tests
cover input validation, check mode, idempotency, create, the immutable
delete-and-recreate behaviour of entries, prune, delete and error handling.

Run with:
    PYTHONPATH=/tmp/acoll2 .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_pbr_action_list.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

import pytest

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_pbr_action_list,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_pbr_action_list"
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


def build_action_list(exists):
    pal = MagicMock()
    pal.config_attrs = []
    if exists:
        pal.get.return_value = True
    else:
        pal.get.side_effect = Exception("not found")
    return pal


def build_session(action_list, existing_entries=None, new_entry=None):
    session = MagicMock()
    session.resource_prefix = "/rest/v10.09/"
    existing_entries = existing_entries or {}

    def get_module(sess, module, index=None, **kwargs):
        if module == "PbrActionList":
            return action_list
        if module == "PbrActionListEntry":
            if new_entry is not None:
                return new_entry
            created = MagicMock()
            created.config_attrs = []
            return created
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
            aoscx_pbr_action_list.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_name_rejected():
    session = build_session(build_action_list(False))
    result = run_module({"name": "bad/name"}, session)
    assert result["failed"] is True
    assert "Invalid PBR action list name" in result["msg"]


def test_duplicate_sequence_number_rejected():
    session = build_session(build_action_list(False))
    result = run_module(
        {
            "name": "P1",
            "entries": [
                {"sequence_number": 10, "type": "blackhole"},
                {"sequence_number": 10, "type": "blackhole"},
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "Duplicate entry sequence_number" in result["msg"]


def test_nexthop_requires_ip():
    session = build_session(build_action_list(False))
    result = run_module(
        {
            "name": "P1",
            "entries": [{"sequence_number": 10, "type": "nexthop"}],
        },
        session,
    )
    assert result["failed"] is True
    assert "requires 'ip'" in result["msg"]


def test_nexthop_rejects_interface():
    session = build_session(build_action_list(False))
    result = run_module(
        {
            "name": "P1",
            "entries": [
                {
                    "sequence_number": 10,
                    "type": "nexthop",
                    "ip": "10.0.0.1",
                    "interface": "1/1/1",
                }
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "must not set 'interface'" in result["msg"]


def test_interface_requires_interface():
    session = build_session(build_action_list(False))
    result = run_module(
        {
            "name": "P1",
            "entries": [{"sequence_number": 10, "type": "interface"}],
        },
        session,
    )
    assert result["failed"] is True
    assert "requires 'interface'" in result["msg"]


def test_interface_rejects_ip():
    session = build_session(build_action_list(False))
    result = run_module(
        {
            "name": "P1",
            "entries": [
                {
                    "sequence_number": 10,
                    "type": "interface",
                    "interface": "1/1/1",
                    "ip": "10.0.0.1",
                }
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "must not set 'ip'" in result["msg"]


def test_blackhole_rejects_ip():
    session = build_session(build_action_list(False))
    result = run_module(
        {
            "name": "P1",
            "entries": [
                {
                    "sequence_number": 10,
                    "type": "blackhole",
                    "ip": "10.0.0.1",
                }
            ],
        },
        session,
    )
    assert result["failed"] is True
    assert "must not set 'ip'" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_new_action_list():
    pal = build_action_list(False)
    session = build_session(pal)
    result = run_module({"name": "P1", "state": "create"}, session)
    assert result["changed"] is True
    pal.create.assert_called_once()


def test_create_check_mode_does_not_write():
    pal = build_action_list(False)
    session = build_session(pal)
    result = run_module(
        {"name": "P1", "state": "create", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    pal.create.assert_not_called()


def test_create_interface_entry_builds_uri():
    pal = build_action_list(False)
    entry = MagicMock()
    entry.config_attrs = []
    session = build_session(pal, new_entry=entry)
    result = run_module(
        {
            "name": "P1",
            "entries": [
                {
                    "sequence_number": 10,
                    "type": "interface",
                    "interface": "1/1/1",
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    entry.create.assert_called_once()
    called = [
        c
        for c in session.api.get_module.call_args_list
        if c.args[1] == "PbrActionListEntry"
    ][-1]
    assert called.kwargs["type"] == "interface"
    assert called.kwargs["interface"] == (
        "/rest/v10.09/system/interfaces/1%2F1%2F1"
    )


# --------------------------------------------------------------------------
# Idempotency / immutable replace
# --------------------------------------------------------------------------
def test_idempotent_entry_no_change():
    pal = build_action_list(True)
    existing = MagicMock()
    existing.get.return_value = True
    existing.type = "nexthop"
    existing.ip = "10.0.0.1"
    session = build_session(pal, existing_entries={"10": existing})
    result = run_module(
        {
            "name": "P1",
            "state": "update",
            "entries": [
                {"sequence_number": 10, "type": "nexthop", "ip": "10.0.0.1"}
            ],
        },
        session,
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


def test_changed_entry_is_deleted_and_recreated():
    pal = build_action_list(True)
    existing = MagicMock()
    existing.get.return_value = True
    existing.type = "nexthop"
    existing.ip = "10.0.0.1"
    new_entry = MagicMock()
    new_entry.config_attrs = []
    session = build_session(
        pal, existing_entries={"10": existing}, new_entry=new_entry
    )
    result = run_module(
        {
            "name": "P1",
            "state": "update",
            "entries": [
                {"sequence_number": 10, "type": "nexthop", "ip": "10.0.0.2"}
            ],
        },
        session,
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()
    new_entry.create.assert_called_once()


def test_idempotent_interface_entry_no_change():
    pal = build_action_list(True)
    existing = MagicMock()
    existing.get.return_value = True
    existing.type = "interface"
    existing.interface = {"1/1/1": "/rest/v10.09/system/interfaces/1%2F1%2F1"}
    session = build_session(pal, existing_entries={"10": existing})
    result = run_module(
        {
            "name": "P1",
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "type": "interface",
                    "interface": "1/1/1",
                }
            ],
        },
        session,
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


# --------------------------------------------------------------------------
# Prune
# --------------------------------------------------------------------------
def test_prune_removes_stale_entry():
    pal = build_action_list(True)
    stale = MagicMock()
    session = build_session(pal, existing_entries={"20": stale})
    result = run_module(
        {
            "name": "P1",
            "state": "update",
            "entries": [{"sequence_number": 10, "type": "blackhole"}],
        },
        session,
    )
    assert result["changed"] is True
    stale.delete.assert_called_once()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    pal = build_action_list(True)
    session = build_session(pal)
    result = run_module({"name": "P1", "state": "delete"}, session)
    assert result["changed"] is True
    pal.delete.assert_called_once()


def test_delete_absent_no_change():
    pal = build_action_list(False)
    session = build_session(pal)
    result = run_module({"name": "P1", "state": "delete"}, session)
    assert result["changed"] is False
    pal.delete.assert_not_called()


# --------------------------------------------------------------------------
# Error handling
# --------------------------------------------------------------------------
def test_create_error_is_reported():
    pal = build_action_list(False)
    pal.create.side_effect = Exception("boom")
    session = build_session(pal)
    result = run_module({"name": "P1", "state": "create"}, session)
    assert result["failed"] is True
    assert "Could not create PBR action list" in result["msg"]
