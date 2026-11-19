# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_bgp_neighbor module.

The real module and pyaoscx SDK run against an in-memory REST transport, so
no switch is required.
"""

import copy
import json
from urllib.parse import quote, unquote
from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_bgp_neighbor,
)
from pyaoscx import vrf
from pyaoscx.rest.v10_16.api import v10_16

PREFIX = "/rest/v10.16/"
NEIGHBORS = "system/vrfs/default/bgp_routers/65000/bgp_neighbors"
PG_REF = {"spine-RR": PREFIX + NEIGHBORS + "/spine-RR"}
LO0_REF = {"loopback0": PREFIX + "system/interfaces/loopback0"}

PEER_GROUP = {
    "asn": 65000,
    "neighbor": "spine-RR",
    "is_peer_group": True,
    "remote_as": 65000,
    "description": "Spine and RR peer-group",
    "update_source": "loopback 0",
    "address_families": [
        {"address_family": "l2vpn_evpn", "send_community": "both"}
    ],
}

SPINE = {
    "asn": 65000,
    "neighbor": "10.147.253.132",
    "peer_group": "spine-RR",
    "address_families": [{"address_family": "l2vpn_evpn", "activate": True}],
}


def flatten(value):
    """{"a": {"b": x}} -> {"a,b": x}, as returned by the switch."""
    return {
        "{0},{1}".format(key, sub): item
        for key, nested in (value or {}).items()
        for sub, item in nested.items()
    }


COMPOUND = ("route_maps", "ORF_prefix_list")


def encrypt(body):
    """The switch stores the password encrypted."""
    password = body.get("password")
    if password and not password.startswith("ENC:"):
        body["password"] = "ENC:" + password
    return body


def has_compound_keys(value):
    return any("," in key for key in (value or {}))


class ModuleResult(Exception):
    pass


@pytest.fixture
def switch(monkeypatch):
    """Run the real module and SDK against an in-memory REST transport."""
    state = SimpleNamespace(
        routers={("default", "65000")},
        neighbors={},
        interfaces={"loopback0", "1/1/3"},
        route_maps={"RM_IN", "RM_OUT", "RM_DEFAULT"},
        prefix_lists={"PL_ORF"},
        keychains={"KC1"},
        writes=[],
    )

    def neighbor_response(name, params):
        # The switch returns references as {name: uri}. is_peer_group is
        # create-only, so it is not returned with the writable selector.
        data = dict(state.neighbors[name], ip_or_ifname_or_group_name=name)
        for attribute in COMPOUND:
            if attribute in data:
                data[attribute] = flatten(data[attribute])
        if params.get("selector") != "configuration":
            data.pop("is_peer_group", None)
            data.pop("nbr_interface", None)
        if "attributes" in params:
            wanted = params["attributes"].split(",")
            data = {k: v for k, v in data.items() if k in wanted}
        return data

    def request(method, path, params=None, data=None):
        body = json.loads(data) if data is not None else None
        if method != "GET":
            state.writes.append((method, path, copy.deepcopy(body)))
        parts = path.split("/")
        code, response = 404, {}
        if body and any(has_compound_keys(body.get(a)) for a in COMPOUND):
            # The switch rejects the format it returns
            code = 400
        elif path.startswith("system/route_maps/"):
            code = 200 if parts[2] in state.route_maps else 404
        elif path.startswith("system/prefix_lists/"):
            code = 200 if parts[2] in state.prefix_lists else 404
        elif path.startswith("system/keychains/"):
            code = 200 if parts[2] in state.keychains else 404
        elif path.startswith("system/interfaces/"):
            if unquote(parts[2]) in state.interfaces:
                # Interface sub-collections (IPv6 addresses, ...) are empty
                code = 200
                response = {"name": parts[2]} if len(parts) == 3 else {}
        elif len(parts) == 3 and parts[2] == "default":
            code, response = 200, {"name": "default"}
        elif len(parts) >= 5 and (parts[2], parts[4]) in state.routers:
            if len(parts) == 5:
                code, response = 200, {"asn": int(parts[4])}
            elif path == NEIGHBORS and method == "GET":
                code = 200
                response = {
                    name: PREFIX + NEIGHBORS + "/" + quote(name, safe="")
                    for name in state.neighbors
                }
            elif path == NEIGHBORS and method == "POST":
                name = body.pop("ip_or_ifname_or_group_name")
                state.neighbors[name] = encrypt(body)
                code = 201
            elif path.startswith(NEIGHBORS + "/"):
                name = unquote(parts[-1])
                if name in state.neighbors:
                    if method == "GET":
                        code = 200
                        response = neighbor_response(name, params or {})
                    elif method == "PUT":
                        assert "is_peer_group" not in body
                        assert "nbr_interface" not in body
                        current = state.neighbors[name]
                        state.neighbors[name] = encrypt(body)
                        for key in ("is_peer_group", "nbr_interface"):
                            if key in current:
                                state.neighbors[name][key] = current[key]
                        code = 204
                    elif method == "DELETE":
                        del state.neighbors[name]
                        code = 204
            elif method == "GET":
                # Other child collections (aggregate addresses, ...)
                code = 200
        elif method == "GET" and len(parts) == 4 and parts[2] == "default":
            code = 200
        return SimpleNamespace(status_code=code, text=json.dumps(response))

    def run(**params):
        monkeypatch.setattr(basic, "_load_params", lambda: params)
        with pytest.raises(ModuleResult) as result:
            aoscx_bgp_neighbor.main()
        return result.value.args[0]

    def finish(module, **result):
        raise ModuleResult(result)

    def fail(module, **result):
        finish(module, failed=True, **result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", finish)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail)
    session = SimpleNamespace(
        api=v10_16(), connected=True, request=request, resource_prefix=PREFIX
    )
    monkeypatch.setattr(
        aoscx_bgp_neighbor, "get_pyaoscx_session", lambda _: session
    )
    monkeypatch.setattr(
        vrf,
        "Device",
        lambda _: SimpleNamespace(materialized=True, capabilities=[]),
    )
    return state, run


def test_user_config_create_then_rerun_is_idempotent(switch):
    state, run = switch

    assert run(_ansible_check_mode=True, **PEER_GROUP) == {"changed": True}
    assert not state.writes

    assert run(**PEER_GROUP) == {"changed": True}
    assert state.neighbors["spine-RR"] == {
        "is_peer_group": True,
        "remote_as": 65000,
        "description": "Spine and RR peer-group",
        "local_interface": LO0_REF,
        "send_community": {"l2vpn-evpn": "both"},
    }

    for ip in ("10.147.253.132", "10.147.253.165"):
        assert run(**dict(SPINE, neighbor=ip)) == {"changed": True}
        assert state.neighbors[ip] == {
            "is_peer_group": False,
            "bgp_peer_group": PG_REF,
            "activate": {"l2vpn-evpn": True},
        }

    state.writes.clear()
    assert run(**dict(PEER_GROUP, update_source="loopback0")) == {
        "changed": False
    }
    for ip in ("10.147.253.132", "10.147.253.165"):
        assert run(**dict(SPINE, neighbor=ip)) == {"changed": False}
    assert not state.writes


def test_update_only_changes_given_settings(switch):
    state, run = switch
    state.neighbors["10.0.0.1"] = {
        "is_peer_group": False,
        "remote_as": 65001,
        "description": "keep",
        "activate": {"ipv4-unicast": True, "l2vpn-evpn": False},
        "send_community": {"ipv4-unicast": "standard", "l2vpn-evpn": "none"},
    }
    families = [
        {
            "address_family": "l2vpn_evpn",
            "activate": True,
            "send_community": "extended",
        }
    ]

    result = run(
        asn=65000,
        neighbor="10.0.0.1",
        remote_as=65002,
        address_families=families,
    )
    assert result == {"changed": True}
    assert state.writes == [
        (
            "PUT",
            NEIGHBORS + "/10.0.0.1",
            {
                "remote_as": 65002,
                "description": "keep",
                "activate": {"ipv4-unicast": True, "l2vpn-evpn": True},
                "send_community": {
                    "ipv4-unicast": "standard",
                    "l2vpn-evpn": "extended",
                },
            },
        )
    ]


def test_update_source_ip_and_removal(switch):
    state, run = switch
    state.neighbors["spine-RR"] = {
        "is_peer_group": True,
        "local_interface": LO0_REF,
    }
    args = dict(asn=65000, neighbor="spine-RR", is_peer_group=True)

    assert run(update_source="10.0.0.9", **args) == {"changed": True}
    assert state.neighbors["spine-RR"]["update_source"] == "10.0.0.9"
    assert state.neighbors["spine-RR"]["local_interface"] is None

    assert run(update_source="", **args) == {"changed": True}
    assert state.neighbors["spine-RR"]["update_source"] is None
    assert run(update_source="", **args) == {"changed": False}


def test_leave_peer_group(switch):
    state, run = switch
    state.neighbors["spine-RR"] = {"is_peer_group": True}
    state.neighbors["10.0.0.1"] = {
        "is_peer_group": False,
        "bgp_peer_group": PG_REF,
    }

    assert run(asn=65000, neighbor="10.0.0.1", peer_group="") == {
        "changed": True
    }
    assert state.neighbors["10.0.0.1"]["bgp_peer_group"] is None


def test_neighbors_list_gets_same_settings(switch):
    state, run = switch
    state.neighbors["leaf"] = {"is_peer_group": True}
    state.neighbors["10.0.0.9"] = {"is_peer_group": False}
    leafs = dict(
        asn=65000,
        neighbors=["10.147.253.170", "10.147.253.171"],
        peer_group="leaf",
        address_families=[{"address_family": "l2vpn_evpn", "activate": True}],
    )

    assert run(_ansible_check_mode=True, **leafs) == {"changed": True}
    assert not state.writes
    assert run(**leafs) == {"changed": True}
    for ip in leafs["neighbors"]:
        assert state.neighbors[ip] == {
            "is_peer_group": False,
            "bgp_peer_group": {"leaf": PREFIX + NEIGHBORS + "/leaf"},
            "activate": {"l2vpn-evpn": True},
        }
    assert state.neighbors["10.0.0.9"] == {"is_peer_group": False}

    state.writes.clear()
    assert run(**leafs) == {"changed": False}
    assert not state.writes

    delete = dict(asn=65000, neighbors=leafs["neighbors"], state="delete")
    assert run(**delete) == {"changed": True}
    assert sorted(state.neighbors) == ["10.0.0.9", "leaf"]


def test_neighbors_list_validated_before_any_write(switch):
    state, run = switch
    state.neighbors["10.0.0.2"] = {"is_peer_group": True}
    result = run(
        asn=65000, neighbors=["10.0.0.1", "10.0.0.2"], remote_as=65001
    )
    assert result["failed"] is True
    assert "delete 10.0.0.2 first" in result["msg"]
    assert not state.writes


def test_delete_only_given_neighbor(switch):
    state, run = switch
    state.neighbors["10.0.0.1"] = {"is_peer_group": False}
    state.neighbors["10.0.0.2"] = {"is_peer_group": False}
    args = dict(asn=65000, neighbor="10.0.0.1", state="delete")

    assert run(_ansible_check_mode=True, **args) == {"changed": True}
    assert not state.writes
    assert run(**args) == {"changed": True}
    assert state.writes == [("DELETE", NEIGHBORS + "/10.0.0.1", None)]
    assert list(state.neighbors) == ["10.0.0.2"]
    assert run(**args) == {"changed": False}


def test_delete_without_router_is_no_change(switch):
    state, run = switch
    state.routers.clear()
    assert run(asn=65000, neighbor="10.0.0.1", state="delete") == {
        "changed": False
    }


@pytest.mark.parametrize(
    "setup, params, message",
    [
        ("no_router", {}, "create it with aoscx_bgp_router first"),
        (None, {"peer_group": "missing"}, "Could not find peer group"),
        (None, {"update_source": "loopback9"}, "Could not find interface"),
        ("neighbor", {"is_peer_group": True}, "is_peer_group cannot be"),
        ("neighbor", {"peer_group": "10.0.0.2"}, "is not a peer group"),
    ],
)
def test_errors(switch, setup, params, message):
    state, run = switch
    state.neighbors["10.0.0.2"] = {"is_peer_group": False}
    if setup == "no_router":
        state.routers.clear()
    if setup == "neighbor":
        state.neighbors["10.0.0.1"] = {"is_peer_group": False}
    result = run(asn=65000, neighbor="10.0.0.1", **params)
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes


@pytest.mark.parametrize(
    "params, message",
    [
        ({"neighbor": "a/b"}, "Invalid neighbor"),
        ({"neighbor": None, "neighbors": []}, "neighbors must not be empty"),
        (
            {"neighbor": None, "neighbors": ["10.0.0.1", "10.0.0.1"]},
            "Duplicate entries in neighbors",
        ),
        (
            {"neighbor": None, "neighbors": ["leaf"], "peer_group": "leaf"},
            "cannot belong to itself",
        ),
        ({"neighbors": ["10.0.0.2"]}, "mutually exclusive"),
        ({"neighbor": None}, "one of the following is required"),
        ({"remote_as": 0}, "remote_as must be between"),
        (
            {"is_peer_group": True, "peer_group": "spine-RR"},
            "peer_group is not supported",
        ),
        (
            {
                "address_families": [
                    {"address_family": "l2vpn_evpn", "next_hop_self": True}
                ]
            },
            "next_hop_self is not supported for l2vpn_evpn",
        ),
        (
            {
                "address_families": [
                    {"address_family": "ipv4_unicast"},
                    {"address_family": "ipv4_unicast"},
                ]
            },
            "Duplicate address family",
        ),
    ],
)
def test_invalid_params_rejected(switch, params, message):
    state, run = switch
    args = dict({"asn": 65000, "neighbor": "10.0.0.1"}, **params)
    result = run(**{k: v for k, v in args.items() if v is not None})
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes


def test_missing_parent_in_check_mode_or_delete(switch):
    state, run = switch
    state.routers.clear()
    args = dict(asn=65000, neighbors=["10.0.0.1"], peer_group="spine-RR")
    assert run(_ansible_check_mode=True, **args) == {"changed": True}
    assert run(vrf="missing", _ansible_check_mode=True, **args) == {
        "changed": True
    }
    assert run(
        asn=65000, neighbor="10.0.0.1", vrf="missing", state="delete"
    ) == {"changed": False}
    assert not state.writes


def test_ebgp_multihop(switch):
    state, run = switch
    args = dict(asn=65000, neighbor="spine-RR", is_peer_group=True)

    assert run(ebgp_multihop=1, **args) == {"changed": True}
    assert "ebgp_hop_count" not in state.neighbors["spine-RR"]
    # Not configured on the switch is the same as 1
    assert run(ebgp_multihop=1, **args) == {"changed": False}

    assert run(ebgp_multihop=255, **args) == {"changed": True}
    assert state.neighbors["spine-RR"]["ebgp_hop_count"] == 255
    assert run(ebgp_multihop=255, **args) == {"changed": False}

    assert run(ebgp_multihop=1, **args) == {"changed": True}
    assert state.neighbors["spine-RR"]["ebgp_hop_count"] == 1


@pytest.mark.parametrize("value", [0, 256])
def test_invalid_ebgp_multihop(switch, value):
    state, run = switch
    result = run(asn=65000, neighbor="10.0.0.1", ebgp_multihop=value)
    assert result["failed"] is True
    assert "ebgp_multihop must be between 1 and 255" in result["msg"]
    assert not state.writes


def test_route_maps_and_default_originate(switch):
    state, run = switch
    rm = PREFIX + "system/route_maps/"
    state.neighbors["10.0.0.1"] = {
        "is_peer_group": False,
        "route_maps": {"ipv6-unicast": {"in": rm + "RM_IN"}},
    }
    families = [
        {
            "address_family": "ipv4_unicast",
            "route_map_in": "RM_IN",
            "route_map_out": "RM_OUT",
            "default_originate": True,
            "default_originate_route_map": "RM_DEFAULT",
        }
    ]
    args = dict(asn=65000, neighbor="10.0.0.1", address_families=families)

    assert run(_ansible_check_mode=True, **args) == {"changed": True}
    assert not state.writes
    assert run(**args) == {"changed": True}
    neighbor = state.neighbors["10.0.0.1"]
    assert neighbor["route_maps"] == {
        "ipv4-unicast": {"in": rm + "RM_IN", "out": rm + "RM_OUT"},
        "ipv6-unicast": {"in": rm + "RM_IN"},
    }
    assert neighbor["default_originate"] == {"ipv4-unicast": True}
    assert neighbor["default_originate_route_map"] == {
        "ipv4-unicast": rm + "RM_DEFAULT"
    }

    # The switch returns compound keys: no change
    state.writes.clear()
    assert run(**args) == {"changed": False}
    assert not state.writes

    # Another option is updated: route maps are sent as nested dicts
    assert run(asn=65000, neighbor="10.0.0.1", description="x") == {
        "changed": True
    }

    removal = [
        {
            "address_family": "ipv4_unicast",
            "route_map_in": "",
            "route_map_out": "",
            "default_originate": False,
            "default_originate_route_map": "",
        },
        {"address_family": "ipv6_unicast", "route_map_in": ""},
    ]
    assert run(asn=65000, neighbor="10.0.0.1", address_families=removal) == {
        "changed": True
    }
    neighbor = state.neighbors["10.0.0.1"]
    assert neighbor["route_maps"] == {}
    assert neighbor["default_originate"] == {"ipv4-unicast": False}
    assert neighbor["default_originate_route_map"] == {}


@pytest.mark.parametrize(
    "family, message",
    [
        (
            {"address_family": "ipv4_unicast", "route_map_in": "MISSING"},
            "Could not find route map MISSING",
        ),
        (
            {"address_family": "l2vpn_evpn", "default_originate": True},
            "default_originate is not supported for l2vpn_evpn",
        ),
        (
            {
                "address_family": "ipv4_unicast",
                "default_originate": False,
                "default_originate_route_map": "RM_DEFAULT",
            },
            "default_originate_route_map requires default_originate",
        ),
    ],
)
def test_route_map_errors(switch, family, message):
    state, run = switch
    state.neighbors["10.0.0.1"] = {"is_peer_group": False}
    result = run(asn=65000, neighbor="10.0.0.1", address_families=[family])
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes


def test_session_options(switch):
    state, run = switch
    state.neighbors["10.0.0.1"] = {
        "is_peer_group": False,
        "timers": {"connect-retry": 120, "holdtime": 180, "keepalive": 60},
        "gshut": {"local_pref": 0, "timer": 180},
        "invalid_attributes": {"accept_route": "all"},
        "ao_options": {
            "accept_ao_mismatch": False,
            "include_tcp_options": False,
        },
    }
    params = dict(
        asn=65000,
        neighbor="10.0.0.1",
        fall_over=True,
        fall_over_bfd=True,
        passive=True,
        remove_private_as=True,
        slow_peer=True,
        weight=100,
        local_as=65100,
        local_as_mode="no-prepend",
        port=1790,
        ttl_security_hops=5,
        timers={"keepalive": 20, "holdtime": 60},
        graceful_shutdown={"timer": 60, "local_preference": 10},
        accept_invalid_attributes=False,
        ao={"keychain": "KC1", "include_tcp_options": True},
    )

    assert run(**params) == {"changed": True}
    neighbor = state.neighbors["10.0.0.1"]
    assert {k: v for k, v in neighbor.items() if k != "is_peer_group"} == {
        "fall_over": True,
        "bfd_enable": True,
        "passive": True,
        "remove_private_as": True,
        "slow_peer": True,
        "weight": 100,
        "local_as": 65100,
        "local_as_mode": "no-prepend",
        "tcp_port_number": 1790,
        "ttl_security_hops": 5,
        "timers": {"connect-retry": 120, "holdtime": 60, "keepalive": 20},
        "gshut": {"local_pref": 10, "timer": 60},
        "invalid_attributes": {"accept_route": "none"},
        "ao_options": {
            "accept_ao_mismatch": False,
            "include_tcp_options": True,
        },
        "ao_keychain": PREFIX + "system/keychains/KC1",
    }
    neighbor["ao_keychain"] = {"KC1": neighbor["ao_keychain"]}
    state.writes.clear()
    assert run(**params) == {"changed": False}
    assert not state.writes

    removal = dict(
        asn=65000,
        neighbor="10.0.0.1",
        local_as=0,
        port=0,
        ttl_security_hops=0,
        ao={"keychain": ""},
    )
    assert run(**removal) == {"changed": True}
    neighbor = state.neighbors["10.0.0.1"]
    for key in ("local_as", "tcp_port_number", "ttl_security_hops"):
        assert neighbor[key] is None
    assert neighbor["ao_keychain"] is None
    assert run(**removal) == {"changed": False}


def test_password(switch):
    state, run = switch
    state.neighbors["10.0.0.1"] = {"is_peer_group": False}
    args = dict(asn=65000, neighbor="10.0.0.1")

    assert run(password="secret", **args) == {"changed": True}
    assert state.neighbors["10.0.0.1"]["password"] == "ENC:secret"
    # on_create: the encrypted password cannot be compared, it is kept
    assert run(password="other", **args) == {"changed": False}
    # Another update sends back the encrypted password unchanged
    assert run(description="x", **args) == {"changed": True}
    assert state.neighbors["10.0.0.1"]["password"] == "ENC:secret"

    assert run(password="other", update_password="always", **args) == {
        "changed": True
    }
    assert state.neighbors["10.0.0.1"]["password"] == "ENC:other"
    assert run(password="", **args) == {"changed": True}
    assert state.neighbors["10.0.0.1"]["password"] is None
    assert run(password="", **args) == {"changed": False}


def test_family_options(switch):
    state, run = switch
    state.neighbors["10.0.0.1"] = {
        "is_peer_group": False,
        "add_paths": {"ipv4-unicast": "disable", "ipv6-unicast": "disable"},
        "allow_as_in": {"l2vpn-evpn": 1},
        "max_prefix_options": {"ipv6-unicast": {"maximum_prefix_limit": 10}},
    }
    families = [
        {
            "address_family": "ipv4_unicast",
            "allowas_in": 2,
            "advertisement_interval": 10,
            "add_paths": "both",
            "add_paths_advertise_best": 3,
            "maximum_prefix": {
                "limit": 1000,
                "threshold": 80,
                "restart": 60,
                "warning_only": True,
            },
            "orf_capability": "receive",
            "orf_prefix_list": "PL_ORF",
        },
        {
            "address_family": "l2vpn_evpn",
            "allowas_in": 3,
            "replace_rt_asn": True,
            "maximum_prefix": {"limit": 500, "warning_only": False},
        },
    ]
    args = dict(asn=65000, neighbor="10.0.0.1", address_families=families)

    assert run(**args) == {"changed": True}
    neighbor = state.neighbors["10.0.0.1"]
    assert neighbor["allow_as_in"] == {"ipv4-unicast": 2, "l2vpn-evpn": 3}
    assert neighbor["advertisement_interval"] == {"ipv4-unicast": 10}
    assert neighbor["add_paths"] == {
        "ipv4-unicast": "both",
        "ipv6-unicast": "disable",
    }
    assert neighbor["add_paths_adv_best_n"] == {"ipv4-unicast": 3}
    assert neighbor["max_prefix_options"] == {
        "ipv4-unicast": {
            "maximum_prefix_limit": 1000,
            "threshold": 80,
            "restart": 60,
        },
        "ipv6-unicast": {"maximum_prefix_limit": 10},
        "l2vpn-evpn": {"maximum_prefix_limit": 500, "warning_disable": True},
    }
    assert neighbor["ORF_capability"] == {
        "ipv4-unicast": {"prefix-list": "receive"}
    }
    assert neighbor["ORF_prefix_list"] == {
        "ipv4-unicast": {"in": PREFIX + "system/prefix_lists/PL_ORF"}
    }
    assert neighbor["replace_rt_asn"] == {"l2vpn-evpn": True}

    # ORF_prefix_list is returned with compound keys
    state.writes.clear()
    assert run(**args) == {"changed": False}
    assert not state.writes
    assert run(asn=65000, neighbor="10.0.0.1", description="x") == {
        "changed": True
    }

    removal = [
        {
            "address_family": "ipv4_unicast",
            "allowas_in": 0,
            "maximum_prefix": {"limit": 0},
            "orf_capability": "none",
            "orf_prefix_list": "",
        }
    ]
    assert run(asn=65000, neighbor="10.0.0.1", address_families=removal) == {
        "changed": True
    }
    neighbor = state.neighbors["10.0.0.1"]
    assert neighbor["allow_as_in"] == {"l2vpn-evpn": 3}
    assert "ipv4-unicast" not in neighbor["max_prefix_options"]
    assert neighbor["ORF_capability"] == {}
    assert neighbor["ORF_prefix_list"] == {}
    assert run(asn=65000, neighbor="10.0.0.1", address_families=removal) == {
        "changed": False
    }


def test_unnumbered_neighbor(switch):
    state, run = switch
    args = dict(
        asn=65000, neighbor="1/1/3", interface="1/1/3", remote_as=65001
    )

    assert run(**args) == {"changed": True}
    assert state.writes == [
        (
            "POST",
            NEIGHBORS,
            {
                "ip_or_ifname_or_group_name": "1/1/3",
                "is_peer_group": False,
                "nbr_interface": PREFIX + "system/interfaces/1%2F1%2F3",
                "remote_as": 65001,
            },
        )
    ]
    state.neighbors["1/1/3"]["nbr_interface"] = {
        "1/1/3": PREFIX + "system/interfaces/1%2F1%2F3"
    }
    state.writes.clear()
    assert run(**args) == {"changed": False}
    assert run(asn=65000, neighbor="1/1/3", weight=5) == {"changed": True}
    assert state.writes[-1][1] == NEIGHBORS + "/1%2F1%2F3"

    state.interfaces.add("1/1/4")
    result = run(asn=65000, neighbor="1/1/3", interface="1/1/4")
    assert result["failed"] is True
    assert "interface cannot be changed" in result["msg"]
    assert run(asn=65000, neighbor="1/1/3", state="delete") == {
        "changed": True
    }
    assert "1/1/3" not in state.neighbors


@pytest.mark.parametrize(
    "params, message",
    [
        ({"weight": 65536}, "weight must be between 0 and 65535"),
        (
            {"password": "x", "ao": {"keychain": "KC1"}},
            "password and ao.keychain are mutually exclusive",
        ),
        ({"ttl_security_hops": 255}, "ttl_security_hops must be between"),
        ({"graceful_shutdown": {"timer": 5}}, "graceful_shutdown.timer must"),
        ({"neighbor": "a/b"}, "Invalid neighbor"),
        ({"interface": "1/1/9"}, "Could not find interface 1/1/9"),
        ({"ao": {"keychain": "NOPE"}}, "Could not find keychain NOPE"),
        (
            {
                "address_families": [
                    {"address_family": "ipv4_unicast", "orf_prefix_list": "NO"}
                ]
            },
            "Could not find prefix list NO",
        ),
        (
            {
                "address_families": [
                    {"address_family": "l2vpn_evpn", "add_paths": "both"}
                ]
            },
            "add_paths is not supported for l2vpn_evpn",
        ),
        (
            {
                "address_families": [
                    {"address_family": "ipv4_unicast", "replace_rt_asn": True}
                ]
            },
            "replace_rt_asn is not supported for ipv4_unicast",
        ),
        (
            {
                "address_families": [
                    {"address_family": "ipv4_unicast", "allowas_in": 11}
                ]
            },
            "allowas_in must be between 0 and 10",
        ),
        (
            {
                "address_families": [
                    {
                        "address_family": "ipv4_unicast",
                        "maximum_prefix": {"limit": 10, "restart": 5},
                    }
                ]
            },
            "maximum_prefix.restart must be between 30 and 65535",
        ),
    ],
)
def test_new_options_validation(switch, params, message):
    state, run = switch
    result = run(**dict({"asn": 65000, "neighbor": "10.0.0.1"}, **params))
    assert result["failed"] is True
    assert message in result["msg"]
    assert not state.writes
