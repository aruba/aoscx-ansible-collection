# (C) Copyright 2019-2024 Hewlett Packard Enterprise Development LP.
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Unit tests for the aoscx_nae_script, aoscx_nae_agent, aoscx_nae_lite_agent
and aoscx_nae_info modules.

These tests mock the pyaoscx session entirely, so no switch is required.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import base64

import pytest

from unittest.mock import MagicMock, patch

from ansible.module_utils import basic

from ansible_collections.arubanetworks.aoscx.plugins.modules import (
    aoscx_nae_agent,
    aoscx_nae_info,
    aoscx_nae_lite_agent,
    aoscx_nae_script,
)

PACKAGE = "ansible_collections.arubanetworks.aoscx.plugins.modules."


class AnsibleExitJson(Exception):
    """Raised by the mocked exit_json to stop module execution."""


class AnsibleFailJson(Exception):
    """Raised by the mocked fail_json to stop module execution."""


def exit_json(*args, **kwargs):
    kwargs.setdefault("changed", False)
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


@pytest.fixture(autouse=True)
def patch_ansible_module():
    with patch.multiple(
        basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json
    ):
        yield


def run_module(module, args, session):
    with patch.object(basic, "_load_params", lambda: dict(args)), patch(
        PACKAGE + module.__name__.split(".")[-1] + ".get_pyaoscx_session",
        return_value=session,
    ):
        with pytest.raises((AnsibleExitJson, AnsibleFailJson)) as exc:
            module.main()
    return exc.value.args[0]


def b64(text):
    return base64.b64encode(text.encode()).decode()


# --------------------------------------------------------------------------
# aoscx_nae_script
# --------------------------------------------------------------------------
def build_script(exists, content="code", origin="user", state="VALIDATED"):
    script = MagicMock()
    script.config_attrs = ["expert_only", "script"]
    if exists:
        script.script = b64(content)
        script.expert_only = False
    else:
        script.get.side_effect = Exception("not found")
    script.get_status.return_value = {"origin": origin, "state": state}
    script.wait_for_validation.return_value = {
        "state": state,
        "error_description": "invalid syntax" if state == "ERROR" else None,
    }
    script.get_parameters.return_value = {}
    return script


def script_session(current, created=None):
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if kwargs:
            created.kwargs = kwargs
            return created
        return current

    session.api.get_module.side_effect = get_module
    return session


def test_script_upload_from_src(tmp_path):
    src = tmp_path / "monitor.py"
    src.write_text("Manifest = {}\n")
    created = build_script(exists=True)
    session = script_session(build_script(exists=False), created)

    result = run_module(
        aoscx_nae_script,
        {"name": "qa_monitor", "src": str(src)},
        session,
    )

    assert result["changed"] is True
    assert created.kwargs == {"script": b64("Manifest = {}\n")}
    created.create.assert_called_once()
    created.wait_for_validation.assert_called_once_with(timeout=60)


def test_script_upload_from_base64():
    created = build_script(exists=True)
    session = script_session(build_script(exists=False), created)
    encoded = b64("Manifest = {}\n")

    result = run_module(
        aoscx_nae_script,
        # Line breaks of wrapped Base64 lines are ignored
        {
            "name": "qa_monitor",
            "script_base64": encoded[:8] + "\n" + encoded[8:],
        },
        session,
    )

    assert result["changed"] is True
    assert created.kwargs == {"script": encoded}


def test_script_invalid_base64_fails_before_any_change():
    session = script_session(build_script(exists=False))
    result = run_module(
        aoscx_nae_script,
        {"name": "qa_monitor", "script_base64": "not base64!"},
        session,
    )
    assert result["failed"] is True
    assert "Invalid Base64" in result["msg"]
    session.api.get_module.assert_not_called()


def test_script_same_content_is_idempotent():
    script = build_script(exists=True, content="code")
    result = run_module(
        aoscx_nae_script,
        {"name": "qa_monitor", "script": "code"},
        script_session(script),
    )
    assert result["changed"] is False
    script.update.assert_not_called()
    script.wait_for_validation.assert_not_called()


def test_script_update_fails_when_not_valid():
    script = build_script(exists=True, content="old", state="ERROR")
    result = run_module(
        aoscx_nae_script,
        {"name": "qa_monitor", "script": "new"},
        script_session(script),
    )
    script.update.assert_called_once()
    assert result["failed"] is True
    assert "invalid syntax" in result["msg"]


def test_script_unchanged_in_error_fails():
    script = build_script(exists=True, content="invalid", state="ERROR")
    script.get_status.return_value = {
        "origin": "user",
        "state": "ERROR",
        "error_description": "invalid syntax",
    }
    result = run_module(
        aoscx_nae_script,
        {"name": "qa_monitor", "script": "invalid"},
        script_session(script),
    )
    script.update.assert_not_called()
    assert result["failed"] is True
    assert "invalid syntax" in result["msg"]


@pytest.mark.parametrize("origin", ["system", "generated"])
def test_script_refuses_system_and_generated_scripts(origin):
    script = build_script(exists=True, origin=origin)
    result = run_module(
        aoscx_nae_script,
        {"name": "qa_monitor", "state": "delete"},
        script_session(script),
    )
    assert result["failed"] is True
    script.delete.assert_not_called()


def test_script_create_requires_content():
    result = run_module(
        aoscx_nae_script,
        {"name": "qa_monitor"},
        script_session(build_script(exists=False)),
    )
    assert result["failed"] is True
    assert "script_base64" in result["msg"]


# --------------------------------------------------------------------------
# aoscx_nae_agent
# --------------------------------------------------------------------------
DEFINITIONS = {
    "threshold": {"encrypt": False},
    "label": {"encrypt": False},
    "token": {"encrypt": True},
}


def build_agent(exists, **attrs):
    agent = MagicMock()
    agent.config_attrs = ["disabled", "parameters_values"]
    agent.encrypted_parameters_names = attrs.pop("encrypted", [])
    if exists:
        agent.disabled = False
        agent.vrf = "default"
        agent.parameters_values = {}
        for key, value in attrs.items():
            setattr(agent, key, value)
    else:
        agent.get.side_effect = Exception("not found")
    agent.get_status.return_value = {"alert_level": "NORMAL"}
    return agent


def agent_session(agent, script_state="VALIDATED", created=None):
    script = MagicMock()
    script.name = "qa_script"
    script.get_status.return_value = {"state": script_state}
    script.get_parameters.return_value = DEFINITIONS
    session = MagicMock()

    def get_module(sess, module, index=None, **kwargs):
        if module == "NaeScript":
            return script
        if set(kwargs) - {"parent_nae_script"}:
            created.kwargs = kwargs
            return created
        return agent

    session.api.get_module.side_effect = get_module
    return session


def agent_args(**extra):
    args = {"name": "qa_agent", "script_name": "qa_script"}
    args.update(extra)
    return args


def test_agent_create_body():
    created = build_agent(exists=True)
    session = agent_session(build_agent(exists=False), created=created)
    result = run_module(
        aoscx_nae_agent,
        agent_args(
            parameters={"threshold": 5},
            encrypted_parameters={"token": "s3cr3t"},
            vrf="mgmt",
        ),
        session,
    )
    assert result["changed"] is True
    kwargs = dict(created.kwargs)
    kwargs.pop("parent_nae_script")
    assert kwargs == {
        "parameters_values": {"threshold": "5"},
        "encrypted_parameters_values": {"token": "s3cr3t"},
        "vrf": "mgmt",
    }
    created.create.assert_called_once()


def test_agent_update_merges_parameters():
    agent = build_agent(
        exists=True, parameters_values={"threshold": "5", "label": "lab"}
    )
    result = run_module(
        aoscx_nae_agent,
        agent_args(parameters={"threshold": 10}),
        agent_session(agent),
    )
    assert result["changed"] is True
    assert agent.parameters_values == {"threshold": "10", "label": "lab"}
    agent.update.assert_called_once()


def test_agent_is_idempotent_with_encrypted_parameters_on_create():
    agent = build_agent(
        exists=True,
        parameters_values={"threshold": "5"},
        encrypted=["token"],
    )
    result = run_module(
        aoscx_nae_agent,
        agent_args(
            parameters={"threshold": "5"},
            encrypted_parameters={"token": "s3cr3t"},
        ),
        agent_session(agent),
    )
    assert result["changed"] is False
    agent.update.assert_not_called()


def test_agent_sets_encrypted_parameters_always():
    agent = build_agent(exists=True, encrypted=["token"])
    result = run_module(
        aoscx_nae_agent,
        agent_args(
            encrypted_parameters={"token": "s3cr3t"},
            update_encrypted_parameters="always",
        ),
        agent_session(agent),
    )
    assert result["changed"] is True
    assert agent.encrypted_parameters_values == {"token": "s3cr3t"}


@pytest.mark.parametrize(
    "args,message",
    [
        ({"parameters": {"unknown": 1}}, "Unknown parameter unknown"),
        ({"parameters": {"token": "x"}}, "set it with encrypted_parameters"),
        ({"encrypted_parameters": {"label": "x"}}, "set it with parameters"),
        ({"vrf": "mgmt"}, "vrf cannot be changed"),
    ],
)
def test_agent_rejects_invalid_requests(args, message):
    agent = build_agent(exists=True)
    result = run_module(
        aoscx_nae_agent, agent_args(**args), agent_session(agent)
    )
    assert result["failed"] is True
    assert message in result["msg"]
    agent.update.assert_not_called()


def test_agent_requires_a_validated_script():
    result = run_module(
        aoscx_nae_agent,
        agent_args(),
        agent_session(build_agent(exists=False), script_state="ERROR"),
    )
    assert result["failed"] is True
    assert "not validated" in result["msg"]


# --------------------------------------------------------------------------
# aoscx_nae_lite_agent
# --------------------------------------------------------------------------
MONITORS = {"cpu": {"resource": "system cpu"}}
ACTIVE = {
    "action_alert_description": None,
    "action_alert_state": "critical",
    "action_cli_commands": "show clock\\nshow version",
    "action_schedule": None,
    "action_snmp": None,
    "action_syslog": {
        "facility": "daemon",
        "message": '"High CPU"',
        "severity": "warning",
    },
    "expression": "gt 90",
    "expression_type": "monitor_resource",
    "resource_name": {"0": "cpu"},
}
CLEAR = {
    "action_alert_state": "normal",
    "action_syslog": {"facility": "daemon", "severity": "info"},
    "expression": "lt 50",
    "expression_type": "monitor_resource",
    "resource_name": {"0": "cpu"},
}


def build_condition(current):
    condition = MagicMock()
    if current is None:
        condition.get.side_effect = Exception("not found")
        condition.config_attrs = []
    else:
        condition.config_attrs = list(current)
        for key, value in current.items():
            setattr(condition, key, value)
    return condition


def lite_session(agent, conditions, created=None):
    session = MagicMock()
    session.created_conditions = []

    def get_module(sess, module, index=None, **kwargs):
        if module == "NaeLiteAgent":
            if kwargs:
                created.kwargs = kwargs
                return created
            return agent
        condition_type = kwargs.pop("condition_type")
        kwargs.pop("parent_nae_lite_agent")
        if kwargs:
            new = MagicMock()
            new.kwargs = kwargs
            new.condition_type = condition_type
            session.created_conditions.append(new)
            return new
        return conditions[condition_type]

    session.api.get_module.side_effect = get_module
    return session


def build_lite(exists, ready=True, state="AGENT_CREATED", error=None):
    agent = MagicMock()
    agent.config_attrs = ["description", "monitors", "ready", "watches"]
    if exists:
        agent.monitors = dict(MONITORS)
        agent.watches = {}
        agent.ready = ready
        agent.description = None
    else:
        agent.get.side_effect = Exception("not found")
    status = {"state": state, "error_description": error, "agent": None}
    agent.wait_for_activation.return_value = status
    agent.get_status.return_value = status
    return agent


def lite_args(**extra):
    args = {
        "name": "high_cpu",
        "monitors": [{"name": "cpu", "resource": "system cpu"}],
        "condition": {
            "source": "cpu",
            "expression": "gt 90",
            "alert_level": "critical",
            "syslog": {"text": "High CPU", "severity": "warning"},
            "cli_commands": ["show clock", "show version"],
        },
        "clear_condition": {"source": "cpu", "expression": "lt 50"},
    }
    args.update(extra)
    return args


def test_lite_create_conditions_and_activate():
    created = build_lite(exists=True, ready=False)
    session = lite_session(
        build_lite(exists=False),
        {
            "active_condition": build_condition(None),
            "clear_condition": build_condition(None),
        },
        created,
    )
    result = run_module(aoscx_nae_lite_agent, lite_args(), session)

    assert result["changed"] is True
    assert created.kwargs == {"monitors": MONITORS, "watches": {}}
    active, clear = session.created_conditions
    assert active.condition_type == "active_condition"
    # The CLI commands are separated with a literal "\n"
    assert active.kwargs["action_cli_commands"] == "show clock\\nshow version"
    assert active.kwargs["action_syslog"] == {
        "message": "High CPU",
        "severity": "warning",
        "facility": "daemon",
    }
    assert clear.kwargs["expression"] == "lt 50"
    created.activate.assert_called_once()
    created.wait_for_activation.assert_called_once_with(timeout=60)


def test_lite_is_idempotent_with_cli_quoted_messages():
    agent = build_lite(exists=True)
    session = lite_session(
        agent,
        {
            "active_condition": build_condition(ACTIVE),
            "clear_condition": build_condition(CLEAR),
        },
    )
    result = run_module(aoscx_nae_lite_agent, lite_args(), session)

    assert result["changed"] is False
    agent.update.assert_not_called()
    agent.activate.assert_not_called()


def test_lite_condition_change_regenerates_the_agent():
    agent = build_lite(exists=True)
    active = build_condition(dict(ACTIVE, action_alert_description="kept"))
    session = lite_session(
        agent,
        {
            "active_condition": active,
            "clear_condition": build_condition(CLEAR),
        },
    )
    args = lite_args()
    args["condition"]["expression"] = "gt 80"
    result = run_module(aoscx_nae_lite_agent, args, session)

    assert result["changed"] is True
    active.update.assert_called_once()
    assert active.expression == "gt 80"
    # A description set with the CLI is kept
    assert active.action_alert_description == "kept"
    agent.activate.assert_called_once()


def test_lite_omitted_clear_condition_is_removed():
    clear = build_condition(CLEAR)
    agent = build_lite(exists=True)
    session = lite_session(
        agent,
        {
            "active_condition": build_condition(ACTIVE),
            "clear_condition": clear,
        },
    )
    args = lite_args()
    del args["clear_condition"]
    result = run_module(aoscx_nae_lite_agent, args, session)

    assert result["changed"] is True
    clear.delete.assert_called_once()


def test_lite_fails_when_the_generated_agent_fails():
    agent = build_lite(
        exists=True, ready=False, state="ERROR", error="Python errors"
    )
    session = lite_session(
        agent,
        {
            "active_condition": build_condition(ACTIVE),
            "clear_condition": build_condition(CLEAR),
        },
    )
    result = run_module(aoscx_nae_lite_agent, lite_args(), session)

    assert result["failed"] is True
    assert "Python errors" in result["msg"]


def test_lite_deactivate():
    agent = build_lite(exists=True, ready=True)
    session = lite_session(agent, {})
    result = run_module(
        aoscx_nae_lite_agent,
        {"name": "high_cpu", "activate": False, "state": "update"},
        session,
    )
    assert result["changed"] is True
    agent.deactivate.assert_called_once()
    agent.activate.assert_not_called()


@pytest.mark.parametrize(
    "args,message",
    [
        (
            {
                "monitors": [
                    {"name": n, "resource": "system cpu"}
                    for n in ("cpu", "cpu2", "cpu3")
                ]
            },
            "at most two monitors",
        ),
        (
            {"condition": {"source": "memory", "expression": "gt 1"}},
            "is not a monitor or watch",
        ),
        (
            {
                "monitors": None,
                "watches": [{"name": "logs", "event_ids": [42]}],
                "condition": {"source": "logs", "expression": "count 1"},
                "clear_condition": None,
            },
            "Invalid event ID 42",
        ),
    ],
)
def test_lite_rejects_invalid_requests(args, message):
    agent = build_lite(exists=True)
    module_args = lite_args(**args)
    module_args = {k: v for k, v in module_args.items() if v is not None}
    result = run_module(
        aoscx_nae_lite_agent, module_args, lite_session(agent, {})
    )
    assert result["failed"] is True
    assert message in result["msg"]
    agent.update.assert_not_called()


# --------------------------------------------------------------------------
# aoscx_nae_info
# --------------------------------------------------------------------------
def info_session(lite_error=None):
    def agent_status(name, level):
        return {
            "script": "qa_script",
            "alert_level": level,
            "alert_description": "desc",
            "alert_level_updated_at": 1,
            "alerts_count": 1,
        }

    agent_class = MagicMock()
    agent_class.get_aggregated_alert_level.return_value = "CRITICAL"
    agent_class.get_facts.return_value = {
        "normal_agent": agent_status("normal_agent", "NORMAL"),
        "minor_agent": agent_status("minor_agent", "MINOR"),
        "critical_agent": agent_status("critical_agent", "CRITICAL"),
    }
    script_class = MagicMock()
    script_class.get_facts.return_value = {"qa_script": {"state": "VALIDATED"}}
    lite_class = MagicMock()
    if lite_error:
        lite_class.get_facts.side_effect = lite_error
    else:
        lite_class.get_facts.return_value = {
            "high_cpu": {
                "name": "high_cpu",
                "ready": True,
                "status": {"state": "AGENT_CREATED"},
            }
        }
    classes = {
        "NaeAgent": agent_class,
        "NaeScript": script_class,
        "NaeLiteAgent": lite_class,
    }
    session = MagicMock()
    session.api.get_module_class.side_effect = lambda s, name: classes[name]
    return session


def test_info_lists_alerts_by_severity():
    result = run_module(aoscx_nae_info, {}, info_session())
    nae = result["nae"]

    assert result["changed"] is False
    assert nae["aggregated_alert_level"] == "CRITICAL"
    assert [a["agent"] for a in nae["alerts"]] == [
        "critical_agent",
        "minor_agent",
    ]
    assert nae["lite_agents"]["high_cpu"]["state"] == "AGENT_CREATED"
    assert "status" not in nae["lite_agents"]["high_cpu"]


def test_info_without_nae_lite_support():
    error = Exception("not found")
    error.response_code = 404
    result = run_module(
        aoscx_nae_info, {"agent_name": "minor_agent"}, info_session(error)
    )
    assert result["nae"]["lite_agents"] == {}
    assert list(result["nae"]["agents"]) == ["minor_agent"]
