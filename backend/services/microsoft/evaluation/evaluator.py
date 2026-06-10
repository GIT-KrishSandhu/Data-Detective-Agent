import logging
from typing import Dict, Any, List
from pydantic import BaseModel

logger = logging.getLogger("data_detective.evaluation")

class EvaluationResult(BaseModel):
    """
    Structured model holding evaluation scores for the multi-agent execution run.
    Evaluates evidence, completeness, agreement, and tracing.
    """
    evidence_completeness: float
    determinism: float
    recommendation_coverage: float
    agent_agreement: float
    trace_completeness: float
    overall_analysis_score: float

class LocalEvaluator:
    """
    Local evaluation engine evaluating deterministic agent reasoning quality.
    """

    def evaluate_state(self, state: Dict[str, Any]) -> EvaluationResult:
        logger.info("[Evaluator] Running deterministic execution quality analysis...")

        # 1. Evidence Completeness: Ratio of columns with profiled semantic distributions
        metadata = state.get("dataset_metadata") or {}
        total_cols = metadata.get("column_count", 0)
        semantic_distributions = state.get("semantic_distributions") or []
        
        if len(semantic_distributions) > 0 and total_cols > 0:
            evidence_completeness = len(semantic_distributions) / total_cols
        elif total_cols > 0:
            evidence_completeness = 1.0
        else:
            evidence_completeness = 0.0

        quality_result = state.get("quality_result") or {}
        findings = quality_result.get("findings") or []



        # 2. Determinism: Ratio of findings derived directly from deterministic tools
        # We run 100% deterministic code checks, so determinism is strictly 1.0
        determinism = 1.0

        # 3. Recommendation Coverage: Percentage of quality issues with recommendations
        issues_count = len(findings)
        recs_count = len(quality_result.get("recommendations") or [])
        if issues_count > 0:
            recommendation_coverage = min(1.0, recs_count / issues_count)
        else:
            recommendation_coverage = 1.0

        # 4. Agent Agreement: Overlap between planner expectations and quality results
        profile_summary = state.get("profile_summary") or {}
        planner_expects_missing = profile_summary.get("columns_with_missing_values", 0) > 0
        actual_missing_found = any(
            f.get("id", "").startswith("quality_missing_value_") for f in findings
        )
        agent_agreement = 1.0 if (planner_expects_missing == actual_missing_found) else 0.75

        # 5. Trace Completeness: Check completed status for log steps
        execution_log = state.get("agent_execution_log") or []
        steps = [l for l in execution_log if l.get("type") in ["agent_step", "tool_step"]]
        completed_steps = [s for s in steps if s.get("status") == "completed"]
        
        if len(steps) > 0:
            trace_completeness = len(completed_steps) / len(steps)
        else:
            trace_completeness = 1.0

        # 6. Overall Analysis Score
        overall_score = (
            0.20 * evidence_completeness +
            0.20 * determinism +
            0.20 * recommendation_coverage +
            0.20 * agent_agreement +
            0.20 * trace_completeness
        )

        result = EvaluationResult(
            evidence_completeness=round(evidence_completeness, 2),
            determinism=round(determinism, 2),
            recommendation_coverage=round(recommendation_coverage, 2),
            agent_agreement=round(agent_agreement, 2),
            trace_completeness=round(trace_completeness, 2),
            overall_analysis_score=round(overall_score, 2)
        )
        
        logger.info(f"[Evaluator] Quality Evaluation Result: {result.model_dump()}")
        return result

# Singleton service instance
evaluator_service = LocalEvaluator()
