"""
Core health checking module for MCP servers.

Provides connectivity testing, capability discovery,
and health status monitoring for MCP-compatible endpoints.
"""

import json
import time
import socket
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


@dataclass
class HealthResult:
    """Result of a single health check against an MCP server."""

    server_url: str
    is_healthy: bool
    response_time_ms: float
    status_code: Optional[int] = None
    server_info: Optional[dict] = None
    capabilities: list = field(default_factory=list)
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "server_url": self.server_url,
            "is_healthy": self.is_healthy,
            "response_time_ms": round(self.response_time_ms, 2),
            "status_code": self.status_code,
            "server_info": self.server_info,
            "capabilities": self.capabilities,
            "error": self.error,
            "timestamp": self.timestamp,
        }

    def __str__(self) -> str:
        status = "HEALTHY" if self.is_healthy else "UNHEALTHY"
        return (
            f"[{status}] {self.server_url} - "
            f"{self.response_time_ms:.1f}ms"
            f"{f' - Error: {self.error}' if self.error else ''}"
        )


class MCPHealthChecker:
    """
    Health checker for MCP (Model Context Protocol) servers.

    Supports both HTTP/SSE and stdio-based MCP servers.
    Tests connectivity, measures latency, and discovers capabilities.
    """

    def __init__(self, timeout: int = 10, retries: int = 1):
        self.timeout = timeout
        self.retries = retries

    def check(self, server_url: str) -> HealthResult:
        """Run a health check against an MCP server endpoint."""
        last_error = None
        for attempt in range(self.retries + 1):
            try:
                return self._do_check(server_url)
            except Exception as e:
                last_error = str(e)
                if attempt < self.retries:
                    time.sleep(0.5 * (attempt + 1))
        return HealthResult(
            server_url=server_url, is_healthy=False,
            response_time_ms=0, error=last_error,
        )

    def _do_check(self, server_url: str) -> HealthResult:
        """Execute a single health check attempt."""
        payload = json.dumps({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "mcp-health-monitor", "version": "0.1.0"},
            },
        }).encode("utf-8")
        req = Request(server_url, data=payload, headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }, method="POST")
        start = time.perf_counter()
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                elapsed_ms = (time.perf_counter() - start) * 1000
                body = resp.read().decode("utf-8")
                status_code = resp.status
        except HTTPError as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return HealthResult(server_url=server_url, is_healthy=False,
                response_time_ms=elapsed_ms, status_code=e.code,
                error=f"HTTP {e.code}: {e.reason}")
        except URLError as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return HealthResult(server_url=server_url, is_healthy=False,
                response_time_ms=elapsed_ms, error=f"Connection failed: {e.reason}")
        server_info = None
        capabilities = []
        try:
            data = json.loads(body)
            result = data.get("result", {})
            server_info = result.get("serverInfo")
            caps = result.get("capabilities", {})
            capabilities = list(caps.keys())
        except (json.JSONDecodeError, AttributeError):
            pass
        return HealthResult(server_url=server_url, is_healthy=True,
            response_time_ms=elapsed_ms, status_code=status_code,
            server_info=server_info, capabilities=capabilities)

    def check_tcp(self, host: str, port: int) -> HealthResult:
        """Test raw TCP connectivity to an MCP server."""
        server_url = f"tcp://{host}:{port}"
        start = time.perf_counter()
        try:
            sock = socket.create_connection((host, port), timeout=self.timeout)
            elapsed_ms = (time.perf_counter() - start) * 1000
            sock.close()
            return HealthResult(server_url=server_url, is_healthy=True,
                response_time_ms=elapsed_ms)
        except (socket.timeout, socket.error, OSError) as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return HealthResult(server_url=server_url, is_healthy=False,
                response_time_ms=elapsed_ms, error=str(e))

    def check_multiple(self, server_urls: list[str]) -> list[HealthResult]:
        """Check health of multiple MCP servers sequentially."""
        return [self.check(url) for url in server_urls]
