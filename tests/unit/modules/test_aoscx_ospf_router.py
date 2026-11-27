# GNU General Public License v3.0+

from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_ospf_router as module,
)

URI = "/rest/v10.13/system/route_maps/RM"


class ModuleResult(Exception):
    pass


class FakeRouter:
    existing = None
    instances = []

    def __init__(self, session, tag, vrf, **kwargs):
        self.kwargs = kwargs
        self.applied = False
        self.redistribute = []
        self.redistribute_route_map = dict(FakeRouter.existing or {})
        self.passive_interface_default = False
        self.passive_interfaces = []
        self.active_interfaces = []
        FakeRouter.instances.append(self)

    def get(self):
        if FakeRouter.existing is None:
            raise Exception("absent")

    def create(self):
        self.applied = True

    def apply(self):
        self.applied = True


@pytest.fixture
def run(monkeypatch):
    FakeRouter.instances = []
    session = SimpleNamespace(resource_prefix="/rest/v10.13/")
    monkeypatch.setattr(module, "HAS_PYAOSCX", True)
    monkeypatch.setattr(module, "OspfRouter", FakeRouter, raising=False)
    monkeypatch.setattr(
        module,
        "Vrf",
        lambda *a: SimpleNamespace(get=lambda: None),
        raising=False,
    )
    monkeypatch.setattr(
        module, "get_pyaoscx_session", lambda m: session, raising=False
    )
    monkeypatch.setattr(
        module, "check_reference", lambda *a: None, raising=False
    )
    monkeypatch.setattr(
        module,
        "reference_uri",
        lambda s, k, n: URI.replace("RM", n),
        raising=False,
    )

    def finish(self, **result):
        raise ModuleResult(result)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", finish)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", finish)

    def _run(existing, **params):
        FakeRouter.existing = existing
        args = dict(dict(vrf="v", instance_tag=1, state="update"), **params)
        monkeypatch.setattr(basic, "_load_params", lambda: args)
        with pytest.raises(ModuleResult) as result:
            module.main()
        return result.value.args[0], FakeRouter.instances[-1]

    return _run


def test_attach_to_existing(run):
    result, router = run({}, redistribute_route_maps={"bgp": "RM"})
    assert result["changed"] and router.applied
    assert router.redistribute_route_map == {"bgp": URI}


def test_idempotent(run):
    result, router = run({"bgp": URI}, redistribute_route_maps={"bgp": "RM"})
    assert not result["changed"] and not router.applied


def test_empty_name_detaches(run):
    result, router = run({"bgp": URI}, redistribute_route_maps={"bgp": ""})
    assert result["changed"]
    assert router.redistribute_route_map == {}


def test_create_passes_route_map(run):
    result, router = run(
        None, state="create", redistribute_route_maps={"bgp": "RM"}
    )
    assert result["changed"]
    assert router.kwargs["redistribute_route_map"] == {"bgp": URI}


def test_unknown_source(run):
    with pytest.raises(IndexError):
        run({}, redistribute_route_maps={"foo": "RM"})
