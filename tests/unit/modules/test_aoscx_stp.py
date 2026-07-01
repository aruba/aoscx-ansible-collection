# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+

"""Offline unit tests for aoscx_stp. SDK + AnsibleModule mocked."""

import sys

from unittest.mock import MagicMock, patch

import pytest

MODULES = "ansible_collections.arubanetworks.aoscx.plugins.modules"


@pytest.fixture
def run():
    def _run(module, params, sdk_mocks):
        full = MODULES + "." + module
        with patch(full + ".AnsibleModule") as am, patch(
            full + ".get_pyaoscx_session", return_value=MagicMock()
        ):
            mod = sys.modules[full]
            inst = MagicMock(params=params, check_mode=False)
            result = {}

            def _exit(**k):
                result.update(k)
                raise SystemExit

            inst.exit_json.side_effect = _exit
            am.return_value = inst
            for name, obj in sdk_mocks.items():
                setattr(mod, name, obj)
            try:
                mod.main()
            except SystemExit:
                pass
            return result

    return _run


def test_change(run):
    import ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_stp  # NOQA

    s = MagicMock()
    s.get.return_value = True
    s.priority = 8
    s.config_attrs = []
    res = run(
        "aoscx_stp",
        {
            "instance": "mstp,0",
            "priority": 4,
            "hello_time": None,
            "forward_delay": None,
            "max_age": None,
            "topology_change_trap_enable": None,
            "state": "update",
        },
        {"Stp": MagicMock(return_value=s)},
    )
    assert res["changed"] is True


def test_delete(run):
    import ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_stp  # NOQA

    s = MagicMock()
    s.get.return_value = True
    res = run(
        "aoscx_stp",
        {
            "instance": "mstp,0",
            "priority": None,
            "hello_time": None,
            "forward_delay": None,
            "max_age": None,
            "topology_change_trap_enable": None,
            "state": "delete",
        },
        {"Stp": MagicMock(return_value=s)},
    )
    assert res["changed"] is True
