from worldsim_schemas import AgentManifest, AgentPhase

from .agent import run

MANIFEST = AgentManifest(
    name="npc-mind",
    package="worldsim_npc_mind",
    entrypoint="run",
    phase=AgentPhase.NPC_RESPOND,
    optional=True,
    model_tier="default",
    description="Ответ NPC от первого лица.",
)

__all__ = ["run", "MANIFEST"]
