# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for the aoscx_radius_config_attribute module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_radius_config_attribute,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_radius_config_attribute"
)
PA = {"service_type": "port-access"}
UM = {"service_type": "user-management"}


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


def build_entry(exists, **attrs):
    entry = MagicMock()
    for k, v in attrs.items():
        setattr(entry, k, v)
    if exists:
        entry.get.return_value = True
    else:
        entry.get.side_effect = [Exception("nf"), True]
    return entry


def build_session(entry, grp_exists=True):
    session = MagicMock()
    session.resource_prefix = "/rest/latest/"
    session.api.compound_index_separator = ","

    def get_module(sess, module, index=None, **kwargs):
        if module == "RadiusConfigAttribute":
            return entry
        grp = MagicMock()
        if grp_exists:
            grp.get.return_value = True
        else:
            grp.get.side_effect = Exception("nf")
        return grp

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_radius_config_attribute.main()
    return exc.value.args[0]


def test_invalid_server_group():
    result = run_module(
        {"server_group": "a,b"}, build_session(build_entry(False))
    )
    assert result["failed"] is True


def test_missing_server_group():
    session = build_session(build_entry(False), grp_exists=False)
    result = run_module({"server_group": "g", "nas_id": True}, session)
    assert result["failed"] is True
    assert "Could not find AAA server group" in result["msg"]


def test_create_enables_with_correct_service_type():
    entry = build_entry(
        False, framed_ip_addr={}, nas_id={}, nas_ip_addr={},
        tunnel_private_group_id={},
    )
    session = build_session(entry)
    result = run_module(
        {"server_group": "g", "nas_id": True, "nas_ip_addr": True}, session
    )
    assert result["changed"] is True
    entry.create.assert_called_once()
    assert entry.nas_id == PA
    assert entry.nas_ip_addr == UM


def test_idempotent():
    entry = build_entry(
        True, framed_ip_addr=PA, nas_id=PA, nas_ip_addr=UM,
        tunnel_private_group_id=PA,
    )
    session = build_session(entry)
    result = run_module(
        {"server_group": "g", "nas_id": True, "nas_ip_addr": True,
         "state": "update"},
        session,
    )
    assert result["changed"] is False
    entry.update.assert_not_called()


def test_disable_attribute():
    entry = build_entry(
        True, framed_ip_addr=PA, nas_id=PA, nas_ip_addr=UM,
        tunnel_private_group_id=PA,
    )
    session = build_session(entry)
    result = run_module(
        {"server_group": "g", "nas_id": False, "state": "update"}, session
    )
    assert result["changed"] is True
    assert entry.nas_id == {}


def test_delete_idempotent():
    entry = build_entry(False)
    session = build_session(entry)
    result = run_module({"server_group": "g", "state": "delete"}, session)
    assert result["changed"] is False
    entry.delete.assert_not_called()
