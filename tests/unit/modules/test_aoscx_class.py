# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_class module.

The pyaoscx session is fully mocked through session.request, so no switch is
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
    aoscx_class,
)

MODULE = "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_class"

COLLECTION = "system/classes"
NAME = "c1"
TYPE = "ipv4"
INDEX = "{0},{1}".format(NAME, TYPE)
CPATH = "{0}/{1}".format(COLLECTION, INDEX)

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


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = {} if payload is None else payload
        self.text = ""

    def json(self):
        return self._payload


def build_session(exists=False, entries=None):
    """
    entries: {seq(int): <full configuration dict>}
    """
    entries = entries or {}
    writes = []

    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"
    session.api.compound_index_separator = ","

    def router(operation, path, params=None, data=None):
        if operation != "GET":
            writes.append((operation, path, data))
            code = {"POST": 201, "PUT": 200, "DELETE": 204}[operation]
            return FakeResponse(code)
        if path == CPATH:
            return FakeResponse(200 if exists else 404)
        if path.endswith("/cfg_entries"):
            payload = {str(seq): data for seq, data in entries.items()}
            return FakeResponse(200, payload)
        return FakeResponse(404)

    session.request.side_effect = router
    session._writes = writes
    return session


def run(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_class.main()
    return exc.value.args[0]


def writes_of(session, operation):
    return [w for w in session._writes if w[0] == operation]


def test_create_empty_class():
    session = build_session(exists=False)
    result = run({"name": NAME, "type": TYPE}, session)
    assert result["changed"] is True
    posts = writes_of(session, "POST")
    assert any(p[1] == COLLECTION for p in posts)
    body = json.loads([p for p in posts if p[1] == COLLECTION][0][2])
    assert body == {"name": NAME, "type": TYPE}


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
    posts = writes_of(session, "POST")
    entry_posts = [p for p in posts if p[1].endswith("/cfg_entries")]
    assert entry_posts
    body = json.loads(entry_posts[0][2])
    assert body["sequence_number"] == 10
    assert body["type"] == "match"
    assert body["protocol"] == 6
    assert body["dst_ip"] == "10.0.0.0/255.255.255.0"
    assert body["count"] is True


def test_delete():
    session = build_session(exists=True)
    result = run({"name": NAME, "type": TYPE, "state": "delete"}, session)
    assert result["changed"] is True
    deletes = writes_of(session, "DELETE")
    assert any(d[1] == CPATH for d in deletes)


def test_delete_absent():
    session = build_session(exists=False)
    result = run({"name": NAME, "type": TYPE, "state": "delete"}, session)
    assert result["changed"] is False
    assert not session._writes


def test_idempotent_entry():
    entries = {
        10: full_entry(
            sequence_number=10,
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
    entries = {10: full_entry(sequence_number=10, protocol=6, comment="x")}
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
    deletes = writes_of(session, "DELETE")
    posts = writes_of(session, "POST")
    assert any(d[1].endswith("/cfg_entries/10") for d in deletes)
    assert any(p[1].endswith("/cfg_entries") for p in posts)


def test_comment_only_change_uses_put():
    entries = {10: full_entry(sequence_number=10, protocol=6, comment="old")}
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
    puts = writes_of(session, "PUT")
    assert any(p[1].endswith("/cfg_entries/10") for p in puts)
    assert not writes_of(session, "DELETE")
    assert not [
        p for p in writes_of(session, "POST") if p[1].endswith("/cfg_entries")
    ]


def test_action_ignore_recreates():
    entries = {10: full_entry(sequence_number=10, protocol=6)}
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
    assert writes_of(session, "DELETE")


def test_remove_all_entries():
    entries = {10: full_entry(sequence_number=10, protocol=6)}
    session = build_session(exists=True, entries=entries)
    result = run(
        {"name": NAME, "type": TYPE, "state": "update", "entries": []},
        session,
    )
    assert result["changed"] is True
    deletes = writes_of(session, "DELETE")
    assert any(d[1].endswith("/cfg_entries/10") for d in deletes)
    assert not any(d[1] == CPATH for d in deletes)


def test_entries_omitted_leaves_entries_untouched():
    entries = {10: full_entry(sequence_number=10, protocol=6)}
    session = build_session(exists=True, entries=entries)
    result = run({"name": NAME, "type": TYPE, "state": "update"}, session)
    assert result["changed"] is False
    assert not session._writes


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
        10: full_entry(sequence_number=10, protocol=6),
        20: full_entry(sequence_number=20, protocol=17),
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
    deletes = writes_of(session, "DELETE")
    assert any(d[1].endswith("/cfg_entries/20") for d in deletes)
    assert not any(d[1].endswith("/cfg_entries/10") for d in deletes)
    assert not [
        p for p in writes_of(session, "POST") if p[1].endswith("/cfg_entries")
    ]
