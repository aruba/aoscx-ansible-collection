# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_port_access_role module.

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
    aoscx_port_access_role,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_port_access_role"
)

CPP_URI = "/rest/v10.16/system/captive_portal_profiles/cp1"


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


def build_role(exists, **attrs):
    role = MagicMock()
    role.config_attrs = []
    for key, value in attrs.items():
        setattr(role, key, value)
    if exists:
        role.get.return_value = True
    else:
        role.get.side_effect = Exception("not found")
    return role


def build_session(existing, new_instance=None, cpp_exists=True):
    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"

    def get_module(sess, module, index=None, **kwargs):
        if module == "PortAccessRole":
            if kwargs and new_instance is not None:
                return new_instance
            return existing
        if module == "CaptivePortalProfile":
            cpp = MagicMock()
            if cpp_exists:
                cpp.get.return_value = True
            else:
                cpp.get.side_effect = Exception("not found")
            return cpp
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_port_access_role.main()
    return exc.value.args[0]


def test_create():
    existing = build_role(False)
    new = build_role(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "role1",
            "description": "r",
            "vlan_mode": "access",
            "vlan_tag": 10,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_role(False)
    new = build_role(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "role1",
            "vlan_mode": "access",
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


def test_create_with_captive_portal():
    existing = build_role(False)
    new = build_role(False)
    session = build_session(existing, new_instance=new, cpp_exists=True)
    result = run_module(
        {
            "name": "role1",
            "vlan_mode": "access",
            "captive_portal_profile": "cp1",
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_captive_portal_missing_fails():
    existing = build_role(False)
    new = build_role(False)
    session = build_session(existing, new_instance=new, cpp_exists=False)
    result = run_module(
        {
            "name": "role1",
            "captive_portal_profile": "cp1",
        },
        session,
    )
    assert result["failed"] is True


def test_update_scalar():
    existing = build_role(True, description="old", vlan_mode="access")
    session = build_session(existing)
    result = run_module(
        {"name": "role1", "state": "update", "description": "new"}, session
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_role(True, description="r", vlan_tag=10)
    session = build_session(existing)
    result = run_module(
        {
            "name": "role1",
            "state": "update",
            "description": "r",
            "vlan_tag": 10,
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_vlan_trunks_order_insensitive():
    existing = build_role(True, vlan_trunks=[10, 20])
    session = build_session(existing)
    result = run_module(
        {"name": "role1", "state": "update", "vlan_trunks": [20, 10]},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_captive_portal_idempotent():
    existing = build_role(True, captive_portal_profile={"cp1": CPP_URI})
    session = build_session(existing)
    result = run_module(
        {
            "name": "role1",
            "state": "update",
            "captive_portal_profile": "cp1",
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_delete():
    existing = build_role(True, description="r")
    session = build_session(existing)
    result = run_module({"name": "role1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent():
    existing = build_role(False)
    session = build_session(existing)
    result = run_module({"name": "role1", "state": "delete"}, session)
    assert result["changed"] is False
