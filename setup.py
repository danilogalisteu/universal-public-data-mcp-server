#!/usr/bin/env python3
"""
Setup script for Universal Public Data MCP Server
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="universal-public-data-mcp",
    version="1.0.0",
    description="A comprehensive MCP server for accessing public data sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/universal-public-data-mcp",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="mcp, llm, ai, public-data, api, government, scientific, financial",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0",
        "aiohttp>=3.8.0",
        "requests>=2.31.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "redis>=5.0.0",
        "aioredis>=2.0.0",
        "cachetools>=5.3.0",
        "feedparser>=6.0.0",
        "beautifulsoup4>=4.12.0",
        "xmltodict>=0.13.0",
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
        "yfinance>=0.2.0",
        "structlog>=23.1.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0.0",
    ],
    extras_require={
        "whois": ["python-whois>=0.8.0"],
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.7.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "universal-public-data-mcp=server:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-org/universal-public-data-mcp/issues",
        "Source": "https://github.com/your-org/universal-public-data-mcp",
        "Documentation": "https://github.com/your-org/universal-public-data-mcp/blob/main/README.md",
    },
) 