# GNU General Public License v3.0+

import json
from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible_collections.arubanetworks.aoscx.plugins.modules import aoscx_vrf
from pyaoscx import vrf
from pyaoscx.rest.v10_16.api import v10_16

VRF_PATH = "system/vrfs/CAMPUS"
FAMILIES_PATH = VRF_PATH + "/vrf_address_families"
RD = "10.140.253.13:20000"
EVPN = {
    "address_family": "evpn",
    "export_route_targets": ["1:1", "65001:20000"],
    "import_route_targets": ["1:1", "65001:20000"],
}


class ModuleResult(Exception):
    pass


@pytest.fixture
def switch(monkeypatch):
    """Run the real module and SDK against an in-memory REST transport."""
    state = SimpleNamespace(vrf=None, families={}, writes=[], errors={})

    def request(method, path, params=None, data=None):
        body = json.loads(data) if data is not None else None
        if method != "GET":
            state.writes.append((method, path, body))
        if path in state.errors:
            code, response = state.errors[path], {}
        elif method == "POST" and path == "system/vrfs":
            state.vrf = body
            code, response = 201, {}
        elif method == "POST" and path == FAMILIES_PATH:
            state.families[body["address_family"]] = body
            code, response = 201, {}
        elif state.vrf is None:
            code, response = 404, {}
        elif path == VRF_PATH:
            if method == "PUT":
                state.vrf = dict(body, name="CAMPUS")
            elif method == "DELETE":
                state.vrf = None
            code, response = (200, state.vrf) if method == "GET" else (204, {})
        elif path == FAMILIES_PATH:
            code, response = 200, {
                name: f"/rest/v10.16/{FAMILIES_PATH}/{name}"
                for name in state.families
            }
        elif path.startswith(FAMILIES_PATH + "/"):
            name = path.rsplit("/", 1)[-1]
            if method == "PUT":
                assert body["address_family"] == name
                state.families[name] = body
            code, response = (
                (200, state.families[name]) if method == "GET" else (204, {})
            )
        else:
            assert (method, path) == ("GET", VRF_PATH + "/static_routes")
            code, response = 200, {}
        return SimpleNamespace(status_code=code, text=json.dumps(response))

    def run(**params):
        monkeypatch.setattr(
            basic, "_load_params", lambda: dict(name="CAMPUS", **params)
        )
        with pytest.raises(ModuleResult) as result:
            aoscx_vrf.main()
        return result.value.args[0]

    def finish(module, **result):
        raise ModuleResult(result)

    def fail(module, **result):
        finish(module, failed=True, **result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", finish)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail)
    session = SimpleNamespace(api=v10_16(), connected=True, request=request)
    monkeypatch.setattr(aoscx_vrf, "get_pyaoscx_session", lambda _: session)
    monkeypatch.setattr(
        vrf,
        "Device",
        lambda _: SimpleNamespace(materialized=True, capabilities=[]),
    )
    monkeypatch.setattr(vrf.Vrf, "get_interfaces", lambda _: [])
    return state, run


def test_create_rd_and_evpn_targets_then_rerun_in_different_order(switch):
    state, run = switch
    assert run(rd=RD, address_families=[EVPN], _ansible_check_mode=True) == {
        "changed": True
    }
    assert not state.writes
    assert run(rd=RD, address_families=[EVPN]) == {"changed": True}
    assert state.writes == [
        (
            "POST",
            "system/vrfs",
            {
                "name": "CAMPUS",
                "rd": RD,
                "evpn_export_route_targets": ["1:1", "65001:20000"],
                "evpn_import_route_targets": ["1:1", "65001:20000"],
            },
        ),
    ]
    state.writes.clear()
    reordered = dict(EVPN, export_route_targets=["65001:20000", "1:1", "1:1"])
    assert run(rd=RD, address_families=[reordered]) == {"changed": False}
    assert not state.writes


def test_update_and_clear_one_direction_without_touching_others(switch):
    state, run = switch
    state.vrf = {
        "name": "CAMPUS",
        "evpn_import_route_targets": ["1:1"],
        "evpn_export_route_targets": ["2:2"],
    }
    state.families["ipv4_unicast"] = {
        "address_family": "ipv4_unicast",
        "export_route_map_name": "EXPORT",
        "export_route_targets": ["2:2"],
        "import_route_targets": ["1:1"],
    }
    families = [
        {"address_family": "evpn", "export_route_targets": []},
        {"address_family": "ipv4_unicast", "import_route_targets": []},
        {"address_family": "ipv6_unicast", "import_route_targets": ["3:3"]},
    ]
    assert run(rd=RD, address_families=families, _ansible_check_mode=True) == {
        "changed": True
    }
    assert not state.writes
    assert run(rd=RD, address_families=families) == {"changed": True}
    assert state.writes == [
        (
            "PUT",
            VRF_PATH,
            {
                "rd": RD,
                "evpn_import_route_targets": ["1:1"],
                "evpn_export_route_targets": [],
            },
        ),
        (
            "PUT",
            FAMILIES_PATH + "/ipv4_unicast",
            {
                "address_family": "ipv4_unicast",
                "export_route_map_name": "EXPORT",
                "export_route_targets": ["2:2"],
                "import_route_targets": [],
            },
        ),
        (
            "POST",
            FAMILIES_PATH,
            {
                "address_family": "ipv6_unicast",
                "import_route_targets": ["3:3"],
            },
        ),
    ]
    state.writes.clear()
    assert run(rd=RD, address_families=families, _ansible_check_mode=True) == {
        "changed": False
    }
    assert not state.writes


def test_existing_create_and_delete_without_route_options(switch):
    state, run = switch
    assert run() == {"changed": True}
    assert run() == {"changed": False}
    assert run(state="delete", _ansible_check_mode=True) == {"changed": True}
    assert run(state="delete") == {"changed": True}
    assert run(state="delete") == {"changed": False}
    assert state.writes == [
        ("POST", "system/vrfs", {"name": "CAMPUS"}),
        ("DELETE", VRF_PATH, None),
    ]


@pytest.mark.parametrize(
    "families",
    [
        [EVPN, EVPN],
        [{"address_family": "evpn"}],
        [{"address_family": "invalid"}],
    ],
)
def test_invalid_family_configuration_fails_without_writes(switch, families):
    state, run = switch
    assert run(address_families=families)["failed"]
    assert not state.writes


@pytest.mark.parametrize("path, code", [(VRF_PATH, 403), (FAMILIES_PATH, 404)])
def test_read_failure_is_not_treated_as_missing_vrf(switch, path, code):
    state, run = switch
    state.vrf = {"name": "CAMPUS"}
    state.errors[path] = code
    assert str(code) in run(rd=RD)["msg"]
    assert not state.writes
