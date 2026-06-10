import logging
from typing import Dict, Any, List

logger = logging.getLogger("data_detective.powerbi_readiness_engine")

class PowerBIReadinessEngine:
    """
    Engine calculating ratings and recommendations for Power BI ingestion.
    Runs 100% deterministic rules on dataset schemas, quality records, and dates.
    """

    def evaluate(
        self,
        schema_info: List[Dict[str, Any]],
        quality_findings: List[Dict[str, Any]],
        metric_pairings: Dict[str, Any],
        schema_relations: Dict[str, Any],
        datetime_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        logger.info("[Readiness Engine] Running Power BI readiness scoring...")

        # 1. Counts of issues
        critical_count = sum(1 for f in quality_findings if str(f.get("severity")).lower() == "critical")
        warning_count = sum(1 for f in quality_findings if str(f.get("severity")).lower() == "warning")

        # 2. Category 1: Schema Quality (0.0 to 5.0)
        schema_rating = 5.0
        mixed_types_count = sum(1 for f in quality_findings if "mixed_type" in str(f.get("id")).lower())
        schema_rating -= 0.8 * mixed_types_count
        if len(schema_info) > 50 or len(schema_info) < 2:
            schema_rating -= 0.5
        schema_rating = max(1.0, min(5.0, schema_rating))

        # 3. Category 2: Data Quality (0.0 to 5.0)
        quality_rating = 5.0
        avg_null_pct = 0.0
        if len(schema_info) > 0:
            avg_null_pct = sum(c.get("null_percentage", 0.0) for c in schema_info) / len(schema_info)
        quality_rating -= (avg_null_pct * 4.0)
        
        has_duplicates = any("duplicate" in str(f.get("id")).lower() for f in quality_findings)
        if has_duplicates:
            quality_rating -= 1.0
        quality_rating = max(1.0, min(5.0, quality_rating))

        # 4. Category 3: Relationships (0.0 to 5.0)
        relationships_rating = 2.5
        pks = schema_relations.get("primary_keys") or []
        fks = schema_relations.get("foreign_keys") or []
        if len(pks) > 0:
            relationships_rating += 1.5
        if len(fks) > 0:
            relationships_rating += 1.0
        relationships_rating = max(1.0, min(5.0, relationships_rating))

        # 5. Category 4: Date Columns (0.0 to 5.0)
        date_summary_dict = datetime_summary.get("datetime_columns") or {}
        date_rating = 1.0
        if len(date_summary_dict) > 0:
            date_rating = 4.0
            for col, dt_stats in date_summary_dict.items():
                if dt_stats.get("continuity_ratio", 1.0) > 0.9:
                    date_rating = 5.0
                elif dt_stats.get("continuity_ratio", 1.0) < 0.5:
                    date_rating -= 1.5
        date_rating = max(1.0, min(5.0, date_rating))

        # 6. Category 5: Business Metrics (0.0 to 5.0)
        metrics_rating = 2.5
        measures = metric_pairings.get("measures") or []
        if len(measures) > 0:
            metrics_rating = 5.0
        metrics_rating = max(1.0, min(5.0, metrics_rating))

        # 7. Category 6: Identifier Quality (0.0 to 5.0)
        identifier_rating = 2.5
        if len(pks) > 0:
            identifier_rating = 5.0
        identifier_rating = max(1.0, min(5.0, identifier_rating))

        # 8. Overall Score
        total_rating = (
            schema_rating +
            quality_rating +
            relationships_rating +
            date_rating +
            metrics_rating +
            identifier_rating
        )
        readiness_score = int(round((total_rating / 30.0) * 100))

        # 9. Overall Rating Text
        if critical_count > 0:
            overall_rating_text = "NEEDS ATTENTION"
        elif warning_count > 0 or readiness_score < 85:
            overall_rating_text = "PASS WITH WARNINGS"
        else:
            overall_rating_text = "ENTERPRISE READY"

        # 10. Star Schema Recommender
        dim_candidates = schema_relations.get("dim_candidates") or []
        fact_candidates = schema_relations.get("fact_candidates") or []
        
        dimensions_list = [d["table_name"] for d in dim_candidates]
        if len(date_summary_dict) > 0:
            dimensions_list.append("Calendar")
            
        facts_list = [f["table_name"] for f in fact_candidates]
        if len(facts_list) == 0:
            facts_list.append("FactTable")

        star_schema = {
            "dimension_tables": dimensions_list,
            "fact_tables": facts_list,
            "reasoning": f"Inferred {len(dimensions_list)} dimensions (based on unique keys & datetime columns) and {len(facts_list)} fact tables (based on aggregatable metrics)."
        }

        # 11. Compile Recommendations
        business_recommendations = []
        if critical_count > 0:
            business_recommendations.append(f"Resolve the {critical_count} critical data quality issues identified before building dashboard relationships.")
        if warning_count > 0:
            business_recommendations.append(f"Audit the {warning_count} schema warnings to prevent join errors and empty cells in visual reports.")
        
        for col, dt_stats in date_summary_dict.items():
            if dt_stats.get("continuity_ratio", 1.0) < 0.8:
                business_recommendations.append(f"Date column '{col}' has low continuity ({dt_stats['continuity_ratio']:.0%}). Create a standard Calendar dimension table in Power BI to ensure complete date intelligence functionality.")
                
        for pairing in metric_pairings.get("pairings") or []:
            if not pairing.get("analyzable"):
                business_recommendations.append(pairing.get("reasoning"))

        if len(business_recommendations) == 0:
            business_recommendations.append("The dataset schema is fully consistent and ready for direct import into Power BI.")

        return {
            "readiness_score": readiness_score,
            "category_ratings": {
                "schema": round(schema_rating, 1),
                "quality": round(quality_rating, 1),
                "relationships": round(relationships_rating, 1),
                "dates": round(date_rating, 1),
                "metrics": round(metrics_rating, 1),
                "identifiers": round(identifier_rating, 1)
            },
            "overall_rating_text": overall_rating_text,
            "star_schema_suggestions": star_schema,
            "business_recommendations": business_recommendations
        }

# Singleton instance
readiness_engine = PowerBIReadinessEngine()
