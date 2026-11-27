# GNU General Public License v3.0+

import json
from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_evpn,
    aoscx_evpn_vlan,
)
from pyaoscx.evpn_vlan import EvpnVlan
from pyaoscx.rest.v10_16.api import v10_16

EVPN_PATH = "system/evpn"
EVPN_VLAN_PATH = "system/evpn/evpn_vlans/190"
EVPN_VLAN = {
    "arp_suppression_config": None,
    "arp_suppression_extended_config": None,
    "arp_suppression_extended_ip_exemption": [],
    "arp_suppression_ip_exemption": [],
    "nd_suppression_config": None,
    "nd_suppression_extended_config": None,
    "nd_suppression_extended_ip_exemption": [],
    "nd_suppression_ip_exemption": [],
    "rd": "auto",
}
EVPN = {
    "arp_suppression_enable": True,
    "arp_suppression_extended_enable": False,
    "nd_suppression_enable": False,
    "nd_suppression_extended_enable": False,
    "mac_move_count": 5,
}


class ModuleResult(Exception):
    pass


@pytest.fixture
def switch(monkeypatch):
    """Run the real modules and SDK against an in-memory REST transport."""
    state = SimpleNamespace(
        evpn=dict(EVPN), evpn_vlan=dict(EVPN_VLAN), writes=[]
    )

    def request(method, path, params=None, data=None):
        body = json.loads(data) if data is not None else None
        if method != "GET":
            state.writes.append((method, path, body))
        code, response = 200, {}
        if path == EVPN_PATH:
            if method == "PUT":
                state.evpn = body
            code, response = (
                (200, state.evpn) if method == "GET" else (200, {})
            )
        elif path == "system/evpn/evpn_vlans" and method == "POST":
            body.pop("vlan")
            state.evpn_vlan = body
            code = 201
        elif path == EVPN_VLAN_PATH:
            if state.evpn_vlan is None:
                code = 404
            elif method == "PUT":
                state.evpn_vlan = body
            elif method == "GET":
                response = state.evpn_vlan
        elif path == "system/vlans/190":
            response = {"id": 190, "name": "VLAN190"}
        elif path.startswith("system/vlans/190/"):
            response = {}
        else:
            raise AssertionError((method, path))
        return SimpleNamespace(status_code=code, text=json.dumps(response))

    def run(module, **params):
        monkeypatch.setattr(basic, "_load_params", lambda: params)
        with pytest.raises(ModuleResult) as result:
            module.main()
        return result.value.args[0]

    def finish(module, **result):
        raise ModuleResult(result)

    def fail(module, **result):
        finish(module, failed=True, **result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", finish)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail)
    session = SimpleNamespace(
        api=v10_16(),
        connected=True,
        request=request,
        resource_prefix="/rest/v10.16/",
    )
    for module in (aoscx_evpn, aoscx_evpn_vlan):
        monkeypatch.setattr(module, "get_pyaoscx_session", lambda _: session)
    return state, run


def vlan(run, **params):
    return run(aoscx_evpn_vlan, vlan=190, **params)


def test_create_with_suppression_then_rerun_in_another_order(switch):
    state, run = switch
    state.evpn_vlan = None
    options = dict(
        arp_suppression="enable",
        nd_suppression_extended="enable",
        arp_suppression_exclude=["10.1.1.2", "10.1.1.1"],
        nd_suppression_extended_exclude=["FD00::1"],
    )
    assert vlan(run, _ansible_check_mode=True, **options) == {"changed": True}
    assert not state.writes
    assert vlan(run, **options) == {"changed": True}
    ((method, path, body),) = state.writes
    assert (method, path) == ("POST", "system/evpn/evpn_vlans")
    assert body["arp_suppression_config"] == "enable"
    assert body["nd_suppression_extended_config"] == "enable"
    assert body["arp_suppression_ip_exemption"] == ["10.1.1.1", "10.1.1.2"]
    assert body["nd_suppression_extended_ip_exemption"] == ["fd00::1"]
    state.writes.clear()
    options["arp_suppression_exclude"] = ["10.1.1.1", "10.1.1.2", "10.1.1.1"]
    options["nd_suppression_extended_exclude"] = ["fd00:0::1"]
    assert vlan(run, **options) == {"changed": False}
    assert not state.writes


def test_update_keeps_the_other_settings_and_is_idempotent(switch):
    state, run = switch
    options = dict(nd_suppression="disable", nd_suppression_exclude=[])
    assert vlan(run, _ansible_check_mode=True, **options) == {"changed": True}
    assert not state.writes
    assert vlan(run, **options) == {"changed": True}
    ((method, path, body),) = state.writes
    assert (method, path) == ("PUT", EVPN_VLAN_PATH)
    assert body == dict(EVPN_VLAN, nd_suppression_config="disable")
    state.writes.clear()
    assert vlan(run, **options) == {"changed": False}
    assert not state.writes


def test_migration_to_extended_and_back_to_the_global_setting(switch):
    state, run = switch
    vlan(run, arp_suppression="enable")
    assert vlan(
        run, arp_suppression="disable", arp_suppression_extended="enable"
    ) == {"changed": True}
    assert state.evpn_vlan["arp_suppression_config"] == "disable"
    assert state.evpn_vlan["arp_suppression_extended_config"] == "enable"
    assert vlan(
        run, arp_suppression="global", arp_suppression_extended="global"
    ) == {"changed": True}
    assert state.evpn_vlan == EVPN_VLAN


def test_clear_the_exclusions(switch):
    state, run = switch
    state.evpn_vlan["arp_suppression_ip_exemption"] = ["10.1.1.1"]
    assert vlan(run, arp_suppression_exclude=[]) == {"changed": True}
    assert state.evpn_vlan["arp_suppression_ip_exemption"] == []


def test_plain_and_extended_enabled_together_is_refused_in_check_mode(switch):
    state, run = switch
    result = vlan(
        run,
        arp_suppression="enable",
        arp_suppression_extended="enable",
        _ansible_check_mode=True,
    )
    assert result["failed"]
    assert "cannot be enabled together" in result["msg"]
    assert not state.writes


@pytest.mark.parametrize(
    "option, address",
    [
        ("arp_suppression_exclude", "fd00::1"),
        ("nd_suppression_exclude", "10.1.1.1"),
        ("arp_suppression_extended_exclude", "not-an-ip"),
    ],
)
def test_wrong_address_is_refused(switch, option, address):
    state, run = switch
    result = vlan(run, **{option: [address]})
    assert result["failed"]
    assert option.replace("_exclude", "_ip_exemption") in result["msg"]
    assert not state.writes


def test_firmware_without_the_attributes_is_refused(switch):
    state, run = switch
    state.evpn_vlan = {"rd": "auto"}
    result = vlan(run, arp_suppression="enable")
    assert result["failed"]
    assert "not supported by this switch firmware" in result["msg"]
    assert not state.writes


def test_old_pyaoscx_is_reported(switch, monkeypatch):
    state, run = switch
    monkeypatch.delattr(EvpnVlan, "set_suppression_ip_exemption")
    result = vlan(run, arp_suppression="enable")
    assert result["failed"]
    assert "Upgrade pyaoscx" in result["msg"]
    assert vlan(run, rd="auto") == {"changed": False}


def test_global_migration_to_the_extended_versions(switch):
    state, run = switch
    options = dict(
        arp_suppression_enable=False, arp_suppression_extended_enable=True
    )
    assert run(aoscx_evpn, _ansible_check_mode=True, **options) == {
        "changed": True
    }
    assert not state.writes
    assert run(aoscx_evpn, **options) == {"changed": True}
    ((method, path, body),) = state.writes
    assert (method, path) == ("PUT", EVPN_PATH)
    assert body == dict(
        EVPN,
        arp_suppression_enable=False,
        arp_suppression_extended_enable=True,
    )
    state.writes.clear()
    assert run(aoscx_evpn, **options) == {"changed": False}
    assert not state.writes


def test_global_extended_with_the_plain_version_is_refused(switch):
    state, run = switch
    result = run(
        aoscx_evpn,
        nd_suppression_enable=True,
        nd_suppression_extended_enable=True,
    )
    assert result["failed"]
    assert "cannot be enabled together" in result["msg"]
    assert not state.writes


def test_global_extended_on_a_firmware_without_it_is_refused(switch):
    state, run = switch
    del state.evpn["nd_suppression_extended_enable"]
    result = run(aoscx_evpn, nd_suppression_extended_enable=True)
    assert result["failed"]
    assert "not supported by the firmware" in result["msg"]
    assert not state.writes
