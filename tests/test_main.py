import sys
from datetime import datetime, timedelta

import pytest

import src.main as main_module


def setup_mock_dependencies(monkeypatch, status="UP"):
    services = [{"name": "Test API", "url": "https://example.com"}]

    result = {
        "name": "Test API",
        "url": "https://example.com",
        "status": status,
        "http_status": 200,
        "response_time_ms": 120.5,
        "reason": None,
        "attempts": 1,
    }

    saved_data = {}

    monkeypatch.setattr(
        main_module,
        "load_config",
        lambda config_path: services,
    )
    monkeypatch.setattr(
        main_module,
        "check_service",
        lambda service: result,
    )
    monkeypatch.setattr(
        main_module,
        "format_result",
        lambda result: f"Test API - {result['status']}",
    )
    monkeypatch.setattr(
        main_module,
        "generate_summary",
        lambda results: {
            "total": 1,
            "up": 1 if status == "UP" else 0,
            "degraded": 1 if status == "DEGRADED" else 0,
            "down": 1 if status == "DOWN" else 0,
        },
    )
    monkeypatch.setattr(
        main_module,
        "format_summary",
        lambda summary: (
            f"Total: {summary['total']} | "
            f"UP: {summary['up']} | "
            f"DEGRADED: {summary['degraded']} | "
            f"DOWN: {summary['down']}"
        ),
    )

    def mock_save_json_report(
        results,
        summary,
        timestamp,
        duration_seconds,
        output_directory,
    ):
        saved_data["results"] = results
        saved_data["summary"] = summary
        saved_data["timestamp"] = timestamp
        saved_data["duration_seconds"] = duration_seconds
        saved_data["output_directory"] = output_directory

        return f"{output_directory}/health-report.json"

    monkeypatch.setattr(
        main_module,
        "save_json_report",
        mock_save_json_report,
    )

    return saved_data


def test_main_runs_successfully(monkeypatch, capsys):
    saved_data = setup_mock_dependencies(monkeypatch)

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "config/services.yaml", "--output", "custom_reports"],
    )

    exit_code = main_module.main()

    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Checking 1 services" in output
    assert "Test API - UP" in output
    assert "Total: 1 | UP: 1" in output
    assert "Report saved: custom_reports/health-report.json" in output
    assert saved_data["output_directory"] == "custom_reports"


def test_main_uses_default_output_directory(monkeypatch):
    saved_data = setup_mock_dependencies(monkeypatch)

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "config/services.yaml"],
    )

    exit_code = main_module.main()

    assert exit_code == 0
    assert saved_data["output_directory"] == "reports"


@pytest.mark.parametrize(
    "status",
    ["DEGRADED", "DOWN"],
)
def test_main_returns_one_when_service_is_unhealthy(
    monkeypatch,
    status,
):
    setup_mock_dependencies(monkeypatch, status=status)

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "config/services.yaml"],
    )

    exit_code = main_module.main()

    assert exit_code == 1


@pytest.mark.parametrize(
    "error",
    [
        FileNotFoundError("Configuration file not found"),
        ValueError("Invalid configuration"),
    ],
)
def test_main_handles_config_errors(monkeypatch, capsys, error):
    saved_data = setup_mock_dependencies(monkeypatch)

    def mock_load_config(config_path):
        raise error

    monkeypatch.setattr(
        main_module,
        "load_config",
        mock_load_config,
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "invalid.yaml"],
    )

    exit_code = main_module.main()

    output = capsys.readouterr().out

    assert exit_code == 2
    assert f"Error: {error}" in output
    assert "Checking" not in output
    assert saved_data == {}


def test_main_displays_help(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--help"],
    )

    with pytest.raises(SystemExit) as exception:
        main_module.main()

    output = capsys.readouterr().out

    assert exception.value.code == 0
    assert "Check the health of API endpoints" in output
    assert "--output" in output


def test_main_generates_utc_timestamp(monkeypatch):
    saved_data = setup_mock_dependencies(monkeypatch)

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "config/services.yaml"],
    )

    main_module.main()

    timestamp = datetime.fromisoformat(saved_data["timestamp"])

    assert timestamp.tzinfo is not None
    assert timestamp.utcoffset() == timedelta(0)


def test_main_records_duration(monkeypatch):
    saved_data = setup_mock_dependencies(monkeypatch)

    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "config/services.yaml"],
    )

    main_module.main()

    assert isinstance(saved_data["duration_seconds"], float)
    assert saved_data["duration_seconds"] >= 0