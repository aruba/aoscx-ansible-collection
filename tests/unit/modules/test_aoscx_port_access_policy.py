# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_port_access_policy module.

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
    aoscx_port_access_policy,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_port_access_policy"
)

POLICY = "system/port_access_policies"
ACTION = "policy_action_set"
NAME = "p1"


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


def build_session(
    policy_exists=False, class_exists=True, entries=None, action_sets=None
):
    entries = entries or {}
    action_sets = action_sets or {}
    writes = []

    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"
    session.api.compound_index_separator = ","

    def router(operation, path, params=None, data=None):
        if operation != "GET":
            writes.append((operation, path, data))
            code = {"POST": 201, "PUT": 200, "DELETE": 204}[operation]
            return FakeResponse(code)
        if path == "{0}/{1}".format(POLICY, NAME):
            return FakeResponse(200 if policy_exists else 404)
        if path.startswith("system/classes/"):
            return FakeResponse(200 if class_exists else 404)
        if path.endswith("/cfg_entries"):
            payload = {str(seq): data for seq, data in entries.items()}
            return FakeResponse(200, payload)
        if path.endswith("/" + ACTION):
            seq = int(path.split("/cfg_entries/")[1].split("/")[0])
            if seq in action_sets:
                return FakeResponse(200, action_sets[seq])
            return FakeResponse(404)
        return FakeResponse(404)

    session.request.side_effect = router
    session._writes = writes
    return session


def run_module(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_port_access_policy.main()
    return exc.value.args[0]


def writes_of(session, operation):
    return [w for w in session._writes if w[0] == operation]


def entry(seq, cls="c1", ctype="ipv4", **kw):
    data = {"sequence_number": seq, "class_name": cls, "class_type": ctype}
    data.update(kw)
    return data


def test_create_empty():
    session = build_session(policy_exists=False)
    result = run_module({"name": NAME}, session)
    assert result["changed"] is True
    assert any(p[1] == POLICY for p in writes_of(session, "POST"))


def test_create_with_redirect_entry():
    session = build_session(policy_exists=False, class_exists=True)
    result = run_module(
        {
            "name": NAME,
            "entries": [entry(10, redirect="captive-portal")],
        },
        session,
    )
    assert result["changed"] is True
    posts = writes_of(session, "POST")
    action_posts = [p for p in posts if p[1].endswith("/" + ACTION)]
    assert action_posts
    body = json.loads(action_posts[0][2])
    assert body["redirect"] == "captive-portal"


def test_class_missing_fails():
    session = build_session(policy_exists=False, class_exists=False)
    result = run_module({"name": NAME, "entries": [entry(10)]}, session)
    assert result["failed"] is True


def test_delete():
    session = build_session(policy_exists=True)
    result = run_module({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is True
    assert writes_of(session, "DELETE")


def test_delete_absent():
    session = build_session(policy_exists=False)
    result = run_module({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is False


def test_idempotent():
    cls_uri = "/rest/v10.16/system/classes/c1,ipv4"
    entries = {10: {"class": {"c1,ipv4": cls_uri}, "comment": "x"}}
    action_sets = {10: {"drop": True, "dscp": 10}}
    session = build_session(
        policy_exists=True, entries=entries, action_sets=action_sets
    )
    result = run_module(
        {
            "name": NAME,
            "state": "update",
            "entries": [entry(10, comment="x", drop=True, dscp=10)],
        },
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_entries_omitted_does_not_touch_entries():
    cls_uri = "/rest/v10.16/system/classes/c1,ipv4"
    entries = {10: {"class": {"c1,ipv4": cls_uri}, "comment": "x"}}
    session = build_session(policy_exists=True, entries=entries)
    result = run_module({"name": NAME, "state": "update"}, session)
    assert result["changed"] is False
    assert not session._writes


def test_class_change_recreates_entry():
    cls_uri = "/rest/v10.16/system/classes/c1,ipv4"
    entries = {10: {"class": {"c1,ipv4": cls_uri}, "comment": None}}
    session = build_session(policy_exists=True, entries=entries)
    result = run_module(
        {
            "name": NAME,
            "state": "update",
            "entries": [entry(10, cls="c2")],
        },
        session,
    )
    assert result["changed"] is True
    assert any(
        d[1].endswith("/cfg_entries/10") for d in writes_of(session, "DELETE")
    )
    assert any(
        p[1].endswith("/cfg_entries") for p in writes_of(session, "POST")
    )


def test_action_set_change():
    cls_uri = "/rest/v10.16/system/classes/c1,ipv4"
    entries = {10: {"class": {"c1,ipv4": cls_uri}, "comment": None}}
    action_sets = {10: {"drop": False}}
    session = build_session(
        policy_exists=True, entries=entries, action_sets=action_sets
    )
    result = run_module(
        {
            "name": NAME,
            "state": "update",
            "entries": [entry(10, drop=True, cir=1000)],
        },
        session,
    )
    assert result["changed"] is True
    puts = writes_of(session, "PUT")
    action_puts = [p for p in puts if p[1].endswith("/" + ACTION)]
    assert action_puts
    body = json.loads(action_puts[0][2])
    assert body["drop"] is True
    assert body["cir"] == 1000
