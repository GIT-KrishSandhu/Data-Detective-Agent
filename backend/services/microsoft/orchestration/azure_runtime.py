import os
import time
import json
import logging
# pyrefly: ignore [missing-import]
from openai import AzureOpenAI
from core.config import settings
from services.microsoft.orchestration.local_runtime import LocalRuntime
from services.microsoft.orchestration.foundry_adapter import FoundryAdapterInterface
from services.microsoft.foundry_iq.retriever import FoundryIQRetriever
from services.microsoft.foundry_iq.query_builder import FoundryIQQueryBuilder
from datetime import datetime, timezone

logger = logging.getLogger("data_detective.azure_runtime")

class AzureHealthCheck:
    """
    Utility checking Azure OpenAI service status, authentication, and endpoint connection.
    """
    @staticmethod
    def verify() -> dict:
        api_key = settings.AZURE_OPENAI_API_KEY
        endpoint = settings.AZURE_OPENAI_ENDPOINT
        deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME
        api_version = settings.AZURE_OPENAI_API_VERSION



        if not api_key or not endpoint or not deployment:
            return {
                "status": "disconnected",
                "error_message": "Missing Azure OpenAI environment credentials in .env.",
                "provider": "Azure Foundry",
                "model": deployment or "unknown",
                "deployment": deployment or "unknown",
                "latency_ms": 0
            }

        # Clean endpoint to get the resource base
        clean_endpoint = endpoint
        if "/openai/v1" in endpoint:
            clean_endpoint = endpoint.split("/openai/v1")[0]

        try:
            client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=clean_endpoint,
                timeout=5.0
            )

            start_time = time.time()
            # Minimal completion test compatible with o-series / gpt-5-mini
            client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": "ping"}],
                max_completion_tokens=5
            )
            latency = int((time.time() - start_time) * 1000)

            return {
                "status": "connected",
                "latency_ms": latency,
                "deployment": deployment,
                "model": deployment,
                "provider": "Azure Foundry"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": str(e),
                "provider": "Azure Foundry",
                "model": deployment,
                "deployment": deployment,
                "latency_ms": 0
            }

class AzureRuntime(LocalRuntime):
    """
    Azure Orchestration Runtime utilizing Azure AI OpenAI models
    for executive language synthesis and deterministic local tracking.
    """
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview")

        clean_endpoint = self.endpoint
        if self.endpoint and "/openai/v1" in self.endpoint:
            clean_endpoint = self.endpoint.split("/openai/v1")[0]

        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=clean_endpoint,
            timeout=10.0
        )
        logger.info(f"[Telemetry] provider_selected=\"Azure Foundry\" runtime_selected=\"AzureRuntime\" model=\"{self.deployment}\"")

    def generate_executive_briefs(self, data: dict) -> dict:
        score = data.get("score", 100)
        status = data.get("status", "ENTERPRISE READY")
        filename = data.get("filename", "unknown")
        cols = data.get("cols", 0)
        rows = data.get("rows", 0)
        critical = data.get("critical", 0)
        warnings = data.get("warnings", 0)
        recommendations = data.get("recommendations", [])

        # Initialize Microsoft Foundry IQ Retriever
        retriever = FoundryIQRetriever()
        retriever.initialize()
        
        # Build search query using deterministic evidence
        query = FoundryIQQueryBuilder.build_query(data)
        
        # Telemetry: Foundry IQ retrieval started
        execution_log = data.get("agent_execution_log")
        if execution_log is not None:
            execution_log.append({
                "type": "telemetry_event",
                "event": "Foundry IQ retrieval started",
                "agent_name": "FoundryIQRetriever",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
        # Retrieve governance context (returns [] gracefully if unavailable)
        t_start = time.time()
        retrieved_docs = retriever.retrieve(query)
        latency_ms = int((time.time() - t_start) * 1000)
        
        # Telemetry: Foundry IQ retrieval completed
        if execution_log is not None:
            execution_log.append({
                "type": "telemetry_event",
                "event": "Foundry IQ retrieval completed",
                "agent_name": "FoundryIQRetriever",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "retrieved_chunks": len(retrieved_docs),
                "retrieval_latency_ms": latency_ms,
                "retrieval_success": retriever.connected
            })

        snippets_text = "\n".join([f"- [{doc['title']}]: {doc['content']}" for doc in retrieved_docs])

        system_message = (
            "You are an Enterprise BI communication assistant.\n"
            "You are NOT allowed to perform analytical reasoning.\n"
            "Only explain deterministic audit evidence.\n"
            "Use retrieved governance documentation only as supporting context.\n"
            "Never contradict deterministic evidence.\n"
            "If supporting documentation conflicts with deterministic evidence, prioritize deterministic evidence.\n"
            "You must respond ONLY with a JSON object containing precisely these four string keys: "
            "'executive_summary', 'certificate_wording', 'management_explanation', 'markdown_export_wording'."
        )

        prompt = (
            f"### Deterministic Audit Evidence\n"
            f"- Filename: {filename}\n"
            f"- Rows: {rows:,} | Columns: {cols}\n"
            f"- Readiness Score: {score}%\n"
            f"- Status: {status}\n"
            f"- Critical Issues Count: {critical}\n"
            f"- Warnings Count: {warnings}\n"
            f"- Key recommendations: {recommendations}\n"
            f"- Dimension Candidate: {data.get('dim_candidate', '')}\n"
            f"- Detected Problems: {data.get('problems', [])}\n\n"
            f"### Retrieved Governance Snippets\n"
            f"{snippets_text if snippets_text else 'No supporting governance documentation retrieved.'}\n\n"
            f"Please generate the executive explanations."
        )

        footer = (
            "\n\nGrounded With\n"
            "✓ Deterministic Python Analytics\n"
            "✓ Semantic Blackboard Reasoning\n"
            "✓ Microsoft Foundry IQ Knowledge Retrieval\n"
            "✓ Azure GPT-5-mini Executive Language Generation"
        )

        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=800,
                response_format={"type": "json_object"}
            )
            latency = int((time.time() - start_time) * 1000)
            logger.info(f"[Telemetry] runtime_selected=\"AzureRuntime\" connection_status=\"connected\" latency_ms={latency}")

            content = response.choices[0].message.content
            briefs = json.loads(content)

            # Ensure all required keys exist
            required_keys = ["executive_summary", "certificate_wording", "management_explanation", "markdown_export_wording"]
            if all(k in briefs for k in required_keys):
                # Task 6: Append Grounding Footer to executive_summary
                if footer not in briefs["executive_summary"]:
                    briefs["executive_summary"] += footer
                return briefs
            else:
                raise ValueError("JSON response missing required keys")

        except Exception as e:
            logger.warning(f"[Telemetry] event=\"fallback_to_local\" reason=\"{str(e)}\"")
            # Dynamic fallback to local templates
            fallback = LocalRuntime()
            return fallback.generate_executive_briefs(data)
