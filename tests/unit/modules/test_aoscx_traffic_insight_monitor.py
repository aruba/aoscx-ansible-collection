# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_traffic_insight_monitor module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_traffic_insight_monitor.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_traffic_insight_monitor,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_traffic_insight_monitor"
)

SCALAR_ATTRS = (
    "filter_by_single_value",
    "group_by",
    "monitor_n_flows",
    "running_stats_reset_interval",
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


def build_instance(exists=True):
    instance = MagicMock()
    if exists:
        instance.get.return_value = True
    else:
        instance.get.side_effect = Exception("not found")
    return instance


def build_monitor(exists, **attrs):
    monitor = MagicMock()
    monitor.config_attrs = []
    for attr in SCALAR_ATTRS:
        setattr(monitor, attr, attrs.get(attr))
    if exists:
        monitor.get.return_value = True
    else:
        monitor.get.side_effect = Exception("not found")
    return monitor


def build_session(instance, existing_monitor, new_monitor=None):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if module == "TrafficInsight":
            return instance
        if module == "TrafficInsightMonitor":
            if (
                any(k in kwargs for k in SCALAR_ATTRS)
                and new_monitor is not None
            ):
                return new_monitor
            return existing_monitor
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_traffic_insight_monitor.main()
    return exc.value.args[0]


BASE = {
    "traffic_insight_instance": "TI-01",
    "monitor_name": "TopN-1",
    "monitor_type": "topN-flows",
}


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    instance = build_instance(exists=True)
    existing = build_monitor(False)
    new = build_monitor(False)
    session = build_session(instance, existing, new_monitor=new)
    args = dict(BASE)
    args.update({"group_by": "appid", "monitor_n_flows": 10})
    result = run_module(args, session)
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    instance = build_instance(exists=True)
    existing = build_monitor(False)
    new = build_monitor(False)
    session = build_session(instance, existing, new_monitor=new)
    args = dict(BASE)
    args.update({"monitor_n_flows": 10, "_ansible_check_mode": True})
    result = run_module(args, session)
    assert result["changed"] is True
    new.create.assert_not_called()


def test_missing_parent_fails():
    instance = build_instance(exists=False)
    existing = build_monitor(False)
    session = build_session(instance, existing)
    args = dict(BASE)
    result = run_module(args, session)
    assert result["failed"] is True


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_n_flows():
    instance = build_instance(exists=True)
    existing = build_monitor(True, monitor_n_flows=10)
    session = build_session(instance, existing)
    args = dict(BASE)
    args.update({"state": "update", "monitor_n_flows": 15})
    result = run_module(args, session)
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    instance = build_instance(exists=True)
    existing = build_monitor(True, group_by="appid", monitor_n_flows=10)
    session = build_session(instance, existing)
    args = dict(BASE)
    args.update(
        {"state": "update", "group_by": "appid", "monitor_n_flows": 10}
    )
    result = run_module(args, session)
    assert result["changed"] is False
    existing.update.assert_not_called()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    instance = build_instance(exists=True)
    existing = build_monitor(True)
    session = build_session(instance, existing)
    args = dict(BASE)
    args.update({"state": "delete"})
    result = run_module(args, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    instance = build_instance(exists=True)
    existing = build_monitor(False)
    session = build_session(instance, existing)
    args = dict(BASE)
    args.update({"state": "delete"})
    result = run_module(args, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
