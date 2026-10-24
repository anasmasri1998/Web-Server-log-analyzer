# Web Server Log Analyzer (Python CLI)

A beginner-friendly command-line tool that analyzes **Apache and Nginx access logs** (Common Log Format and Combined Log Format). It counts requests, finds popular pages and source IPs, highlights busy hours and 404/5xx errors, and generates human-readable or JSON reports.

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies

## Quick start (without installing)

From the project root:

```bash
python -m log_analyzer samples/access.log
python -m log_analyzer samples/access.log --top 3
python -m log_analyzer samples/access.log --format json
python -m log_analyzer samples/access.log --format json --output report.json
```

On Windows, you may need to use `py` instead of `python`.

## Install as a CLI command (optional)

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
weblog samples/access.log
weblog samples/access.log --format json --output report.json
```

## Example results

The included sample has **9 valid requests** and **1 malformed line**. Two responses are **404**, and two are **5xx**. The most visited page is `/products` with 3 visits (query strings are omitted for page grouping). Hours are grouped using the timestamp's original timezone offset. For logs with mixed offsets, normalize your logs before analysis for accurate hourly grouping.

## CLI options

| Option | Description |
|---|---|
| `logfile` | Required path to Apache/Nginx access log |
| `--top N` | Number of results in top pages/IPs/hours (default: 5) |
| `--format text\|json` | Report format (default: text) |
| `--output FILE` | Save report to a file instead of printing |
| `-h`, `--help` | Show usage information |

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Code guide

- `log_analyzer/parser.py`: regular expression parser and `LogEntry` data structure
- `log_analyzer/analyzer.py`: reads logs line by line; calculates counts, rankings, and average request frequency
- `log_analyzer/cli.py`: processes terminal arguments and prints/saves reports
- `tests/`: automated tests for parsing, aggregation, and CLI errors
- `samples/access.log`: demo log with a deliberate malformed line

## How malformed data is handled

Blank lines are ignored. Unrecognized lines and invalid timestamps are counted as `malformed_lines` and skipped. Files with encoding issues are opened using UTF-8 replacement characters. Unreadable or missing files cause a clear error message and exit code 1. The analyzer streams lines rather than reading the whole file into memory.

## Known limitations

- Supports standard Apache/Nginx **common and combined** access log formats, not arbitrary custom formats.
- Does not decode escaped quotes inside request/referrer/user-agent fields.
- Ignores 404/5xx response URL lists; it reports counts and popular pages overall.
- `average_requests_per_minute` is calculated as total requests divided by the elapsed period from the first to last valid request; when only one timestamp exists, it is `null` / N/A.
- The top-hours breakdown groups by the offset written in the log; logs mixing timezones should be normalized first.
- Large files are streamed, but high-cardinality unique pages/IPs are stored in counters.

## Potential next upgrades

1. Separate top 404 URLs and top 5xx URLs.
2. Analyze multiple files or compressed `.gz` logs.
3. Add date and status-code filters.
4. Generate CSV reports or hourly charts.
5. Add tests for edge cases and a GitHub Actions test workflow.

## Privacy

Web access logs may contain sensitive data such as IP addresses, URL query parameters, and personal identifiers. Use synthetic or anonymized logs in public repositories.
