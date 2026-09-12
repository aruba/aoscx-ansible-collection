# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the aoscx_radius_proxy_client_group module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_radius_proxy_client_group,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_radius_proxy_client_group"
)


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def exit_json(*args, **kwargs):
    kwargs.setdefault("changed", False)
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def set_module_args(args):
    basic._ANSIBLE_ARGS = to_bytes(json.dumps({"ANSIBLE_MODULE_ARGS": args}))


@pytest.fixture(autouse=True)
def patch_ansible_module():
    with patch.multiple(
        basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
    ):
        yield


def build_group(exists, clients=None):
    group = MagicMock()
    group.clients = clients or {}
    if exists:
        group.get.return_value = True
    else:
        group.get.side_effect = [Exception("nf"), True]
    return group


def build_session(group):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        assert module == "RadiusProxyClientGroup"
        return group

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_radius_proxy_client_group.main()
    return exc.value.args[0]


def test_invalid_group_name():
    result = run_module({"group_name": "a/b"}, build_session(build_group(False)))
    assert result["failed"] is True


def test_create_with_clients():
    group = build_group(False)
    session = build_session(group)
    result = run_module(
        {
            "group_name": "g",
            "clients": [{"address": "192.0.2.50", "secret_key": "s"}],
        },
        session,
    )
    assert result["changed"] is True
    group.create.assert_called_once()
    assert "192.0.2.50" in group.clients


def test_idempotent_without_secret():
    group = build_group(
        True, clients={"192.0.2.50": {"connection_type": "udp"}}
    )
    session = build_session(group)
    result = run_module(
        {"group_name": "g", "clients": [{"address": "192.0.2.50"}],
         "state": "update"},
        session,
    )
    assert result["changed"] is False
    group.update.assert_not_called()


def test_secret_forces_update():
    group = build_group(
        True, clients={"192.0.2.50": {"connection_type": "udp"}}
    )
    session = build_session(group)
    result = run_module(
        {
            "group_name": "g",
            "clients": [{"address": "192.0.2.50", "secret_key": "s"}],
            "state": "update",
        },
        session,
    )
    assert result["changed"] is True


def test_clear_clients():
    group = build_group(
        True, clients={"192.0.2.50": {"connection_type": "udp"}}
    )
    session = build_session(group)
    result = run_module(
        {"group_name": "g", "clients": [], "state": "update"}, session
    )
    assert result["changed"] is True
    assert group.clients == {}


def test_delete_idempotent():
    group = build_group(False)
    session = build_session(group)
    result = run_module({"group_name": "g", "state": "delete"}, session)
    assert result["changed"] is False
    group.delete.assert_not_called()
