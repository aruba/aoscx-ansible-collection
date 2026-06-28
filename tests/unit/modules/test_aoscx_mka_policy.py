# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_mka_policy module.

The module is backed by the pyaoscx MkaPolicy SDK class, and resolves the
referenced keychain through the Keychain SDK class. Both are obtained through
session.api.get_module, which is replaced here by a fake that returns
controllable objects, so no switch is required.
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
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_mka_policy"
)

NAME = "mka1"
KC_NAME = "kc1"
KC_URI = "/rest/v10.16/system/keychains/kc1"


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


class FakePolicy:
    def __init__(self, exists=True, attrs=None):
        self._exists = exists
        self.config_attrs = []
        self.created = False
        self.updated = False
        self.deleted = False
        for key, value in (attrs or {}).items():
            setattr(self, key, value)

    def get(self, selector=None):
        if not self._exists:
            raise Exception("not found")
        return True

    def create(self):
        self.created = True

    def update(self):
        self.updated = True

    def delete(self):
        self.deleted = True


class FakeKeychain:
    def __init__(self, exists=True, uri=KC_URI):
        self._exists = exists
        self._uri = uri

    def get(self, selector=None):
        if not self._exists:
            raise Exception("not found")
        return True

    def get_uri(self):
        return self._uri


def make_session(
    exists=True, attrs=None, keychain_exists=True, keychain_uri=KC_URI
):
    policy = FakePolicy(exists=exists, attrs=attrs)
    keychain = FakeKeychain(exists=keychain_exists, uri=keychain_uri)
    calls = []

    def get_module(session, class_name, index, **kwargs):
        calls.append((class_name, index, kwargs))
        if class_name == "Keychain":
            return keychain
        for key, value in kwargs.items():
            setattr(policy, key, value)
            if key not in policy.config_attrs:
                policy.config_attrs.append(key)
        return policy

    session = MagicMock()
    session.api.get_module.side_effect = get_module
    return session, policy, keychain, calls


def run(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_mka_policy.main()
    return exc.value.args[0]


def create_kwargs(calls):
    creates = [c for c in calls if c[0] == "MkaPolicy" and c[2]]
    return creates[-1][2] if creates else {}


def test_create_minimal():
    session, policy, keychain, calls = make_session(exists=False)
    result = run({"name": NAME}, session)
    assert result["changed"] is True
    assert policy.created is True


def test_create_with_fields():
    session, policy, keychain, calls = make_session(exists=False)
    result = run(
        {
            "name": NAME,
            "mode": "psk",
            "transmit_interval": 5,
            "keychain": KC_NAME,
        },
        session,
    )
    assert result["changed"] is True
    assert policy.created is True
    kwargs = create_kwargs(calls)
    assert kwargs["mode"] == "psk"
    assert kwargs["transmit_interval"] == 5
    assert kwargs["keychain"] == KC_URI


def test_create_with_secret():
    session, policy, keychain, calls = make_session(exists=False)
    result = run(
        {"name": NAME, "cak": "secret", "ckn": "0011"},
        session,
    )
    assert result["changed"] is True
    kwargs = create_kwargs(calls)
    assert kwargs["cak"] == "secret"
    assert kwargs["ckn"] == "0011"


def test_keychain_missing():
    session, policy, keychain, calls = make_session(
        exists=False, keychain_exists=False
    )
    result = run({"name": NAME, "keychain": KC_NAME}, session)
    assert result["failed"] is True


def test_delete():
    session, policy, keychain, calls = make_session(exists=True)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is True
    assert policy.deleted is True


def test_delete_absent():
    session, policy, keychain, calls = make_session(exists=False)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is False
    assert policy.deleted is False


def test_idempotent():
    session, policy, keychain, calls = make_session(
        exists=True, attrs={"mode": "psk"}
    )
    result = run(
        {"name": NAME, "state": "update", "mode": "psk"},
        session,
    )
    assert result["changed"] is False
    assert policy.updated is False


def test_update_scalar():
    session, policy, keychain, calls = make_session(
        exists=True, attrs={"transmit_interval": 2}
    )
    result = run(
        {"name": NAME, "state": "update", "transmit_interval": 5},
        session,
    )
    assert result["changed"] is True
    assert policy.updated is True
    assert policy.transmit_interval == 5


def test_keychain_idempotent():
    session, policy, keychain, calls = make_session(
        exists=True, attrs={"keychain": {KC_NAME: KC_URI}}
    )
    result = run(
        {"name": NAME, "state": "update", "keychain": KC_NAME},
        session,
    )
    assert result["changed"] is False
    assert policy.updated is False


def test_keychain_update():
    other_uri = "/rest/v10.16/system/keychains/other"
    session, policy, keychain, calls = make_session(
        exists=True, attrs={"keychain": {"other": other_uri}}
    )
    result = run(
        {"name": NAME, "state": "update", "keychain": KC_NAME},
        session,
    )
    assert result["changed"] is True
    assert policy.updated is True
    assert policy.keychain == KC_URI
