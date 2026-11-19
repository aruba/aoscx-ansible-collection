# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_bgp_router module.

The real module and pyaoscx SDK run against an in-memory REST transport, so
no switch is required.
"""

import json
from urllib.parse import quote_plus, unquote
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


def flatten(value):
    """{"a": {"b": x}} -> {"a,b": x}, as returned by the switch."""
    return {
        "{0},{1}".format(key, sub): item
        for key, nested in (value or {}).items()
        for sub, item in nested.items()
    }


def has_compound_keys(value):
    return any("," in key for key in (value or {}))


class ModuleResult(Exception):
    pass


@pytest.fixture
def switch(monkeypatch):
    """Run the real module and SDK against an in-memory REST transport."""
    state = SimpleNamespace(
        vrfs={"default", "sense"},
        routers={},
        aggregates={},
        route_maps={"RM_CONN", "RM_STATIC"},
        writes=[],
        errors={},
    )

    def request(method, path, params=None, data=None):
        body = json.loads(data) if data is not None else None
        if method != "GET":
            state.writes.append((method, path, body))
        parts = path.split("/")
        code, response = 404, {}
        compound = ("redistribute_route_map", "networks_route_maps")
        if body and any(has_compound_keys(body.get(a)) for a in compound):
            # The switch rejects the format it returns
            code = 400
        elif path in state.errors:
            code = state.errors[path]
        elif path.startswith("system/route_maps/"):
            code = 200 if parts[2] in state.route_maps else 404
        elif len(parts) < 3 or parts[2] not in state.vrfs:
            pass
        elif len(parts) == 3:
            code, response = 200, {"name": parts[2]}
        elif len(parts) >= 6 and parts[5] == "aggregate_addresses":
            code, response = aggregate_request(method, parts, body)
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
                response = dict(state.routers.get(key, {}))
                for attribute in compound:
                    if attribute in response:
                        response[attribute] = flatten(response[attribute])
        elif method == "GET":
            # Child collections (address families, static routes, neighbors)
            code = 200
        return SimpleNamespace(status_code=code, text=json.dumps(response))

    def aggregate_request(method, parts, body):
        router = (parts[2], parts[4])
        if router not in state.routers:
            return 404, {}
        aggregates = state.aggregates.setdefault(router, {})
        base = "/rest/v10.16/" + "/".join(parts[:6])
        if len(parts) == 6:
            if method == "POST":
                key = "{0},{1}".format(
                    body.pop("address-family"), body.pop("ip_prefix")
                )
                aggregates[key] = dict({"options": "none"}, **body)
                return 201, {}
            uris = {}
            for key in aggregates:
                family, prefix = key.split(",")
                uris[key] = "{0}/{1},{2}".format(
                    base, family, quote_plus(prefix)
                )
            return 200, uris
        key = unquote(parts[6])
        if key not in aggregates:
            return 404, {}
        if method == "GET":
            return 200, aggregates[key]
        if method == "PUT":
            aggregates[key] = body
            return 200, {}
        del aggregates[key]
        return 204, {}

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
    session = SimpleNamespace(
        api=v10_16(),
        connected=True,
        request=request,
        resource_prefix="/rest/v10.16/",
    )
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


def test_redistribute_route_maps(switch):
    state, run = switch
    rm = "/rest/v10.16/system/route_maps/"
    state.routers[("default", "65000")] = {
        "asn": 65000,
        "redistribute": {"ipv6-unicast": ["connected"]},
    }
    redistribute = [
        {
            "address_family": "ipv4_unicast",
            "route_types": ["connected", "static", "ospf"],
            "route_maps": {"connected": "RM_CONN", "static": "RM_STATIC"},
        }
    ]

    assert run(asn=65000, redistribute=redistribute) == {"changed": True}
    router = state.routers[("default", "65000")]
    assert router["redistribute"] == {
        "ipv4-unicast": ["ospf"],
        "ipv6-unicast": ["connected"],
    }
    assert router["redistribute_route_map"] == {
        "ipv4-unicast": {
            "connected": rm + "RM_CONN",
            "static": rm + "RM_STATIC",
        }
    }

    # The switch returns compound keys: no change, and a later update of
    # another option sends nested dictionaries again
    state.writes.clear()
    assert run(asn=65000, redistribute=redistribute) == {"changed": False}
    assert not state.writes
    assert run(asn=65000, router_id="1.1.1.1") == {"changed": True}
    assert router is not state.routers[("default", "65000")]
    assert state.routers[("default", "65000")]["redistribute_route_map"] == {
        "ipv4-unicast": {
            "connected": rm + "RM_CONN",
            "static": rm + "RM_STATIC",
        }
    }

    # Without route_maps, the route types are redistributed without them
    plain = [dict(redistribute[0], route_maps=None)]
    assert run(asn=65000, redistribute=plain) == {"changed": True}
    router = state.routers[("default", "65000")]
    assert router["redistribute"]["ipv4-unicast"] == [
        "connected",
        "ospf",
        "static",
    ]
    assert router["redistribute_route_map"] == {}


@pytest.mark.parametrize(
    "route_maps, message",
    [
        ({"static": "RM_STATIC"}, "static is not in the route_types"),
        ({"connected": "MISSING"}, "Could not find route map MISSING"),
    ],
)
def test_redistribute_route_map_errors(switch, route_maps, message):
    state, run = switch
    redistribute = [
        {
            "address_family": "ipv4_unicast",
            "route_types": ["connected"],
            "route_maps": route_maps,
        }
    ]
    result = run(asn=65000, redistribute=redistribute)
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes


def test_global_options(switch):
    state, run = switch
    params = dict(
        asn=65000,
        cluster_id="1.1.1.1",
        default_local_preference=150,
        maxas_limit=20,
        asnotation="dotted",
        trap_enable=True,
        disable=False,
        aggregate_split_horizon=False,
        bestpath_as_path_ignore=True,
        bestpath_compare_routerid=True,
        bestpath_med_confed=True,
        bestpath_med_missing_as_worst=True,
        bestpath_bgp_std_selection=True,
        timers={"keepalive": 20, "holdtime": 60},
        distance={"ebgp": 30, "ibgp": 210},
        graceful_restart={
            "enable": True,
            "restart_time": 200,
            "stalepath_time": 400,
        },
        confederation={"identifier": 100, "peers": [65011, 65010]},
    )
    state.routers[("default", "65000")] = {
        "asn": 65000,
        "timers": {"connect-retry": 120, "holdtime": 180, "keepalive": 60},
    }

    assert run(**params) == {"changed": True}
    router = state.routers[("default", "65000")]
    assert {k: v for k, v in router.items() if k != "asn"} == {
        "cluster_id": "1.1.1.1",
        "local_pref": 150,
        "maxas_limit": 20,
        "asnotation": "dotted",
        "trap_enable": True,
        "protocol_disable": False,
        "agg_split_horizon": False,
        "bestpath_as_path_ignore": True,
        "bestpath_compare_routerid": True,
        "bestpath_med_confed": True,
        "bestpath_med_missing_as_worst": True,
        "bestpath_bgp_std_selection": True,
        "timers": {"connect-retry": 120, "holdtime": 60, "keepalive": 20},
        "ebgp_distance": 30,
        "ibgp_distance": 210,
        "gr_enable": True,
        "gr_restart_timer": 200,
        "gr_stale_timer": 400,
        "confederation_id": 100,
        "confederation_peers": [65010, 65011],
    }
    state.writes.clear()
    assert run(**params) == {"changed": False}
    assert not state.writes

    removal = dict(
        asn=65000,
        cluster_id="",
        confederation={"identifier": 0, "peers": []},
    )
    assert run(**removal) == {"changed": True}
    router = state.routers[("default", "65000")]
    assert router["cluster_id"] is None
    assert router["confederation_id"] is None
    assert router["confederation_peers"] == []
    assert run(**removal) == {"changed": False}


def test_networks_and_dampening(switch):
    state, run = switch
    rm = "/rest/v10.16/system/route_maps/"
    state.routers[("default", "65000")] = {
        "asn": 65000,
        "networks": {"ipv6-unicast": ["2001:db8::/32"]},
    }
    families = [
        {
            "address_family": "ipv4_unicast",
            "networks": [
                {"prefix": "10.1.0.0/16", "route_map": "RM_CONN"},
                {"prefix": "10.3.0.1/16"},
            ],
            "dampening": {"half_life": 10, "reuse": 800},
            "dampening_route_map": "RM_STATIC",
        }
    ]

    assert run(asn=65000, address_families=families) == {"changed": True}
    router = state.routers[("default", "65000")]
    assert router["networks"] == {
        "ipv4-unicast": ["10.3.0.0/16"],
        "ipv6-unicast": ["2001:db8::/32"],
    }
    assert router["networks_route_maps"] == {
        "ipv4-unicast": {"10.1.0.0/16": rm + "RM_CONN"}
    }
    assert router["dampening"] == {
        "ipv4-unicast": {"half_life": 10, "reuse": 800}
    }
    assert router["dampening_route_map"] == {"ipv4-unicast": rm + "RM_STATIC"}

    # The switch returns networks_route_maps with compound keys
    state.writes.clear()
    assert run(asn=65000, address_families=families) == {"changed": False}
    assert not state.writes
    assert run(asn=65000, router_id="1.1.1.1") == {"changed": True}

    removal = [
        {
            "address_family": "ipv4_unicast",
            "networks": [],
            "dampening": {},
            "dampening_route_map": "",
        }
    ]
    assert run(asn=65000, address_families=removal) == {"changed": True}
    router = state.routers[("default", "65000")]
    assert router["networks"] == {"ipv6-unicast": ["2001:db8::/32"]}
    assert router["networks_route_maps"] == {}
    assert router["dampening"] == {}
    assert router["dampening_route_map"] == {}


def test_aggregate_addresses(switch):
    state, run = switch
    rm = "/rest/v10.16/system/route_maps/"
    state.routers[("default", "65000")] = {"asn": 65000}
    state.aggregates[("default", "65000")] = {
        "ipv4-unicast,10.9.0.0/16": {"options": "none"},
        "ipv6-unicast,2001:db8::/32": {"options": "as-set"},
    }
    families = [
        {
            "address_family": "ipv4_unicast",
            "aggregate_addresses": [
                {
                    "prefix": "10.2.0.0/16",
                    "options": "summary-only",
                    "suppress_map": "RM_CONN",
                },
                {"prefix": "10.4.0.0/16"},
            ],
        }
    ]

    assert run(
        _ansible_check_mode=True, asn=65000, address_families=families
    ) == {"changed": True}
    assert not state.writes
    assert run(asn=65000, address_families=families) == {"changed": True}
    assert state.aggregates[("default", "65000")] == {
        "ipv4-unicast,10.2.0.0/16": {
            "options": "summary-only",
            "aggregate_route_map": {"suppress": rm + "RM_CONN"},
        },
        "ipv4-unicast,10.4.0.0/16": {
            "options": "none",
            "aggregate_route_map": {},
        },
        "ipv6-unicast,2001:db8::/32": {"options": "as-set"},
    }

    state.writes.clear()
    assert run(asn=65000, address_families=families) == {"changed": False}
    assert not state.writes

    families[0]["aggregate_addresses"] = [
        {"prefix": "10.2.0.0/16", "options": "as-set"}
    ]
    assert run(asn=65000, address_families=families) == {"changed": True}
    assert state.aggregates[("default", "65000")] == {
        "ipv4-unicast,10.2.0.0/16": {
            "options": "as-set",
            "aggregate_route_map": {},
        },
        "ipv6-unicast,2001:db8::/32": {"options": "as-set"},
    }


def test_maximum_paths_per_address_family(switch):
    state, run = switch
    state.routers[("default", "65000")] = {
        "asn": 65000,
        "maximum_paths": {"all-afs": 4},
    }
    families = [{"address_family": "l2vpn_evpn", "maximum_paths": 2}]

    assert run(asn=65000, maximum_paths=8, address_families=families) == {
        "changed": True
    }
    assert state.routers[("default", "65000")]["maximum_paths"] == {
        "all-afs": 8,
        "l2vpn-evpn": 2,
    }

    state.session.api = v10_09()
    state.routers[("default", "65000")]["maximum_paths"] = 4
    result = run(asn=65000, address_families=families)
    assert result["failed"] is True
    assert "requires REST API version 10.13" in result["msg"]
    # Other settings of address_families still work with REST API 10.09
    networks = [
        {
            "address_family": "ipv4_unicast",
            "networks": [{"prefix": "10.0.0.0/8"}],
        }
    ]
    assert run(asn=65000, maximum_paths=8, address_families=networks) == {
        "changed": True
    }


@pytest.mark.parametrize(
    "params, message",
    [
        ({"maxas_limit": 33}, "maxas_limit must be between 1 and 32"),
        ({"timers": {"connect_retry": 0}}, "timers.connect_retry must be"),
        ({"confederation": {"peers": [0]}}, "confederation.peers must be"),
        (
            {
                "address_families": [
                    {"address_family": "l2vpn_evpn", "networks": []}
                ]
            },
            "networks is not supported for l2vpn_evpn",
        ),
        (
            {
                "address_families": [
                    {
                        "address_family": "ipv6_unicast",
                        "networks": [{"prefix": "10.0.0.0/8"}],
                    }
                ]
            },
            "is not an ipv6_unicast prefix",
        ),
        (
            {
                "address_families": [
                    {
                        "address_family": "ipv4_unicast",
                        "aggregate_addresses": [
                            {"prefix": "10.0.0.0/8"},
                            {"prefix": "10.0.0.1/8"},
                        ],
                    }
                ]
            },
            "duplicate prefix 10.0.0.0/8",
        ),
        (
            {
                "address_families": [
                    {
                        "address_family": "ipv4_unicast",
                        "dampening": {"half_life": 46},
                    }
                ]
            },
            "dampening.half_life must be between 1 and 45",
        ),
        (
            {
                "address_families": [
                    {
                        "address_family": "ipv4_unicast",
                        "aggregate_addresses": [
                            {"prefix": "10.0.0.0/8", "advertise_map": "NO"}
                        ],
                    }
                ]
            },
            "Could not find route map NO",
        ),
    ],
)
def test_new_options_validation(switch, params, message):
    state, run = switch
    result = run(asn=65000, **params)
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes
