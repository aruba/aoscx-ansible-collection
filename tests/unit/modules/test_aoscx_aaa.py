# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the state=delete handling of the aoscx_aaa module.

The pyaoscx session and Aaa object are fully mocked, so no switch is required.
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

from ansible_collections.arubanetworks.aoscx.plugins.modules import aoscx_aaa

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_aaa"


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


def run_module(args, current):
    if patch_module_args is None:
        basic._ANSIBLE_ARGS = to_bytes(
            json.dumps({"ANSIBLE_MODULE_ARGS": args})
        )
        args_context = nullcontext()
    else:
        args_context = patch_module_args(args)
    aaa = MagicMock()
    aaa.aaa = dict(current)
    session = MagicMock()
    session.api.get_module.return_value = aaa
    with args_context:
        with patch(MODULE + ".get_pyaoscx_session", return_value=session):
            with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
                aoscx_aaa.main()
    return exc.value.args[0], aaa


CURRENT = {
    "dot1x_auth_enable": True,
    "dot1x_radius_server_group": "clearpass-radius",
    "fail_through": True,
}


def test_delete_removes_server_group_and_disables_flags():
    result, aaa = run_module(
        {
            "dot1x_auth_enable": True,
            "dot1x_radius_server_group": "clearpass-radius",
            "state": "delete",
        },
        CURRENT,
    )
    assert result["changed"] is True
    assert aaa.aaa == {"dot1x_auth_enable": False, "fail_through": True}
    aaa.apply.assert_called_once()


def test_delete_absent_server_group_is_idempotent():
    result, aaa = run_module(
        {
            "mac_auth_radius_server_group": "clearpass-radius",
            "state": "delete",
        },
        CURRENT,
    )
    assert result["changed"] is False
    aaa.apply.assert_not_called()
