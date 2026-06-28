# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_mirror_endpoint module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_mirror_endpoint.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_mirror_endpoint,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules"
    ".aoscx_mirror_endpoint"
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


def build_port(name):
    port = MagicMock()
    port.name = name
    return port


def build_endpoint(
    exists,
    admin="down",
    comment=None,
    output_port=None,
    tunnel=None,
):
    endpoint = MagicMock()
    endpoint.admin = admin
    endpoint.comment = comment
    endpoint.output_port = [build_port(p) for p in (output_port or [])]
    endpoint.tunnel = dict(tunnel) if tunnel else {}
    if exists:
        endpoint.get.return_value = True
    else:
        endpoint.get.side_effect = Exception("not found")
    return endpoint


def build_session(existing, new_endpoint=None):
    session = MagicMock()
    create_kwargs = ("admin", "comment", "output_port", "tunnel")

    def get_module(sess, module, index=None, **kwargs):
        if module == "MirrorEndpoint":
            if (
                any(k in kwargs for k in create_kwargs)
                and new_endpoint is not None
            ):
                return new_endpoint
            return existing
        if module == "Interface":
            return build_port(index)
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_mirror_endpoint.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create():
    existing = build_endpoint(False)
    new = build_endpoint(False)
    session = build_session(existing, new_endpoint=new)
    result = run_module(
        {
            "name": "erspan1",
            "admin": "up",
            "output_port": ["1/1/10"],
            "tunnel": {
                "src_ip_address": "10.0.0.1",
                "dest_ip_address": "10.0.0.2",
                "id": 100,
            },
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_endpoint(False)
    new = build_endpoint(False)
    session = build_session(existing, new_endpoint=new)
    result = run_module(
        {"name": "erspan1", "admin": "up", "_ansible_check_mode": True},
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_admin():
    existing = build_endpoint(True, admin="down")
    session = build_session(existing)
    result = run_module(
        {"name": "erspan1", "state": "update", "admin": "up"}, session
    )
    assert result["changed"] is True
    assert existing.admin == "up"
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_endpoint(True, admin="up", output_port=["1/1/10"])
    session = build_session(existing)
    result = run_module(
        {
            "name": "erspan1",
            "state": "update",
            "admin": "up",
            "output_port": ["1/1/10"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_output_port_set():
    existing = build_endpoint(True, output_port=["1/1/10"])
    session = build_session(existing)
    result = run_module(
        {
            "name": "erspan1",
            "state": "update",
            "output_port": ["1/1/11"],
        },
        session,
    )
    assert result["changed"] is True
    assert [p.name for p in existing.output_port] == ["1/1/11"]


def test_update_tunnel_merge():
    existing = build_endpoint(
        True, tunnel={"src_ip_address": "10.0.0.1", "id": 100}
    )
    session = build_session(existing)
    result = run_module(
        {
            "name": "erspan1",
            "state": "update",
            "tunnel": {"dest_ip_address": "10.0.0.9"},
        },
        session,
    )
    assert result["changed"] is True
    assert existing.tunnel["dest_ip_address"] == "10.0.0.9"
    # existing keys are preserved
    assert existing.tunnel["src_ip_address"] == "10.0.0.1"
    assert existing.tunnel["id"] == 100


def test_update_tunnel_idempotent():
    existing = build_endpoint(
        True, tunnel={"src_ip_address": "10.0.0.1", "id": 100}
    )
    session = build_session(existing)
    result = run_module(
        {
            "name": "erspan1",
            "state": "update",
            "tunnel": {"id": 100},
        },
        session,
    )
    assert result["changed"] is False


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete_existing():
    existing = build_endpoint(True)
    session = build_session(existing)
    result = run_module({"name": "erspan1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent():
    existing = build_endpoint(False)
    session = build_session(existing)
    result = run_module({"name": "erspan1", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
