from setuptools import setup, find_packages

setup(
    name="mcp-health-monitor",
    version="0.1.0",
    description="Monitor, test, and benchmark MCP (Model Context Protocol) servers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Mukunda Katta",
    author_email="mukunda.vjcs6@gmail.com",
    url="https://github.com/MukundaKatta/mcp-health-monitor",
    packages=find_packages(),
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "mcp-health-monitor=mcp_health_monitor.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Monitoring",
    ],
)
