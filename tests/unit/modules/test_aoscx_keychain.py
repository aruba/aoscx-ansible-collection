# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_keychain module.

The module is backed by the pyaoscx Keychain and KeychainKey SDK classes,
imported directly. Tests replace those classes with controllable fakes, so no
switch is required. Keychain keys are immutable on the switch, so a changed key
is reconciled as delete + recreate.
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
    "ansible_collections.arubanetworks.aoscx.plugins.modules." "aoscx_keychain"
)

NAME = "kc1"


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


class FakeKeychain:
    def __init__(self, exists=True):
        self._exists = exists
        self.name = NAME
        self.created = False
        self.deleted = False

    def get(self, selector=None):
        if not self._exists:
            raise Exception("not found")
        return True

    def create(self):
        self.created = True

    def delete(self):
        self.deleted = True


class KeyRecorder:
    """Track key reconcile operations and seed the current switch state."""

    def __init__(self, existing=None):
        # {int key_id: {comparable_field: value}}
        self.existing = existing or {}
        self.created = []
        self.deleted = []

    def make_class(self):
        recorder = self

        class FakeKey:
            def __init__(
                self, session, key_id, parent_keychain=None, **kwargs
            ):
                self.session = session
                self.key_id = key_id
                self._attrs = kwargs

            def get(self, selector=None):
                data = recorder.existing.get(int(self.key_id), {})
                for field, value in data.items():
                    setattr(self, field, value)
                return True

            def create(self):
                recorder.created.append((int(self.key_id), self._attrs))

            def delete(self):
                recorder.deleted.append(int(self.key_id))

            @classmethod
            def get_all(cls, session, parent_keychain):
                result = {}
                for kid in recorder.existing:
                    result[str(kid)] = cls(session, str(kid), parent_keychain)
                return result

        return FakeKey


def run(args, keychain, key_cls):
    set_module_args(args)
    session = MagicMock()
    with patch(MODULE + ".get_pyaoscx_session", return_value=session), patch(
        MODULE + ".HAS_PYAOSCX_KEYCHAIN", True
    ), patch(MODULE + ".Keychain", return_value=keychain), patch(
        MODULE + ".KeychainKey", key_cls
    ):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_keychain.main()
    return exc.value.args[0]


def test_create_minimal():
    keychain = FakeKeychain(exists=False)
    recorder = KeyRecorder()
    result = run({"name": NAME}, keychain, recorder.make_class())
    assert result["changed"] is True
    assert keychain.created is True


def test_delete():
    keychain = FakeKeychain(exists=True)
    recorder = KeyRecorder()
    result = run(
        {"name": NAME, "state": "delete"}, keychain, recorder.make_class()
    )
    assert result["changed"] is True
    assert keychain.deleted is True


def test_delete_absent():
    keychain = FakeKeychain(exists=False)
    recorder = KeyRecorder()
    result = run(
        {"name": NAME, "state": "delete"}, keychain, recorder.make_class()
    )
    assert result["changed"] is False
    assert keychain.deleted is False


def test_create_with_keys():
    keychain = FakeKeychain(exists=False)
    recorder = KeyRecorder()
    result = run(
        {
            "name": NAME,
            "keys": [
                {
                    "key_id": 1,
                    "auth_type": "sha256",
                    "auth_key": "deadbeef",
                }
            ],
        },
        keychain,
        recorder.make_class(),
    )
    assert result["changed"] is True
    assert keychain.created is True
    assert [kid for kid, _ in recorder.created] == [1]
    attrs = dict(recorder.created)[1]
    assert attrs["auth_type"] == "sha256"
    assert attrs["auth_key"] == "deadbeef"


def test_keys_idempotent():
    keychain = FakeKeychain(exists=True)
    recorder = KeyRecorder(existing={1: {"auth_type": "sha256"}})
    result = run(
        {
            "name": NAME,
            "state": "update",
            "keys": [
                {
                    "key_id": 1,
                    "auth_type": "sha256",
                    "auth_key": "deadbeef",
                }
            ],
        },
        keychain,
        recorder.make_class(),
    )
    assert result["changed"] is False
    assert recorder.created == []
    assert recorder.deleted == []


def test_keys_remove_extra():
    keychain = FakeKeychain(exists=True)
    recorder = KeyRecorder(
        existing={1: {"auth_type": "sha256"}, 2: {"auth_type": "md5"}}
    )
    result = run(
        {
            "name": NAME,
            "state": "update",
            "keys": [{"key_id": 1, "auth_type": "sha256"}],
        },
        keychain,
        recorder.make_class(),
    )
    assert result["changed"] is True
    assert recorder.deleted == [2]
    assert recorder.created == []


def test_keys_recreate_changed():
    keychain = FakeKeychain(exists=True)
    recorder = KeyRecorder(existing={1: {"auth_type": "sha256"}})
    result = run(
        {
            "name": NAME,
            "state": "update",
            "keys": [{"key_id": 1, "auth_type": "md5"}],
        },
        keychain,
        recorder.make_class(),
    )
    assert result["changed"] is True
    assert recorder.deleted == [1]
    assert [kid for kid, _ in recorder.created] == [1]


def test_no_keys_param_idempotent():
    keychain = FakeKeychain(exists=True)
    recorder = KeyRecorder(existing={1: {"auth_type": "sha256"}})
    result = run(
        {"name": NAME, "state": "update"}, keychain, recorder.make_class()
    )
    assert result["changed"] is False
    assert recorder.created == []
    assert recorder.deleted == []
