"""Benchmark example: Compare latency across MCP servers."""

from mcp_health_monitor import MCPBenchmark
from mcp_health_monitor.reporter import HealthReporter


def main():
    bench = MCPBenchmark(num_requests=20, timeout=10, delay_between_ms=50)
    servers = [
        "http://localhost:3000/mcp",
        "http://localhost:8080/mcp",
    ]
    print("Benchmarking MCP servers...\n")
    results = bench.compare(servers)
    for result in results:
        print(result.summary())
        print()
    reporter = HealthReporter()
    print(reporter.benchmark_comparison_table(results))


if __name__ == "__main__":
    main()
