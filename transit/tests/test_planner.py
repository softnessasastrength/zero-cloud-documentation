import io
import tempfile
import unittest
from pathlib import Path
from fixtures.make_demo import build
from fixtures.make_preview import tables
from percival_transit.core import import_feed, instant
from percival_transit.planner import round_trip


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Path(self.temp.name)
        self.now = instant('2026-11-14T12:00:00Z')
        self.tables = tables()
        self.save()

    def save(self):
        buf = io.BytesIO()
        build(buf, self.tables)
        import_feed(buf.getvalue(), self.store, 'fixture:preview', True, self.now.isoformat())

    def plan(self, **changes):
        args = dict(store=self.store, origin='windsor-locks', destination='hartford',
            depart_after=instant('2026-11-14T15:00:00-05:00'), arrive_by=instant('2026-11-14T18:00:00-05:00'),
            return_after=instant('2026-11-14T21:00:00-05:00'), return_by=instant('2026-11-15T01:00:00-05:00'), now=self.now)
        return round_trip(**(args | changes))

    def test_round_trip_and_last_return(self):
        result = self.plan()
        self.assertEqual(result['status'], 'Scheduled')
        self.assertEqual(result['outbound'][0]['source_trip_id'], 'demo-out')
        self.assertEqual(result['last_return'][0]['source_trip_id'], 'fixture-overnight')
        self.assertEqual(result['last_return'][0]['service_date'], '2026-11-14')
        self.assertEqual(result['last_return'][0]['departure'], '2026-11-15T00:30:00-05:00')
        self.assertTrue(result['last_return'][0]['fixture'])

    def test_last_return_deadline(self):
        result = self.plan(return_by=instant('2026-11-14T23:59:00-05:00'))
        self.assertEqual(result['last_return'][0]['source_trip_id'], 'demo-last')

    def test_no_service_is_bounded_infeasible(self):
        result = self.plan(return_after=instant('2026-11-15T00:55:00-05:00'))
        self.assertEqual(result['status'], 'Infeasible')
        self.assertIn('Other operators', result['reason'])

    def test_unknown_for_stale_or_coverage_or_bad_constraints(self):
        for changes in [dict(now=instant('2026-11-25T12:00:00Z')),
                        dict(origin='not-in-feed'), dict(margin_minutes=float('nan')),
                        dict(return_by=instant('2028-01-01T00:00:00Z'))]:
            self.assertEqual(self.plan(**changes)['status'], 'Unknown')

    def test_transfer_margin_and_missed_connection(self):
        # Replace the outbound with two trains through the same source stop.
        self.tables['trips'] = self.tables['trips'].replace('r,daily,demo-out,FICTIONAL preview\n', '')
        self.tables['stop_times'] = '\n'.join(r for r in self.tables['stop_times'].split('\n') if not r.startswith('demo-out,'))
        self.tables['trips'] += 'r,daily,connection-a,DEMO\nr,daily,connection-b,DEMO\n'
        self.tables['stop_times'] += 'connection-a,16:00:00,16:00:00,fixture-w,1\nconnection-a,16:15:00,16:15:00,fixture-end,2\nconnection-b,16:20:00,16:20:00,fixture-end,1\nconnection-b,16:40:00,16:40:00,fixture-h,2\n'
        self.save()
        self.assertEqual(self.plan(margin_minutes=10)['status'], 'Infeasible')
        result = self.plan(margin_minutes=5)
        self.assertEqual(result['status'], 'Scheduled')
        self.assertEqual(len(result['outbound']), 2)

    def test_holiday_exception_and_dst_dates(self):
        for d in ('2026-12-25', '2026-03-08', '2026-11-01'):
            times = {k: instant(d + value) for k, value in {
                'depart_after':'T15:00:00-05:00', 'arrive_by':'T18:00:00-05:00',
                'return_after':'T21:00:00-05:00', 'return_by':'T23:59:00-05:00'}.items()}
            result = self.plan(**times)
            self.assertEqual(result['status'], 'Infeasible' if d.endswith('12-25') else 'Scheduled')
