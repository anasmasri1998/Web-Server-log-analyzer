import unittest
from log_analyzer.parser import parse_line


class ParserTests(unittest.TestCase):
    def test_combined_format(self):
        entry = parse_line('127.0.0.1 - - [24/Oct/2026:10:01:02 +0200] "GET /a?q=1 HTTP/1.1" 200 123 "-" "Agent"')
        self.assertEqual((entry.ip, entry.path, entry.status, entry.size), ('127.0.0.1', '/a?q=1', 200, 123))

    def test_common_format_and_dash_size(self):
        entry = parse_line('127.0.0.1 - - [24/Oct/2026:10:01:02 +0200] "GET / HTTP/1.1" 404 -')
        self.assertEqual((entry.status, entry.size), (404, 0))

    def test_invalid_entries(self):
        for line in ['', 'junk', '127.0.0.1 - - [wrong] "GET / HTTP/1.1" 200 3']:
            with self.subTest(line=line), self.assertRaises(ValueError):
                parse_line(line)
