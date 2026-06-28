# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_mka_policy module.

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
    aoscx_mka_policy,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_mka_policy"
)

COLLECTION = "system/mka_policies"
NAME = "mka1"
PATH = "{0}/{1}".format(COLLECTION, NAME)
PREFIX = "/rest/v10.16/"


def kc_uri(name):
    return "{0}system/keychains/{1}".format(PREFIX, name)


WRITABLE_DEFAULTS = {
    "cak": None,
    "ckn": None,
    "eapol_destination_mac": "01:80:c2:00:00:03",
    "eapol_dot1q_tagged": False,
    "eapol_eth_type": "888e",
    "key_server_priority": 0,
    "mode": "psk",
    "transmit_interval": 2,
}


def writable(**overrides):
    rep = json.loads(json.dumps(WRITABLE_DEFAULTS))
    rep.update(overrides)
    return rep


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


def build_session(exists=False, current=None, keychain_exists=True):
    writes = []

    session = MagicMock()
    session.resource_prefix = PREFIX
    session.api.compound_index_separator = ","

    def router(operation, path, params=None, data=None):
        if operation != "GET":
            writes.append((operation, path, data))
            code = {"POST": 201, "PUT": 200, "DELETE": 204}[operation]
            return FakeResponse(code)
        if path == PATH:
            if exists:
                return FakeResponse(200, current or writable())
            return FakeResponse(404)
        if path.startswith("system/keychains/"):
            return FakeResponse(200 if keychain_exists else 404)
        return FakeResponse(404)

    session.request.side_effect = router
    session._writes = writes
    return session


def run(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_mka_policy.main()
    return exc.value.args[0]


def writes_of(session, operation):
    return [w for w in session._writes if w[0] == operation]


def test_create_minimal():
    session = build_session(exists=False)
    result = run({"name": NAME}, session)
    assert result["changed"] is True
    posts = writes_of(session, "POST")
    assert posts and posts[0][1] == COLLECTION
    assert json.loads(posts[0][2]) == {"name": NAME}


def test_create_with_keychain_and_secrets():
    session = build_session(exists=False, keychain_exists=True)
    result = run(
        {
            "name": NAME,
            "mode": "psk",
            "keychain": "kc1",
            "cak": "00112233",
            "ckn": "11",
            "transmit_interval": 6,
        },
        session,
    )
    assert result["changed"] is True
    body = json.loads(writes_of(session, "POST")[0][2])
    assert body["keychain"] == kc_uri("kc1")
    assert body["cak"] == "00112233"
    assert body["ckn"] == "11"
    assert body["transmit_interval"] == 6


def test_create_keychain_missing_fails():
    session = build_session(exists=False, keychain_exists=False)
    result = run({"name": NAME, "keychain": "ghost"}, session)
    assert result.get("failed") is True
    assert not session._writes


def test_delete():
    session = build_session(exists=True)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is True
    assert writes_of(session, "DELETE")


def test_delete_absent():
    session = build_session(exists=False)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is False
    assert not session._writes


def test_idempotent():
    current = writable(transmit_interval=6)
    session = build_session(exists=True, current=current)
    result = run(
        {"name": NAME, "state": "update", "transmit_interval": 6},
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_update_scalar():
    current = writable(transmit_interval=2)
    session = build_session(exists=True, current=current)
    result = run(
        {"name": NAME, "state": "update", "transmit_interval": 6},
        session,
    )
    assert result["changed"] is True
    puts = writes_of(session, "PUT")
    assert puts and puts[0][1] == PATH
    body = json.loads(puts[0][2])
    assert body["transmit_interval"] == 6
    assert body["eapol_eth_type"] == "888e"


def test_update_keychain_ref():
    current = writable(keychain={"kc1": kc_uri("kc1")})
    session = build_session(exists=True, current=current)
    result = run(
        {"name": NAME, "state": "update", "keychain": "kc2"},
        session,
    )
    assert result["changed"] is True
    body = json.loads(writes_of(session, "PUT")[0][2])
    assert body["keychain"] == kc_uri("kc2")


def test_idempotent_keychain_ref():
    current = writable(keychain={"kc1": kc_uri("kc1")})
    session = build_session(exists=True, current=current)
    result = run(
        {"name": NAME, "state": "update", "keychain": "kc1"},
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_secrets_not_compared():
    current = writable(transmit_interval=2)
    session = build_session(exists=True, current=current)
    result = run(
        {
            "name": NAME,
            "state": "update",
            "transmit_interval": 2,
            "cak": "deadbeef",
            "ckn": "22",
        },
        session,
    )
    assert result["changed"] is False
    assert not session._writes
