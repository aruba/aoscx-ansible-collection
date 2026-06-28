# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_keychain module.

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
    aoscx_keychain,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_keychain"
)

COLLECTION = "system/keychains"
NAME = "mka_keys"
PATH = "{0}/{1}".format(COLLECTION, NAME)
KEYS_PATH = "{0}/keys".format(PATH)


def key_config(key_id, **fields):
    """Build the configuration-selector representation of a key."""
    rep = {
        "key_id": key_id,
        "auth_type": "sha256",
        "auth_key": "AQBEncryptedBlob==",
        "name": None,
        "accept_start": 1577836800,
        "accept_end": 2556143999,
        "send_start": 1577836800,
        "send_end": 2556143999,
        "recv_id": 1,
        "send_id": 1,
    }
    rep.update(fields)
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


def build_session(exists=False, keys=None):
    keys = keys or {}
    writes = []

    session = MagicMock()
    session.resource_prefix = "/rest/v10.16/"
    session.api.compound_index_separator = ","

    def router(operation, path, params=None, data=None):
        if operation != "GET":
            writes.append((operation, path, data))
            code = {"POST": 201, "PUT": 200, "DELETE": 204}[operation]
            return FakeResponse(code)
        if path == PATH:
            return FakeResponse(200 if exists else 404)
        if path == KEYS_PATH:
            payload = {str(k): v for k, v in keys.items()}
            return FakeResponse(200, payload)
        return FakeResponse(404)

    session.request.side_effect = router
    session._writes = writes
    return session


def run(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_keychain.main()
    return exc.value.args[0]


def writes_of(session, operation):
    return [w for w in session._writes if w[0] == operation]


def test_create_empty_keychain():
    session = build_session(exists=False)
    result = run({"name": NAME}, session)
    assert result["changed"] is True
    posts = writes_of(session, "POST")
    assert len(posts) == 1
    assert posts[0][1] == COLLECTION
    assert json.loads(posts[0][2]) == {"name": NAME}


def test_create_with_key():
    session = build_session(exists=False)
    result = run(
        {
            "name": NAME,
            "keys": [
                {
                    "key_id": 1,
                    "auth_type": "sha256",
                    "auth_key": "S3cretKey123",
                    "send_start": 1577836800,
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    posts = writes_of(session, "POST")
    assert posts[0][1] == COLLECTION
    key_post = [p for p in posts if p[1] == KEYS_PATH]
    assert key_post
    body = json.loads(key_post[0][2])
    assert body["key_id"] == 1
    assert body["auth_type"] == "sha256"
    assert body["auth_key"] == "S3cretKey123"


def test_delete():
    session = build_session(exists=True)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is True
    deletes = writes_of(session, "DELETE")
    assert deletes and deletes[0][1] == PATH


def test_delete_absent():
    session = build_session(exists=False)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is False
    assert not session._writes


def test_idempotent_key():
    session = build_session(exists=True, keys={1: key_config(1)})
    result = run(
        {
            "name": NAME,
            "keys": [
                {
                    "key_id": 1,
                    "auth_type": "sha256",
                    "accept_start": 1577836800,
                    "accept_end": 2556143999,
                    "send_start": 1577836800,
                    "send_end": 2556143999,
                    "recv_id": 1,
                    "send_id": 1,
                }
            ],
        },
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_auth_key_not_compared():
    session = build_session(exists=True, keys={1: key_config(1)})
    result = run(
        {
            "name": NAME,
            "keys": [
                {
                    "key_id": 1,
                    "auth_type": "sha256",
                    "auth_key": "ADifferentPlaintext",
                    "accept_start": 1577836800,
                    "accept_end": 2556143999,
                    "send_start": 1577836800,
                    "send_end": 2556143999,
                    "recv_id": 1,
                    "send_id": 1,
                }
            ],
        },
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_key_change_recreates():
    session = build_session(exists=True, keys={1: key_config(1)})
    result = run(
        {
            "name": NAME,
            "keys": [
                {
                    "key_id": 1,
                    "auth_type": "sha512",
                    "send_start": 1577836800,
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    deletes = writes_of(session, "DELETE")
    posts = writes_of(session, "POST")
    assert any(d[1] == "{0}/1".format(KEYS_PATH) for d in deletes)
    assert any(p[1] == KEYS_PATH for p in posts)


def test_remove_all_keys():
    session = build_session(exists=True, keys={1: key_config(1)})
    result = run({"name": NAME, "keys": []}, session)
    assert result["changed"] is True
    deletes = writes_of(session, "DELETE")
    assert any(d[1] == "{0}/1".format(KEYS_PATH) for d in deletes)


def test_keys_omitted_leaves_untouched():
    session = build_session(exists=True, keys={1: key_config(1)})
    result = run({"name": NAME}, session)
    assert result["changed"] is False
    assert not session._writes


def test_add_key_to_existing():
    session = build_session(exists=True, keys={})
    result = run(
        {
            "name": NAME,
            "keys": [
                {
                    "key_id": 2,
                    "auth_type": "sha256",
                    "send_start": 1577836800,
                }
            ],
        },
        session,
    )
    assert result["changed"] is True
    posts = writes_of(session, "POST")
    assert any(p[1] == KEYS_PATH for p in posts)


def test_duplicate_key_id_fails():
    session = build_session(exists=False)
    result = run(
        {
            "name": NAME,
            "keys": [
                {"key_id": 1, "auth_type": "sha256"},
                {"key_id": 1, "auth_type": "sha512"},
            ],
        },
        session,
    )
    assert result.get("failed") is True
