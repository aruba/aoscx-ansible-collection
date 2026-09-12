# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_macsec_policy module.

The module is backed by the pyaoscx MacsecPolicy SDK class, obtained through
session.api.get_module. Tests replace get_module with a fake that returns a
controllable policy object, so no switch or real SDK call is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import MagicMock, patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_macsec_policy,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_macsec_policy"
)

NAME = "mp1"


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


def make_session(exists=True, attrs=None):
    policy = FakePolicy(exists=exists, attrs=attrs)
    calls = []

    def get_module(session, class_name, index, **kwargs):
        calls.append((class_name, index, kwargs))
        for key, value in kwargs.items():
            setattr(policy, key, value)
            if key not in policy.config_attrs:
                policy.config_attrs.append(key)
        return policy

    session = MagicMock()
    session.api.get_module.side_effect = get_module
    return session, policy, calls


def run(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_macsec_policy.main()
    return exc.value.args[0]


def create_kwargs(calls):
    creates = [c for c in calls if c[2]]
    return creates[-1][2] if creates else {}


def test_create_minimal():
    session, policy, calls = make_session(exists=False)
    result = run({"name": NAME}, session)
    assert result["changed"] is True
    assert policy.created is True


def test_create_with_fields():
    session, policy, calls = make_session(exists=False)
    result = run(
        {
            "name": NAME,
            "secure_mode": "should-secure",
            "replay_window": 100,
            "cipher_suites": {"gcm_aes_256_enabled": True},
            "bypass": {"ieee_bpdu_enabled": True},
        },
        session,
    )
    assert result["changed"] is True
    assert policy.created is True
    kwargs = create_kwargs(calls)
    assert kwargs["secure_mode"] == "should-secure"
    assert kwargs["replay_window"] == 100
    assert kwargs["cipher_suites"] == {"gcm_aes_256_enabled": True}
    assert kwargs["bypass"] == {"ieee_bpdu_enabled": True}


def test_delete():
    session, policy, calls = make_session(exists=True)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is True
    assert policy.deleted is True


def test_delete_absent():
    session, policy, calls = make_session(exists=False)
    result = run({"name": NAME, "state": "delete"}, session)
    assert result["changed"] is False
    assert policy.deleted is False


def test_idempotent():
    session, policy, calls = make_session(
        exists=True, attrs={"secure_mode": "should-secure"}
    )
    result = run(
        {"name": NAME, "state": "update", "secure_mode": "should-secure"},
        session,
    )
    assert result["changed"] is False
    assert policy.updated is False


def test_update_scalar():
    session, policy, calls = make_session(
        exists=True, attrs={"secure_mode": "must-secure"}
    )
    result = run(
        {"name": NAME, "state": "update", "secure_mode": "should-secure"},
        session,
    )
    assert result["changed"] is True
    assert policy.updated is True
    assert policy.secure_mode == "should-secure"
    assert "secure_mode" in policy.config_attrs


def test_update_nested_merges():
    session, policy, calls = make_session(
        exists=True, attrs={"cipher_suites": {"gcm_aes_128_enabled": True}}
    )
    result = run(
        {
            "name": NAME,
            "state": "update",
            "cipher_suites": {"gcm_aes_256_enabled": True},
        },
        session,
    )
    assert result["changed"] is True
    assert policy.updated is True
    assert policy.cipher_suites["gcm_aes_256_enabled"] is True
    assert policy.cipher_suites["gcm_aes_128_enabled"] is True


def test_idempotent_nested():
    session, policy, calls = make_session(
        exists=True, attrs={"bypass": {"ieee_bpdu_enabled": True}}
    )
    result = run(
        {
            "name": NAME,
            "state": "update",
            "bypass": {"ieee_bpdu_enabled": True},
        },
        session,
    )
    assert result["changed"] is False
    assert policy.updated is False
