# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_aaa_server_group module.

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
    aoscx_aaa_server_group,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_aaa_server_group"
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


def build_group(exists, group_type=None):
    group = MagicMock()
    group.config_attrs = []
    group.group_type = group_type
    if exists:
        group.get.return_value = True
    else:
        group.get.side_effect = Exception("not found")
    return group


def build_session(existing, new_instance=None):
    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"

    def get_module(sess, module, index=None, **kwargs):
        if module == "AaaServerGroup":
            if "group_type" in kwargs and new_instance is not None:
                return new_instance
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_aaa_server_group.main()
    return exc.value.args[0]


def test_create():
    existing = build_group(False)
    new = build_group(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {"group_name": "grp1", "group_type": "radius"}, session
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_group(False)
    new = build_group(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "group_name": "grp1",
            "group_type": "radius",
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


def test_create_requires_group_type():
    existing = build_group(False)
    session = build_session(existing)
    result = run_module({"group_name": "grp1"}, session)
    assert result["failed"] is True


def test_builtin_group_rejected():
    existing = build_group(True)
    session = build_session(existing)
    result = run_module(
        {"group_name": "radius", "group_type": "radius"}, session
    )
    assert result["failed"] is True


def test_update_group_type():
    existing = build_group(True, group_type="radius")
    session = build_session(existing)
    result = run_module(
        {"group_name": "grp1", "state": "update", "group_type": "tacacs"},
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_group(True, group_type="radius")
    session = build_session(existing)
    result = run_module(
        {"group_name": "grp1", "state": "update", "group_type": "radius"},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_delete():
    existing = build_group(True)
    session = build_session(existing)
    result = run_module({"group_name": "grp1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent():
    existing = build_group(False)
    session = build_session(existing)
    result = run_module({"group_name": "grp1", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
