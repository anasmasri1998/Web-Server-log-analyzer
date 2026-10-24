"""Aggregate web access requests into a useful report."""
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from .parser import parse_line


def analyze_file(path: Path, top: int = 5) -> dict:
    """Analyze a file one line at a time to limit memory use."""
    paths, ips, hours, statuses, methods = (Counter() for _ in range(5))
    total = malformed = not_found = server_errors = bytes_sent = 0
    first: datetime | None = None
    last: datetime | None = None

    with path.open('r', encoding='utf-8-sig', errors='replace') as stream:
        for line in stream:
            if not line.strip():
                continue
            try:
                entry = parse_line(line)
            except ValueError:
                malformed += 1
                continue
            total += 1
            # Paths are counted without query strings to group equivalent pages.
            page = urlsplit(entry.path).path or '/'
            paths[page] += 1
            ips[entry.ip] += 1
            hours[entry.timestamp.strftime('%Y-%m-%d %H:00 %z')] += 1
            statuses[str(entry.status)] += 1
            methods[entry.method] += 1
            bytes_sent += entry.size
            if entry.status == 404:
                not_found += 1
            if 500 <= entry.status <= 599:
                server_errors += 1
            # Compare timestamps as timezone-aware datetime objects.
            first = entry.timestamp if first is None or entry.timestamp < first else first
            last = entry.timestamp if last is None or entry.timestamp > last else last

    duration_seconds = (last - first).total_seconds() if first and last else 0
    return {
        'file': str(path),
        'total_requests': total,
        'malformed_lines': malformed,
        'not_found_404': not_found,
        'server_errors_5xx': server_errors,
        'bytes_sent': bytes_sent,
        'first_request': first.isoformat() if first else None,
        'last_request': last.isoformat() if last else None,
        'average_requests_per_minute': round(total / (duration_seconds / 60), 2) if duration_seconds > 0 else None,
        'top_pages': paths.most_common(top),
        'top_ips': ips.most_common(top),
        'busiest_hours': hours.most_common(top),
        'status_codes': dict(sorted(statuses.items())),
        'http_methods': dict(sorted(methods.items())),
    }
