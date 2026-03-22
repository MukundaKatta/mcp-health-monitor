"""
Reporting module for MCP health check results.

Generates formatted reports in plain text, JSON, or Markdown
from health check and benchmark results.
"""

import json
import time
from typing import Union

from .checker import HealthResult
from .benchmark import BenchmarkResult


class HealthReporter:
    """Report generator for MCP health monitoring results."""

    @staticmethod
    def to_json(results, indent=2):
        """Convert results to a JSON string."""
        data = [r.to_dict() for r in results]
        return json.dumps(data, indent=indent)

    @staticmethod
    def to_markdown(results):
        """Generate a Markdown health report."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        lines = [
            "# MCP Server Health Report", "",
            f"Generated: {timestamp}", "",
            "| Server | Status | Latency (ms) | Capabilities | Error |",
            "|--------|--------|-------------|--------------|-------|",
        ]
        for r in results:
            status = "Healthy" if r.is_healthy else "Down"
            caps = ", ".join(r.capabilities) if r.capabilities else "-"
            error = r.error or "-"
            latency = f"{r.response_time_ms:.1f}" if r.response_time_ms > 0 else "-"
            lines.append(f"| {r.server_url} | {status} | {latency} | {caps} | {error} |")
        healthy = sum(1 for r in results if r.is_healthy)
        total = len(results)
        lines.extend(["", f"**Summary**: {healthy}/{total} servers healthy"])
        return "\n".join(lines)

    @staticmethod
    def to_text(results):
        """Generate a plain text health report."""
        lines = ["MCP Server Health Report", "=" * 40, ""]
        for r in results:
            lines.append(str(r))
        lines.append("")
        healthy = sum(1 for r in results if r.is_healthy)
        lines.append(f"Summary: {healthy}/{len(results)} servers healthy")
        return "\n".join(lines)

    @staticmethod
    def benchmark_comparison_table(results):
        """Generate a Markdown comparison table from benchmark results."""
        lines = [
            "# MCP Server Benchmark Comparison", "",
            "| Server | Avg (ms) | P50 (ms) | P95 (ms) | P99 (ms) | Success % | RPS |",
            "|--------|----------|----------|----------|----------|-----------|-----|",
        ]
        for r in results:
            lines.append(
                f"| {r.server_url} "
                f"| {r.avg_latency_ms:.1f} "
                f"| {r.p50_latency_ms:.1f} "
                f"| {r.p95_latency_ms:.1f} "
                f"| {r.p99_latency_ms:.1f} "
                f"| {r.success_rate * 100:.1f}% "
                f"| {r.requests_per_second:.1f} |")
        return "\n".join(lines)
