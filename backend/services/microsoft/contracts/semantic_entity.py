from abc import ABC, abstractmethod
from typing import Any, Dict, List

class SemanticEntity(ABC):
    """
    Contract for representing a business semantic entity.
    Maps dataset schema details, column types, and data quality states
    into standard Microsoft Fabric/Power BI semantic constructs.
    """

    @abstractmethod
    def to_fabric_schema(self) -> Dict[str, Any]:
        """
        Translates columns, types, and relationships into Fabric Semantic Model schema JSON.
        """
        pass

    @abstractmethod
    def get_relationship_mappings(self) -> List[Dict[str, Any]]:
        """
        Returns primary-foreign key relationship rules mapping to other semantic models.
        """
        pass
