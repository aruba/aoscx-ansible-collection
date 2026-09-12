# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_sflow module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_sflow.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_sflow,
)

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_sflow"


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


def build_sflow(exists, **attrs):
    sflow = MagicMock()
    for attr in (
        "agent_address",
        "enabled",
        "header",
        "max_datagram",
        "mode",
        "polling",
        "sampling",
    ):
        setattr(sflow, attr, attrs.get(attr))
    if exists:
        sflow.get.return_value = True
    else:
        sflow.get.side_effect = Exception("not found")
    return sflow


def build_session(existing, new_sflow=None):
    session = MagicMock()
    scalar_attrs = (
        "agent_address",
        "enabled",
        "header",
        "max_datagram",
        "mode",
        "polling",
        "sampling",
    )

    def get_module(sess, module, index=None, **kwargs):
        if module == "SFlow":
            if (
                any(k in kwargs for k in scalar_attrs)
                and new_sflow is not None
            ):
                return new_sflow
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_sflow.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    existing = build_sflow(False)
    new = build_sflow(False)
    session = build_session(existing, new_sflow=new)
    result = run_module(
        {
            "name": "global",
            "enabled": True,
            "mode": "both",
            "sampling": 4096,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_sflow(False)
    new = build_sflow(False)
    session = build_session(existing, new_sflow=new)
    result = run_module(
        {"name": "global", "mode": "both", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_sampling():
    existing = build_sflow(True, sampling=4096)
    session = build_session(existing)
    result = run_module(
        {"name": "global", "state": "update", "sampling": 2048}, session
    )
    assert result["changed"] is True
    assert existing.sampling == 2048
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_sflow(True, enabled=True, mode="both", sampling=4096)
    session = build_session(existing)
    result = run_module(
        {
            "name": "global",
            "state": "update",
            "enabled": True,
            "mode": "both",
            "sampling": 4096,
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_disable():
    existing = build_sflow(True, enabled=True)
    session = build_session(existing)
    result = run_module(
        {"name": "global", "state": "update", "enabled": False}, session
    )
    assert result["changed"] is True
    assert existing.enabled is False


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    existing = build_sflow(True)
    session = build_session(existing)
    result = run_module({"name": "global", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    existing = build_sflow(False)
    session = build_session(existing)
    result = run_module({"name": "global", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
