# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_gbp_role module.

The pyaoscx session is fully mocked, so no switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from contextlib import nullcontext
from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

try:
    from ansible.module_utils.testing import patch_module_args
except ImportError:  # ansible-core < 2.19
    patch_module_args = None

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_gbp_role,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_gbp_role"
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


@pytest.fixture(autouse=True)
def patch_ansible_module():
    with patch.multiple(
        basic.AnsibleModule,
        exit_json=exit_json,
        fail_json=fail_json,
    ):
        yield


def build_role(exists, role_id=None):
    role = MagicMock()
    role.config_attrs = []
    role.gbp_role_id = role_id
    if exists:
        role.get.return_value = True
    else:
        role.get.side_effect = Exception("not found")
    return role


def build_session(existing, new_instance=None):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if module == "GbpRole":
            if "gbp_role_id" in kwargs and new_instance is not None:
                return new_instance
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    if patch_module_args is None:
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({"ANSIBLE_MODULE_ARGS": args})
        )
        args_context = nullcontext()
    else:
        args_context = patch_module_args(args)
    with args_context:
        with patch(MODULE + ".get_pyaoscx_session", return_value=session):
            with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
                aoscx_gbp_role.main()
    return exc.value.args[0]


def test_create():
    new = build_role(False)
    session = build_session(build_role(False), new_instance=new)
    result = run_module({"name": "fabric_user1", "role_id": 1010}, session)
    assert result["changed"] is True
    new.create.assert_called_once()
    _, _, index = session.api.get_module.call_args.args
    assert index == "fabric_user1"
    assert session.api.get_module.call_args.kwargs == {"gbp_role_id": 1010}


def test_create_check_mode():
    new = build_role(False)
    session = build_session(build_role(False), new_instance=new)
    result = run_module(
        {"name": "r1", "role_id": 400, "_ansible_check_mode": True}, session
    )
    assert result["changed"] is True
    new.create.assert_not_called()


def test_create_requires_role_id():
    result = run_module({"name": "r1"}, build_session(build_role(False)))
    assert result["failed"] is True
    assert "role_id is required" in result["msg"]


def test_create_existing_role_is_idempotent():
    existing = build_role(True, role_id=400)
    result = run_module(
        {"name": "r1", "role_id": 400}, build_session(existing)
    )
    assert result["changed"] is False
    existing.update.assert_not_called()
    existing.create.assert_not_called()


def test_update_role_id():
    existing = build_role(True, role_id=400)
    result = run_module(
        {"name": "r1", "role_id": 401, "state": "update"},
        build_session(existing),
    )
    assert result["changed"] is True
    assert existing.gbp_role_id == 401
    assert "gbp_role_id" in existing.config_attrs
    existing.update.assert_called_once()


@pytest.mark.parametrize("role_id", [-1, 8192])
def test_role_id_out_of_range_rejected(role_id):
    result = run_module(
        {"name": "r1", "role_id": role_id}, build_session(build_role(False))
    )
    assert result["failed"] is True
    assert "between 0 and 8191" in result["msg"]


def test_builtin_role_rejected():
    existing = build_role(True, role_id=2)
    result = run_module(
        {"name": "infra", "state": "delete"}, build_session(existing)
    )
    assert result["failed"] is True
    existing.delete.assert_not_called()


def test_delete():
    existing = build_role(True, role_id=400)
    result = run_module(
        {"name": "r1", "state": "delete"}, build_session(existing)
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent():
    existing = build_role(False)
    result = run_module(
        {"name": "r1", "state": "delete"}, build_session(existing)
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


def test_unsupported_pyaoscx_reports_error():
    session = MagicMock()
    session.api.get_module.side_effect = Exception("unknown module GbpRole")
    result = run_module({"name": "r1", "role_id": 400}, session)
    assert result["failed"] is True
    assert "Upgrade pyaoscx" in result["msg"]
