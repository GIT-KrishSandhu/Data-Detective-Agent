from abc import ABC, abstractmethod
from typing import Any, Dict, List

class FabricProvider(ABC):
    """
    Interface for interacting with Microsoft Fabric workspaces and OneLake.
    Handles semantic model registrations and table sync controls.
    """

    @abstractmethod
    async def create_semantic_model(
        self, 
        workspace_id: str, 
        dataset_name: str, 
        schema_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Registers a new semantic model in the specified Fabric workspace.
        """
        pass

    @abstractmethod
    async def sync_onelake_table(self, table_name: str, local_file_path: str) -> bool:
        """
        Uploads and synchronizes a local file into a Fabric Lakehouse table.
        """
        pass
