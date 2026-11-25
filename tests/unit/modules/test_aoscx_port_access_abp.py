# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_port_access_abp module.

The pyaoscx SDK (PortAccessAbp container, its entries and action sets, and the
Class resolution via session.api.get_module) is fully mocked, so no switch is
required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_port_access_abp,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_port_access_abp"
)

NAME = "a1"


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


class FakeClass:
    def __init__(self, session, name, type=None):
        self.session = session
        self.name = name
        self.type = type

    def get(self, depth=None, selector=None):
        if not self.session._class_exists:
            raise Exception("no class")
        return True

    def get_uri(self):
        return "/rest/v10.16/system/classes/{0},{1}".format(
            self.name, self.type
        )


class FakeActionSet:
    action_key = "abp_action_set"

    def __init__(self, session, parent_entry, **kwargs):
        self.session = session
        self.parent_entry = parent_entry
        self.config_attrs = []
        self._original_attributes = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, depth=None, selector=None):
        data = self.session._action_sets.get(
            int(self.parent_entry.sequence_number)
        )
        if data is None:
            raise Exception("no action set")
        self._original_attributes = dict(data)
        return True

    def _payload(self):
        return {key: getattr(self, key) for key in self.config_attrs}

    def create(self):
        self.session._writes.append(
            (
                "action_create",
                int(self.parent_entry.sequence_number),
                self._payload(),
            )
        )

    def update(self):
        self.session._writes.append(
            (
                "action_update",
                int(self.parent_entry.sequence_number),
                self._payload(),
            )
        )


class FakeEntry:
    action_set_class = FakeActionSet

    def __init__(self, session, sequence_number, parent_container, **kwargs):
        self.session = session
        self.sequence_number = sequence_number
        self.parent_container = parent_container
        self._attrs = kwargs
        self.config_attrs = []
        self._original_attributes = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, depth=None, selector=None):
        data = self.session._entries[int(self.sequence_number)]
        for key, value in data.items():
            setattr(self, key, value)
        self._original_attributes = dict(data)
        return True

    def create(self):
        self.session._writes.append(
            ("entry_create", int(self.sequence_number), dict(self._attrs))
        )

    def update(self):
        payload = {key: getattr(self, key) for key in self.config_attrs}
        self.session._writes.append(
            ("entry_update", int(self.sequence_number), payload)
        )

    def delete(self):
        self.session._writes.append(
            ("entry_delete", int(self.sequence_number), None)
        )

    @classmethod
    def get_all(cls, session, parent_container):
        return {
            str(seq): cls(session, str(seq), parent_container)
            for seq in session._entries
        }


class FakeContainer:
    entry_class = FakeEntry
    base_uri = "system/port_access_abps"

    def __init__(self, session, name, **kwargs):
        self.session = session
        self.name = name
        self.path = "{0}/{1}".format(self.base_uri, name)

    def get(self, depth=None, selector=None):
        if not self.session._exists:
            raise Exception("no container")
        return True

    def create(self):
        self.session._writes.append(("container_create", self.name, None))

    def delete(self):
        self.session._writes.append(("container_delete", self.name, None))


def build_session(
    abp_exists=False, class_exists=True, entries=None, action_sets=None
):
    """
    entries: {seq(int): {"class": {clsname: uri}, "comment": str}}
    action_sets: {seq(int): {...}}
    """
    session = MagicMock()
    session._exists = abp_exists
    session._class_exists = class_exists
    session._entries = entries or {}
    session._action_sets = action_sets or {}
    session._writes = []

    def get_module(sess, name, index, **kwargs):
        return FakeClass(session, index, kwargs.get("type"))

    session.api.get_module.side_effect = get_module
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session), patch(
        MODULE + ".PortAccessAbp", FakeContainer
    ), patch(MODULE + ".HAS_PYAOSCX_PORT_ACCESS", True):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_port_access_abp.main()
    return exc.value.args[0]


def writes_of(session, op):
    return [w for w in session._writes if w[0] == op]


def test_create_empty():
    session = build_session(abp_exists=False)
    result = run_module({"name": NAME}, session)
    assert result["changed"] is True
    assert ("container_create", NAME, None) in session._writes


def test_create_with_entry():
    session = build_session(abp_exists=False, class_exists=True)
    result = run_module(
        {
            "name": NAME,
            "entries": [
                {
                    "sequence_number": 10,
                    "class_name": "c1",
                    "class_type": "abp-ipv4",
                    "comment": "x",
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    creates = writes_of(session, "entry_create")
    assert creates and creates[0][1] == 10
    assert creates[0][2]["class"] == (
        "/rest/v10.16/system/classes/c1,abp-ipv4"
    )


def test_class_missing_fails():
    session = build_session(abp_exists=False, class_exists=False)
    result = run_module(
        {
            "name": NAME,
            "entries": [
                {
                    "sequence_number": 10,
                    "class_name": "c1",
                    "class_type": "abp-ipv4",
                }
            ],
        },
        session,
    )
    assert result["failed"] is True


def test_delete():
    session = build_session(abp_exists=True)
    result = run_module({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is True
    assert ("container_delete", NAME, None) in session._writes


def test_delete_absent():
    session = build_session(abp_exists=False)
    result = run_module({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is False
    assert not session._writes


def test_idempotent():
    cls_uri = "/rest/v10.16/system/classes/c1,abp-ipv4"
    entries = {10: {"class": {"c1,abp-ipv4": cls_uri}, "comment": "x"}}
    session = build_session(abp_exists=True, entries=entries)
    result = run_module(
        {
            "name": NAME,
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "class_name": "c1",
                    "class_type": "abp-ipv4",
                    "comment": "x",
                }
            ],
        },
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_action_set_create_when_absent():
    cls_uri = "/rest/v10.16/system/classes/c1,abp-ipv4"
    entries = {10: {"class": {"c1,abp-ipv4": cls_uri}, "comment": None}}
    session = build_session(abp_exists=True, entries=entries)
    result = run_module(
        {
            "name": NAME,
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "class_name": "c1",
                    "class_type": "abp-ipv4",
                    "dscp": 46,
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    creates = writes_of(session, "action_create")
    assert creates and creates[0][1] == 10
    assert creates[0][2]["dscp"] == 46


def test_action_set_update_when_present():
    cls_uri = "/rest/v10.16/system/classes/c1,abp-ipv4"
    entries = {10: {"class": {"c1,abp-ipv4": cls_uri}, "comment": None}}
    action_sets = {10: {"dscp": 10}}
    session = build_session(
        abp_exists=True, entries=entries, action_sets=action_sets
    )
    result = run_module(
        {
            "name": NAME,
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "class_name": "c1",
                    "class_type": "abp-ipv4",
                    "dscp": 46,
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    updates = writes_of(session, "action_update")
    assert updates and updates[0][2]["dscp"] == 46
