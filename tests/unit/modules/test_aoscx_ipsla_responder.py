# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_ipsla_responder module.

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
    aoscx_ipsla_responder,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_ipsla_responder"
)

SCALAR_ATTRS = (
    "type",
    "responder_port_number",
    "responder_type",
    "responder_ip",
    "persistence",
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


def build_responder(
    exists, vrf_name="default", responder_interface=None, **attrs
):
    responder = MagicMock()
    responder.config_attrs = []
    for attr in SCALAR_ATTRS:
        setattr(responder, attr, attrs.get(attr))
    responder.vrf = {vrf_name: "/rest/v10.16/system/vrfs/" + vrf_name}
    responder.responder_interface = responder_interface
    if exists:
        responder.get.return_value = True
    else:
        responder.get.side_effect = Exception("not found")
    return responder


def build_session(existing, new_instance=None):
    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"
    vrf = MagicMock()
    vrf.get.return_value = True
    interface = MagicMock()
    interface.get.return_value = True

    def get_module(sess, module, index=None, **kwargs):
        if module == "Vrf":
            return vrf
        if module == "Interface":
            return interface
        if module == "IpslaResponder":
            if "vrf" in kwargs and new_instance is not None:
                return new_instance
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_ipsla_responder.main()
    return exc.value.args[0]


def test_create():
    existing = build_responder(False)
    new = build_responder(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "resp1",
            "type": "udp_echo",
            "responder_port_number": 5000,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_with_interface():
    existing = build_responder(False)
    new = build_responder(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "resp1",
            "type": "udp_echo",
            "responder_port_number": 5000,
            "responder_interface": "1/1/1",
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_recreate_on_interface_change():
    uri = "/rest/v10.16/system/interfaces/1%2F1%2F1"
    existing = build_responder(
        True,
        type="udp_echo",
        responder_port_number=5000,
        responder_interface={"1/1/1": uri},
    )
    new = build_responder(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "resp1",
            "type": "udp_echo",
            "responder_port_number": 5000,
            "responder_interface": "1/1/2",
        },
        session,
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()
    new.create.assert_called_once()


def test_interface_idempotent():
    uri = "/rest/v10.16/system/interfaces/1%2F1%2F1"
    existing = build_responder(
        True,
        type="udp_echo",
        responder_port_number=5000,
        responder_interface={"1/1/1": uri},
    )
    session = build_session(existing)
    result = run_module(
        {
            "name": "resp1",
            "type": "udp_echo",
            "responder_port_number": 5000,
            "responder_interface": "1/1/1",
        },
        session,
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


def test_create_check_mode():
    existing = build_responder(False)
    new = build_responder(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "resp1",
            "type": "udp_echo",
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


def test_recreate_on_diff():
    existing = build_responder(
        True, type="udp_echo", responder_port_number=5000
    )
    new = build_responder(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "resp1",
            "type": "udp_echo",
            "responder_port_number": 6000,
        },
        session,
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()
    new.create.assert_called_once()


def test_idempotent():
    existing = build_responder(
        True, type="udp_echo", responder_port_number=5000
    )
    session = build_session(existing)
    result = run_module(
        {
            "name": "resp1",
            "type": "udp_echo",
            "responder_port_number": 5000,
        },
        session,
    )
    assert result["changed"] is False
    existing.delete.assert_not_called()


def test_delete():
    existing = build_responder(True)
    session = build_session(existing)
    result = run_module({"name": "resp1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    existing = build_responder(False)
    session = build_session(existing)
    result = run_module({"name": "resp1", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
