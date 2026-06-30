# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_tacacs_server module.

The pyaoscx session is fully mocked, so no switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_tacacs_server,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_tacacs_server"
)

SCALAR_ATTRS = (
    "user_group_priority",
    "auth_type",
    "timeout",
    "tracking_enable",
)


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


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


def build_server(exists, group=None, default_group_priority=1, **attrs):
    server = MagicMock()
    server.config_attrs = []
    for attr in SCALAR_ATTRS:
        setattr(server, attr, attrs.get(attr))
    server.group = group
    server.default_group_priority = default_group_priority
    if exists:
        server.get.return_value = True
    else:
        server.get.side_effect = Exception("not found")
    return server


def build_session(existing, new_instance=None):
    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"
    vrf = MagicMock()
    vrf.get.return_value = True
    group_obj = MagicMock()
    group_obj.get.return_value = True

    def get_module(sess, module, index=None, **kwargs):
        if module == "Vrf":
            return vrf
        if module == "AaaServerGroup":
            return group_obj
        if module == "TacacsServer":
            if "group" in kwargs and new_instance is not None:
                return new_instance
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_tacacs_server.main()
    return exc.value.args[0]


def test_create():
    existing = build_server(False)
    new = build_server(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "address": "192.0.2.20",
            "passkey": "secret",
            "group": ["tacacs"],
            "timeout": 10,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_requires_group():
    existing = build_server(False)
    session = build_session(existing)
    result = run_module(
        {"address": "192.0.2.20", "passkey": "secret"}, session
    )
    assert result["failed"] is True


def test_create_check_mode():
    existing = build_server(False)
    new = build_server(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "address": "192.0.2.20",
            "group": ["tacacs"],
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


def test_update_timeout():
    existing = build_server(True, timeout=10)
    session = build_session(existing)
    result = run_module(
        {"address": "192.0.2.20", "state": "update", "timeout": 20},
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_server(True, timeout=10, default_group_priority=1)
    session = build_session(existing)
    result = run_module(
        {"address": "192.0.2.20", "state": "update", "timeout": 10},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_group():
    existing = build_server(
        True,
        group={"tacacs": "/rest/v10.16/system/aaa_server_groups/tacacs"},
    )
    session = build_session(existing)
    result = run_module(
        {
            "address": "192.0.2.20",
            "state": "update",
            "group": ["my-tacacs"],
        },
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_group_idempotent():
    existing = build_server(
        True,
        group={"tacacs": "/rest/v10.16/system/aaa_server_groups/tacacs"},
    )
    session = build_session(existing)
    result = run_module(
        {
            "address": "192.0.2.20",
            "state": "update",
            "group": ["tacacs"],
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_passkey_always_changes():
    existing = build_server(True, timeout=10)
    session = build_session(existing)
    result = run_module(
        {"address": "192.0.2.20", "state": "update", "passkey": "secret"},
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_delete():
    existing = build_server(True)
    session = build_session(existing)
    result = run_module({"address": "192.0.2.20", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()
