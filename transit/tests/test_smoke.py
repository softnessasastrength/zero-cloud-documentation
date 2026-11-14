import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fixtures.make_demo import build
from percival_transit.core import board
from percival_transit.smoke import run


class SmokeTests(unittest.TestCase):
    def test_fixture_report_includes_both_http_boards(self):
        def fake_http(store, at):
            return {s: {'http_status': 200, 'body': board(store, s, at=at, hours=1)}
                    for s in ('hartford', 'windsor-locks')}
        with patch('percival_transit.smoke.http_boards', side_effect=fake_http):
            report = run(fixture=True)
        self.assertEqual(report['result'], 'Passed')
        self.assertTrue(report['fixture'])
        self.assertEqual(report['source'], 'fixture:generated-demo')
        self.assertEqual(len(report['sha256']), 64)
        for station in ('hartford', 'windsor-locks'):
            self.assertEqual(report['http'][station]['http_status'], 200)
            self.assertEqual(report['boards'][station]['departures'][0]['service_date'], '2026-11-14')

    def test_network_failure_never_substitutes_fixtures(self):
        with patch('urllib.request.urlopen', side_effect=OSError('offline')):
            report = run()
        self.assertEqual(report['result'], 'Unknown')
        self.assertFalse(report['fixture'])
        self.assertEqual(report['error'], 'offline')
        self.assertNotIn('snapshot_date', report)
        self.assertNotIn('boards', report)

    def test_broken_download_reports_hash_and_unknown(self):
        report = run(raw=b'broken')
        self.assertEqual(report['result'], 'Unknown')
        self.assertEqual(len(report['sha256']), 64)
        self.assertNotIn('boards', report)

    def test_http_failure_cannot_pass(self):
        with patch('percival_transit.smoke.http_boards', side_effect=OSError('socket blocked')):
            report = run(fixture=True)
        self.assertEqual(report['result'], 'Unknown')
        self.assertEqual(report['error'], 'socket blocked')
        self.assertIn('boards', report)
