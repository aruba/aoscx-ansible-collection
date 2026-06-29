# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_ipfix_flow_exporter module.

The pyaoscx session is fully mocked, so no switch is required.

Run with:
    PYTHONPATH=/tmp/acoll2x .venv/bin/python -m pytest \
        tests/unit/modules/test_aoscx_ipfix_flow_exporter.py -v
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_ipfix_flow_exporter,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_ipfix_flow_exporter"
)


class AnsibleExitJson(Exception):
    """Raised by the mocked exit_json to stop module execution."""


class AnsibleFailJson(Exception):
    """Raised by the mocked fail_json to stop module execution."""


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


EXPORTER_ATTRS = (
    "description",
    "destination_type",
    "destination_hostname_or_ip_addr",
    "destination_traffic_insight",
    "template_data_timeout",
    "transport",
)


def build_exporter(exists, **attrs):
    exporter = MagicMock()
    exporter.config_attrs = []
    for attr in EXPORTER_ATTRS:
        setattr(exporter, attr, attrs.get(attr))
    if exists:
        exporter.get.return_value = True
    else:
        exporter.get.side_effect = Exception("not found")
    return exporter


def build_session(existing, new_exporter=None):
    session = MagicMock()
    session.resource_prefix = "/rest/v10.13/"

    def get_module(sess, module, index=None, **kwargs):
        if module == "IpfixFlowExporter":
            if (
                any(k in kwargs for k in EXPORTER_ATTRS)
                and new_exporter is not None
            ):
                return new_exporter
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_ipfix_flow_exporter.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# Create
# --------------------------------------------------------------------------
def test_create_collector():
    existing = build_exporter(False)
    new = build_exporter(False)
    session = build_session(existing, new_exporter=new)
    result = run_module(
        {
            "name": "collector-1",
            "destination_type": "hostname-or-ip-addr",
            "destination": "10.0.0.5",
            "vrf": "default",
            "transport_port": 4739,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()
    # The destination must be turned into a {host: vrf_uri} mapping.
    _, kwargs = session.api.get_module.call_args
    assert kwargs["destination_hostname_or_ip_addr"] == {
        "10.0.0.5": "/rest/v10.13/system/vrfs/default"
    }
    assert kwargs["transport"] == {"port": 4739, "protocol": "udp"}


def test_create_traffic_insight():
    existing = build_exporter(False)
    new = build_exporter(False)
    session = build_session(existing, new_exporter=new)
    result = run_module(
        {
            "name": "ti-exporter",
            "destination_type": "traffic-insight",
            "traffic_insight": "TI-01",
        },
        session,
    )
    assert result["changed"] is True
    _, kwargs = session.api.get_module.call_args
    assert kwargs["destination_traffic_insight"] == "TI-01"


def test_create_check_mode():
    existing = build_exporter(False)
    new = build_exporter(False)
    session = build_session(existing, new_exporter=new)
    result = run_module(
        {
            "name": "collector-1",
            "destination_type": "traffic-insight",
            "traffic_insight": "TI-01",
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


# --------------------------------------------------------------------------
# Update
# --------------------------------------------------------------------------
def test_update_timeout():
    existing = build_exporter(True, template_data_timeout=300)
    session = build_session(existing)
    result = run_module(
        {
            "name": "collector-1",
            "state": "update",
            "template_data_timeout": 600,
        },
        session,
    )
    assert result["changed"] is True
    assert existing.template_data_timeout == 600
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_exporter(
        True,
        destination_type="traffic-insight",
        destination_traffic_insight="TI-01",
    )
    session = build_session(existing)
    result = run_module(
        {
            "name": "ti-exporter",
            "state": "update",
            "destination_type": "traffic-insight",
            "traffic_insight": "TI-01",
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


# --------------------------------------------------------------------------
# Delete
# --------------------------------------------------------------------------
def test_delete():
    existing = build_exporter(True)
    session = build_session(existing)
    result = run_module({"name": "collector-1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    existing = build_exporter(False)
    session = build_session(existing)
    result = run_module({"name": "collector-1", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
