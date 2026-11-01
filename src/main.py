from src.checker import check_service
from src.config_loader import load_config
from src.reporter import format_result


def main():
    services = load_config("config/services.yaml")

    print(f"Checking {len(services)} services...\n")

    for service in services:
        result = check_service(service)

        print(format_result(result))
        print()


if __name__ == "__main__":
    main()