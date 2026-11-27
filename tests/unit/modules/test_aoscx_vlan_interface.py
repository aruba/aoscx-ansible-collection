# GNU General Public License v3.0+

import json
from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_vlan_interface,
)
from pyaoscx import device
from pyaoscx.interface import Interface
from pyaoscx.rest.v10_16.api import v10_16

PATH = "system/interfaces/vlan100"
ATTR = "local_proxy_arp_ip_exemption"


class ModuleResult(Exception):
    pass


@pytest.fixture
def switch(monkeypatch):
    """Run the real module and SDK against an in-memory REST transport."""
    state = SimpleNamespace(interface={"vrf": None, ATTR: []}, writes=[])

    def request(method, path, params=None, data=None):
        if method != "GET":
            state.writes.append((method, path, json.loads(data)))
            if method == "PUT":
                state.interface = json.loads(data)
            return SimpleNamespace(status_code=200, text="{}")
        body = state.interface if path == PATH else {}
        return SimpleNamespace(status_code=200, text=json.dumps(body))

    def run(**params):
        monkeypatch.setattr(
            basic, "_load_params", lambda: dict(vlan_id="100", **params)
        )
        with pytest.raises(ModuleResult) as result:
            aoscx_vlan_interface.main()
        return result.value.args[0]

    def finish(module, **result):
        raise ModuleResult(result)

    def fail(module, **result):
        finish(module, failed=True, **result)

    session = SimpleNamespace(
        api=v10_16(),
        connected=True,
        request=request,
        resource_prefix="/rest/v10.16/",
    )

    def interface(name):
        iface = Interface(session, name)
        iface.get()
        return iface

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", finish)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail)
    monkeypatch.setattr(
        aoscx_vlan_interface, "get_pyaoscx_session", lambda _: session
    )
    monkeypatch.setattr(
        device, "Device", lambda _: SimpleNamespace(interface=interface)
    )
    # The SVI creation is not what these tests are about
    monkeypatch.setattr(Interface, "configure_svi", lambda *a, **k: False)
    return state, run


def test_exclusions_are_set_then_rerun_in_another_order(switch):
    state, run = switch
    assert run(local_proxy_arp_exclude=["10.1.1.2", "10.1.1.1"]) == {
        "changed": True
    }
    ((method, path, body),) = state.writes
    assert (method, path.rsplit("/", 1)[-1]) == ("PUT", "vlan100")
    assert body[ATTR] == ["10.1.1.1", "10.1.1.2"]
    state.writes.clear()
    reordered = ["10.1.1.1", "10.1.1.2", "10.1.1.1"]
    assert run(local_proxy_arp_exclude=reordered) == {"changed": False}
    assert not state.writes


def test_empty_list_clears_the_exclusions(switch):
    state, run = switch
    state.interface[ATTR] = ["10.1.1.1"]
    assert run(local_proxy_arp_exclude=[], state="update") == {"changed": True}
    assert state.interface[ATTR] == []


def test_omitted_option_leaves_the_exclusions_unchanged(switch):
    state, run = switch
    state.interface[ATTR] = ["10.1.1.1"]
    assert run() == {"changed": False}
    assert not state.writes


def test_state_delete_ignores_the_option(switch, monkeypatch):
    state, run = switch
    monkeypatch.setattr(Interface, "delete", lambda self: None)
    state.interface[ATTR] = ["10.1.1.1"]
    run(local_proxy_arp_exclude=[], state="delete")
    assert state.interface[ATTR] == ["10.1.1.1"]


@pytest.mark.parametrize("address", ["fd00::1", "not-an-ip"])
def test_wrong_address_is_refused(switch, address):
    state, run = switch
    result = run(local_proxy_arp_exclude=[address])
    assert result["failed"]
    assert ATTR in result["msg"]
    assert not state.writes


def test_firmware_without_the_attribute_is_refused(switch):
    state, run = switch
    del state.interface[ATTR]
    result = run(local_proxy_arp_exclude=["10.1.1.1"])
    assert result["failed"]
    assert "not supported by this switch firmware" in result["msg"]
    assert not state.writes


def test_old_pyaoscx_is_reported(switch, monkeypatch):
    state, run = switch
    monkeypatch.delattr(Interface, "set_local_proxy_arp_ip_exemption")
    result = run(local_proxy_arp_exclude=["10.1.1.1"])
    assert result["failed"]
    assert "please upgrade pyaoscx" in result["msg"]
    assert run() == {"changed": False}
