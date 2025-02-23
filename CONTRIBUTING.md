# Contributing to CrewAI MCP Adapter

Thank you for your interest in contributing to CrewAI MCP Adapter! This document will guide you through the setup process and development workflow.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/dshivendra/crewai_mcp_adapter.git
cd crewai_mcp_adapter
```

2. Install dependencies:
```bash
pip install -e ".[test,docs]"
```

## Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_basic_adapter.py -v

# Run tests with asyncio support
pytest tests/ -v --asyncio-mode=strict
```

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure tests pass
3. Update documentation if needed
4. Create a pull request

## Documentation

To build the documentation locally:

```bash
mkdocs serve
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints for function parameters and return types
- Write docstrings for classes and functions
- Ensure new features have corresponding tests

## Publishing

Publishing is handled automatically by GitHub Actions when a new tag is pushed. To create a new release:

1. Update version in pyproject.toml
2. Create and push a new tag:
```bash
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin vX.Y.Z
```

## Need Help?

If you have questions or need help, feel free to:
- Open an issue
- Create a discussion
- Contact the maintainers
