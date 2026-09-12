# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the aoscx_radius_dynauth_proxy_profile module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_radius_dynauth_proxy_profile,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_radius_dynauth_proxy_profile"
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


def build_profile(exists, **attrs):
    profile = MagicMock()
    for k, v in attrs.items():
        setattr(profile, k, v)
    if exists:
        profile.get.return_value = True
    else:
        profile.get.side_effect = [Exception("nf"), True]
    return profile


def build_session(profile, ref_exists=True):
    session = MagicMock()
    session.resource_prefix = PREFIX
    session.api.compound_index_separator = ","

    def get_module(sess, module, index=None, **kwargs):
        if module == "RadiusDynauthProxyProfile":
            return profile
        ref = MagicMock()
        if ref_exists:
            ref.get.return_value = True
        else:
            ref.get.side_effect = Exception("nf")
        return ref

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_radius_dynauth_proxy_profile.main()
    return exc.value.args[0]


def test_invalid_profile_name():
    session = build_session(build_profile(False))
    result = run_module({"profile_name": "a/b"}, session)
    assert result["failed"] is True


def test_missing_client_group():
    session = build_session(build_profile(False), ref_exists=False)
    result = run_module(
        {"profile_name": "p", "client_group": "cg"}, session
    )
    assert result["failed"] is True
    assert "Could not find client group" in result["msg"]


def test_create_ties_refs():
    profile = build_profile(
        False, enabled=False, vrf={}, dynauth_client_group={},
        dynauth_server={},
    )
    session = build_session(profile)
    result = run_module(
        {
            "profile_name": "p",
            "enabled": True,
            "client_group": "cg",
            "server": {"address": "192.0.2.30"},
        },
        session,
    )
    assert result["changed"] is True
    profile.create.assert_called_once()
    assert profile.enabled is True
    assert "cg" in profile.dynauth_client_group
    assert "192.0.2.30,3799,udp" in profile.dynauth_server


def test_idempotent():
    profile = build_profile(
        True,
        enabled=True,
        vrf={"default": PREFIX + "system/vrfs/default"},
        dynauth_client_group={
            "cg": PREFIX + "system/radius_dynauth_proxy_client_groups/cg"
        },
        dynauth_server={},
    )
    session = build_session(profile)
    result = run_module(
        {
            "profile_name": "p",
            "enabled": True,
            "client_group": "cg",
            "state": "update",
        },
        session,
    )
    assert result["changed"] is False
    profile.update.assert_not_called()


def test_disable_update():
    profile = build_profile(
        True,
        enabled=True,
        vrf={"default": PREFIX + "system/vrfs/default"},
        dynauth_client_group={},
        dynauth_server={},
    )
    session = build_session(profile)
    result = run_module(
        {"profile_name": "p", "enabled": False, "state": "update"}, session
    )
    assert result["changed"] is True
    assert profile.enabled is False


def test_delete_idempotent():
    profile = build_profile(False)
    session = build_session(profile)
    result = run_module({"profile_name": "p", "state": "delete"}, session)
    assert result["changed"] is False
    profile.delete.assert_not_called()
