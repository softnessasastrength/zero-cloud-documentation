import io
import json
import tempfile
import unittest
from unittest.mock import patch
from datetime import timedelta
from pathlib import Path
from fixtures.make_demo import TABLES, build
from percival_transit.core import board, import_feed, instant, load
from percival_transit.__main__ import response


class TransitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Path(self.temp.name) / 'store'
        buf = io.BytesIO()
        build(buf)
        self.raw = buf.getvalue()
        self.now = instant('2026-11-14T12:00:00Z')
        self.meta = import_feed(self.raw, self.store, 'fixture:test', True, self.now.isoformat())

    def query(self, station='hartford', at='2026-11-15T00:00:00-05:00', hours=1, now=None):
        return board(self.store, station, instant(at), now or self.now, hours)

    def test_both_boards_overnight_provenance(self):
        for station in ('hartford', 'windsor-locks'):
            r = self.query(station)
            self.assertEqual(r['status'], 'Scheduled')
            self.assertTrue(r['fixture'])
            self.assertEqual(len(r['departures']), 1)
            d = r['departures'][0]
            self.assertEqual(d['service_date'], '2026-11-14')
            self.assertEqual(d['source_trip_id'], 'fixture-overnight')
            self.assertEqual(d['snapshot'], self.meta['snapshot'])
            self.assertFalse(r['live'])

    def test_dst_noon_minus_twelve_elapsed_hours(self):
        for station, minute in [('hartford', '00'), ('windsor-locks', '20')]:
            for date, offset in [('2026-03-08', '-04:00'), ('2026-11-01', '-05:00')]:
                r = self.query(station, date + 'T11:00:00' + offset, 2)
                event = next(d for d in r['departures'] if d['source_trip_id'] == 'fixture-day')
                self.assertEqual(event['departure'], date + 'T12:' + minute + ':00' + offset)

    def test_holiday_removal_and_addition(self):
        for station in ('hartford', 'windsor-locks'):
            r = self.query(station, '2026-12-25T09:00:00-05:00', 15)
            self.assertEqual([d['source_trip_id'] for d in r['departures']], ['fixture-holiday'])
            r = self.query(station, '2026-12-26T00:00:00-05:00', 1)
            self.assertEqual(r['departures'], [])  # Christmas overnight service removed
            self.assertEqual(r['status'], 'Scheduled')

    def test_missing_stale_outside_and_corrupt(self):
        for station in ('hartford', 'windsor-locks'):
            self.assertEqual(board('/missing', station)['status'], 'Unknown')
            self.assertEqual(self.query(station, now=self.now + timedelta(days=8))['status'], 'Unknown')
            self.assertEqual(self.query(station, '2028-01-02T00:00:00Z')['status'], 'Unknown')
        target = self.store / self.meta['snapshot'] / 'feed.zip'
        target.chmod(0o644)
        target.write_bytes(b'broken')
        self.assertEqual(self.query()['status'], 'Unknown')

    def test_broken_import_preserves_snapshot(self):
        for change in ({'trips': TABLES['trips'].replace('r,daily', 'bad,daily')},
                       {'stop_times': TABLES['stop_times'].replace('24:30:00', '24:99:00')},
                       {'calendar_dates': TABLES['calendar_dates'] + 'daily,20261225,1\n'},
                       {'agency': TABLES['agency'].replace('America/New_York', 'Invalid/Timezone')}):
            buf = io.BytesIO()
            build(buf, TABLES | change)
            with self.assertRaises((ValueError, KeyError)):
                import_feed(buf.getvalue(), self.store, 'fixture:broken', True)
            self.assertEqual((self.store / 'current').read_text(), self.meta['snapshot'])
        with self.assertRaises(Exception):
            load(b'not zip')

    def test_immutable_reimport(self):
        again = import_feed(self.raw, self.store, 'changed', True)
        self.assertEqual(again, self.meta)

    @patch("percival_transit.__main__.board")
    def test_api_contract(self, mock_board):
        mock_board.side_effect = lambda *args, **kwargs: board(*args, now=self.now, **kwargs)
        for station in ('hartford', 'windsor-locks'):
            status, r = response('/v1/stations/' + station + '/departures?at=2026-11-15T05:00:00Z&hours=1', self.store)
            self.assertEqual(status, 200)
            self.assertEqual(r['api_version'], 'v1')
        self.assertEqual(response('/v2/foo', self.store)[0], 404)
        self.assertEqual(response('/v1/stations/hartford/departures?at=nope', self.store)[0], 400)
        self.assertEqual(response('/v1/stations/hartford/departures?hours=nan', self.store)[0], 503)

    def test_identical_authoritative_bytes_can_be_revalidated_without_mutation(self):
        later = self.now + timedelta(days=8)
        original = (self.store / self.meta['snapshot'] / 'metadata.json').read_bytes()
        import_feed(self.raw, self.store, 'fixture:test', True, later.isoformat())
        result = self.query(now=later)
        self.assertEqual(result['status'], 'Scheduled')
        self.assertEqual(result['snapshot_date'], self.meta['fetched_at'])
        self.assertEqual(result['source_checked_at'], later.isoformat())
        self.assertEqual((self.store / self.meta['snapshot'] / 'metadata.json').read_bytes(), original)

    def test_calendar_dates_only(self):
        tables = dict(TABLES)
        del tables['calendar']
        tables['calendar_dates'] = 'service_id,date,exception_type\ndaily,20261114,1\nholiday,20261225,1\n'
        buf = io.BytesIO()
        build(buf, tables)
        import_feed(buf.getvalue(), self.store, 'fixture:exceptions', True, self.now.isoformat())
        self.assertEqual(len(self.query()['departures']), 1)


if __name__ == '__main__':
    unittest.main()
