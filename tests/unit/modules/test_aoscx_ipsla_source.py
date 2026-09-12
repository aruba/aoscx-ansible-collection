# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_ipsla_source module.

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
    aoscx_ipsla_source,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_ipsla_source"
)

SCALAR_ATTRS = (
    "type",
    "enable",
    "frequency",
    "history_interval",
    "ipsla_timeout",
    "payload_size",
    "source_ip",
    "source_port_number",
    "tos",
    "domain_name_server",
    "http_sla",
    "https_sla",
    "voip_jitter_sla",
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


def build_source(exists, source_interface=None, **attrs):
    source = MagicMock()
    source.config_attrs = []
    for attr in SCALAR_ATTRS:
        setattr(source, attr, attrs.get(attr))
    source.source_interface = source_interface
    if exists:
        source.get.return_value = True
    else:
        source.get.side_effect = Exception("not found")
    return source


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
        if module == "IpslaSource":
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
            aoscx_ipsla_source.main()
    return exc.value.args[0]


def test_create():
    existing = build_source(False)
    new = build_source(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {"name": "src1", "type": "icmp_echo", "frequency": 30},
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_source(False)
    new = build_source(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "src1",
            "type": "icmp_echo",
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


def test_create_requires_type():
    existing = build_source(False)
    session = build_session(existing)
    result = run_module({"name": "src1"}, session)
    assert result["failed"] is True


def test_update_frequency():
    existing = build_source(True, frequency=60)
    session = build_session(existing)
    result = run_module(
        {"name": "src1", "state": "update", "frequency": 90},
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_source(True, frequency=60, tos=8)
    session = build_session(existing)
    result = run_module(
        {"name": "src1", "state": "update", "frequency": 60, "tos": 8},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_type_is_ignored():
    existing = build_source(True, type="icmp_echo")
    session = build_session(existing)
    result = run_module(
        {"name": "src1", "state": "update", "type": "udp_echo"},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_create_with_interface_and_sla():
    existing = build_source(False)
    new = build_source(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "src1",
            "type": "http",
            "source_interface": "1/1/1",
            "http_sla": {
                "cache_disable": True,
                "type": "get",
                "version_number": "1.1",
            },
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_update_source_interface():
    uri = "/rest/v10.16/system/interfaces/1%2F1%2F1"
    existing = build_source(True, source_interface={"1/1/1": uri})
    session = build_session(existing)
    result = run_module(
        {"name": "src1", "state": "update", "source_interface": "1/1/2"},
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_source_interface_idempotent():
    uri = "/rest/v10.16/system/interfaces/1%2F1%2F1"
    existing = build_source(True, source_interface={"1/1/1": uri})
    session = build_session(existing)
    result = run_module(
        {"name": "src1", "state": "update", "source_interface": "1/1/1"},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_update_sla_idempotent():
    sla = {"cache_disable": True, "type": "get", "version_number": "1.1"}
    existing = build_source(True, http_sla=sla)
    session = build_session(existing)
    result = run_module(
        {"name": "src1", "state": "update", "http_sla": dict(sla)},
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_delete():
    existing = build_source(True)
    session = build_session(existing)
    result = run_module({"name": "src1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    existing = build_source(False)
    session = build_session(existing)
    result = run_module({"name": "src1", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
