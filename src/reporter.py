import json
from collections import Counter
from pathlib import Path


def format_result(result: dict) -> str:
    lines = [
        result["name"],
        f"Status: {result['status']}",
    ]

    if result["http_status"] is not None:
        lines.append(
            f"HTTP: {result['http_status']}"
        )

    if result["response_time_ms"] is not None:
        lines.append(
            f"Response time: {result['response_time_ms']} ms"
        )

    lines.append(
        f"Attempts: {result['attempts']}"
    )

    if result["reason"]:
        lines.append(
            f"Reason: {result['reason']}"
        )

    return "\n".join(lines)


def generate_summary(results: list[dict]) -> dict:
    status_counts = Counter(
        result["status"]
        for result in results
    )

    return {
        "total": len(results),
        "up": status_counts.get("UP", 0),
        "degraded": status_counts.get("DEGRADED", 0),
        "down": status_counts.get("DOWN", 0),
    }


def get_overall_status(summary: dict) -> str:
    if summary["down"] > 0:
        return "DOWN"

    if summary["degraded"] > 0:
        return "DEGRADED"

    return "UP"


def format_summary(summary: dict) -> str:
    return "\n".join(
        [
            "Summary",
            f"Total: {summary['total']}",
            f"UP: {summary['up']}",
            f"DEGRADED: {summary['degraded']}",
            f"DOWN: {summary['down']}",
        ]
    )


def save_json_report(
    results: list[dict],
    summary: dict,
    timestamp: str,
    duration_seconds: float,
    output_directory: str = "reports",
) -> str:
    output_path = Path(output_directory)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_path = output_path / "health-report.json"

    report = {
        "timestamp": timestamp,
        "duration_seconds": duration_seconds,
        "overall_status": get_overall_status(summary),
        "summary": summary,
        "services": results,
    }

    with open(
        report_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
        )

    return str(report_path)