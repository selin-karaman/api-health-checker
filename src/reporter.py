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