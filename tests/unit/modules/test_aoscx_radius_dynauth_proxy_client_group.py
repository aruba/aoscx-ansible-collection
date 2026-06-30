# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the aoscx_radius_dynauth_proxy_client_group module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_radius_dynauth_proxy_client_group,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_radius_dynauth_proxy_client_group"
)
PREFIX = "/rest/latest/"


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


def coa_uri(address, conn="udp", vrf="default"):
    return (
        PREFIX
        + "system/vrfs/%s/radius_dynamic_authorization_clients/%s,%s"
        % (vrf, address, conn)
    )


def build_group(exists, clients=None):
    group = MagicMock()
    group.clients = clients or {}
    if exists:
        group.get.return_value = True
    else:
        group.get.side_effect = [Exception("nf"), True]
    return group


def build_session(group, coa_exists=True):
    session = MagicMock()
    session.resource_prefix = PREFIX
    session.api.compound_index_separator = ","

    def get_module(sess, module, index=None, **kwargs):
        if module == "RadiusDynauthProxyClientGroup":
            return group
        if module == "RadiusDynamicAuthorizationClient":
            coa = MagicMock()
            if coa_exists:
                coa.get.return_value = True
            else:
                coa.get.side_effect = Exception("no coa")
            return coa
        raise AssertionError(module)

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_radius_dynauth_proxy_client_group.main()
    return exc.value.args[0]


def test_invalid_group_name():
    session = build_session(build_group(False))
    result = run_module({"group_name": "a/b"}, session)
    assert result["failed"] is True


def test_missing_coa_client():
    session = build_session(build_group(False), coa_exists=False)
    result = run_module(
        {"group_name": "g", "clients": [{"address": "192.0.2.41"}]}, session
    )
    assert result["failed"] is True
    assert "Could not find CoA client" in result["msg"]


def test_create_with_clients():
    group = build_group(False)
    session = build_session(group)
    result = run_module(
        {
            "group_name": "g",
            "clients": [{"address": "192.0.2.41"}, {"address": "192.0.2.42"}],
        },
        session,
    )
    assert result["changed"] is True
    group.create.assert_called_once()
    assert group.clients == {"1": coa_uri("192.0.2.41"),
                             "2": coa_uri("192.0.2.42")}


def test_idempotent():
    group = build_group(True, clients={"1": coa_uri("192.0.2.41")})
    session = build_session(group)
    result = run_module(
        {"group_name": "g", "clients": [{"address": "192.0.2.41"}],
         "state": "update"},
        session,
    )
    assert result["changed"] is False
    group.update.assert_not_called()


def test_clear_clients():
    group = build_group(True, clients={"1": coa_uri("192.0.2.41")})
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
