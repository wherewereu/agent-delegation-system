"""
Test: HTTP API Server
Red first - tests for REST API
"""
import pytest
import json
from api_server import APIServer, DelegationAPI


class TestAPIServer:
    """Test REST API server."""

    def test_server_initialization(self):
        """API server should initialize"""
        server = APIServer(host="127.0.0.1", port=8080)
        
        assert server.host == "127.0.0.1"
        assert server.port == 8080

    def test_delegation_endpoint(self):
        """Should have delegation endpoint"""
        from api_server import DelegationAPI
        
        api = DelegationAPI()
        
        # Test delegation
        result = api.delegate("research bitcoin")
        
        assert result["task_id"] is not None
        assert result["agent"] in ["scout", "milo"]

    def test_status_endpoint(self):
        """Should have status endpoint"""
        from api_server import DelegationAPI
        
        api = DelegationAPI()
        
        status = api.get_status()
        
        assert "agents" in status

    def test_metrics_endpoint(self):
        """Should have metrics endpoint"""
        from api_server import DelegationAPI
        
        api = DelegationAPI()
        
        metrics = api.get_metrics()
        
        assert "total_delegations" in metrics or "status" in metrics


class TestAPIRequests:
    """Test API request handling."""

    def test_parse_delegation_request(self):
        """Should parse delegation request"""
        from api_server import parse_delegation_request, ValidationError
        
        request = {
            "request": "research bitcoin",
            "priority": "urgent"
        }
        
        parsed = parse_delegation_request(request)
        
        assert parsed["request"] == "research bitcoin"
        assert parsed["priority"] == "urgent"

    def test_default_priority(self):
        """Should default priority to normal"""
        from api_server import parse_delegation_request, ValidationError
        
        request = {"request": "test"}
        
        parsed = parse_delegation_request(request)
        
        assert parsed["priority"] == "normal"

    def test_validation_missing_request(self):
        """Should reject missing request"""
        from api_server import ValidationError
        
        with pytest.raises(ValidationError):
            parse_delegation_request({})