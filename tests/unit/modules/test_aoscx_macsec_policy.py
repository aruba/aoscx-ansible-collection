# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_macsec_policy module.

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
    aoscx_macsec_policy,
)

MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules."
    "aoscx_macsec_policy"
)

COLLECTION = "system/macsec_policies"
NAME = "mp1"
PATH = "{0}/{1}".format(COLLECTION, NAME)

# Default writable representation returned by the switch for a fresh policy.
WRITABLE_DEFAULTS = {
    "bypass": {"ieee_bpdu_enabled": False},
    "cipher_suites": {
        "gcm_aes_128_enabled": False,
        "gcm_aes_256_enabled": False,
        "gcm_aes_xpn_128_enabled": False,
        "gcm_aes_xpn_256_enabled": False,
    },
    "clear_tag_mode": "none",
    "confidentiality_disable": False,
    "confidentiality_offset": "byte_0",
    "data_delay_protection_enable": False,
    "include_sci_disable": False,
    "replay_protect_disable": False,
    "replay_window": 0,
    "secure_mode": "must-secure",
}


def writable(**overrides):
    rep = json.loads(json.dumps(WRITABLE_DEFAULTS))
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(rep.get(key), dict):
            rep[key].update(value)
        else:
            rep[key] = value
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


def build_session(exists=False, current=None):
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
            if exists:
                return FakeResponse(200, current or writable())
            return FakeResponse(404)
        return FakeResponse(404)

    session.request.side_effect = router
    session._writes = writes
    return session


def run(args, session):
    set_module_args(args)
    with patch(MODULE + ".get_pyaoscx_session", return_value=session):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_macsec_policy.main()
    return exc.value.args[0]


def writes_of(session, operation):
    return [w for w in session._writes if w[0] == operation]


def test_create_minimal():
    session = build_session(exists=False)
    result = run({"name": NAME}, session)
    assert result["changed"] is True
    posts = writes_of(session, "POST")
    assert posts and posts[0][1] == COLLECTION
    body = json.loads(posts[0][2])
    assert body == {"name": NAME}


def test_create_with_fields():
    session = build_session(exists=False)
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
    body = json.loads(writes_of(session, "POST")[0][2])
    assert body["secure_mode"] == "should-secure"
    assert body["replay_window"] == 100
    assert body["cipher_suites"] == {"gcm_aes_256_enabled": True}
    assert body["bypass"] == {"ieee_bpdu_enabled": True}


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
    current = writable(secure_mode="should-secure")
    session = build_session(exists=True, current=current)
    result = run(
        {"name": NAME, "state": "update", "secure_mode": "should-secure"},
        session,
    )
    assert result["changed"] is False
    assert not session._writes


def test_update_scalar():
    current = writable(secure_mode="must-secure")
    session = build_session(exists=True, current=current)
    result = run(
        {"name": NAME, "state": "update", "secure_mode": "should-secure"},
        session,
    )
    assert result["changed"] is True
    puts = writes_of(session, "PUT")
    assert puts and puts[0][1] == PATH
    body = json.loads(puts[0][2])
    assert body["secure_mode"] == "should-secure"
    # other fields preserved from current
    assert body["replay_window"] == 0


def test_update_nested_merges():
    current = writable(
        cipher_suites={"gcm_aes_128_enabled": True},
    )
    session = build_session(exists=True, current=current)
    result = run(
        {
            "name": NAME,
            "state": "update",
            "cipher_suites": {"gcm_aes_256_enabled": True},
        },
        session,
    )
    assert result["changed"] is True
    body = json.loads(writes_of(session, "PUT")[0][2])
    # supplied key set and previously-set key preserved
    assert body["cipher_suites"]["gcm_aes_256_enabled"] is True
    assert body["cipher_suites"]["gcm_aes_128_enabled"] is True


def test_idempotent_nested():
    current = writable(bypass={"ieee_bpdu_enabled": True})
    session = build_session(exists=True, current=current)
    result = run(
        {
            "name": NAME,
            "state": "update",
            "bypass": {"ieee_bpdu_enabled": True},
        },
        session,
    )
    assert result["changed"] is False
    assert not session._writes
