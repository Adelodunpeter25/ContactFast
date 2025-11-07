"""
Rate limiting utilities.

In-memory rate limiting implementation for IP addresses and domains.
"""

from datetime import datetime, timedelta

# Rate limiting storage
rate_limit_store: dict[str, list[datetime]] = {}


def check_rate_limit(key: str, limit: int, window_minutes: int) -> bool:
    """
    Check if a key is within rate limit.

    Args:
        key: Unique identifier (e.g., 'ip_192.168.1.1', 'domain_example.com')
        limit: Maximum number of requests allowed
        window_minutes: Time window in minutes

    Returns:
        bool: True if within limit, False if exceeded
    """
    now = datetime.utcnow()
    if key not in rate_limit_store:
        rate_limit_store[key] = []

    # Remove old entries
    rate_limit_store[key] = [
        timestamp
        for timestamp in rate_limit_store[key]
        if now - timestamp < timedelta(minutes=window_minutes)
    ]

    if len(rate_limit_store[key]) >= limit:
        return False

    rate_limit_store[key].append(now)
    return True
