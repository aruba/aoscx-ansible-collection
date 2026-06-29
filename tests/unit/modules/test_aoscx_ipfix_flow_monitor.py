# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_ipfix_flow_monitor module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_ipfix_flow_monitor.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_ipfix_flow_monitor,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_ipfix_flow_monitor"
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


def named_obj(name):
    obj = MagicMock()
    obj.name = name
    return obj


MONITOR_ATTRS = (
    "description",
    "cache_timeout_active",
    "cache_timeout_inactive",
    "exporter",
    "record",
)


def build_monitor(exists, exporters=None, record=None, **attrs):
    monitor = MagicMock()
    monitor.config_attrs = []
    for attr in (
        "description",
        "cache_timeout_active",
        "cache_timeout_inactive",
    ):
        setattr(monitor, attr, attrs.get(attr))
    monitor.exporter = (
        [named_obj(n) for n in exporters] if exporters is not None else None
    )
    monitor.record = named_obj(record) if record is not None else None
    if exists:
        monitor.get.return_value = True
    else:
        monitor.get.side_effect = Exception("not found")
    return monitor


def build_session(existing, new_monitor=None):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if module == "IpfixFlowMonitor":
            if (
                any(k in kwargs for k in MONITOR_ATTRS)
                and new_monitor is not None
            ):
                return new_monitor
            return existing
        if module in ("IpfixFlowExporter", "IpfixFlowRecord"):
            return named_obj(index)
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_ipfix_flow_monitor.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    existing = build_monitor(False)
    new = build_monitor(False)
    session = build_session(existing, new_monitor=new)
    result = run_module(
        {
            "name": "monitor-1",
            "record": "ipv4-record",
            "exporters": ["collector-1"],
            "cache_timeout_active": 60,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_monitor(False)
    new = build_monitor(False)
    session = build_session(existing, new_monitor=new)
    result = run_module(
        {
            "name": "monitor-1",
            "record": "ipv4-record",
            "exporters": ["collector-1"],
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_add_exporter():
    existing = build_monitor(
        True, exporters=["collector-1"], record="ipv4-record"
    )
    session = build_session(existing)
    result = run_module(
        {
            "name": "monitor-1",
            "state": "update",
            "exporters": ["collector-1", "collector-2"],
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_monitor(
        True,
        exporters=["collector-1"],
        record="ipv4-record",
        cache_timeout_active=60,
    )
    session = build_session(existing)
    result = run_module(
        {
            "name": "monitor-1",
            "state": "update",
            "exporters": ["collector-1"],
            "record": "ipv4-record",
            "cache_timeout_active": 60,
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_exporter_order_insensitive():
    existing = build_monitor(True, exporters=["collector-1", "collector-2"])
    session = build_session(existing)
    result = run_module(
        {
            "name": "monitor-1",
            "state": "update",
            "exporters": ["collector-2", "collector-1"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_record():
    existing = build_monitor(True, record="ipv4-record")
    session = build_session(existing)
    result = run_module(
        {
            "name": "monitor-1",
            "state": "update",
            "record": "ipv6-record",
        },
        session,
    )
    assert result["changed"] is True
    assert existing.record.name == "ipv6-record"
    existing.update.assert_called_once()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    existing = build_monitor(True)
    session = build_session(existing)
    result = run_module({"name": "monitor-1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    existing = build_monitor(False)
    session = build_session(existing)
    result = run_module({"name": "monitor-1", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
