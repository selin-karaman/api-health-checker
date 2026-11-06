# API Health Checker

A lightweight Python-based API health monitoring tool that checks service availability, validates HTTP responses, measures response times, and generates JSON health reports.

The application uses a YAML configuration file to define monitored services and provides a command-line interface for running health checks.

## Features

- **YAML-based Configuration:** Define monitored services and their expected responses in a YAML file.
- **HTTP Health Checks:** Send HTTP requests and verify service availability.
- **Status Classification:** Categorize services as `UP`, `DEGRADED`, or `DOWN`.
- **Retry Mechanism:** Retry failed requests to handle temporary connection and server errors.
- **Response Validation:** Validate HTTP status codes and expected response content.
- **Response Time Measurement:** Measure and report service response times.
- **JSON Reporting:** Generate structured JSON reports containing individual service results and an overall health summary.
- **CLI Exit Codes:** Return different exit codes depending on the execution result.
- **Automated Testing:** Verify application behavior using pytest.
- **Continuous Integration:** Automatically run tests through GitHub Actions on pushes and pull requests.

## Project Structure

```text
api-health-checker/
├── .github/
│   └── workflows/
│       └── ci.yml
├── config/
│   └── services.yaml
├── reports/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── checker.py
│   ├── config_loader.py
│   ├── main.py
│   └── reporter.py
├── tests/
│   ├── test_checker.py
│   ├── test_config_loader.py
│   ├── test_main.py
│   └── test_reporter.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/selin-karaman/api-health-checker.git
cd api-health-checker
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

Activate the virtual environment:

**macOS / Linux**

```bash
source .venv/bin/activate
```

**Windows**

```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run Health Checks

Run the application using the default service configuration:

```bash
python -m src.main config/services.yaml
```

You can also specify a custom output directory:

```bash
python -m src.main config/services.yaml --output reports
```

To see available command-line options:

```bash
python -m src.main --help
```

## Service Statuses

The application classifies monitored services into three health states:

| Status | Description |
|---|---|
| UP | The service responds as expected. |
| DEGRADED | The service is available but does not fully meet the configured health criteria. |
| DOWN | The service is unavailable or fails the configured health checks. |

The overall application status is determined by the health results of all monitored services.

## JSON Reports

After each execution, the application generates a JSON report in the configured output directory.

The report includes:

- Execution timestamp in UTC
- Total execution duration
- Overall health status
- Service summary
- Individual service results
- HTTP status codes
- Response times
- Failure reasons
- Number of request attempts

Example report structure:

```json
{
  "timestamp": "2026-11-05T07:18:24.941955+00:00",
  "duration_seconds": 1.792,
  "overall_status": "DOWN",
  "summary": {
    "total": 5,
    "up": 3,
    "degraded": 0,
    "down": 2
  },
  "services": [
    {
      "name": "JSONPlaceholder",
      "url": "https://jsonplaceholder.typicode.com/posts/1",
      "status": "UP",
      "http_status": 200,
      "response_time_ms": 304.61,
      "reason": null,
      "attempts": 1
    }
  ]
}
```

The example illustrates the report structure. Actual results depend on service availability and configuration.

## CLI Exit Codes

The application uses exit codes to indicate the execution result:

| Exit Code | Meaning |
|---|---|
| 0 | All monitored services are UP. |
| 1 | At least one service is DEGRADED or DOWN. |
| 2 | Configuration file is missing or invalid, or command-line arguments are invalid. |

These exit codes make the application suitable for integration into automated scripts and CI/CD pipelines.

## Running Tests

Run the complete test suite with:

```bash
python -m pytest -v
```

The test suite covers:

- HTTP health-check behavior
- Retry handling and response validation
- YAML configuration loading and validation
- Status classification and summary generation
- JSON report generation
- CLI execution and exit codes

**Current test coverage:** 36 passing tests.

## Continuous Integration

The project uses GitHub Actions to automate testing.

The CI workflow is triggered by:

- Pushes to the `main` branch
- Pull requests targeting the `main` branch

The workflow sets up Python, installs project dependencies, and executes the complete pytest suite.

## Key Learning Outcomes

- Building a modular Python CLI application
- Working with HTTP requests and API response validation
- Implementing retry logic and error handling
- Managing application configuration with YAML
- Generating structured JSON reports
- Using exit codes for automation and process integration
- Writing unit tests with pytest
- Implementing automated testing with GitHub Actions
- Organizing a maintainable Python project structure

