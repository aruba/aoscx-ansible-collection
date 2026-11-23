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

GROUP_URI = "/rest/v10.16/system/aaa_server_groups/{0}"

SCALAR_ATTRS = (
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


def build_server(
    exists,
    server_group=None,
    default_group_priority=1,
    group=None,
    user_group_priority=None,
    **attrs
):
    """server_group: firmware 10.19+ model; group: firmware 10.18 model."""
    server = MagicMock()
    server.config_attrs = [] if server_group is None else ["server_group"]
    for attr in SCALAR_ATTRS:
        setattr(server, attr, attrs.get(attr))
    server.server_group = server_group
    server.group = group
    server.user_group_priority = user_group_priority
    server.default_group_priority = default_group_priority
    if exists:
        server.get.return_value = True
    else:
        server.get.side_effect = Exception("not found")
    return server


def build_session(existing, new_instance=None):
    """new_instance: server, or list of servers returned for each creation."""
    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"
    vrf = MagicMock()
    vrf.get.return_value = True
    group_obj = MagicMock()
    group_obj.get.return_value = True
    new_instances = (
        list(new_instance)
        if isinstance(new_instance, (list, tuple))
        else [new_instance]
    )

    def get_module(sess, module, index=None, **kwargs):
        if module == "Vrf":
            return vrf
        if module == "AaaServerGroup":
            return group_obj
        if module == "TacacsServer":
            membership = "server_group" in kwargs or "group" in kwargs
            if membership and new_instances[0] is not None:
                return (
                    new_instances.pop(0)
                    if len(new_instances) > 1
                    else new_instances[0]
                )
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
    create_kwargs = session.api.get_module.call_args.kwargs
    assert create_kwargs["server_group"] == {GROUP_URI.format("tacacs"): 1}
    assert "group" not in create_kwargs


def test_create_uses_user_group_priority():
    new = build_server(False)
    session = build_session(build_server(False), new_instance=new)
    run_module(
        {
            "address": "192.0.2.20",
            "group": ["clearpass-tacacs"],
            "user_group_priority": 2,
        },
        session,
    )
    create_kwargs = session.api.get_module.call_args.kwargs
    assert create_kwargs["server_group"] == {
        GROUP_URI.format("clearpass-tacacs"): 2
    }
    assert "user_group_priority" not in create_kwargs


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
        server_group={GROUP_URI.format("tacacs"): 1},
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
    assert existing.server_group == {GROUP_URI.format("my-tacacs"): 1}


def test_update_group_idempotent():
    existing = build_server(
        True,
        server_group={GROUP_URI.format("tacacs"): 1},
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


def test_create_falls_back_to_group_on_firmware_10_18():
    rejected = build_server(False)
    rejected.create.side_effect = Exception(
        "GENERIC OPERATION ERROR: values in post body not configurable"
    )
    accepted = build_server(False)
    session = build_session(
        build_server(False), new_instance=[rejected, accepted]
    )
    result = run_module(
        {"address": "192.0.2.20", "group": ["clearpass-tacacs"]}, session
    )
    assert result["changed"] is True
    accepted.create.assert_called_once()
    create_kwargs = session.api.get_module.call_args.kwargs
    assert create_kwargs["group"] == [GROUP_URI.format("clearpass-tacacs")]
    assert create_kwargs["user_group_priority"] == 1
    assert "server_group" not in create_kwargs


def test_update_group_on_firmware_10_18():
    existing = build_server(
        True,
        group={"tacacs": GROUP_URI.format("tacacs")},
        user_group_priority=1,
    )
    result = run_module(
        {
            "address": "192.0.2.20",
            "state": "update",
            "group": ["clearpass-tacacs"],
        },
        build_session(existing),
    )
    assert result["changed"] is True
    assert existing.group == [GROUP_URI.format("clearpass-tacacs")]
    assert "group" in existing.config_attrs
    existing.update.assert_called_once()


def test_group_idempotent_on_firmware_10_18():
    existing = build_server(
        True,
        group={"clearpass-tacacs": GROUP_URI.format("clearpass-tacacs")},
        user_group_priority=1,
    )
    result = run_module(
        {
            "address": "192.0.2.20",
            "state": "update",
            "group": ["clearpass-tacacs"],
        },
        build_session(existing),
    )
    assert result["changed"] is False
    existing.update.assert_not_called()
