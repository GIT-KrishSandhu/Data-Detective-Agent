import os
import pytest
from unittest.mock import patch, MagicMock
from services.microsoft.orchestration.runtime_selector import get_active_runtime, reset_runtime
from services.microsoft.orchestration.azure_runtime import AzureRuntime, AzureHealthCheck
from services.microsoft.orchestration.local_runtime import LocalRuntime

def test_runtime_selection_fallback_when_credentials_missing():
    # Remove credentials from env
    with patch.dict(os.environ, {}, clear=True):
        reset_runtime()
        runtime = get_active_runtime()
        assert isinstance(runtime, LocalRuntime)

def test_runtime_selection_when_credentials_present():
    env_mock = {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test-deployment",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview"
    }
    with patch.dict(os.environ, env_mock), \
         patch("services.microsoft.orchestration.azure_runtime.AzureOpenAI") as mock_client:
        reset_runtime()
        runtime = get_active_runtime()
        assert isinstance(runtime, AzureRuntime)
        assert runtime.api_key == "test-key"
        assert runtime.endpoint == "https://test-resource.openai.azure.com/"

def test_azure_health_check_failure_cases():
    from core.config import settings
    # Credentials missing
    with patch.object(settings, "AZURE_OPENAI_API_KEY", ""), \
         patch.object(settings, "AZURE_OPENAI_ENDPOINT", ""), \
         patch.object(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", ""):
        res = AzureHealthCheck.verify()
        assert res["status"] == "disconnected"
        assert "Missing" in res["error_message"]

    # Connection failure
    with patch.object(settings, "AZURE_OPENAI_API_KEY", "test-key"), \
         patch.object(settings, "AZURE_OPENAI_ENDPOINT", "https://test-resource.openai.azure.com/"), \
         patch.object(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "test-deployment"), \
         patch("services.microsoft.orchestration.azure_runtime.AzureOpenAI") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.chat.completions.create.side_effect = Exception("Connection Timeout")
        
        res = AzureHealthCheck.verify()
        assert res["status"] == "error"
        assert "Connection Timeout" in res["error_message"]

def test_azure_health_check_success():
    from core.config import settings
    with patch.object(settings, "AZURE_OPENAI_API_KEY", "test-key"), \
         patch.object(settings, "AZURE_OPENAI_ENDPOINT", "https://test-resource.openai.azure.com/"), \
         patch.object(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "test-deployment"), \
         patch("services.microsoft.orchestration.azure_runtime.AzureOpenAI") as mock_client:
        mock_instance = mock_client.return_value
        # Mock success response
        mock_response = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_response
        
        res = AzureHealthCheck.verify()
        assert res["status"] == "connected"
        assert res["deployment"] == "test-deployment"
        assert res["latency_ms"] >= 0

def test_azure_runtime_generate_briefs_fallback_on_api_error():
    env_mock = {
        "AZURE_OPENAI_API_KEY": "test-key",
        "AZURE_OPENAI_ENDPOINT": "https://test-resource.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test-deployment"
    }
    with patch.dict(os.environ, env_mock), \
         patch("services.microsoft.orchestration.azure_runtime.AzureOpenAI") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.chat.completions.create.side_effect = Exception("API rate limit exceeded")
        
        runtime = AzureRuntime()
        brief_data = {
            "score": 85,
            "status": "PASS WITH WARNINGS",
            "filename": "sales.csv",
            "cols": 5,
            "rows": 1000,
            "critical": 1,
            "warnings": 3
        }
        res = runtime.generate_executive_briefs(brief_data)
        # Should fallback gracefully to LocalRuntime template descriptions
        assert "sales.csv" in res["executive_summary"]
        assert "85%" in res["executive_summary"]
        assert "1 critical" in res["executive_summary"]

def test_azure_runtime_generate_briefs_success():
    from core.config import settings
    with patch.object(settings, "AZURE_OPENAI_API_KEY", "test-key"), \
         patch.object(settings, "AZURE_OPENAI_ENDPOINT", "https://test-resource.openai.azure.com/"), \
         patch.object(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "test-deployment"), \
         patch("services.microsoft.orchestration.azure_runtime.AzureOpenAI") as mock_client:
        mock_instance = mock_client.return_value
        # Mock completion choices returning expected json object
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """
        {
            "executive_summary": "Azure Summary text.",
            "certificate_wording": "Azure Cert text.",
            "management_explanation": "Azure Mgmt text.",
            "markdown_export_wording": "Azure MD text."
        }
        """
        mock_instance.chat.completions.create.return_value = mock_response
        
        runtime = AzureRuntime()
        brief_data = {"score": 85, "status": "PASS WITH WARNINGS", "filename": "sales.csv", "cols": 5, "rows": 1000, "critical": 1, "warnings": 3}
        res = runtime.generate_executive_briefs(brief_data)
        assert "Azure Summary text." in res["executive_summary"]
        assert "Grounded With" in res["executive_summary"]
        assert res["certificate_wording"] == "Azure Cert text."
        assert res["management_explanation"] == "Azure Mgmt text."
        assert res["markdown_export_wording"] == "Azure MD text."

def test_system_runtime_endpoint():
    from fastapi.testclient import TestClient
    from main import app
    from core.config import settings
    
    # 1. Local fallback status
    with patch.object(settings, "AZURE_OPENAI_API_KEY", ""), \
         patch.object(settings, "AZURE_OPENAI_ENDPOINT", ""), \
         patch.object(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", ""):
        client = TestClient(app)
        response = client.get("/api/v1/system/runtime")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "Local"
        assert data["execution_mode"] == "Deterministic"
        assert data["reasoning_source"] == "Semantic Blackboard"
        assert data["language_generation"] == "Local Template"
        assert data["endpoint"] == "Local Loopback"

    # 2. Configured Azure connection success
    with patch.object(settings, "AZURE_OPENAI_API_KEY", "test-key"), \
         patch.object(settings, "AZURE_OPENAI_ENDPOINT", "https://test-resource.eastus2.openai.azure.com/"), \
         patch.object(settings, "AZURE_OPENAI_DEPLOYMENT_NAME", "test-deployment"), \
         patch("services.microsoft.orchestration.azure_runtime.AzureOpenAI") as mock_client:
        mock_instance = mock_client.return_value
        mock_response = MagicMock()
        mock_instance.chat.completions.create.return_value = mock_response
        
        client = TestClient(app)
        response = client.get("/api/v1/system/runtime")
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "Azure Foundry"
        assert data["status"] == "connected"
        assert data["execution_mode"] == "Deterministic"
        assert data["reasoning_source"] == "Semantic Blackboard"
        assert data["language_generation"] == "Azure GPT-5-mini"
        assert data["endpoint"] == "East US 2"

