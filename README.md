# worldsim-npc-mind

Разум NPC. Отвечает от лица одного конкретного NPC на реплику игрока,
исходя из того, что **этот NPC** знает, во что верит, чего хочет и
как относится к игроку.

Часть игры **worldsim**.

## Почему отдельный агент

Чтобы NPC не "знал всё, что знает автор". Он оперирует только
своим `knowledge`, `goals`, `traits`, `attitude_to_player`.
Это защищает канон от утечек тайн через диалог.

## API

```python
from worldsim_npc_mind import run

resp = run(
    {
        "npc": {...},                    # полный Character
        "player_said": "...",
        "player_character": {...},       # что NPC видит в игроке
        "scene_context": {
            "location": {...},
            "other_npcs_present": [...],
            "recent_events": [...]
        },
        "intent": {...},                 # нормализованное намерение игрока
    },
    client=client,
    model="claude-haiku-4-5-20251001",
)
# resp: {"speech": str, "action_hint": str | None,
#        "attitude_delta": float, "revealed_facts": [str, ...]}
```

- `speech` — реплика от имени NPC.
- `action_hint` — что NPC делает в момент реплики (мелкий жест, движение).
- `attitude_delta` — предлагаемое изменение `attitude_to_player` в
  диапазоне `[-0.2, 0.2]` (мягкая нотификация world-builder'у,
  финальное значение клампит он).
- `revealed_facts` — какие факты NPC явно раскрыл в реплике (для
  обновления `known_facts` игрока).

## Структура

- `prompts/dialog.md` — промпт с правилами "мыслить как NPC".
- `src/worldsim_npc_mind/agent.py` — клей.

См. [CLAUDE.md](CLAUDE.md).
