"""Command-line interface for access-log analysis."""
import argparse
import json
import sys
from pathlib import Path

from .analyzer import analyze_file


def render_text(data: dict) -> str:
    lines = [
        'WEB SERVER LOG ANALYSIS', '=' * 42,
        f"File: {data['file']}",
        f"Valid requests: {data['total_requests']}",
        f"Malformed lines skipped: {data['malformed_lines']}",
        f"404 Not Found: {data['not_found_404']}",
        f"5xx Server Errors: {data['server_errors_5xx']}",
        f"Total bytes sent: {data['bytes_sent']}",
        f"First request: {data['first_request'] or 'N/A'}",
        f"Last request: {data['last_request'] or 'N/A'}",
        f"Average requests/minute: {data['average_requests_per_minute'] if data['average_requests_per_minute'] is not None else 'N/A'}",
    ]
    for title, key in [
        ('Top pages', 'top_pages'), ('Top IP addresses', 'top_ips'),
        ('Busiest hours', 'busiest_hours'), ('Status codes', 'status_codes'),
        ('HTTP methods', 'http_methods'),
    ]:
        lines.extend(['', title + ':'])
        rows = data[key].items() if isinstance(data[key], dict) else data[key]
        entries = list(rows)
        lines.extend(f'  {label}: {count}' for label, count in entries)
        if not entries:
            lines.append('  (none)')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Analyze Apache/Nginx common or combined access logs.')
    parser.add_argument('logfile', type=Path, help='Path to an access log file')
    parser.add_argument('--top', type=int, default=5, help='Number of top pages/IPs/hours (default: 5)')
    parser.add_argument('--format', choices=('text', 'json'), default='text', help='Output format')
    parser.add_argument('--output', type=Path, help='Optional path to save the report')
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error('--top must be at least 1')
    try:
        data = analyze_file(args.logfile, top=args.top)
        report = json.dumps(data, indent=2) if args.format == 'json' else render_text(data)
        if args.output:
            args.output.write_text(report + '\n', encoding='utf-8')
            print(f'Report saved to {args.output}')
        else:
            print(report)
        return 0
    except (OSError, UnicodeError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
