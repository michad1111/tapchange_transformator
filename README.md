# Student Task Service

A Python-based service for the VU "Informationstechnik in Smart Grids" course exercise. This service implements a control algorithm for voltage regulation in a simulated power grid environment.

## Features

- Voltage monitoring and control
- Tap changer position management
- Spreading control implementation
- Range control factor adjustment
- Real-time communication with simulator
- FastAPI-based REST endpoints

## Prerequisites

- Python 3.12 or higher
- uv (Python package manager) or pip

## Installation

### Option 1: Using uv (Recommended)

1. Install uv if you haven't already:

   ```bash
   pip install uv
   ```

2. Install dependencies:

   ```bash
   uv sync
   ```

### Option 2: Using plain pip

Install dependencies directly:

```bash
pip install -r requirements.txt
```

## Running the Service

### Using uv

```bash
uv run studenttask
```

### Using plain Python

```bash
python -m studenttask
```

The service will start on `http://localhost:7777`

## Project Structure

- `studenttask/` - Main package directory
  - `StudentTask.py` - Core control algorithm implementation
  - `api_client.py` - API client for simulator communication
  - `eSteps.py` - Enumeration for tap changer control steps

## Configuration

The service can be configured using the following environment variables:

- `SIMULATOR_URL` - URL of the simulator service (default: <http://localhost:8000>)
- `STUDENTTASK_URL` - URL of this service (default: <http://localhost:7777>)

## Testing

Run the test suite using pytest:

### Using uv

```bash
uv run pytest
```

### Using plain Python

```bash
pytest
```

### Test Coverage

To run tests with coverage report:

#### Using uv

```bash
uv run pytest --cov=studenttask
```

#### Using plain Python

```bash
pytest --cov=studenttask
```

### Available Test Suites

The project includes the following test categories:

- Unit tests for the StudentTask class
  - Normal operation scenarios

### Test Configuration

Tests are configured using pytest markers and fixtures. The test configuration can be found in `pyproject.toml` under the `[tool.pytest.ini_options]` section.

### Running Specific Tests

To run a specific test category:

```bash
# Using uv
uv run pytest -m unit

# Using plain Python
pytest -m unit
```

To run a specific test file:

```bash
# Using uv
uv run pytest tests/test_studenttask.py

# Using plain Python
pytest tests/test_studenttask.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- Dominic Hoffmann <dominic.hoffmann@tuwien.ac.at>
- Denis Vystaukin <denis.vystaukin@tuwien.ac.at>
