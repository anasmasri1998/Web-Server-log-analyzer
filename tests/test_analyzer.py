import tempfile
import unittest
from pathlib import Path
from log_analyzer.analyzer import analyze_file
from log_analyzer.cli import main


class AnalyzerTests(unittest.TestCase):
    def test_counts_and_query_normalization(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / 'access.log'
            file.write_text(
                '1.2.3.4 - - [24/Oct/2026:10:00:00 +0200] "GET /items?id=1 HTTP/1.1" 200 12\n'
                '1.2.3.4 - - [24/Oct/2026:10:01:00 +0200] "GET /items?id=2 HTTP/1.1" 404 0\n'
                '5.6.7.8 - - [24/Oct/2026:11:01:00 +0200] "GET / HTTP/1.1" 503 4\n'
                'bad line\n', encoding='utf-8')
            result = analyze_file(file)
            self.assertEqual(result['total_requests'], 3)
            self.assertEqual(result['malformed_lines'], 1)
            self.assertEqual(result['not_found_404'], 1)
            self.assertEqual(result['server_errors_5xx'], 1)
            self.assertEqual(result['top_pages'][0], ('/items', 2))
            self.assertEqual(result['average_requests_per_minute'], 0.05)

    def test_missing_file_returns_error(self):
        self.assertEqual(main(['/path/that/does/not/exist.log']), 1)

    def test_invalid_top_argument(self):
        with self.assertRaises(SystemExit) as caught:
            main(['sample.log', '--top', '0'])
        self.assertEqual(caught.exception.code, 2)
