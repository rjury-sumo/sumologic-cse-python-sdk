# sumologic-cse-python-sdk

A Python SDK for the Sumo Logic Cloud SIEM (CSE) API. This client provides useful functionality for common Cloud SIEM use cases rather than being a comprehensive API client.

**API Documentation**: https://api.sumologic.com/docs/sec/#

## Requirements

- Python 3.9 or higher
- Sumo Logic Cloud SIEM access credentials

## Installation

### Using pip
```bash
pip install sumologiccse
```

### Using uv (recommended for development)
```bash
uv add sumologiccse
```

## Getting Started

See the scripts section for examples. Configure your credentials using either:

**Environment Variables:**
```bash
export SUMO_ACCESS_ID="your_access_id"
export SUMO_ACCESS_KEY="your_access_key"
```

**Or provide as arguments when creating the client.**

## Endpoints

See: https://help.sumologic.com/docs/api/getting-started/#which-endpoint-should-i-should-use

The default endpoint is: https://api.sumologic.com/docs/sec  
Using `--endpoint 'prod'` or `'us1'` will also resolve to this value.

For other endpoints, use the short form name:
```bash
--endpoint 'us2'
--endpoint 'au' 
--endpoint 'in'
```

## Usage

### Create a Connection
```python
from sumologiccse.sumologiccse import SumoLogicCSE

# Using environment variables
cse = SumoLogicCSE(endpoint='us2')

# Or with explicit credentials
cse = SumoLogicCSE(
    endpoint='us2',
    access_id='your_access_id',
    access_key='your_access_key'
)
```

### Query Insights
```python
q = '-status:"closed" created:>2022-11-17T00:00:00+00:00'
insights = cse.get_insights(q=q)
```

### Direct API Calls
You can call any API endpoint directly:
```python
statuses = cse.get('/insight-status')
```

## Development Setup

### Using uv (recommended)
```bash
# Clone the repository
git clone https://github.com/rjury-sumo/sumologic-cse-python-sdk.git
cd sumologic-cse-python-sdk

# Install with development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code
uv run black .

# Lint code  
uv run ruff check .

# Type checking
uv run mypy src/
```

### Using traditional pip
```bash
pip install -e ".[dev]"
pytest
black .
ruff check .
mypy src/
```

### Publishing (for maintainers)
```bash
# Build the package
uv run python -m build

# Upload to PyPI (requires credentials)
uv run twine upload dist/*

# Upload to Test PyPI first (recommended)
uv run twine upload --repository testpypi dist/*
```

## Example Use Case Scripts

Find example scripts in `./scripts/`:
- [Insights scripts readme](scripts/insights/readme.md)


## Docker

Build the Docker image:
```bash
docker build -t sumocse-test .
```

Run with environment variables:
```bash
docker run -it \
  -e SUMO_ACCESS_ID="$SUMO_ACCESS_ID" \
  -e SUMO_ACCESS_KEY="$SUMO_ACCESS_KEY" \
  sumocse-test bash
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite: `uv run pytest`
5. Format code: `uv run black .`
6. Lint code: `uv run ruff check .`
7. Submit a pull request

## TODOs

- Add comprehensive endpoint coverage
- Expand unit and integration test suite
- Add async support
- Improve error handling and logging