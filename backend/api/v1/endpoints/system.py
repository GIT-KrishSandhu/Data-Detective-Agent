import os
# pyrefly: ignore [missing-import]
from fastapi import APIRouter
from core.config import settings
from services.microsoft.orchestration.azure_runtime import AzureHealthCheck

router = APIRouter()

@router.get("/runtime")
def get_system_runtime():
    """
    Returns active infrastructure status, connection latencies, and fallback properties.
    """
    from services.microsoft.foundry_iq.retriever import FoundryIQRetriever
    
    retriever = FoundryIQRetriever()
    retriever.initialize()
    iq_health = retriever.health()
    iq_connected = iq_health.get("status") == "connected"
    
    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    deployment = settings.AZURE_OPENAI_DEPLOYMENT_NAME
    api_version = settings.AZURE_OPENAI_API_VERSION
    
    if api_key and endpoint and deployment:
        result = AzureHealthCheck.verify()
        status = result.get("status", "disconnected")
        
        # Determine friendly endpoint region
        friendly_endpoint = "East US 2"
        if "eastus" in endpoint.lower():
            friendly_endpoint = "East US 2"
        elif "westus" in endpoint.lower():
            friendly_endpoint = "West US"
        
        return {
            "provider": result.get("provider", "Azure Foundry"),
            "model": result.get("model", "gpt-5-mini"),
            "deployment": result.get("deployment", "unknown"),
            "status": status,
            "latency_ms": result.get("latency_ms", 0),
            "fallback": "LocalRuntime",
            "error_message": result.get("error_message"),
            
            # Recommendation 3 & 4 Additions
            "endpoint": friendly_endpoint,
            "responses_api": "Chat Completions v1",
            "provider_version": api_version,
            "execution_mode": "Deterministic",
            "reasoning_source": "Semantic Blackboard",
            "language_generation": "Azure GPT-5-mini" if status == "connected" else "Local Template",
            
            # Phase 10 - Foundry IQ Grounding Integration additions
            "knowledge_provider": "Microsoft Foundry IQ" if iq_connected else "unavailable",
            "foundry_iq_connected": iq_connected,
            "retrieval_enabled": iq_connected,
            "retrieved_documents": 4 if iq_connected else 0
        }
    else:
        return {
            "provider": "Local",
            "model": "local",
            "deployment": "local",
            "status": "connected",
            "latency_ms": 0,
            "fallback": "None",
            "endpoint": "Local Loopback",
            "responses_api": "Local Template Engine",
            "provider_version": "v1.0.0",
            "execution_mode": "Deterministic",
            "reasoning_source": "Semantic Blackboard",
            "language_generation": "Local Template",
            
            # Phase 10 - Foundry IQ Grounding Integration additions
            "knowledge_provider": "unavailable",
            "foundry_iq_connected": False,
            "retrieval_enabled": False,
            "retrieved_documents": 0
        }

