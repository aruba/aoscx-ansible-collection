# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_bgp_router module.

The real module and pyaoscx SDK run against an in-memory REST transport, so
no switch is required.
"""

import json
from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_bgp_router,
)
from pyaoscx import vrf
from pyaoscx.rest.v10_09.api import v10_09
from pyaoscx.rest.v10_16.api import v10_16

ROUTER_PATH = "system/vrfs/{0}/bgp_routers/65000"

USER_CONFIG = {
    "asn": 65000,
    "router_id": "10.147.253.160",
    "maximum_paths": 8,
    "log_neighbor_changes": True,
    "deterministic_med": True,
    "always_compare_med": True,
    "bestpath_as_path_multipath_relax": True,
    "redistribute": [
        {"address_family": "ipv4_unicast", "route_types": ["connected"]}
    ],
}

SWITCH_CONFIG = {
    "asn": 65000,
    "router_id": "10.147.253.160",
    "maximum_paths": {"all-afs": 8},
    "log_neighbor_changes": True,
    "deterministic_med": True,
    "always_compare_med": True,
    "bestpath_as_path_multipath_relax": True,
    "redistribute": {"ipv4-unicast": ["connected"]},
}


class ModuleResult(Exception):
    pass


@pytest.fixture
def switch(monkeypatch):
    """Run the real module and SDK against an in-memory REST transport."""
    state = SimpleNamespace(
        vrfs={"default", "sense"}, routers={}, writes=[], errors={}
    )

    def request(method, path, params=None, data=None):
        body = json.loads(data) if data is not None else None
        if method != "GET":
            state.writes.append((method, path, body))
        parts = path.split("/")
        code, response = 404, {}
        if path in state.errors:
            code = state.errors[path]
        elif len(parts) < 3 or parts[2] not in state.vrfs:
            pass
        elif len(parts) == 3:
            code, response = 200, {"name": parts[2]}
        elif parts[3:] == ["bgp_routers"] and method == "POST":
            state.routers[(parts[2], str(body["asn"]))] = body
            code = 201
        elif parts[3] == "bgp_routers" and len(parts) == 5:
            key = (parts[2], parts[4])
            if key in state.routers:
                if method == "PUT":
                    state.routers[key] = dict(body, asn=int(parts[4]))
                elif method == "DELETE":
                    del state.routers[key]
                code = 200 if method == "GET" else 204
                response = state.routers.get(key, {})
        elif method == "GET":
            # Child collections (address families, static routes, neighbors)
            code = 200
        return SimpleNamespace(status_code=code, text=json.dumps(response))

    def run(**params):
        monkeypatch.setattr(basic, "_load_params", lambda: params)
        with pytest.raises(ModuleResult) as result:
            aoscx_bgp_router.main()
        return result.value.args[0]

    def finish(module, **result):
        raise ModuleResult(result)

    def fail(module, **result):
        finish(module, failed=True, **result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", finish)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail)
    session = SimpleNamespace(api=v10_16(), connected=True, request=request)
    state.session = session
    monkeypatch.setattr(
        aoscx_bgp_router, "get_pyaoscx_session", lambda _: session
    )
    monkeypatch.setattr(
        vrf,
        "Device",
        lambda _: SimpleNamespace(materialized=True, capabilities=[]),
    )
    return state, run


@pytest.mark.parametrize("vrf_name", ["default", "sense"])
def test_create_then_rerun_is_idempotent(switch, vrf_name):
    state, run = switch
    params = dict(USER_CONFIG, vrf=vrf_name)

    assert run(_ansible_check_mode=True, **params) == {"changed": True}
    assert not state.writes

    assert run(**params) == {"changed": True}
    assert state.writes == [
        ("POST", "system/vrfs/{0}/bgp_routers".format(vrf_name), SWITCH_CONFIG)
    ]

    state.writes.clear()
    reordered = dict(
        params,
        redistribute=[
            {
                "address_family": "ipv4_unicast",
                "route_types": ["connected", "connected"],
            }
        ],
    )
    assert run(**reordered) == {"changed": False}
    assert not state.writes


def test_maximum_paths_is_an_integer_up_to_rest_v10_09(switch):
    state, run = switch
    state.session.api = v10_09()
    params = dict(asn=65000, maximum_paths=8)

    assert run(**params) == {"changed": True}
    assert state.writes == [
        (
            "POST",
            "system/vrfs/default/bgp_routers",
            {"asn": 65000, "maximum_paths": 8},
        )
    ]
    state.writes.clear()
    assert run(**params) == {"changed": False}
    assert run(asn=65000, maximum_paths=4) == {"changed": True}
    assert state.routers[("default", "65000")]["maximum_paths"] == 4


def test_update_only_changes_given_families(switch):
    state, run = switch
    state.routers[("default", "65000")] = {
        "asn": 65000,
        "router_id": "1.1.1.1",
        "maximum_paths": {"all-afs": 4, "l2vpn-evpn": 2},
        "redistribute": {
            "ipv4-unicast": ["static"],
            "ipv6-unicast": ["connected"],
        },
    }
    redistribute = [
        {
            "address_family": "ipv4_unicast",
            "route_types": ["static", "connected"],
        }
    ]

    assert run(asn=65000, maximum_paths=8, redistribute=redistribute) == {
        "changed": True
    }
    assert state.writes == [
        (
            "PUT",
            ROUTER_PATH.format("default"),
            {
                "router_id": "1.1.1.1",
                "maximum_paths": {"all-afs": 8, "l2vpn-evpn": 2},
                "redistribute": {
                    "ipv4-unicast": ["connected", "static"],
                    "ipv6-unicast": ["connected"],
                },
            },
        )
    ]


def test_empty_route_types_removes_redistribution(switch):
    state, run = switch
    state.routers[("default", "65000")] = {
        "asn": 65000,
        "redistribute": {"ipv4-unicast": ["connected"]},
    }
    redistribute = [{"address_family": "ipv4_unicast", "route_types": []}]

    assert run(asn=65000, redistribute=redistribute) == {"changed": True}
    assert state.routers[("default", "65000")]["redistribute"] == {}
    state.writes.clear()
    assert run(asn=65000, redistribute=redistribute) == {"changed": False}
    assert not state.writes


def test_delete(switch):
    state, run = switch
    state.routers[("sense", "65000")] = {"asn": 65000}
    args = dict(asn=65000, vrf="sense", state="delete")

    assert run(_ansible_check_mode=True, **args) == {"changed": True}
    assert not state.writes
    assert run(**args) == {"changed": True}
    # pyaoscx may send a second DELETE (404, ignored) when it unregisters
    # the router from its parent VRF.
    assert {write[:2] for write in state.writes} == {
        ("DELETE", ROUTER_PATH.format("sense"))
    }
    assert not state.routers
    state.writes.clear()
    assert run(**args) == {"changed": False}
    assert not state.writes


def test_missing_vrf_is_reported(switch):
    state, run = switch
    result = run(asn=65000, vrf="missing")
    assert result["failed"] is True
    assert "VRF missing does not exist" in result["msg"]
    assert not state.writes


def test_router_read_error_is_not_treated_as_missing(switch):
    state, run = switch
    state.errors[ROUTER_PATH.format("default")] = 500
    result = run(**USER_CONFIG)
    assert result["failed"] is True
    assert not state.writes


@pytest.mark.parametrize(
    "params, message",
    [
        ({"asn": 0}, "asn must be between"),
        ({"asn": 65000, "maximum_paths": 0}, "maximum_paths must be"),
        (
            {
                "asn": 65000,
                "redistribute": [
                    {"address_family": "ipv4_unicast", "route_types": []},
                    {"address_family": "ipv4_unicast", "route_types": []},
                ],
            },
            "Duplicate redistribute address family",
        ),
    ],
)
def test_invalid_params_rejected(switch, params, message):
    state, run = switch
    result = run(**params)
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes


def test_missing_vrf_in_check_mode_or_delete(switch):
    state, run = switch
    assert run(asn=65000, vrf="missing", _ansible_check_mode=True) == {
        "changed": True
    }
    assert run(asn=65000, vrf="missing", state="delete") == {"changed": False}
    assert not state.writes
