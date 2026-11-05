import argparse
from datetime import datetime, timezone
from time import perf_counter

from src.checker import check_service
from src.config_loader import load_config
from src.reporter import (
    format_result,
    format_summary,
    generate_summary,
    save_json_report,
)


def main():
    parser = argparse.ArgumentParser(
        description="Check the health of API endpoints."
    )

    parser.add_argument(
        "config",
        help="Path to the YAML service configuration file",
    )

    parser.add_argument(
        "--output",
        default="reports",
        help="Directory where the JSON report will be saved",
    )

    args = parser.parse_args()

    timestamp = datetime.now(timezone.utc).isoformat()
    start_time = perf_counter()

    try:
        services = load_config(args.config)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return 2

    print(f"Checking {len(services)} services...\n")

    results = []

    for service in services:
        result = check_service(service)
        results.append(result)

        print(format_result(result))
        print()

    summary = generate_summary(results)

    print(format_summary(summary))

    duration_seconds = round(
        perf_counter() - start_time,
        3,
    )

    report_path = save_json_report(
        results,
        summary,
        timestamp=timestamp,
        duration_seconds=duration_seconds,
        output_directory=args.output,
    )

    print(f"\nReport saved: {report_path}")

    if summary["up"] == summary["total"]:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())