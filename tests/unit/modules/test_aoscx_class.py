# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_class module.

The pyaoscx SDK (Class via session.api.get_module and ClassEntry) is fully
mocked, so no switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_class,
)

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_class"

NAME = "c1"
TYPE = "ipv4"

# Default representation of an entry as returned by selector=configuration.
ENTRY_DEFAULTS = {
    "count": False,
    "fragment": False,
    "tcp_ack": False,
    "tcp_cwr": False,
    "tcp_ece": False,
    "tcp_established": False,
    "tcp_fin": False,
    "tcp_psh": False,
    "tcp_rst": False,
    "tcp_syn": False,
    "tcp_urg": False,
    "type": "match",
    "comment": None,
}


def full_entry(**fields):
    entry = dict(ENTRY_DEFAULTS)
    entry.update(fields)
    return entry


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
        self.index = "{0},{1}".format(name, type)

    def get(self, depth=None, selector=None):
        if not self.session._exists:
            raise Exception("not found")
        return True

    def create(self):
        self.session._class_creates.append((self.name, self.type))

    def delete(self):
        self.session._class_deletes.append((self.name, self.type))


class FakeClassEntry:
    def __init__(self, session, sequence_number, parent_class, **kwargs):
        self.session = session
        self.sequence_number = sequence_number
        self.parent_class = parent_class
        self._attrs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, depth=None, selector=None):
        data = self.session._existing_entries[int(self.sequence_number)]
        for key, value in data.items():
            setattr(self, key, value)
        return True

    def create(self):
        self.session._writes.append(
            ("create", int(self.sequence_number), self._attrs)
        )

    def update(self):
        self.session._writes.append(
            ("update", int(self.sequence_number), self._attrs)
        )

    def delete(self):
        self.session._writes.append(
            ("delete", int(self.sequence_number), None)
        )

    @classmethod
    def get_all(cls, session, parent_class):
        return {
            str(seq): cls(session, str(seq), parent_class)
            for seq in session._existing_entries
        }


def build_session(exists=False, entries=None):
    """
    entries: {seq(int): <full configuration dict>}
    """
    session = MagicMock()
    session._exists = exists
    session._existing_entries = entries or {}
    session._class_creates = []
    session._class_deletes = []
    session._writes = []

    def get_module(sess, name, index, **kwargs):
        return FakeClass(session, index, kwargs.get("type"))

    session.api.get_module.side_effect = get_module
    return session


def run(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session), patch(
        MODULE + ".ClassEntry", FakeClassEntry
    ), patch(MODULE + ".HAS_PYAOSCX_CLASS", True):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_class.main()
    return exc.value.args[0]


def entry_writes(session, op):
    return [w for w in session._writes if w[0] == op]


def test_create_empty_class():
    session = build_session(exists=False)
    result = run({"name": NAME, "type": TYPE}, session)
    assert result["changed"] is True
    assert (NAME, TYPE) in session._class_creates


def test_create_with_entry():
    session = build_session(exists=False)
    result = run(
        {
            "name": NAME,
            "type": TYPE,
            "entries": [
                {
                    "sequence_number": 10,
                    "protocol": 6,
                    "dst_ip": "10.0.0.0/255.255.255.0",
                    "dst_l4_port_min": 443,
                    "dst_l4_port_max": 443,
                    "count": True,
                    "comment": "web",
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    creates = entry_writes(session, "create")
    assert creates
    assert creates[0][1] == 10
    attrs = creates[0][2]
    assert attrs["type"] == "match"
    assert attrs["protocol"] == 6
    assert attrs["dst_ip"] == "10.0.0.0/255.255.255.0"
    assert attrs["count"] is True


def test_delete():
    session = build_session(exists=True)
    result = run({"name": NAME, "type": TYPE, "state": "delete"}, session)
    assert result["changed"] is True
    assert (NAME, TYPE) in session._class_deletes


def test_delete_absent():
    session = build_session(exists=False)
    result = run({"name": NAME, "type": TYPE, "state": "delete"}, session)
    assert result["changed"] is False
    assert not session._class_deletes
    assert not session._class_creates
    assert not session._writes


def test_idempotent_entry():
    entries = {
        10: full_entry(
            protocol=6,
            dst_ip="10.0.0.0/255.255.255.0",
            dst_l4_port_min=443,
            dst_l4_port_max=443,
            count=True,
            comment="web",
        )
    }
    session = build_session(exists=True, entries=entries)
    result = run(
        {
            "name": NAME,
            "type": TYPE,
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "protocol": 6,
                    "dst_ip": "10.0.0.0/255.255.255.0",
                    "dst_l4_port_min": 443,
                    "dst_l4_port_max": 443,
                    "count": True,
                    "comment": "web",
                }
            ],
        },
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_match_change_recreates_entry():
    entries = {10: full_entry(protocol=6, comment="x")}
    session = build_session(exists=True, entries=entries)
    result = run(
        {
            "name": NAME,
            "type": TYPE,
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "protocol": 17,
                    "comment": "x",
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    assert ("delete", 10, None) in session._writes
    assert any(w[1] == 10 for w in entry_writes(session, "create"))


def test_comment_only_change_uses_put():
    entries = {10: full_entry(protocol=6, comment="old")}
    session = build_session(exists=True, entries=entries)
    result = run(
        {
            "name": NAME,
            "type": TYPE,
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "protocol": 6,
                    "comment": "new",
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    updates = entry_writes(session, "update")
    assert any(w[1] == 10 for w in updates)
    assert updates[0][2]["comment"] == "new"
    assert not entry_writes(session, "delete")
    assert not entry_writes(session, "create")


def test_action_ignore_recreates():
    entries = {10: full_entry(protocol=6)}
    session = build_session(exists=True, entries=entries)
    result = run(
        {
            "name": NAME,
            "type": TYPE,
            "state": "update",
            "entries": [
                {
                    "sequence_number": 10,
                    "action": "ignore",
                    "protocol": 6,
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    assert ("delete", 10, None) in session._writes
    assert any(w[1] == 10 for w in entry_writes(session, "create"))


def test_remove_all_entries():
    entries = {10: full_entry(protocol=6)}
    session = build_session(exists=True, entries=entries)
    result = run(
        {"name": NAME, "type": TYPE, "state": "update", "entries": []},
        session,
    )
    assert result["changed"] is True
    assert ("delete", 10, None) in session._writes
    assert not session._class_deletes


def test_entries_omitted_leaves_entries_untouched():
    entries = {10: full_entry(protocol=6)}
    session = build_session(exists=True, entries=entries)
    result = run({"name": NAME, "type": TYPE, "state": "update"}, session)
    assert result["changed"] is False
    assert not session._writes
    assert not session._class_creates
    assert not session._class_deletes


def test_duplicate_sequence_fails():
    session = build_session(exists=False)
    result = run(
        {
            "name": NAME,
            "type": TYPE,
            "entries": [
                {"sequence_number": 10, "protocol": 6},
                {"sequence_number": 10, "protocol": 17},
            ],
        },
        session,
    )
    assert result["failed"] is True


def test_remove_extra_keep_matching():
    entries = {
        10: full_entry(protocol=6),
        20: full_entry(protocol=17),
    }
    session = build_session(exists=True, entries=entries)
    result = run(
        {
            "name": NAME,
            "type": TYPE,
            "state": "update",
            "entries": [{"sequence_number": 10, "protocol": 6}],
        },
        session,
    )
    assert result["changed"] is True
    assert ("delete", 20, None) in session._writes
    assert not any(w[0] == "delete" and w[1] == 10 for w in session._writes)
    assert not entry_writes(session, "create")
