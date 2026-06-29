# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+

"""Offline unit tests for the SNMP family modules. AnsibleModule and the
pyaoscx SDK are mocked, so no switch is needed."""

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


def test_user_create(run):
    import ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_snmpv3_user  # NOQA

    user = MagicMock()
    user.get.side_effect = Exception("no")
    user.apply.return_value = True
    res = run(
        "aoscx_snmpv3_user",
        {
            "user_name": "u1",
            "access_level": "ro",
            "auth_protocol": None,
            "auth_pass_phrase": None,
            "priv_protocol": None,
            "priv_pass_phrase": None,
            "remote_engine_id": None,
            "state": "create",
        },
        {"Snmpv3User": MagicMock(return_value=user)},
    )
    assert res["changed"] is True


def test_community_delete(run):
    import ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_snmp_community  # NOQA

    comm = MagicMock()
    comm.get.return_value = True
    res = run(
        "aoscx_snmp_community",
        {"name": "c1", "snmp_view": None, "state": "delete"},
        {"SnmpCommunity": MagicMock(return_value=comm)},
    )
    assert res["changed"] is True
    comm.delete.assert_called_once()


def test_trap_create(run):
    import ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_snmp_trap  # NOQA

    trap = MagicMock()
    trap.get.side_effect = Exception("no")
    res = run(
        "aoscx_snmp_trap",
        {
            "vrf": "default",
            "receiver_address": "198.51.100.5",
            "receiver_udp_port": 162,
            "type": "trap",
            "version": "v2c",
            "community_name": "public",
            "state": "create",
        },
        {
            "SnmpTrap": MagicMock(return_value=trap),
            "Vrf": MagicMock(return_value=MagicMock()),
        },
    )
    assert res["changed"] is True
    trap.create.assert_called_once()
