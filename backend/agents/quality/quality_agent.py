import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List
import pandas as pd
from langchain_core.language_models.chat_models import BaseChatModel

from agents.base import BaseAgent
from agents.base.agent_result import AgentResult
from agents.quality.finding import QualityFinding

# Import quality tools
from tools.quality.missing_value_tool import run_missing_value_tool
from tools.quality.duplicate_detector import run_duplicate_detector
from tools.quality.constant_column_detector import run_constant_column_detector
from tools.quality.mixed_type_detector import run_mixed_type_detector
from tools.quality.identifier_detector import run_identifier_detector
from tools.quality.high_cardinality_detector import run_high_cardinality_detector

logger = logging.getLogger("data_detective.quality")

class QualityAgent(BaseAgent):
    """
    Quality Agent responsible for auditing data structure and integrity.
    Executes deterministic pandas-based scanning tools and translates results
    into structured, reproducible QualityFindings and actionable recommendations.
    """

    def __init__(self, name: str, llm: BaseChatModel, system_prompt: str = ""):
        super().__init__(
            name=name,
            llm=llm,
            system_prompt=system_prompt or "You are the Data Detective Quality Agent. Evaluate dataset structures.",
            temperature=0.0
        )

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoked as a LangGraph execution node. Runs quality tools and populates AgentState.
        """
        import uuid
        # Import semantic entities and relationships
        from services.microsoft.semantic_entities.quality_issue import QualityIssueEntity
        from services.microsoft.semantic_entities.recommendation import RecommendationEntity
        from services.microsoft.semantic_entities.agent_memory import AgentMemoryEntity
        from services.microsoft.semantic_entities.relationship import SemanticRelationship
        from services.microsoft.orchestration.local_runtime import local_runtime_service

        task_id = "quality_audit"
        start_time = self.run_telemetry_start(task_id, state)
        
        agent_start_time = time.time()
        agent_started_at = datetime.now(timezone.utc).isoformat()
        
        # Telemetry trace configuration
        root_trace_id = state.get("root_trace_id") or str(uuid.uuid4())
        quality_trace_id = str(uuid.uuid4())

        current_log = list(state.get("agent_execution_log") or [])
        
        # Telemetry quality_started
        current_log.append({
            "type": "telemetry_event",
            "event": "quality_started",
            "agent_name": self.name,
            "timestamp": agent_started_at
        })
        
        # Fetch file path
        path = state.get("dataset_path")
        if not path or not os.path.exists(path):
            err_msg = f"Dataset file path '{path}' does not exist or was not provided."
            logger.error(err_msg)
            current_log.append({
                "type": "telemetry_event",
                "event": "quality_completed",
                "agent_name": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return {"errors": list(state.get("errors") or []) + [err_msg]}

        # Load dataset into pandas DataFrame
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
                raise ValueError(f"Unsupported file format: {ext}")
        except Exception as e:
            err_msg = f"Failed to load dataset file: {str(e)}"
            logger.error(err_msg)
            current_log.append({
                "type": "telemetry_event",
                "event": "quality_completed",
                "agent_name": self.name,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return {"errors": list(state.get("errors") or []) + [err_msg]}

        tool_trace = []
        findings = []

        # Helper method to execute and log a tool
        def run_tool_with_logging(tool_func, friendly_name):
            t_start = time.time()
            t_start_iso = datetime.now(timezone.utc).isoformat()
            tool_trace_id = str(uuid.uuid4())
            
            # Telemetry tool_started
            current_log.append({
                "type": "telemetry_event",
                "event": "tool_started",
                "tool_name": friendly_name,
                "agent_name": self.name,
                "timestamp": t_start_iso
            })
            
            # Execute
            res = tool_func(df)
            
            t_end = time.time()
            t_end_iso = datetime.now(timezone.utc).isoformat()
            t_duration_ms = int((t_end - t_start) * 1000)
            
            # Telemetry tool_completed
            current_log.append({
                "type": "telemetry_event",
                "event": "tool_completed",
                "tool_name": friendly_name,
                "agent_name": self.name,
                "execution_time_ms": t_duration_ms,
                "timestamp": t_end_iso
            })
            
            # Add tool execution log step
            tool_step = {
                "type": "tool_step",
                "trace_id": tool_trace_id,
                "parent_trace_id": quality_trace_id,
                "agent_name": self.name,
                "tool_name": friendly_name,
                "status": "completed",
                "started_at": t_start_iso,
                "completed_at": t_end_iso,
                "duration_ms": t_duration_ms,
                "confidence": 1.0,
                "blackboard_version": 2
            }
            current_log.append(tool_step)

            # Publish trace to local runtime
            local_runtime_service.publish_trace(tool_trace_id, tool_step)
            
            tool_trace.append({
                "tool_name": friendly_name,
                "status": "success",
                "execution_time_ms": t_duration_ms
            })
            
            return res

        # Run Tools and Formulate Findings

        # 1. Missing Value Tool
        missing_res = run_tool_with_logging(run_missing_value_tool, "Missing Value Tool")
        for col, col_info in missing_res.get("columns", {}).items():
            null_count = col_info["null_count"]
            null_pct = col_info["null_percentage"]
            if null_count > 0:
                severity = "Warning"
                if null_pct > 0.15:
                    severity = "Critical"
                
                col_lower = col.lower()
                is_business_metric = any(keyword in col_lower for keyword in ["revenue", "price", "amount", "cost", "sales", "profit", "total"])
                
                if is_business_metric:
                    biz_impact = f"Column '{col}' represents an important business metric. High missingness ({null_pct:.1%}) can bias downstream executive reporting and critical financial trends."
                    rec = f"Investigate upstream ETL process and data entry systems for '{col}' before applying any imputation."
                elif any(keyword in col_lower for keyword in ["id", "key", "pk", "code"]):
                    biz_impact = f"Column '{col}' appears to be a unique key/identifier. Missing identifiers ({null_pct:.1%}) prevent record linkage, join stability, and index integrity."
                    rec = f"Audit data ingestion pipeline; records without valid identifiers should be isolated or discarded."
                else:
                    biz_impact = f"Missing values ({null_pct:.1%}) in column '{col}' will degrade machine learning models and cause aggregate analysis inconsistencies."
                    rec = f"Use median imputation for numeric data, or represent missing categories explicitly as 'Unknown'."
                
                findings.append(QualityFinding(
                    id=f"quality_missing_value_{col}",
                    title=f"Missing Values in '{col}'",
                    description=f"Detected {null_count} null/missing values in column '{col}', representing {null_pct:.1%} of total records.",
                    severity=severity,
                    affected_columns=[col],
                    evidence=f"null_count={null_count}, null_percentage={null_pct:.4f}",
                    business_impact=biz_impact,
                    recommendation=rec,
                    confidence=0.95
                ))

        # 2. Duplicate Detector
        dup_res = run_tool_with_logging(run_duplicate_detector, "Duplicate Detector")
        dup_count = dup_res.get("duplicate_rows_count", 0)
        dup_pct = dup_res.get("duplicate_percentage", 0.0)
        if dup_count > 0:
            severity = "Critical" if dup_pct > 0.05 else "Warning"
            findings.append(QualityFinding(
                id="quality_duplicate_rows",
                title="Duplicate Records Detected",
                description=f"The dataset contains {dup_count} duplicate rows, representing {dup_pct:.1%} of all rows.",
                severity=severity,
                affected_columns=list(df.columns),
                evidence=f"duplicate_rows={dup_count}, duplicate_percentage={dup_pct:.4f}",
                business_impact="Duplicate records artificially inflate metrics like row counts, revenue aggregates, and unique counts, distorting downstream business reports.",
                recommendation="Investigate why duplicate records are being generated at the source. Deduplicate using unique key constraints or drop exact duplicates before analysis.",
                confidence=1.0
            ))

        # 3. Constant Column Detector
        const_res = run_tool_with_logging(run_constant_column_detector, "Constant Column Detector")
        for const_info in const_res.get("constant_columns", []):
            col = const_info["column"]
            val = const_info["value"]
            findings.append(QualityFinding(
                id=f"quality_constant_col_{col}",
                title=f"Constant Column '{col}'",
                description=f"Column '{col}' has only one unique value: '{val}'.",
                severity="Warning",
                affected_columns=[col],
                evidence=f"unique_values_count=1, constant_value={val}",
                business_impact=f"Column '{col}' has zero variance and contributes no information to analytical models or visualizations, adding redundant overhead.",
                recommendation=f"Exclude column '{col}' from active features or report filters since its value never varies.",
                confidence=1.0
            ))

        # 4. Mixed Type Detector
        mixed_res = run_tool_with_logging(run_mixed_type_detector, "Mixed Type Detector")
        for col, mixed_info in mixed_res.get("mixed_type_columns", {}).items():
            types_found = mixed_info["types_found"]
            type_counts = mixed_info["type_counts"]
            findings.append(QualityFinding(
                id=f"quality_mixed_type_{col}",
                title=f"Mixed Data Types in Column '{col}'",
                description=f"Column '{col}' contains multiple conflicting Python types: {types_found}.",
                severity="Critical",
                affected_columns=[col],
                evidence=f"types_found={types_found}, counts={type_counts}",
                business_impact=f"Conflicting types (e.g. integers mixed with strings) in '{col}' trigger execution failures in aggregations, formatting bugs, and runtime exceptions in database queries.",
                recommendation=f"Standardize the column type by parsing/casting all non-null values to a single type (e.g., float or string).",
                confidence=0.95
            ))

        # 5. Identifier Detector
        id_res = run_tool_with_logging(run_identifier_detector, "Identifier Detector")
        for id_info in id_res.get("identifier_columns", []):
            col = id_info["column"]
            reason = id_info["reason"]
            uniqueness = id_info["uniqueness_ratio"]
            findings.append(QualityFinding(
                id=f"quality_identifier_{col}",
                title=f"Unique Identifier Column '{col}'",
                description=f"Column '{col}' is classified as a unique primary key or row identifier.",
                severity="Info",
                affected_columns=[col],
                evidence=f"uniqueness_ratio={uniqueness:.4f}, reason='{reason}'",
                business_impact=f"Column '{col}' serves as a unique lookup. Storing identifiers lets you trace individual records, but applying arithmetic summaries is meaningless.",
                recommendation=f"Keep column '{col}' as the dataset index or join key; exclude it from statistical aggregations (mean, standard deviation).",
                confidence=0.95
            ))

        # 6. High Cardinality Detector
        card_res = run_tool_with_logging(run_high_cardinality_detector, "High Cardinality Detector")
        for card_info in card_res.get("high_cardinality_columns", []):
            col = card_info["column"]
            unique_count = card_info["unique_count"]
            ratio = card_info["cardinality_ratio"]
            findings.append(QualityFinding(
                id=f"quality_high_cardinality_{col}",
                title=f"High Cardinality Categorical Column '{col}'",
                description=f"Categorical column '{col}' has a high unique value count ({unique_count}), representing {ratio:.1%} of total rows.",
                severity="Warning",
                affected_columns=[col],
                evidence=f"unique_count={unique_count}, cardinality_ratio={ratio:.4f}",
                business_impact=f"High cardinality in category '{col}' results in noisy visualizations, unreadable dashboard filters, and overfitted machine learning features.",
                recommendation=f"Apply frequency-based binning to group infrequent categories into a common 'Other' group, or group values into higher-level logical hierarchies.",
                confidence=0.90
            ))

        agent_end_time = time.time()
        agent_completed_at = datetime.now(timezone.utc).isoformat()
        agent_duration_ms = int((agent_end_time - agent_start_time) * 1000)
        
        # Telemetry quality_completed
        current_log.append({
            "type": "telemetry_event",
            "event": "quality_completed",
            "agent_name": self.name,
            "timestamp": agent_completed_at
        })
        
        # Calculate Agent overall confidence
        agent_confidence = 0.95
        critical_count = sum(1 for f in findings if f.severity == "Critical")
        if critical_count > 0:
            agent_confidence = max(0.60, agent_confidence - 0.05 * critical_count)
            
        # Agent execution step log
        agent_step = {
            "type": "agent_step",
            "trace_id": quality_trace_id,
            "parent_trace_id": root_trace_id,
            "agent_name": self.name,
            "tool_name": None,
            "status": "completed",
            "started_at": agent_started_at,
            "completed_at": agent_completed_at,
            "execution_time_ms": agent_duration_ms,
            "confidence": agent_confidence,
            "blackboard_version": 2
        }
        current_log.append(agent_step)
        
        # Telemetry blackboard_updated
        current_log.append({
            "type": "telemetry_event",
            "event": "blackboard_updated",
            "agent_name": self.name,
            "timestamp": agent_completed_at
        })
        
        # Deduplicated recommendations list
        recs = list(dict.fromkeys(f.recommendation for f in findings))
        
        summary_msg = f"Quality audit complete. Scanned dataset and identified {len(findings)} data quality issues."
        if critical_count > 0:
            summary_msg += f" Found {critical_count} critical issues requiring attention."
        else:
            summary_msg += " No critical issues were found."
            
        reasoning_msg = "Data quality scan executed 6 deterministic tools (Missing Value Tool, Duplicate Detector, Constant Column Detector, Mixed Type Detector, Identifier Detector, High Cardinality Detector). "
        if len(findings) > 0:
            reasoning_msg += f"Identified issues affecting columns: {', '.join(set(c for f in findings for c in f.affected_columns))}."
        else:
            reasoning_msg += "All checks passed successfully. The dataset is structurally clean."

        # Compile AgentResult dictionary
        agent_result = AgentResult(
            agent_name=self.name,
            summary=summary_msg,
            reasoning=reasoning_msg,
            confidence=agent_confidence,
            findings=[f.model_dump() for f in findings],
            recommendations=recs,
            tool_trace=tool_trace,
            execution_time_ms=agent_duration_ms
        )

        # ----------------- Semantic Entities Formulation -----------------
        dataset_id = state.get("dataset_id") or "default"
        
        semantic_issues_list = []
        semantic_recs_list = []
        relationships = list(state.get("semantic_relationships") or [])
        
        for finding in findings:
            # Create QualityIssueEntity
            issue_id = finding.id
            issue_entity = QualityIssueEntity(
                entity_id=issue_id,
                entity_type="QualityIssue",
                created_by_agent=self.name,
                confidence=finding.confidence,
                dependencies=[f"col_{c}" for c in finding.affected_columns],
                title=finding.title,
                description=finding.description,
                severity=finding.severity,
                affected_columns=finding.affected_columns,
                evidence=finding.evidence,
                business_impact=finding.business_impact
            )
            semantic_issues_list.append(issue_entity.model_dump())
            
            # Create RecommendationEntity
            rec_id = f"rec_{finding.id}"
            rec_entity = RecommendationEntity(
                entity_id=rec_id,
                entity_type="Recommendation",
                created_by_agent=self.name,
                confidence=finding.confidence,
                dependencies=[issue_id],
                recommendation_text=finding.recommendation,
                actionable_steps=[finding.recommendation]
            )
            semantic_recs_list.append(rec_entity.model_dump())
            
            # Semantic Relationships (Explainable Blackboard Graph)
            # QualityAgent creates QualityIssue
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_quality_creates_issue_{finding.id}",
                source_id=self.name,
                target_id=issue_id,
                relationship_type="creates"
            ))
            # QualityAgent creates Recommendation
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_quality_creates_rec_{finding.id}",
                source_id=self.name,
                target_id=rec_id,
                relationship_type="creates"
            ))
            # Column has QualityIssue
            for c in finding.affected_columns:
                relationships.append(SemanticRelationship(
                    relationship_id=f"rel_col_{c}_has_issue_{finding.id}",
                    source_id=f"col_{c}",
                    target_id=issue_id,
                    relationship_type="has"
                ))
            # QualityIssue generates Recommendation
            relationships.append(SemanticRelationship(
                relationship_id=f"rel_issue_{finding.id}_generates_rec_{finding.id}",
                source_id=issue_id,
                target_id=rec_id,
                relationship_type="generates"
            ))
            
        # Agent Memory
        memory_entity = AgentMemoryEntity(
            entity_id=f"memory_quality_{dataset_id}",
            entity_type="AgentMemory",
            created_by_agent=self.name,
            agent_name=self.name,
            cognitive_state=summary_msg,
            internal_variables={"findings_count": len(findings), "critical_count": critical_count},
            confidence=agent_confidence,
            dependencies=[f"dataset_{dataset_id}"]
        )
        memories = list(state.get("semantic_memories") or [])
        memories.append(memory_entity.model_dump())
        
        # QualityAgent creates AgentMemory
        relationships.append(SemanticRelationship(
            relationship_id=f"rel_quality_creates_memory_{dataset_id}",
            source_id=self.name,
            target_id=memory_entity.entity_id,
            relationship_type="creates"
        ))

        # Register capabilities with the local Foundry adapter
        local_runtime_service.register_agent(self.name, {"type": "quality_auditor", "version": "1.0"})
        local_runtime_service.publish_trace(quality_trace_id, agent_step)

        # Dynamic entity count calculation
        total_entities = 0
        if state.get("semantic_goal"):
            total_entities += 1
        if state.get("semantic_dataset"):
            total_entities += 1
            ds = state.get("semantic_dataset") or {}
            cols = ds.get("columns") or []
            total_entities += len(cols)
        
        total_entities += len(memories)
        total_entities += len(semantic_issues_list)
        total_entities += len(semantic_recs_list)

        prev_version = state.get("blackboard_version") or 1
        next_version = prev_version + 1

        # Compile final blackboard updates
        updates = {
            "quality_result": agent_result.model_dump(),
            "quality_findings": [f.model_dump() for f in findings],
            "quality_recommendations": recs,
            "quality_confidence": agent_confidence,
            "agent_execution_log": current_log,
            "current_agent": "quality",
            "current_step": "Quality Complete",
            
            # Phase 5 semantic updates
            "semantic_issues": semantic_issues_list,
            "semantic_recommendations": semantic_recs_list,
            "semantic_memories": memories,
            "semantic_relationships": [r.model_dump() if hasattr(r, "model_dump") else r for r in relationships],
            
            # Blackboard version info
            "blackboard_version": next_version,
            "blackboard_entity_count": total_entities,
            "blackboard_last_updated_by": self.name,
            "blackboard_last_trace_id": quality_trace_id
        }
        
        local_runtime_service.publish_memory(next_version, updates)
        self.run_telemetry_end(task_id, start_time, updates, tokens=150)
        return updates
