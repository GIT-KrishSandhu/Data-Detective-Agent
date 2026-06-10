import logging
import os
import time
import uuid
import pandas as pd
from datetime import datetime, timezone
from typing import Any, Dict, List
# pyrefly: ignore [missing-import]
from langchain_core.language_models.chat_models import BaseChatModel

from agents.base import BaseAgent
from agents.base.agent_result import AgentResult

# Import stats tools
from tools.statistics.numeric_summary_tool import run_numeric_summary_tool
from tools.statistics.distribution_analysis_tool import run_distribution_analysis_tool
from tools.statistics.outlier_summary_tool import run_outlier_summary_tool
from tools.statistics.categorical_summary_tool import run_categorical_summary_tool
from tools.statistics.datetime_summary_tool import run_datetime_summary_tool
from tools.statistics.metric_relationship_tool import run_metric_relationship_tool
from tools.statistics.schema_relationship_tool import run_schema_relationship_tool

# Import semantic models & services
from services.microsoft.semantic_entities.statistics_entity import StatisticsEntity
from services.microsoft.semantic_entities.distribution_entity import DistributionEntity
from services.microsoft.semantic_entities.business_metric_entity import BusinessMetricEntity
from services.microsoft.semantic_entities.aggregation_recommendation import AggregationRecommendationEntity
from services.microsoft.semantic_entities.powerbi_readiness_entity import PowerBIReadinessEntity
from services.microsoft.semantic_entities.relationship import SemanticRelationship
from services.microsoft.semantic_entities.agent_memory import AgentMemoryEntity
from services.microsoft.orchestration.local_runtime import local_runtime_service
from services.microsoft.evaluation.powerbi_readiness_engine import readiness_engine

logger = logging.getLogger("data_detective.bi_readiness_agent")

class BIReadinessAgent(BaseAgent):
    """
    BI Readiness Agent analyzing dataset structures and statistical distributions
    to output typed semantic models and a deterministic Power BI Readiness score.
    """

    def __init__(self, name: str, llm: BaseChatModel, system_prompt: str = ""):
        super().__init__(
            name=name,
            llm=llm,
            system_prompt=system_prompt or "You are the BI Readiness Agent. Audit dataset metadata for business intelligence systems.",
            temperature=0.0
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        task_id = "bi_readiness_assessment"
        start_time = self.run_telemetry_start(task_id, state)
        
        agent_start_time = time.time()
        agent_started_at = datetime.now(timezone.utc).isoformat()
        
        root_trace_id = state.get("root_trace_id") or str(uuid.uuid4())
        bi_trace_id = str(uuid.uuid4())

        current_log = list(state.get("agent_execution_log") or [])
        
        current_log.append({
            "type": "telemetry_event",
            "event": "bi_readiness_started",
            "agent_name": self.name,
            "timestamp": agent_started_at
        })
        
        path = state.get("dataset_path")
        if not path or not os.path.exists(path):
            err_msg = f"Dataset path '{path}' not found."
            logger.error(err_msg)
            return {"errors": list(state.get("errors") or []) + [err_msg]}
            
        # Load dataset
        try:
            ext = os.path.splitext(path)[-1].lower()
            if ext == ".csv":
                try:
                    df = pd.read_csv(path)
                except UnicodeDecodeError:
                    df = pd.read_csv(path, encoding="cp1252")
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(path)
            else:
                raise ValueError(f"Unsupported extension: {ext}")
        except Exception as e:
            err_msg = f"Failed to load dataset in BI agent: {str(e)}"
            return {"errors": list(state.get("errors") or []) + [err_msg]}

        tool_trace = []

        def run_tool_with_trace(tool_func, name):
            t_start = time.time()
            t_start_iso = datetime.now(timezone.utc).isoformat()
            tool_id = str(uuid.uuid4())
            
            res = tool_func(df)
            
            t_duration = int((time.time() - t_start) * 1000)
            tool_step = {
                "type": "tool_step",
                "trace_id": tool_id,
                "parent_trace_id": bi_trace_id,
                "agent_name": self.name,
                "tool_name": name,
                "status": "completed",
                "started_at": t_start_iso,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "duration_ms": t_duration,
                "confidence": 1.0,
                "blackboard_version": 3
            }
            current_log.append(tool_step)
            local_runtime_service.publish_trace(tool_id, tool_step)
            tool_trace.append({"tool_name": name, "status": "success", "execution_time_ms": t_duration})
            return res

        # Run Tools
        num_summary = run_tool_with_trace(run_numeric_summary_tool, "Numeric Summary Tool")
        dist_analysis = run_tool_with_trace(run_distribution_analysis_tool, "Distribution Analysis Tool")
        outliers = run_tool_with_trace(run_outlier_summary_tool, "Outlier Summary Tool")
        categoricals = run_tool_with_trace(run_categorical_summary_tool, "Categorical Summary Tool")
        datetimes = run_tool_with_trace(run_datetime_summary_tool, "Datetime Summary Tool")
        metric_relations = run_tool_with_trace(run_metric_relationship_tool, "Metric Relationship Tool")
        schema_relations = run_tool_with_trace(run_schema_relationship_tool, "Schema Relationship Tool")

        # Call Readiness Engine
        findings_raw = state.get("quality_findings") or []
        readiness_res = readiness_engine.evaluate(
            schema_info=state.get("schema_info") or [],
            quality_findings=findings_raw,
            metric_pairings=metric_relations,
            schema_relations=schema_relations,
            datetime_summary=datetimes
        )

        dataset_id = state.get("dataset_id") or "default"
        relationships = list(state.get("semantic_relationships") or [])
        semantic_distributions = []
        semantic_business_metrics = []
        semantic_aggregation_recs = []

        # Construct Distribution Entities
        for col, dist in dist_analysis.get("distributions", {}).items():
            num_stats = num_summary.get("numeric_columns", {}).get(col, {})
            out_stats = outliers.get("outliers", {}).get(col, {})
            
            dist_entity = DistributionEntity(
                entity_id=f"dist_{col}",
                entity_type="Distribution",
                created_by_agent=self.name,
                confidence=1.0,
                dependencies=[f"col_{col}"],
                trace_id=bi_trace_id,
                column_name=col,
                mean=num_stats.get("mean", 0.0),
                median=num_stats.get("median", 0.0),
                min_val=num_stats.get("min", 0.0),
                max_val=num_stats.get("max", 0.0),
                std_dev=num_stats.get("std", 0.0),
                skewness=num_stats.get("skew", 0.0),
                kurtosis=num_stats.get("kurt", 0.0),
                outlier_count=out_stats.get("outlier_count", 0),
                is_normal=dist.get("is_normal", False),
                skewness_interpretation=dist.get("skewness_desc", "Approximately symmetric")
            )
            semantic_distributions.append(dist_entity.model_dump())
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_bi_creates_dist_{col}",
                source_id=self.name,
                target_id=dist_entity.entity_id,
                relationship_type="creates"
            ))

        # Construct Business Metrics and Aggregation Recommendations
        measures_list = metric_relations.get("measures") or []
        for measure in measures_list:
            dist_stats = dist_analysis.get("distributions", {}).get(measure, {})
            skew = dist_stats.get("skew", 0.0)
            
            rec_agg = "Sum"
            reason = f"Normal numerical field. Default aggregation set to SUM for BI dashboards."
            if abs(skew) > 1.5:
                rec_agg = "Median"
                reason = f"Field is heavily skewed (skew={skew:.2f}). Averaging or summing may distort executive metrics; prefer MEDIAN KPI aggregations."

            metric_entity = BusinessMetricEntity(
                entity_id=f"metric_{measure}",
                entity_type="BusinessMetric",
                created_by_agent=self.name,
                confidence=0.95,
                dependencies=[f"col_{measure}"],
                trace_id=bi_trace_id,
                column_name=measure,
                metric_type="GeneralNumeric",
                is_aggregatable=True,
                default_aggregation=rec_agg
            )
            semantic_business_metrics.append(metric_entity.model_dump())
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_bi_creates_metric_{measure}",
                source_id=self.name,
                target_id=metric_entity.entity_id,
                relationship_type="creates"
            ))

            rec_entity = AggregationRecommendationEntity(
                entity_id=f"rec_agg_{measure}",
                entity_type="AggregationRecommendation",
                created_by_agent=self.name,
                confidence=1.0,
                dependencies=[metric_entity.entity_id],
                trace_id=bi_trace_id,
                column_name=measure,
                recommended_aggregation=rec_agg,
                reasoning=reason
            )
            semantic_aggregation_recs.append(rec_entity.model_dump())
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_bi_creates_rec_agg_{measure}",
                source_id=self.name,
                target_id=rec_entity.entity_id,
                relationship_type="creates"
            ))

        # Primary identifiers: recommended to NOT aggregate
        pks = schema_relations.get("primary_keys") or []
        for pk in pks:
            rec_entity = AggregationRecommendationEntity(
                entity_id=f"rec_agg_{pk}",
                entity_type="AggregationRecommendation",
                created_by_agent=self.name,
                confidence=1.0,
                dependencies=[f"col_{pk}"],
                trace_id=bi_trace_id,
                column_name=pk,
                recommended_aggregation="None",
                reasoning="Unique record identifier. Do not aggregate arithmetic properties; use exclusively as a dimension key."
            )
            semantic_aggregation_recs.append(rec_entity.model_dump())
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_bi_creates_rec_agg_{pk}",
                source_id=self.name,
                target_id=rec_entity.entity_id,
                relationship_type="creates"
            ))

        # Compute dataset stats counts
        tot_nulls = sum(c.get("null_count", 0) for c in state.get("schema_info") or [])
        avg_null = sum(c.get("null_percentage", 0.0) for c in state.get("schema_info") or []) / max(1, len(state.get("schema_info") or []))
        total_outliers = sum(o.get("outlier_count", 0) for o in outliers.get("outliers", {}).values())
        
        stat_entity = StatisticsEntity(
            entity_id=f"stats_{dataset_id}",
            entity_type="Statistics",
            created_by_agent=self.name,
            confidence=1.0,
            dependencies=[f"dataset_{dataset_id}"],
            trace_id=bi_trace_id,
            row_count=len(df),
            column_count=len(df.columns),
            numeric_columns_count=len(df.select_dtypes(include=["number"]).columns),
            categorical_columns_count=len(df.select_dtypes(exclude=["number", "datetime"]).columns),
            datetime_columns_count=len(datetimes.get("datetime_columns", {})),
            constant_columns_count=len([k for k, v in categoricals.get("categorical_columns", {}).items() if v.get("unique_count") == 1]),
            total_nulls=tot_nulls,
            average_null_percentage=avg_null,
            duplicate_rows=int(df.duplicated().sum()),
            outlier_count=total_outliers
        )
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_bi_creates_stats",
            source_id=self.name,
            target_id=stat_entity.entity_id,
            relationship_type="creates"
        ))

        # Create PowerBIReadinessEntity
        readiness_entity = PowerBIReadinessEntity(
            entity_id=f"pbi_readiness_{dataset_id}",
            entity_type="PowerBIReadiness",
            created_by_agent=self.name,
            confidence=1.0,
            dependencies=[stat_entity.entity_id],
            trace_id=bi_trace_id,
            readiness_score=readiness_res["readiness_score"],
            category_ratings=readiness_res["category_ratings"],
            overall_rating_text=readiness_res["overall_rating_text"],
            star_schema_suggestions=readiness_res["star_schema_suggestions"],
            business_recommendations=readiness_res["business_recommendations"]
        )
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_bi_creates_readiness",
            source_id=self.name,
            target_id=readiness_entity.entity_id,
            relationship_type="creates"
        ))

        # Agent Memory
        memory_entity = AgentMemoryEntity(
            entity_id=f"memory_bi_{dataset_id}",
            entity_type="AgentMemory",
            created_by_agent=self.name,
            agent_name=self.name,
            cognitive_state=f"BI readiness scan complete. Readiness Score: {readiness_res['readiness_score']}% [Status: {readiness_res['overall_rating_text']}].",
            internal_variables={"readiness_score": readiness_res["readiness_score"]},
            confidence=1.0,
            dependencies=[stat_entity.entity_id]
        )
        memories = list(state.get("semantic_memories") or [])
        memories.append(memory_entity.model_dump())
        
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_bi_creates_memory",
            source_id=self.name,
            target_id=memory_entity.entity_id,
            relationship_type="creates"
        ))

        evidence_conf = round(1.0 - avg_null, 2)
        reasoning_conf = 1.0 if len(measures_list) > 0 and len(pks) > 0 else 0.85
        rec_conf = 0.95

        agent_end_time = time.time()
        agent_completed_at = datetime.now(timezone.utc).isoformat()
        agent_duration_ms = int((agent_end_time - agent_start_time) * 1000)

        agent_step = {
            "type": "agent_step",
            "trace_id": bi_trace_id,
            "parent_trace_id": root_trace_id,
            "agent_name": self.name,
            "tool_name": None,
            "status": "completed",
            "started_at": agent_started_at,
            "completed_at": agent_completed_at,
            "execution_time_ms": agent_duration_ms,
            "confidence": 1.0,
            "blackboard_version": 3
        }
        current_log.append(agent_step)

        current_log.append({
            "type": "telemetry_event",
            "event": "bi_readiness_completed",
            "agent_name": self.name,
            "timestamp": agent_completed_at
        })

        # Register and telemetry publish
        local_runtime_service.register_statistics_agent(self.name, {"type": "bi_readiness_auditor", "version": "1.0"})
        local_runtime_service.publish_trace(bi_trace_id, agent_step)
        local_runtime_service.publish_statistics_entities(3, semantic_distributions)
        local_runtime_service.publish_powerbi_readiness(3, readiness_res)

        prev_version = state.get("blackboard_version") or 2
        next_version = prev_version + 1

        total_entities = 0
        if state.get("semantic_goal"):
            total_entities += 1
        if state.get("semantic_dataset"):
            total_entities += 1
            ds = state.get("semantic_dataset") or {}
            cols = ds.get("columns") or []
            total_entities += len(cols)
            
        issues = state.get("semantic_issues") or []
        recs = state.get("semantic_recommendations") or []
        
        total_entities += len(memories)
        total_entities += len(issues)
        total_entities += len(recs)
        
        total_entities += 1
        total_entities += len(semantic_distributions)
        total_entities += len(semantic_business_metrics)
        total_entities += len(semantic_aggregation_recs)
        total_entities += 1

        summary_msg = f"Business Intelligence analysis complete. Power BI Readiness Index is {readiness_res['readiness_score']}%."
        reasoning_msg = f"Identified {len(measures_list)} numeric measures and {len(pks)} key dimensions. Default aggregations binned based on skewness boundaries."

        agent_result = AgentResult(
            agent_name=self.name,
            summary=summary_msg,
            reasoning=reasoning_msg,
            confidence=1.0,
            findings=[],
            recommendations=readiness_res["business_recommendations"],
            tool_trace=tool_trace,
            execution_time_ms=agent_duration_ms
        )

        updates = {
            "bi_readiness_result": agent_result.model_dump(),
            "agent_execution_log": current_log,
            "current_agent": "bi_readiness",
            "current_step": "BI Readiness Complete",
            
            # Phase 5 & 6 semantic updates
            "semantic_statistics": stat_entity.model_dump(),
            "semantic_powerbi_readiness": readiness_entity.model_dump(),
            "semantic_business_metrics": semantic_business_metrics,
            "semantic_distributions": semantic_distributions,
            "semantic_aggregation_recommendations": semantic_aggregation_recs,
            "semantic_memories": memories,
            "semantic_relationships": [r.model_dump() if hasattr(r, "model_dump") else r for r in relationships],
            
            # Sub-confidences
            "bi_evidence_confidence": evidence_conf,
            "bi_reasoning_confidence": reasoning_conf,
            "bi_recommendation_confidence": rec_conf,
            
            # Blackboard version info
            "blackboard_version": next_version,
            "blackboard_entity_count": total_entities,
            "blackboard_last_updated_by": self.name,
            "blackboard_last_trace_id": bi_trace_id
        }

        local_runtime_service.publish_memory(next_version, updates)
        self.run_telemetry_end(task_id, start_time, updates, tokens=95)
        return updates
