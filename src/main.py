import argparse

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

    try:
        services = load_config(args.config)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}")
        return

    print(f"Checking {len(services)} services...\n")

    results = []

    for service in services:
        result = check_service(service)
        results.append(result)

        print(format_result(result))
        print()

    summary = generate_summary(results)

    print(format_summary(summary))

    report_path = save_json_report(
        results,
        summary,
        output_directory=args.output,
    )

    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    main()