# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the aoscx_radius_dynauth_proxy_server module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_radius_dynauth_proxy_server,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_radius_dynauth_proxy_server"
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
    basic._ANSIBLE_ARGS = to_bytes(
        json.dumps({"ANSIBLE_MODULE_ARGS": args})
    )


@pytest.fixture(autouse=True)
def patch_ansible_module():
    with patch.multiple(
        basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
    ):
        yield


def build_server(exists):
    server = MagicMock()
    if exists:
        server.get.return_value = True
    else:
        server.get.side_effect = [Exception("nf"), True]
    return server


def build_session(server):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        assert module == "RadiusDynauthProxyServer"
        return server

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_radius_dynauth_proxy_server.main()
    return exc.value.args[0]


def test_invalid_address_rejected():
    session = build_session(build_server(False))
    result = run_module({"address": "a,b"}, session)
    assert result["failed"] is True


def test_create_with_secret():
    server = build_server(False)
    session = build_session(server)
    result = run_module(
        {"address": "192.0.2.30", "secret_key": "s"}, session
    )
    assert result["changed"] is True
    server.create.assert_called_once()
    server.update.assert_called_once()
    assert server.secret_key == "s"


def test_idempotent_without_secret():
    server = build_server(True)
    session = build_session(server)
    result = run_module({"address": "192.0.2.30"}, session)
    assert result["changed"] is False
    server.update.assert_not_called()


def test_delete():
    server = build_server(True)
    session = build_session(server)
    result = run_module({"address": "192.0.2.30", "state": "delete"}, session)
    assert result["changed"] is True
    server.delete.assert_called_once()


def test_delete_idempotent():
    server = build_server(False)
    session = build_session(server)
    result = run_module({"address": "192.0.2.30", "state": "delete"}, session)
    assert result["changed"] is False
    server.delete.assert_not_called()
