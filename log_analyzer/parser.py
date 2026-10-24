"""Parse Apache/Nginx common and combined access-log formats."""
import re
from dataclasses import dataclass
from datetime import datetime

# Combined format optionally ends with a quoted referrer and user agent.
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] '
    r'"(?P<request>[^"]*)" (?P<status>\d{3}) (?P<size>\d+|-)'
    r'(?: "[^"]*" "[^"]*")?\s*$'
)


@dataclass(frozen=True)
class LogEntry:
    ip: str
    timestamp: datetime
    method: str
    path: str
    status: int
    size: int


def parse_line(line: str) -> LogEntry:
    """Parse one log line; raise ValueError if invalid."""
    match = LOG_PATTERN.fullmatch(line.strip())
    if not match:
        raise ValueError("Unsupported or malformed access log line")
    data = match.groupdict()
    try:
        timestamp = datetime.strptime(data['timestamp'], '%d/%b/%Y:%H:%M:%S %z')
    except ValueError as exc:
        raise ValueError("Invalid timestamp") from exc
    pieces = data['request'].split()
    if len(pieces) != 3 or not pieces[2].startswith('HTTP/'):
        raise ValueError("Invalid HTTP request")
    method, path, _ = pieces
    status = int(data['status'])
    if not 100 <= status <= 599:
        raise ValueError("Invalid HTTP status")
    return LogEntry(
        ip=data['ip'], timestamp=timestamp, method=method,
        path=path, status=status,
        size=0 if data['size'] == '-' else int(data['size']),
    )
