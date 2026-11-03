from unittest.mock import Mock, patch

import requests

from src.checker import check_service


def get_service():
    return {
        "name": "Test API",
        "url": "https://example.com/health",
        "expected_status": 200,
        "timeout": 3,
        "contains": None,
    }


@patch("src.checker.requests.get")
def test_service_is_up(mock_get):
    response = Mock()
    response.status_code = 200
    response.text = "healthy"

    mock_get.return_value = response

    with patch(
        "src.checker.time.perf_counter",
        side_effect=[0, 0.2],
    ):
        result = check_service(get_service())

    assert result["status"] == "UP"
    assert result["http_status"] == 200
    assert result["attempts"] == 1
    assert result["reason"] is None


@patch("src.checker.requests.get")
def test_service_is_degraded_when_slow(mock_get):
    response = Mock()
    response.status_code = 200
    response.text = "healthy"

    mock_get.return_value = response

    with patch(
        "src.checker.time.perf_counter",
        side_effect=[0, 0.8],
    ):
        result = check_service(get_service())

    assert result["status"] == "DEGRADED"
    assert result["http_status"] == 200
    assert result["attempts"] == 1
    assert "Response time exceeded" in result["reason"]


@patch("src.checker.requests.get")
def test_unexpected_status_returns_down(mock_get):
    response = Mock()
    response.status_code = 404
    response.text = ""

    mock_get.return_value = response

    with patch(
        "src.checker.time.perf_counter",
        side_effect=[0, 0.2],
    ):
        result = check_service(get_service())

    assert result["status"] == "DOWN"
    assert result["http_status"] == 404
    assert result["attempts"] == 1
    assert "Unexpected status code" in result["reason"]


@patch("src.checker.requests.get")
def test_missing_expected_content_returns_down(mock_get):
    service = get_service()
    service["contains"] = "healthy"

    response = Mock()
    response.status_code = 200
    response.text = "service running"

    mock_get.return_value = response

    with patch(
        "src.checker.time.perf_counter",
        side_effect=[0, 0.2],
    ):
        result = check_service(service)

    assert result["status"] == "DOWN"
    assert result["http_status"] == 200
    assert result["attempts"] == 1
    assert "Expected response content not found" in result["reason"]


@patch("src.checker.requests.get")
def test_timeout_retries_three_times(mock_get):
    mock_get.side_effect = requests.Timeout

    result = check_service(get_service())

    assert result["status"] == "DOWN"
    assert result["attempts"] == 3
    assert result["reason"] == "Connection timeout"
    assert mock_get.call_count == 3


@patch("src.checker.requests.get")
def test_connection_error_retries_three_times(mock_get):
    mock_get.side_effect = requests.ConnectionError

    result = check_service(get_service())

    assert result["status"] == "DOWN"
    assert result["attempts"] == 3
    assert result["reason"] == "Connection failed"
    assert mock_get.call_count == 3


@patch("src.checker.requests.get")
def test_server_error_retries_three_times(mock_get):
    response = Mock()
    response.status_code = 503
    response.text = ""

    mock_get.return_value = response

    with patch(
        "src.checker.time.perf_counter",
        side_effect=[
            0, 0.2,
            1, 1.2,
            2, 2.2,
        ],
    ):
        result = check_service(get_service())

    assert result["status"] == "DOWN"
    assert result["http_status"] == 503
    assert result["attempts"] == 3
    assert "Server error" in result["reason"]
    assert mock_get.call_count == 3