# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+

"""Offline unit tests for aoscx_syslog_remote. SDK + AnsibleModule mocked."""

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


def test_create(run):
    import ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_syslog_remote  # NOQA

    r = MagicMock()
    r.get.side_effect = Exception("no")
    r.apply.return_value = True
    res = run(
        "aoscx_syslog_remote",
        {
            "remote_host": "192.0.2.10",
            "vrf": "default",
            "transport": "tcp",
            "port_number": 514,
            "severity": "info",
            "include_auditable_events": None,
            "disable": None,
            "state": "create",
        },
        {
            "SyslogRemote": MagicMock(return_value=r),
            "Vrf": MagicMock(return_value=MagicMock()),
        },
    )
    assert res["changed"] is True


def test_delete(run):
    import ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_syslog_remote  # NOQA

    r = MagicMock()
    r.get.return_value = True
    res = run(
        "aoscx_syslog_remote",
        {
            "remote_host": "192.0.2.10",
            "vrf": "default",
            "transport": None,
            "port_number": None,
            "severity": None,
            "include_auditable_events": None,
            "disable": None,
            "state": "delete",
        },
        {"SyslogRemote": MagicMock(return_value=r), "Vrf": MagicMock()},
    )
    assert res["changed"] is True
    r.delete.assert_called_once()
