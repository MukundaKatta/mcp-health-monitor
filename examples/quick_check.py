"""Quick example: Check health of MCP servers."""

from mcp_health_monitor import MCPHealthChecker, HealthReporter


def main():
    checker = MCPHealthChecker(timeout=5, retries=2)
    servers = [
        "http://localhost:3000/mcp",
        "http://localhost:8080/mcp",
    ]
    print("Checking MCP server health...\n")
    results = checker.check_multiple(servers)
    reporter = HealthReporter()
    print(reporter.to_text(results))
    print()
    print("--- Markdown Report ---")
    print(reporter.to_markdown(results))


if __name__ == "__main__":
    main()
