# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_sflow_collector module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_sflow_collector.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_sflow_collector,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_sflow_collector"
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


def build_collector(exists):
    collector = MagicMock()
    if exists:
        collector.get.return_value = True
    else:
        collector.get.side_effect = Exception("not found")
    return collector


def build_session(collector, sflow_exists=True):
    session = MagicMock()
    sflow = MagicMock()
    if sflow_exists:
        sflow.get.return_value = True
    else:
        sflow.get.side_effect = Exception("not found")
    vrf = MagicMock()
    vrf.name = "default"

    def get_module(sess, module, index=None, **kwargs):
        if module == "SFlow":
            return sflow
        if module == "Vrf":
            return vrf
        if module == "SFlowCollector":
            return collector
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_sflow_collector.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    collector = build_collector(False)
    session = build_session(collector)
    result = run_module(
        {
            "sflow_name": "global",
            "ip_address": "10.0.0.50",
            "udp_port": 6343,
        },
        session,
    )
    assert result["changed"] is True
    collector.create.assert_called_once()


def test_create_idempotent():
    collector = build_collector(True)
    session = build_session(collector)
    result = run_module(
        {
            "sflow_name": "global",
            "ip_address": "10.0.0.50",
        },
        session,
    )
    assert result["changed"] is False
    collector.create.assert_not_called()


def test_create_check_mode():
    collector = build_collector(False)
    session = build_session(collector)
    result = run_module(
        {
            "sflow_name": "global",
            "ip_address": "10.0.0.50",
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    collector.create.assert_not_called()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    collector = build_collector(True)
    session = build_session(collector)
    result = run_module(
        {
            "sflow_name": "global",
            "ip_address": "10.0.0.50",
            "state": "delete",
        },
        session,
    )
    assert result["changed"] is True
    collector.delete.assert_called_once()


def test_delete_absent_noop():
    collector = build_collector(False)
    session = build_session(collector)
    result = run_module(
        {
            "sflow_name": "global",
            "ip_address": "10.0.0.50",
            "state": "delete",
        },
        session,
    )
    assert result["changed"] is False
    collector.delete.assert_not_called()


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_missing_parent_fails():
    collector = build_collector(False)
    session = build_session(collector, sflow_exists=False)
    result = run_module(
        {
            "sflow_name": "ghost",
            "ip_address": "10.0.0.50",
        },
        session,
    )
    assert result["failed"] is True
    assert "does not exist" in result["msg"]
