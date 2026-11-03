import pytest
import yaml

from src.config_loader import load_config


def test_load_valid_config(tmp_path):
    config_file = tmp_path / "services.yaml"

    config_file.write_text(
        """
services:
  - name: Test API
    url: https://example.com/health
    expected_status: 200
    timeout: 3
        """,
        encoding="utf-8",
    )

    services = load_config(str(config_file))

    assert len(services) == 1
    assert services[0]["name"] == "Test API"
    assert services[0]["url"] == "https://example.com/health"
    assert services[0]["expected_status"] == 200
    assert services[0]["timeout"] == 3


def test_load_config_with_default_values(tmp_path):
    config_file = tmp_path / "services.yaml"

    config_file.write_text(
        """
services:
  - name: Test API
    url: https://example.com/health
        """,
        encoding="utf-8",
    )

    services = load_config(str(config_file))

    assert services[0]["expected_status"] == 200
    assert services[0]["timeout"] == 5
    assert services[0]["contains"] is None


def test_missing_config_file():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")


def test_missing_services_section(tmp_path):
    config_file = tmp_path / "services.yaml"
    config_file.write_text(
        "name: Test API",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="services"):
        load_config(str(config_file))


def test_empty_services_list(tmp_path):
    config_file = tmp_path / "services.yaml"
    config_file.write_text(
        "services: []",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-empty list"):
        load_config(str(config_file))


def test_service_without_name(tmp_path):
    config_file = tmp_path / "services.yaml"
    config_file.write_text(
        """
services:
  - url: https://example.com
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="name"):
        load_config(str(config_file))


def test_service_without_url(tmp_path):
    config_file = tmp_path / "services.yaml"
    config_file.write_text(
        """
services:
  - name: Test API
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="URL"):
        load_config(str(config_file))


def test_invalid_yaml(tmp_path):
    config_file = tmp_path / "services.yaml"
    config_file.write_text(
        "services: [invalid",
        encoding="utf-8",
    )

    with pytest.raises(yaml.YAMLError):
        load_config(str(config_file))


def test_services_must_be_a_list(tmp_path):
    config_file = tmp_path / "services.yaml"
    config_file.write_text(
        """
services:
  name: Test API
  url: https://example.com
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="non-empty list"):
        load_config(str(config_file))