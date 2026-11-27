# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_interfaces module.

The real module and pyaoscx SDK run against an in-memory REST transport, so no
switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import copy
import json
import re

from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_interfaces,
)
from pyaoscx.rest.v10_16.api import v10_16

PORT_1 = "system/interfaces/1%2F1%2F1"
PORT_2 = "system/interfaces/1%2F1%2F2"
AUTH = "/port_access_auth_configurations"
STP_DEFAULT = {
    "admin_edge_port_enable": False,
    "bpdu_guard_enable": False,
    "root_guard_enable": False,
    "restricted_port_tcn_disable": False,
    "link_type": "auto",
}


def default_port(name):
    return {
        "name": name,
        "type": "system",
        "admin": None,
        "description": None,
        "routing": False,
        "vlan_mode": None,
        "vlan_tag": None,
        "vlan_trunks": {},
        "loop_protect_enable": False,
        "app_recognition_enable": False,
        "user_config": {"eee": False},
        "stp_config": dict(STP_DEFAULT),
        "port_access_clients_limit": 1,
        "port_access_allow_bpdu": [],
        "port_access_allow_flood_traffic": False,
        "client_ip_track_configuration": {
            "admin_state": "auto",
            "client_limit": 128,
            "update_interval": 1800,
        },
        "device_fingerprint_configuration": {"client_limit": 256},
    }


def vlan_uri(vlan):
    return {str(vlan): "/rest/v10.16/system/vlans/{0}".format(vlan)}


class ModuleResult(Exception):
    pass


@pytest.fixture
def switch(monkeypatch):
    """Run the real module and SDK against an in-memory REST transport."""
    state = SimpleNamespace(
        resources={
            PORT_1: default_port("1/1/1"),
            PORT_2: default_port("1/1/2"),
            "system/vlans/1": {"id": 1},
            "system/vlans/10": {"id": 10},
            "system/vlans/20": {"id": 20},
        },
        writes=[],
        errors={},
    )

    def respond(code, body=None):
        return SimpleNamespace(status_code=code, text=json.dumps(body or {}))

    def request(method, path, params=None, data=None):
        path = path.split("?")[0]
        body = json.loads(data) if data is not None else None
        if method != "GET":
            state.writes.append((method, path, copy.deepcopy(body)))
        if (method, path) in state.errors:
            return respond(*state.errors[(method, path)])
        resources = state.resources
        if method == "GET":
            if path in resources:
                return respond(200, resources[path])
            if path.endswith(AUTH):
                prefix = path + "/"
                return respond(
                    200,
                    dict(
                        (p[len(prefix) :], "/rest/v10.16/" + p)
                        for p in resources
                        if p.startswith(prefix)
                    ),
                )
            if re.search(r"/(macs|static_macs|ip6_addresses)$", path):
                return respond(200)
            return respond(404)
        if method == "PUT":
            assert path in resources
            resources[path] = dict(resources[path], **body)
            return respond(200)
        if method == "POST":
            assert path.endswith(AUTH)
            child = "{0}/{1}".format(path, body["authentication_method"])
            assert child not in resources
            resources[child] = body
            return respond(201)
        if method == "DELETE":
            del resources[path]
            return respond(204)
        raise AssertionError((method, path))

    session = SimpleNamespace(
        api=v10_16(),
        connected=True,
        request=request,
        resource_prefix="/rest/v10.16/",
    )

    def run(**params):
        monkeypatch.setattr(basic, "_load_params", lambda: params)
        with pytest.raises(ModuleResult) as result:
            aoscx_interfaces.main()
        return result.value.args[0]

    def finish(module, **result):
        raise ModuleResult(result)

    def fail(module, **result):
        finish(module, failed=True, **result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", finish)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail)
    monkeypatch.setattr(
        aoscx_interfaces, "get_pyaoscx_session", lambda _: session
    )
    return state, run


ACCESS_PORT = {
    "description": "colorless_port",
    "enabled": True,
    "mtu": 9100,
    "loop_protect_enable": True,
    "app_recognition_enable": True,
    "vlan_mode": "access",
    "vlan_access": 10,
    "stp": {"admin_edge": True, "bpdu_guard": True, "tcn_guard": True},
    "port_access": {
        "concurrent_onboarding": True,
        "client_limit": 2,
        "allow_bpdu": ["lldp", "cdp"],
        "allow_flood_traffic": True,
        "client_ip_track": {"admin_state": "enable", "update_interval": 120},
        "device_fingerprint": {"profile_name": "campus_clients"},
    },
    "dot1x": {"auth_enable": True, "reauth_enable": True, "eapol_timeout": 10},
    "mac_auth": {"auth_enable": True, "quiet_period": 30},
}


def ports(*names, **settings):
    return [copy.deepcopy(dict(settings, name=name)) for name in names]


def test_configure_ports_check_mode_then_apply_then_rerun(switch):
    state, run = switch
    interfaces = ports("1/1/1", "1/1/2", **ACCESS_PORT)

    result = run(interfaces=interfaces, _ansible_check_mode=True)
    assert result == {
        "changed": True,
        "changed_interfaces": ["1/1/1", "1/1/2"],
    }
    assert not state.writes

    result = run(interfaces=interfaces)
    assert result["changed_interfaces"] == ["1/1/1", "1/1/2"]
    port = state.resources[PORT_1]
    assert port["description"] == "colorless_port"
    assert port["admin"] == "up"
    assert port["user_config"] == {"eee": False, "admin": "up", "mtu": 9100}
    assert port["vlan_mode"] == "access"
    assert port["vlan_tag"] == vlan_uri(10)
    assert port["routing"] is False
    assert port["loop_protect_enable"] is True
    assert port["app_recognition_enable"] is True
    assert port["stp_config"] == dict(
        STP_DEFAULT,
        admin_edge_port_enable=True,
        bpdu_guard_enable=True,
        restricted_port_tcn_disable=True,
    )
    assert port["port_access_clients_limit"] == 2
    assert port["port_access_allow_flood_traffic"] is True
    assert port["client_ip_track_configuration"] == {
        "admin_state": "enable",
        "client_limit": 128,
        "update_interval": 120,
    }
    assert port["device_fingerprint_configuration"] == {
        "client_limit": 256,
        "profile_name": "campus_clients",
    }
    assert state.resources[PORT_1 + AUTH + "/dot1x"] == {
        "auth_enable": True,
        "reauth_enable": True,
        "eapol_timeout": 10,
        "authentication_method": "dot1x",
    }
    assert state.resources[PORT_2 + AUTH + "/mac-auth"]["quiet_period"] == 30
    # One PUT per interface: configure_l2() applies every setting at once.
    puts = [w for w in state.writes if w[0] == "PUT"]
    assert [w[1] for w in puts] == [PORT_1, PORT_2]

    state.writes.clear()
    reordered = copy.deepcopy(ACCESS_PORT)
    reordered["port_access"]["allow_bpdu"] = ["cdp", "lldp"]
    result = run(interfaces=ports("1/1/1", "1/1/2", **reordered))
    assert result == {"changed": False, "changed_interfaces": []}
    assert not state.writes


def test_only_supplied_settings_are_changed(switch):
    state, run = switch
    state.resources[PORT_1]["description"] = "keep"
    state.resources[PORT_1 + AUTH + "/dot1x"] = {"reauth_period": 60}

    result = run(
        interfaces=[
            {"name": "1/1/1", "stp": {"root_guard": True}},
            {"name": "1/1/2", "dot1x": {"reauth_period": 60}},
        ]
    )
    assert result == {
        "changed": True,
        "changed_interfaces": ["1/1/1", "1/1/2"],
    }
    port = state.resources[PORT_1]
    assert port["description"] == "keep"
    assert port["vlan_mode"] is None
    assert port["stp_config"] == dict(STP_DEFAULT, root_guard_enable=True)
    assert [(w[0], w[1]) for w in state.writes] == [
        ("PUT", PORT_1),
        ("POST", PORT_2 + AUTH),
    ]
    assert state.writes[0][2]["stp_config"] == port["stp_config"]
    assert state.writes[1][2] == {
        "reauth_period": 60,
        "authentication_method": "dot1x",
    }


def test_trunk_vlans_compared_without_order(switch):
    state, run = switch
    trunk = {
        "vlan_mode": "trunk",
        "native_vlan_id": 10,
        "vlan_trunks": [20, 10],
    }

    assert run(interfaces=ports("1/1/1", **trunk))["changed"] is True
    port = state.resources[PORT_1]
    assert port["vlan_mode"] == "native-untagged"
    assert port["vlan_tag"] == vlan_uri(10)
    assert port["vlan_trunks"] == dict(vlan_uri(10), **vlan_uri(20))

    state.writes.clear()
    trunk["vlan_trunks"] = [10, 20, 20]
    assert run(interfaces=ports("1/1/1", **trunk))["changed"] is False
    assert not state.writes

    assert (
        run(
            interfaces=ports(
                "1/1/1",
                vlan_mode="trunk",
                native_vlan_id=10,
                trunk_allowed_all=True,
            )
        )["changed"]
        is True
    )
    assert state.resources[PORT_1]["vlan_trunks"] == {}


def test_delete_resets_only_the_supplied_settings(switch):
    state, run = switch
    run(interfaces=ports("1/1/1", **ACCESS_PORT))
    state.resources[PORT_1]["loop_protect_enable"] = True
    state.writes.clear()

    delete = {
        "description": "x",
        "enabled": True,
        "mtu": 1,
        "vlan_mode": "access",
        "stp": {"admin_edge": True, "bpdu_guard": True, "tcn_guard": True},
        "port_access": {
            "client_limit": 1,
            "allow_bpdu": [],
            "client_ip_track": {},
            "device_fingerprint": {},
        },
        "dot1x": {},
    }
    result = run(
        interfaces=ports("1/1/1", **delete),
        state="delete",
        _ansible_check_mode=True,
    )
    assert result == {"changed": True, "changed_interfaces": ["1/1/1"]}
    assert not state.writes

    assert (
        run(interfaces=ports("1/1/1", **delete), state="delete")["changed"]
        is True
    )
    port = state.resources[PORT_1]
    default = default_port("1/1/1")
    for attr in (
        "admin",
        "description",
        "user_config",
        "vlan_mode",
        "vlan_tag",
        "vlan_trunks",
        "stp_config",
        "port_access_clients_limit",
        "port_access_allow_bpdu",
        "client_ip_track_configuration",
        "device_fingerprint_configuration",
    ):
        assert port[attr] == default[attr], attr
    # Settings that were not supplied are kept.
    assert port["loop_protect_enable"] is True
    assert port["port_access_allow_flood_traffic"] is True
    assert PORT_1 + AUTH + "/dot1x" not in state.resources
    assert PORT_1 + AUTH + "/mac-auth" in state.resources

    state.writes.clear()
    assert run(interfaces=ports("1/1/1", **delete), state="delete") == {
        "changed": False,
        "changed_interfaces": [],
    }
    assert not state.writes


@pytest.mark.parametrize(
    "settings, message",
    [
        ({"vlan_access": 10}, "the VLAN options require vlan_mode"),
        (
            {"vlan_mode": "access", "vlan_trunks": [10]},
            "vlan_trunks requires vlan_mode trunk",
        ),
        (
            {"vlan_mode": "trunk", "vlan_access": 10},
            "vlan_access requires vlan_mode access",
        ),
        (
            {
                "vlan_mode": "trunk",
                "vlan_trunks": [10],
                "trunk_allowed_all": True,
            },
            "mutually exclusive",
        ),
    ],
)
def test_inconsistent_vlan_options_rejected(switch, settings, message):
    state, run = switch
    result = run(interfaces=ports("1/1/1", **settings))
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes


def test_duplicate_interfaces_rejected(switch):
    state, run = switch
    result = run(interfaces=ports("1/1/1", "1/1/1", description="x"))
    assert result["failed"] is True
    assert "1/1/1" in result["msg"]
    assert not state.writes


def test_failure_reports_the_interfaces_already_changed(switch):
    state, run = switch
    result = run(interfaces=ports("1/1/1", "1/1/9", "1/1/2", description="x"))
    assert result["failed"] is True
    assert "Could not read interface 1/1/9" in result["msg"]
    assert result["changed_interfaces"] == ["1/1/1"]
    assert result["changed"] is True
    assert state.resources[PORT_2]["description"] is None


def test_switch_refusal_is_reported(switch):
    state, run = switch
    state.errors[("PUT", PORT_1)] = (400, {})
    result = run(interfaces=ports("1/1/1", app_recognition_enable=True))
    assert result["failed"] is True
    assert "Could not configure interface 1/1/1" in result["msg"]
    assert result["changed_interfaces"] == []


def test_missing_sdk_class_is_reported(switch, monkeypatch):
    state, run = switch
    real_get_module = v10_16.get_module

    def get_module(self, session, module, index_id=None, **kwargs):
        if module == "PortAccessAuthConfiguration":
            raise Exception("Wrong module name")
        return real_get_module(self, session, module, index_id, **kwargs)

    monkeypatch.setattr(v10_16, "get_module", get_module)
    result = run(interfaces=ports("1/1/1", dot1x={"auth_enable": True}))
    assert result["failed"] is True
    assert "Upgrade pyaoscx" in result["msg"]
