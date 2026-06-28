# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_mirror module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_mirror.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_mirror,
)

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_mirror"


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


def build_port(name):
    port = MagicMock()
    port.name = name
    return port


def build_vlan(vlan_id):
    vlan = MagicMock()
    vlan.id = vlan_id
    return vlan


def build_mirror(
    exists,
    session_type="port",
    active=False,
    comment=None,
    select_src_port=None,
    output_port=None,
    select_rx_vlan=None,
):
    mirror = MagicMock()
    mirror.session_type = session_type
    mirror.active = active
    mirror.comment = comment
    mirror.output_port = [build_port(p) for p in (output_port or [])]
    mirror.select_src_port = [build_port(p) for p in (select_src_port or [])]
    mirror.select_dst_port = []
    mirror.select_rx_vlan = [build_vlan(v) for v in (select_rx_vlan or [])]
    mirror.select_tx_vlan = []
    if exists:
        mirror.get.return_value = True
    else:
        mirror.get.side_effect = Exception("not found")
    return mirror


def build_session(existing, new_mirror=None):
    session = MagicMock()
    create_kwargs = (
        "session_type",
        "active",
        "comment",
        "output_port",
        "select_src_port",
        "select_dst_port",
        "select_rx_vlan",
        "select_tx_vlan",
    )

    def get_module(sess, module, index=None, **kwargs):
        if module == "Mirror":
            if (
                any(k in kwargs for k in create_kwargs)
                and new_mirror is not None
            ):
                return new_mirror
            return existing
        if module == "Interface":
            return build_port(index)
        if module == "Vlan":
            return build_vlan(index)
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_mirror.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------
def test_invalid_id_rejected():
    session = build_session(build_mirror(False))
    result = run_module({"mirror_id": 0}, session)
    assert result["failed"] is True
    assert "positive integer" in result["msg"]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    existing = build_mirror(False)
    new = build_mirror(False)
    session = build_session(existing, new_mirror=new)
    result = run_module(
        {
            "mirror_id": 5,
            "session_type": "port",
            "active": True,
            "select_src_port": ["1/1/1"],
            "output_port": ["1/1/10"],
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_mirror(False)
    new = build_mirror(False)
    session = build_session(existing, new_mirror=new)
    result = run_module(
        {"mirror_id": 5, "session_type": "port", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_active():
    existing = build_mirror(True, active=False)
    session = build_session(existing)
    result = run_module(
        {"mirror_id": 5, "state": "update", "active": True}, session
    )
    assert result["changed"] is True
    assert existing.active is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_mirror(True, active=True, select_src_port=["1/1/1"])
    session = build_session(existing)
    result = run_module(
        {
            "mirror_id": 5,
            "state": "update",
            "active": True,
            "select_src_port": ["1/1/1"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_src_port_set():
    existing = build_mirror(True, select_src_port=["1/1/1"])
    session = build_session(existing)
    result = run_module(
        {
            "mirror_id": 5,
            "state": "update",
            "select_src_port": ["1/1/2"],
        },
        session,
    )
    assert result["changed"] is True
    assert [p.name for p in existing.select_src_port] == ["1/1/2"]
    existing.update.assert_called_once()


def test_update_rx_vlan_set():
    existing = build_mirror(True, select_rx_vlan=[10])
    session = build_session(existing)
    result = run_module(
        {
            "mirror_id": 5,
            "state": "update",
            "select_rx_vlan": [10, 20],
        },
        session,
    )
    assert result["changed"] is True
    assert sorted(v.id for v in existing.select_rx_vlan) == [10, 20]


def test_update_vlan_idempotent_order_insensitive():
    existing = build_mirror(True, select_rx_vlan=[20, 10])
    session = build_session(existing)
    result = run_module(
        {
            "mirror_id": 5,
            "state": "update",
            "select_rx_vlan": [10, 20],
        },
        session,
    )
    assert result["changed"] is False


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    existing = build_mirror(True)
    session = build_session(existing)
    result = run_module({"mirror_id": 5, "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent():
    existing = build_mirror(False)
    session = build_session(existing)
    result = run_module({"mirror_id": 5, "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
