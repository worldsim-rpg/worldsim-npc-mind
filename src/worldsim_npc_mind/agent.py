"""
npc-mind — диалог от лица одного NPC, ограниченный его знанием.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from worldsim_prompts import AnthropicClient, extract_json, load_prompt

_PROMPTS = Path(__file__).parent.parent.parent / "prompts"


def run(input: dict[str, Any], *, client: AnthropicClient, model: str) -> dict:
    """
    input:
      npc: Character
      player_said: str
      player_character: {...}
      scene_context: {"location", "other_npcs_present", "recent_events"}
      intent: {...}

    returns: {"speech": str, "action_hint": str | None,
              "attitude_delta": float, "revealed_facts": [str, ...]}
    """

    system = load_prompt(_PROMPTS / "dialog.md")
    user = json.dumps(input, ensure_ascii=False, indent=2)

    raw = client.complete(
        model=model,
        system=system,
        user=user,
        max_tokens=700,
        temperature=0.8,
    )
    parsed = extract_json(raw)

    delta = float(parsed.get("attitude_delta") or 0.0)
    delta = max(-0.2, min(0.2, delta))

    return {
        "speech": str(parsed.get("speech") or "").strip(),
        "action_hint": parsed.get("action_hint"),
        "attitude_delta": delta,
        "revealed_facts": list(parsed.get("revealed_facts") or []),
    }
