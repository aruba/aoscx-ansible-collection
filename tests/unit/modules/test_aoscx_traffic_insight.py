# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_traffic_insight module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_traffic_insight.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_traffic_insight,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_traffic_insight"
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


def build_instance(exists, **attrs):
    instance = MagicMock()
    instance.config_attrs = []
    for attr in ("enable", "source"):
        setattr(instance, attr, attrs.get(attr))
    if exists:
        instance.get.return_value = True
    else:
        instance.get.side_effect = Exception("not found")
    return instance


def build_session(existing, new_instance=None):
    session = MagicMock()
    scalar_attrs = ("enable", "source")

    def get_module(sess, module, index=None, **kwargs):
        if module == "TrafficInsight":
            if (
                any(k in kwargs for k in scalar_attrs)
                and new_instance is not None
            ):
                return new_instance
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_traffic_insight.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    existing = build_instance(False)
    new = build_instance(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {"name": "TI-01", "enable": True, "source": ["ipfix"]},
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_instance(False)
    new = build_instance(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "TI-01",
            "enable": True,
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_enable():
    existing = build_instance(True, enable=True)
    session = build_session(existing)
    result = run_module(
        {"name": "TI-01", "state": "update", "enable": False},
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_instance(True, enable=True, source=["ipfix"])
    session = build_session(existing)
    result = run_module(
        {
            "name": "TI-01",
            "state": "update",
            "enable": True,
            "source": ["ipfix"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    existing = build_instance(True)
    session = build_session(existing)
    result = run_module({"name": "TI-01", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    existing = build_instance(False)
    session = build_session(existing)
    result = run_module({"name": "TI-01", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
