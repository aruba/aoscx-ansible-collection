# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_ipsla_track_object module.

The pyaoscx session is fully mocked, so no switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_ipsla_track_object,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_ipsla_track_object"
)

SCALAR_ATTRS = ("track_list_operator", "up_delay", "down_delay")


class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def exit_json(*args, **kwargs):
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def set_module_args(args):
    serialized = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(serialized)


@pytest.fixture(autouse=True)
def patch_ansible_module():
    with patch.multiple(
        basic.AnsibleModule,
        exit_json=exit_json,
        fail_json=fail_json,
    ):
        yield


def build_track(exists, tracked=None, **attrs):
    track = MagicMock()
    track.config_attrs = []
    for attr in SCALAR_ATTRS:
        setattr(track, attr, attrs.get(attr))
    track.tracked_ipsla_session = tracked or {}
    if exists:
        track.get.return_value = True
    else:
        track.get.side_effect = Exception("not found")
    return track


def build_session(existing, new_instance=None):
    session = MagicMock()
    source = MagicMock()
    source.get.return_value = True

    def get_module(sess, module, index=None, **kwargs):
        if module == "IpslaSource":
            return source
        if module == "IpslaTrackObject":
            if "tracked_ipsla_session" in kwargs and new_instance is not None:
                return new_instance
            return existing
        raise AssertionError("unexpected module {0}".format(module))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_ipsla_track_object.main()
    return exc.value.args[0]


def test_create():
    existing = build_track(False)
    new = build_track(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "trk1",
            "tracked_ipsla_session": ["src1"],
            "track_list_operator": "or",
            "up_delay": 5,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_called_once()


def test_create_check_mode():
    existing = build_track(False)
    new = build_track(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "trk1",
            "tracked_ipsla_session": ["src1"],
            "_ansible_check_mode": True,
        },
        session,
    )
    assert result["changed"] is True
    new.create.assert_not_called()


def test_update_scalar():
    existing = build_track(True, up_delay=0)
    session = build_session(existing)
    result = run_module(
        {"name": "trk1", "state": "update", "up_delay": 10},
        session,
    )
    assert result["changed"] is True
    existing.update.assert_called_once()


def test_update_idempotent():
    existing = build_track(True, up_delay=5, down_delay=0)
    session = build_session(existing)
    result = run_module(
        {
            "name": "trk1",
            "state": "update",
            "up_delay": 5,
            "down_delay": 0,
        },
        session,
    )
    assert result["changed"] is False
    existing.update.assert_not_called()


def test_recreate_on_tracked_change():
    existing = build_track(
        True,
        tracked={"old": "/rest/v10.16/system/ipsla_sources/old"},
    )
    new = build_track(False)
    session = build_session(existing, new_instance=new)
    result = run_module(
        {
            "name": "trk1",
            "state": "update",
            "tracked_ipsla_session": ["src1"],
        },
        session,
    )
    assert result["changed"] is True
    existing.delete.assert_called_once()
    new.create.assert_called_once()


def test_delete():
    existing = build_track(True)
    session = build_session(existing)
    result = run_module({"name": "trk1", "state": "delete"}, session)
    assert result["changed"] is True
    existing.delete.assert_called_once()


def test_delete_absent_noop():
    existing = build_track(False)
    session = build_session(existing)
    result = run_module({"name": "trk1", "state": "delete"}, session)
    assert result["changed"] is False
    existing.delete.assert_not_called()
