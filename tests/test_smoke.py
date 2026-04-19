def test_import():
    from worldsim_npc_mind import run  # noqa: F401


def test_prompt_exists():
    from pathlib import Path

    assert (Path(__file__).parent.parent / "prompts" / "dialog.md").exists()
