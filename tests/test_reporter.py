import json

import pytest

from src.reporter import (
    format_result,
    generate_summary,
    get_overall_status,
    format_summary,
    save_json_report,
)


def sample_results():
    return [
        {
            "name": "API One",
            "url": "https://example.com/one",
            "status": "UP",
            "http_status": 200,
            "response_time_ms": 120.5,
            "reason": None,
            "attempts": 1,
        },
        {
            "name": "API Two",
            "url": "https://example.com/two",
            "status": "DEGRADED",
            "http_status": 200,
            "response_time_ms": 650.0,
            "reason": "Response time exceeded 500 ms",
            "attempts": 1,
        },
        {
            "name": "API Three",
            "url": "https://example.com/three",
            "status": "DOWN",
            "http_status": 503,
            "response_time_ms": 200.0,
            "reason": "Server error",
            "attempts": 3,
        },
    ]


def test_format_result():
    result = sample_results()[0]

    output = format_result(result)

    assert "API One" in output
    assert "Status: UP" in output
    assert "HTTP: 200" in output
    assert "Response time: 120.5 ms" in output
    assert "Attempts: 1" in output


def test_format_result_without_http_status():
    result = sample_results()[2]
    result["http_status"] = None
    result["response_time_ms"] = None

    output = format_result(result)

    assert "Status: DOWN" in output
    assert "HTTP:" not in output
    assert "Response time:" not in output


def test_generate_summary():
    summary = generate_summary(sample_results())

    assert summary == {
        "total": 3,
        "up": 1,
        "degraded": 1,
        "down": 1,
    }


def test_generate_summary_with_empty_results():
    summary = generate_summary([])

    assert summary == {
        "total": 0,
        "up": 0,
        "degraded": 0,
        "down": 0,
    }


def test_get_overall_status_when_all_services_are_up():
    summary = {
        "total": 3,
        "up": 3,
        "degraded": 0,
        "down": 0,
    }

    assert get_overall_status(summary) == "UP"


def test_get_overall_status_when_service_is_degraded():
    summary = {
        "total": 3,
        "up": 2,
        "degraded": 1,
        "down": 0,
    }

    assert get_overall_status(summary) == "DEGRADED"


def test_get_overall_status_when_service_is_down():
    summary = {
        "total": 3,
        "up": 1,
        "degraded": 1,
        "down": 1,
    }

    assert get_overall_status(summary) == "DOWN"


def test_get_overall_status_prioritizes_down():
    summary = {
        "total": 3,
        "up": 1,
        "degraded": 1,
        "down": 1,
    }

    assert get_overall_status(summary) == "DOWN"


def test_format_summary():
    summary = generate_summary(sample_results())

    output = format_summary(summary)

    assert "Total: 3" in output
    assert "UP: 1" in output
    assert "DEGRADED: 1" in output
    assert "DOWN: 1" in output


def test_save_json_report(tmp_path):
    results = sample_results()
    summary = generate_summary(results)

    report_path = save_json_report(
        results,
        summary,
        timestamp="2026-11-04T18:30:00+00:00",
        duration_seconds=2.456,
        output_directory=str(tmp_path / "reports"),
    )

    with open(report_path, encoding="utf-8") as file:
        report = json.load(file)

    assert report["timestamp"] == "2026-11-04T18:30:00+00:00"
    assert report["duration_seconds"] == 2.456
    assert report["overall_status"] == "DOWN"
    assert report["summary"] == summary
    assert len(report["services"]) == 3
    assert report["services"][0]["name"] == "API One"


def test_save_json_report_creates_directory(tmp_path):
    output_directory = tmp_path / "new_reports"

    save_json_report(
        [],
        generate_summary([]),
        timestamp="2026-11-04T18:30:00+00:00",
        duration_seconds=0.0,
        output_directory=str(output_directory),
    )

    assert output_directory.exists()
    assert (output_directory / "health-report.json").exists()