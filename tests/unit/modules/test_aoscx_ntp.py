# (C) Copyright 2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_ntp_key and aoscx_ntp_server modules. The pyaoscx
NtpKey, NtpAssociation and Vrf classes are fully mocked, so no switch is
required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from unittest.mock import patch

import pytest

from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_ntp_key,
    aoscx_ntp_server,
)

KEY_MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_ntp_key"
)
SRV_MODULE = (
    "ansible_collections.arubanetworks.aoscx.plugins.modules.aoscx_ntp_server"
)


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


WRITES = []


class FakeNtpKey:
    exists = False

    def __init__(self, session, key_id, **kwargs):
        self.session = session
        self.key_id = key_id
        self.kwargs = kwargs

    def get(self, depth=None, selector=None):
        if not FakeNtpKey.exists:
            raise Exception("no key")
        return True

    def get_uri(self):
        return "/rest/v10.09/system/ntp_keys/{0}".format(self.key_id)

    def delete(self):
        WRITES.append(("key_delete", self.key_id, None))

    def apply(self):
        WRITES.append(("key_apply", self.key_id, dict(self.kwargs)))
        return True


class FakeVrf:
    def __init__(self, session, name):
        self.name = name


class FakeAssoc:
    exists = False

    def __init__(self, session, vrf, address, **kwargs):
        self.session = session
        self.vrf = vrf
        self.address = address
        self.kwargs = kwargs

    def get(self, depth=None, selector=None):
        if not FakeAssoc.exists:
            raise Exception("no assoc")
        return True

    def delete(self):
        WRITES.append(("assoc_delete", self.address, None))

    def apply(self):
        WRITES.append(("assoc_apply", self.address, dict(self.kwargs)))
        return True


def run_key(args):
    WRITES.clear()
    set_module_args(args)
    with patch(KEY_MODULE + ".get_pyaoscx_session", return_value=object()), \
            patch(KEY_MODULE + ".NtpKey", FakeNtpKey), \
            patch(KEY_MODULE + ".HAS_PYAOSCX_NTP", True):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_ntp_key.main()
    return exc.value.args[0]


def run_srv(args):
    WRITES.clear()
    set_module_args(args)
    with patch(SRV_MODULE + ".get_pyaoscx_session", return_value=object()), \
            patch(SRV_MODULE + ".NtpAssociation", FakeAssoc), \
            patch(SRV_MODULE + ".NtpKey", FakeNtpKey), \
            patch(SRV_MODULE + ".Vrf", FakeVrf), \
            patch(SRV_MODULE + ".HAS_PYAOSCX_NTP", True):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            aoscx_ntp_server.main()
    return exc.value.args[0]


# --------------------------------------------------------------------------
# aoscx_ntp_key
# --------------------------------------------------------------------------
def test_key_create():
    FakeNtpKey.exists = False
    result = run_key(
        {
            "key_id": 60001,
            "key_password": "secret",
            "key_type": "md5",
            "trust_enable": True,
        }
    )
    assert result["changed"] is True
    applies = [w for w in WRITES if w[0] == "key_apply"]
    assert applies and applies[0][1] == 60001
    assert applies[0][2]["key_type"] == "md5"


def test_key_delete():
    FakeNtpKey.exists = True
    result = run_key({"key_id": 60001, "state": "delete"})
    assert result["changed"] is True
    assert ("key_delete", 60001, None) in WRITES


def test_key_delete_absent():
    FakeNtpKey.exists = False
    result = run_key({"key_id": 60001, "state": "delete"})
    assert result["changed"] is False
    assert not WRITES


def test_key_check_mode():
    FakeNtpKey.exists = False
    set_module_args(
        {
            "key_id": 60001,
            "key_password": "secret",
            "_ansible_check_mode": True,
        }
    )
    with patch(KEY_MODULE + ".get_pyaoscx_session", return_value=object()), \
            patch(KEY_MODULE + ".NtpKey", FakeNtpKey), \
            patch(KEY_MODULE + ".HAS_PYAOSCX_NTP", True):
        with pytest.raises(AnsibleExitJson) as exc:
            aoscx_ntp_key.main()
    assert exc.value.args[0]["changed"] is False
    assert not WRITES


def test_key_required_password():
    WRITES.clear()
    set_module_args({"key_id": 60001, "state": "create"})
    with patch(KEY_MODULE + ".get_pyaoscx_session", return_value=object()), \
            patch(KEY_MODULE + ".NtpKey", FakeNtpKey), \
            patch(KEY_MODULE + ".HAS_PYAOSCX_NTP", True):
        with pytest.raises(AnsibleFailJson) as exc:
            aoscx_ntp_key.main()
    assert exc.value.args[0]["failed"] is True


# --------------------------------------------------------------------------
# aoscx_ntp_server
# --------------------------------------------------------------------------
def test_srv_create():
    FakeAssoc.exists = False
    result = run_srv(
        {"address": "198.51.100.1", "prefer": True, "ntp_version": 4}
    )
    assert result["changed"] is True
    applies = [w for w in WRITES if w[0] == "assoc_apply"]
    assert applies and applies[0][1] == "198.51.100.1"
    assert applies[0][2]["association_attributes"]["prefer"] is True


def test_srv_create_with_key():
    FakeAssoc.exists = False
    result = run_srv({"address": "198.51.100.2", "key_id": 60001})
    assert result["changed"] is True
    applies = [w for w in WRITES if w[0] == "assoc_apply"]
    assert applies[0][2]["key_id"].endswith("ntp_keys/60001")


def test_srv_delete():
    FakeAssoc.exists = True
    result = run_srv({"address": "198.51.100.1", "state": "delete"})
    assert result["changed"] is True
    assert ("assoc_delete", "198.51.100.1", None) in WRITES


def test_srv_delete_absent():
    FakeAssoc.exists = False
    result = run_srv({"address": "198.51.100.1", "state": "delete"})
    assert result["changed"] is False
    assert not WRITES
