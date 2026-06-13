import pytest
from unittest.mock import patch
from core.config import settings
from services.microsoft.foundry_iq.retriever import FoundryIQRetriever
from services.microsoft.foundry_iq.query_builder import FoundryIQQueryBuilder

def test_query_builder():
    data = {
        "score": 82,
        "critical": 2,
        "warnings": 4,
        "dim_candidate": "PassengerId",
        "problems": ["duplicate keys", "null values", "schema normalization"]
    }
    query = FoundryIQQueryBuilder.build_query(data)
    
    assert "readiness score 82" in query
    assert "schema integrity" in query
    assert "duplicate keys" in query
    assert "null values" in query
    assert "star schema" in query
    assert "Power BI governance" in query
    assert "business intelligence best practices" in query
    assert "semantic model recommendations" in query

def test_retriever_offline_retrieval():
    # Force retriever disconnected / offline
    with patch.object(settings, "AZURE_OPENAI_API_KEY", ""):
        retriever = FoundryIQRetriever()
        retriever.initialize()
        assert retriever.connected is False
        
        # Retrieval should return empty list without crashing
        docs = retriever.retrieve("readiness score 82 duplicate keys")
        assert docs == []
        
        # Health should report disconnected
        health_info = retriever.health()
        assert health_info["status"] == "disconnected"
        assert health_info["latency_ms"] == 0

def test_retriever_online_retrieval():
    # Force retriever connected / online
    with patch.object(settings, "AZURE_OPENAI_API_KEY", "test-api-key"):
        retriever = FoundryIQRetriever()
        retriever.initialize()
        assert retriever.connected is True
        
        # Should retrieve documents matching query keyword "duplicate"
        docs = retriever.retrieve("readiness score 82 duplicate keys", top_k=2)
        assert len(docs) > 0
        assert any("duplicate" in doc["title"].lower() or "duplicate" in doc["content"].lower() for doc in docs)
        
        # Health should report connected
        health_info = retriever.health()
        assert health_info["status"] == "connected"
        assert health_info["latency_ms"] > 0
