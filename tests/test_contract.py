"""Contract-тесты npc-mind."""

import json
from unittest.mock import MagicMock, patch

import pytest

from worldsim_npc_mind.agent import run


def _mock_client(response: str) -> MagicMock:
    client = MagicMock()
    client.complete.return_value = response
    return client


MINIMAL_INPUT = {
    "npc": {"id": "npc_mira", "name": "Мира", "location_id": "loc_a"},
    "player_said": "Ты знаешь что-нибудь о контрабандистах?",
    "player_character": {"id": "pc", "name": "Странник"},
    "scene_context": {
        "location": {"id": "loc_a", "name": "Доки"},
        "other_npcs_present": [],
        "recent_events": [],
    },
    "intent": {"intent": "converse", "raw_text": "спрашиваю о контрабандистах"},
}

VALID_NPC_RESPONSE = {
    "speech": "Слышала кое-что, но не уверена, стоит ли рассказывать...",
    "action_hint": None,
    "attitude_delta": 0.05,
    "revealed_facts": [],
}


# ---------------------------------------------------------------------------
# run — happy path
# ---------------------------------------------------------------------------


def test_run_returns_dict():
    client = _mock_client(json.dumps(VALID_NPC_RESPONSE))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert isinstance(result, dict)
    assert "speech" in result
    assert "attitude_delta" in result
    assert "revealed_facts" in result


def test_run_speech_stripped():
    resp = {**VALID_NPC_RESPONSE, "speech": "  Текст с пробелами.  "}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert result["speech"] == "Текст с пробелами."


# ---------------------------------------------------------------------------
# attitude_delta clamping
# ---------------------------------------------------------------------------


def test_attitude_delta_clamped_high():
    resp = {**VALID_NPC_RESPONSE, "attitude_delta": 0.9}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert result["attitude_delta"] <= 0.2


def test_attitude_delta_clamped_low():
    resp = {**VALID_NPC_RESPONSE, "attitude_delta": -0.9}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert result["attitude_delta"] >= -0.2


def test_attitude_delta_valid_range():
    resp = {**VALID_NPC_RESPONSE, "attitude_delta": 0.15}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert result["attitude_delta"] == pytest.approx(0.15)


def test_attitude_delta_none_defaults_to_zero():
    resp = {**VALID_NPC_RESPONSE, "attitude_delta": None}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert result["attitude_delta"] == 0.0


# ---------------------------------------------------------------------------
# optional fields
# ---------------------------------------------------------------------------


def test_run_missing_optional_fields():
    # Минимальный ответ LLM — только speech
    resp = {"speech": "Не знаю ничего."}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert result["speech"] == "Не знаю ничего."
    assert result["action_hint"] is None
    assert result["attitude_delta"] == 0.0
    assert result["revealed_facts"] == []


def test_run_with_revealed_facts():
    resp = {**VALID_NPC_RESPONSE, "revealed_facts": ["контрабандисты_активны", "лидер_культа"]}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert len(result["revealed_facts"]) == 2


def test_run_with_action_hint():
    resp = {**VALID_NPC_RESPONSE, "action_hint": "Мира оглядывается через плечо."}
    client = _mock_client(json.dumps(resp))
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        result = run(MINIMAL_INPUT, client=client, model="m")
    assert result["action_hint"] == "Мира оглядывается через плечо."


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------


def test_run_invalid_json_raises():
    client = _mock_client("Not JSON at all.")
    with patch("worldsim_npc_mind.agent.load_prompt", return_value="system"):
        with pytest.raises(ValueError):
            run(MINIMAL_INPUT, client=client, model="m")


# ---------------------------------------------------------------------------
# MANIFEST
# ---------------------------------------------------------------------------


def test_manifest_exported():
    from worldsim_npc_mind import MANIFEST
    from worldsim_schemas import AgentPhase
    assert MANIFEST.phase == AgentPhase.NPC_RESPOND
    assert MANIFEST.optional is True


def test_manifest_entrypoint_callable():
    from worldsim_npc_mind import MANIFEST
    import worldsim_npc_mind as pkg
    assert callable(getattr(pkg, MANIFEST.entrypoint, None))
