# mcp-health-monitor

A lightweight Python toolkit to monitor, test, and benchmark [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) servers. Zero external dependencies - built entirely on the Python standard library.

As the MCP ecosystem grows rapidly with thousands of servers powering AI agent workflows, keeping those servers healthy and performant is critical. **mcp-health-monitor** gives you the tools to do exactly that.

## Features

- **Health Checks** - Send MCP initialize handshakes and validate server responses
- **TCP Connectivity** - Test raw TCP reachability before attempting MCP handshakes
- **Latency Benchmarks** - Measure P50/P95/P99 latency with configurable request counts
- **Multi-Server Comparison** - Benchmark multiple servers side by side
- **Multiple Output Formats** - Text, JSON, and Markdown reports
- **CLI Tool** - Run checks and benchmarks directly from the terminal
- **CI/CD Ready** - Non-zero exit codes when servers are unhealthy
- **Zero Dependencies** - Uses only Python standard library modules

## Installation

```bash
pip install -e .
```

Or just copy the `mcp_health_monitor` package into your project.

## Quick Start

### Python API

```python
from mcp_health_monitor import MCPHealthChecker, HealthReporter

# Check server health
checker = MCPHealthChecker(timeout=5, retries=2)
results = checker.check_multiple([
    "http://localhost:3000/mcp",
    "http://localhost:8080/mcp",
])

# Generate a report
reporter = HealthReporter()
print(reporter.to_markdown(results))
```

### Benchmarking

```python
from mcp_health_monitor import MCPBenchmark

bench = MCPBenchmark(num_requests=100, delay_between_ms=50)
result = bench.run("http://localhost:3000/mcp")
print(result.summary())

# Compare multiple servers
results = bench.compare([
    "http://localhost:3000/mcp",
    "http://localhost:8080/mcp",
])
```

### CLI Usage

```bash
# Health check
mcp-health-monitor check http://localhost:3000/mcp --format markdown

# Check multiple servers
mcp-health-monitor check http://localhost:3000/mcp http://localhost:8080/mcp

# Benchmark a server
mcp-health-monitor bench http://localhost:3000/mcp --requests 100

# Compare servers
mcp-health-monitor bench http://localhost:3000/mcp http://localhost:8080/mcp --format markdown

# TCP connectivity test
mcp-health-monitor tcp localhost 3000
```

## Example Output

### Health Check

```
MCP Server Health Report
========================================

[HEALTHY] http://localhost:3000/mcp - 45.2ms
[UNHEALTHY] http://localhost:8080/mcp - 0.0ms - Error: Connection refused

Summary: 1/2 servers healthy
```

### Benchmark

```
Benchmark Results for http://localhost:3000/mcp
==================================================
Total requests:    50
Successful:        50
Failed:            0
Success rate:      100.0%
Duration:          7.82s
Throughput:        6.4 req/s

Latency (ms):
  Average:         42.3
  Min:             38.1
  Max:             89.4
  P50:             41.2
  P95:             52.8
  P99:             85.1
  Std Dev:         7.2
```

## Project Structure

```
mcp-health-monitor/
  mcp_health_monitor/
    __init__.py       # Package exports
    checker.py        # Core health checking logic
    benchmark.py      # Benchmarking and latency measurement
    reporter.py       # Report generation (text, JSON, Markdown)
    cli.py            # Command-line interface
  examples/
    quick_check.py    # Basic health check example
    benchmark_servers.py  # Benchmarking example
  setup.py
  requirements.txt
  LICENSE
  README.md
```

## Use Cases

- **CI/CD Pipelines** - Verify MCP servers are healthy before deploying agent workflows
- **Production Monitoring** - Periodic health checks with alerting on failures
- **Server Comparison** - Evaluate latency and reliability across MCP implementations
- **Development** - Quickly test MCP servers during local development
- **Load Testing** - Measure server performance under sustained request patterns

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
