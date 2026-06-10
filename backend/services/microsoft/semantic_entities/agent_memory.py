from services.microsoft.semantic_entities.semantic_entity import SemanticEntity
from typing import Dict, Any

class AgentMemoryEntity(SemanticEntity):
    """
    Semantic Entity representing individual agent memory checkpoints.
    """
    agent_name: str
    cognitive_state: str
    internal_variables: Dict[str, Any]
