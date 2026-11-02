import time

import requests


SLOW_RESPONSE_THRESHOLD_MS = 500
MAX_ATTEMPTS = 3


def build_result(
    service: dict,
    status: str,
    http_status=None,
    response_time_ms=None,
    reason=None,
    attempts=1,
) -> dict:
    return {
        "name": service["name"],
        "url": service["url"],
        "status": status,
        "http_status": http_status,
        "response_time_ms": response_time_ms,
        "reason": reason,
        "attempts": attempts,
    }


def check_service(service: dict) -> dict:
    url = service["url"]
    expected_status = service["expected_status"]
    timeout = service["timeout"]
    expected_content = service.get("contains")

    last_reason = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        start_time = time.perf_counter()

        try:
            response = requests.get(
                url,
                timeout=timeout,
            )

            response_time_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            if response.status_code == expected_status:
                if (
                    expected_content
                    and expected_content not in response.text
                ):
                    return build_result(
                        service=service,
                        status="DOWN",
                        http_status=response.status_code,
                        response_time_ms=response_time_ms,
                        reason=(
                            "Expected response content not found: "
                            f"'{expected_content}'"
                        ),
                        attempts=attempt,
                    )

                if response_time_ms > SLOW_RESPONSE_THRESHOLD_MS:
                    return build_result(
                        service=service,
                        status="DEGRADED",
                        http_status=response.status_code,
                        response_time_ms=response_time_ms,
                        reason=(
                            "Response time exceeded "
                            f"{SLOW_RESPONSE_THRESHOLD_MS} ms"
                        ),
                        attempts=attempt,
                    )

                return build_result(
                    service=service,
                    status="UP",
                    http_status=response.status_code,
                    response_time_ms=response_time_ms,
                    attempts=attempt,
                )

            if 500 <= response.status_code < 600:
                last_reason = (
                    "Server error "
                    f"(expected {expected_status}, "
                    f"received {response.status_code})"
                )

                if attempt < MAX_ATTEMPTS:
                    continue

                return build_result(
                    service=service,
                    status="DOWN",
                    http_status=response.status_code,
                    response_time_ms=response_time_ms,
                    reason=last_reason,
                    attempts=attempt,
                )

            return build_result(
                service=service,
                status="DOWN",
                http_status=response.status_code,
                response_time_ms=response_time_ms,
                reason=(
                    "Unexpected status code "
                    f"(expected {expected_status}, "
                    f"received {response.status_code})"
                ),
                attempts=attempt,
            )

        except requests.Timeout:
            last_reason = "Connection timeout"

        except requests.ConnectionError:
            last_reason = "Connection failed"

        except requests.RequestException as error:
            return build_result(
                service=service,
                status="DOWN",
                reason=f"Request failed: {error}",
                attempts=attempt,
            )

        if attempt == MAX_ATTEMPTS:
            return build_result(
                service=service,
                status="DOWN",
                reason=last_reason,
                attempts=attempt,
            )

    return build_result(
        service=service,
        status="DOWN",
        reason=last_reason or "Unknown error",
        attempts=MAX_ATTEMPTS,
    )