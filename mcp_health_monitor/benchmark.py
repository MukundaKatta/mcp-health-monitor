"""
Benchmarking module for MCP servers.

Runs repeated health checks to measure latency distribution,
throughput, and reliability over time.
"""

import time
import statistics
from dataclasses import dataclass, field
from typing import Optional

from .checker import MCPHealthChecker, HealthResult


@dataclass
class BenchmarkResult:
    """Aggregated results from a benchmark run against an MCP server."""

    server_url: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    std_dev_ms: float
    success_rate: float
    duration_seconds: float
    requests_per_second: float
    errors: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "server_url": self.server_url,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "min_latency_ms": round(self.min_latency_ms, 2),
            "max_latency_ms": round(self.max_latency_ms, 2),
            "p50_latency_ms": round(self.p50_latency_ms, 2),
            "p95_latency_ms": round(self.p95_latency_ms, 2),
            "p99_latency_ms": round(self.p99_latency_ms, 2),
            "std_dev_ms": round(self.std_dev_ms, 2),
            "success_rate": round(self.success_rate, 4),
            "duration_seconds": round(self.duration_seconds, 2),
            "requests_per_second": round(self.requests_per_second, 2),
            "errors": self.errors,
        }

    def summary(self) -> str:
        """Return a human-readable summary of the benchmark results."""
        lines = [
            f"Benchmark Results for {self.server_url}",
            "=" * 50,
            f"Total requests:    {self.total_requests}",
            f"Successful:        {self.successful_requests}",
            f"Failed:            {self.failed_requests}",
            f"Success rate:      {self.success_rate * 100:.1f}%",
            f"Duration:          {self.duration_seconds:.2f}s",
            f"Throughput:        {self.requests_per_second:.1f} req/s",
            "",
            "Latency (ms):",
            f"  Average:         {self.avg_latency_ms:.1f}",
            f"  Min:             {self.min_latency_ms:.1f}",
            f"  Max:             {self.max_latency_ms:.1f}",
            f"  P50:             {self.p50_latency_ms:.1f}",
            f"  P95:             {self.p95_latency_ms:.1f}",
            f"  P99:             {self.p99_latency_ms:.1f}",
            f"  Std Dev:         {self.std_dev_ms:.1f}",
        ]
        if self.errors:
            lines.append("")
            lines.append(f"Errors ({len(self.errors)}):")
            for err in self.errors[:5]:
                lines.append(f"  - {err}")
            if len(self.errors) > 5:
                lines.append(f"  ... and {len(self.errors) - 5} more")
        return "\n".join(lines)


def _percentile(data, p):
    """Calculate the p-th percentile of a sorted list."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (p / 100.0)
    f = int(k)
    c = f + 1
    if c >= len(sorted_data):
        return sorted_data[f]
    return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


class MCPBenchmark:
    """Benchmark runner for MCP servers."""

    def __init__(self, num_requests=50, timeout=10, delay_between_ms=100):
        self.num_requests = num_requests
        self.timeout = timeout
        self.delay_between_ms = delay_between_ms
        self.checker = MCPHealthChecker(timeout=timeout)

    def run(self, server_url: str) -> BenchmarkResult:
        """Execute a benchmark run against an MCP server."""
        latencies = []
        errors = []
        successful = 0
        failed = 0
        start_time = time.perf_counter()
        for i in range(self.num_requests):
            result = self.checker.check(server_url)
            if result.is_healthy:
                successful += 1
                latencies.append(result.response_time_ms)
            else:
                failed += 1
                if result.error:
                    errors.append(f"Request {i + 1}: {result.error}")
            if self.delay_between_ms > 0 and i < self.num_requests - 1:
                time.sleep(self.delay_between_ms / 1000.0)
        total_duration = time.perf_counter() - start_time
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p50 = _percentile(latencies, 50)
            p95 = _percentile(latencies, 95)
            p99 = _percentile(latencies, 99)
            std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
        else:
            avg_latency = min_latency = max_latency = 0.0
            p50 = p95 = p99 = std_dev = 0.0
        return BenchmarkResult(
            server_url=server_url, total_requests=self.num_requests,
            successful_requests=successful, failed_requests=failed,
            avg_latency_ms=avg_latency, min_latency_ms=min_latency,
            max_latency_ms=max_latency, p50_latency_ms=p50,
            p95_latency_ms=p95, p99_latency_ms=p99, std_dev_ms=std_dev,
            success_rate=successful / self.num_requests if self.num_requests > 0 else 0,
            duration_seconds=total_duration,
            requests_per_second=self.num_requests / total_duration if total_duration > 0 else 0,
            errors=errors)

    def compare(self, server_urls: list[str]) -> list[BenchmarkResult]:
        """Benchmark multiple MCP servers and return results for comparison."""
        results = [self.run(url) for url in server_urls]
        results.sort(key=lambda r: r.avg_latency_ms)
        return results
