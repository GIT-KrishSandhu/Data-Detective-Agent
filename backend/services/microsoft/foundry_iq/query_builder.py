from typing import Dict, Any, List

class FoundryIQQueryBuilder:
    """
    Translates deterministic evidence parameters (readiness score, issues count,
    warnings count, problems list) into a target semantic query for Microsoft Foundry IQ.
    """
    @staticmethod
    def build_query(data: Dict[str, Any]) -> str:
        score = data.get("score", 100)
        critical = data.get("critical", 0)
        warnings = data.get("warnings", 0)
        problems = data.get("problems", [])
        
        # Lowercase problems for flexible matching
        problems_lower = [str(p).lower() for p in problems]
        
        query_parts = []
        
        # 1. Readiness score query component
        query_parts.append(f"Power BI dataset readiness score {score}")
        
        # 2. Schema integrity query component
        if critical > 0 or warnings > 0 or "schema normalization" in problems_lower:
            query_parts.append("schema integrity")
            
        # 3. Specific problem query components
        if any("duplicate" in p for p in problems_lower):
            query_parts.append("duplicate keys")
            
        if any("null" in p or "missing" in p for p in problems_lower):
            query_parts.append("null values")
            
        if any("duplicate" in p for p in problems_lower):
            query_parts.append("star schema")
            
        # 4. Standard enterprise BI governance query topics
        query_parts.append("Power BI governance")
        query_parts.append("business intelligence best practices")
        query_parts.append("semantic model recommendations")
        
        return " ".join(query_parts)
