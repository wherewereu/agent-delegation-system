"""
REST API Server
HTTP server for external access to delegation system
"""
import json
import os
from typing import Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class ValidationError(Exception):
    """Request validation error."""
    pass


class APIServer:
    """REST API server for delegation system."""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8080):
        self.host = host
        self.port = port
        self.router = None
        self._init_router()
    
    def _init_router(self):
        """Initialize the delegation router."""
        from router import DelegationRouter
        self.router = DelegationRouter()
    
    def handle_request(self, method: str, path: str, body: Optional[Dict] = None) -> Dict:
        """Handle incoming API request."""
        
        # Parse path
        parsed = urlparse(path)
        path = parsed.path
        
        # Route to handlers
        if path == "/api/delegation" and method == "POST":
            return self._handle_delegate(body)
        
        elif path == "/api/status":
            return self._handle_status()
        
        elif path == "/api/metrics":
            return self._handle_metrics()
        
        elif path == "/api/agents":
            return self._handle_agents()
        
        elif path.startswith("/api/task/") and method == "GET":
            task_id = path.split("/")[-1]
            return self._handle_task(task_id)
        
        elif path.startswith("/api/task/") and method == "DELETE":
            task_id = path.split("/")[-1]
            return self._handle_task_cancel(task_id)
        
        elif path == "/api/health":
            return {"status": "healthy"}
        
        else:
            return {"error": "Not found", "code": 404}
    
    def _handle_delegate(self, body: Optional[Dict]) -> Dict:
        """Handle delegation request."""
        if not body or "request" not in body:
            raise ValidationError("Missing 'request' field")
        
        request = body["request"]
        priority = body.get("priority", "normal")
        
        result = self.router.delegate(request, priority=priority)
        
        return {
            "task_id": result.task_id,
            "agent": result.agent,
            "action": result.action,
            "success": result.success,
            "priority": result.priority
        }
    
    def _handle_status(self) -> Dict:
        """Handle status request."""
        return self.router.status()
    
    def _handle_metrics(self) -> Dict:
        """Handle metrics request."""
        from metrics import MetricsCollector
        collector = MetricsCollector()
        
        return collector.get_overall_metrics()
    
    def _handle_agents(self) -> Dict:
        """Handle agents list request."""
        return {
            "agents": list(self.router.state.current_tasks.keys())
        }
    
    def _handle_task(self, task_id: str) -> Dict:
        """Handle task status request."""
        status = self.router.state.get_task_status(task_id)
        
        if not status:
            return {"error": "Task not found", "code": 404}
        
        return status
    
    def _handle_task_cancel(self, task_id: str) -> Dict:
        """Handle task cancellation."""
        # For now, just return not implemented
        return {"error": "Not implemented", "code": 501}


class DelegationAPI:
    """Python API for direct access."""
    
    def __init__(self):
        from router import DelegationRouter
        self.router = DelegationRouter()
    
    def delegate(self, request: str, priority: str = "normal") -> Dict:
        """Delegate a request."""
        result = self.router.delegate(request, priority=priority)
        
        return {
            "task_id": result.task_id,
            "agent": result.agent,
            "action": result.action,
            "success": result.success,
            "priority": result.priority
        }
    
    def get_status(self) -> Dict:
        """Get system status."""
        return self.router.status()
    
    def get_metrics(self) -> Dict:
        """Get metrics."""
        from metrics import MetricsCollector
        collector = MetricsCollector()
        return collector.get_overall_metrics()


def parse_delegation_request(body: Dict) -> Dict:
    """Parse and validate delegation request."""
    if not body:
        raise ValidationError("Empty request body")
    
    if "request" not in body:
        raise ValidationError("Missing 'request' field")
    
    return {
        "request": body["request"],
        "priority": body.get("priority", "normal")
    }


class APIRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler."""
    
    server = None
    
    def do_GET(self):
        """Handle GET requests."""
        result = self.server.handle_request("GET", self.path)
        self._send_json(result)
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get("Content-Length", 0))
        
        body = {}
        if content_length > 0:
            body = json.loads(self.rfile.read(content_length))
        
        result = self.server.handle_request("POST", self.path, body)
        self._send_json(result)
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        result = self.server.handle_request("DELETE", self.path)
        self._send_json(result)
    
    def _send_json(self, data: Dict):
        """Send JSON response."""
        code = data.get("code", 200)
        
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        self.wfile.write(json.dumps(data).encode())


def start_server(host: str = "127.0.0.1", port: int = 8080):
    """Start the API server."""
    server = APIServer(host, port)
    
    APIRequestHandler.server = server
    
    httpd = HTTPServer((host, port), APIRequestHandler)
    
    print(f"API Server running on http://{host}:{port}")
    print("Endpoints:")
    print("  POST /api/delegation - Delegate a task")
    print("  GET  /api/status     - Get system status")
    print("  GET  /api/metrics     - Get metrics")
    print("  GET  /api/agents      - List agents")
    print("  GET  /api/task/<id>   - Get task status")
    print("  GET  /api/health      - Health check")
    
    httpd.serve_forever()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "start":
            start_server()
    else:
        # Test API directly
        api = DelegationAPI()
        print(json.dumps(api.delegate("research bitcoin"), indent=2))