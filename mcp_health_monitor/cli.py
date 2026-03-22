"""
Command-line interface for MCP Health Monitor.

Provides a simple CLI to run health checks and benchmarks
against MCP servers from the terminal.
"""

import argparse
import json
import sys

from .checker import MCPHealthChecker
from .benchmark import MCPBenchmark
from .reporter import HealthReporter


def main():
    parser = argparse.ArgumentParser(
        prog="mcp-health-monitor",
        description="Monitor and benchmark MCP (Model Context Protocol) servers",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    check_parser = subparsers.add_parser("check", help="Run health checks")
    check_parser.add_argument("servers", nargs="+", help="MCP server URLs to check")
    check_parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    check_parser.add_argument("--retries", type=int, default=1, help="Number of retries on failure")
    check_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Output format")

    bench_parser = subparsers.add_parser("bench", help="Benchmark MCP servers")
    bench_parser.add_argument("servers", nargs="+", help="MCP server URLs to benchmark")
    bench_parser.add_argument("--requests", type=int, default=50, help="Number of requests per server")
    bench_parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    bench_parser.add_argument("--delay", type=int, default=100, help="Delay between requests in ms")
    bench_parser.add_argument("--format", choices=["text", "json", "markdown"], default="text", help="Output format")

    tcp_parser = subparsers.add_parser("tcp", help="Test TCP connectivity")
    tcp_parser.add_argument("host", help="Hostname or IP address")
    tcp_parser.add_argument("port", type=int, help="Port number")
    tcp_parser.add_argument("--timeout", type=int, default=5, help="Connection timeout in seconds")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "check":
        checker = MCPHealthChecker(timeout=args.timeout, retries=args.retries)
        results = checker.check_multiple(args.servers)
        reporter = HealthReporter()
        if args.format == "json":
            print(reporter.to_json(results))
        elif args.format == "markdown":
            print(reporter.to_markdown(results))
        else:
            print(reporter.to_text(results))
        if not all(r.is_healthy for r in results):
            sys.exit(1)

    elif args.command == "bench":
        bench = MCPBenchmark(
            num_requests=args.requests, timeout=args.timeout,
            delay_between_ms=args.delay)
        if len(args.servers) > 1:
            results = bench.compare(args.servers)
            reporter = HealthReporter()
            if args.format == "json":
                print(reporter.to_json(results))
            elif args.format == "markdown":
                print(reporter.benchmark_comparison_table(results))
            else:
                for r in results:
                    print(r.summary())
                    print()
        else:
            result = bench.run(args.servers[0])
            if args.format == "json":
                print(json.dumps(result.to_dict(), indent=2))
            else:
                print(result.summary())

    elif args.command == "tcp":
        checker = MCPHealthChecker(timeout=args.timeout)
        result = checker.check_tcp(args.host, args.port)
        print(result)
        if not result.is_healthy:
            sys.exit(1)


if __name__ == "__main__":
    main()
