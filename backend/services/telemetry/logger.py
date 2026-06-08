import time
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone

# Configure Python logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("data_detective.telemetry")

class TelemetryLogger:
    """
    Telemetry logger for Data Detective Agent.
    Tracks agent state transitions, LLM token usages, response latencies,
    and structured audit traces for verification.
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def log_agent_start(self, agent_name: str, task_id: str, inputs: Dict[str, Any]) -> float:
        """
        Record the start of an agent step. Returns the current epoch time.
        """
        start_time = time.time()
        msg = {
            "event": "agent_start",
            "agent": agent_name,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "inputs_keys": list(inputs.keys())
        }
        if self.verbose:
            logger.info(f"[{agent_name}] Starting execution for task {task_id}. Inputs: {list(inputs.keys())}")
            logger.debug(json.dumps(msg))
        return start_time

    def log_agent_end(
        self, 
        agent_name: str, 
        task_id: str, 
        start_time: float, 
        outputs: Dict[str, Any], 
        tokens_used: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Record execution completion, computing duration and tracking tokens.
        """
        duration = time.time() - start_time
        metrics = {
            "event": "agent_end",
            "agent": agent_name,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 3),
            "tokens_used": tokens_used,
            "outputs_keys": list(outputs.keys())
        }
        
        logger.info(
            f"[{agent_name}] Finished task {task_id} in {duration:.3f}s. "
            f"Tokens Used: {tokens_used if tokens_used is not None else 'N/A'}"
        )
        
        if self.verbose:
            logger.debug(json.dumps(metrics))
            
        return metrics

    def log_tool_execution(
        self, 
        tool_name: str, 
        agent_name: str, 
        inputs: Dict[str, Any], 
        duration: float, 
        success: bool, 
        error: Optional[str] = None
    ):
        """
        Log tools run by agents, maintaining traceability for dataset actions.
        """
        log_payload = {
            "event": "tool_execution",
            "tool": tool_name,
            "agent": agent_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_seconds": round(duration, 3),
            "success": success,
            "error": error
        }
        status_str = "SUCCESS" if success else f"FAILED: {error}"
        logger.info(f"[{agent_name} -> Tool: {tool_name}] Executed in {duration:.3f}s - Status: {status_str}")
        logger.debug(json.dumps(log_payload))

telemetry_logger = TelemetryLogger()
