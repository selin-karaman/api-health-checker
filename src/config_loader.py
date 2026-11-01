from pathlib import Path

import yaml


def load_config(file_path: str) -> list[dict]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config file not found: {file_path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Config path is not a file: {file_path}"
        )

    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not data or "services" not in data:
        raise ValueError(
            "Config must contain a 'services' section."
        )

    services = data["services"]

    if not isinstance(services, list) or not services:
        raise ValueError(
            "'services' must be a non-empty list."
        )

    for service in services:
        if not isinstance(service, dict):
            raise ValueError(
                "Each service must be a YAML object."
            )

        if not service.get("name"):
            raise ValueError(
                "Each service must have a name."
            )

        if not service.get("url"):
            raise ValueError(
                f"Service '{service['name']}' must have a URL."
            )

        service.setdefault("expected_status", 200)
        service.setdefault("timeout", 5)

    return services