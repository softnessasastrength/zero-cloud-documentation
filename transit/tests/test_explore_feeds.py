import io
import tempfile
import unittest
from pathlib import Path
from fixtures.make_demo import build
from fixtures.make_preview import tables
from percival_transit.core import import_feed, instant, board
from percival_transit.feeds import catalog, feed_store, departures
from percival_transit.planner import explore
from percival_transit.connections import check_transfer


class ExploreFeedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.now = instant('2026-11-14T12:00:00Z')
        self.data = tables()
        self.save()

    def save(self):
        buffer = io.BytesIO()
        build(buffer, self.data)
        import_feed(buffer.getvalue(), self.root, 'fixture:explore', True, self.now.isoformat())

    def test_reachable_outing_checks_complete_return(self):
        result = explore(self.root, 'fixture-w', instant('2026-11-14T15:00:00-05:00'), instant('2026-11-15T01:00:00-05:00'), 60, now=self.now)
        self.assertEqual(result['status'], 'Scheduled')
        hartford = next(r for r in result['results'] if r['destination_id'] == 'fixture-h')
        self.assertEqual(hartford['last_departure'], '2026-11-15T00:30:00-05:00')
        self.assertEqual(hartford['itinerary']['last_return'][-1]['to_stop_id'], 'fixture-w')
        self.assertTrue(hartford['itinerary']['fixture'])
        self.assertEqual({r['destination'] for r in result['unknown']}, {'NYP','BOS'})

    def test_destination_without_usable_return_is_not_recommended(self):
        result = explore(self.root, 'fixture-w', instant('2026-11-14T15:00:00-05:00'), instant('2026-11-14T21:00:00-05:00'), now=self.now)
        self.assertEqual(result['results'], [])
        self.assertEqual(result['status'], 'Unknown')

    def test_weekend_loses_final_bus_home(self):
        self.data['calendar'] += 'weekdays,1,1,1,1,1,0,0,20260101,20271231\n'
        for tid in ('demo-return','demo-last','fixture-overnight'):
            self.data['trips'] = self.data['trips'].replace('r,daily,'+tid, 'r,weekdays,'+tid)
        self.save()
        def query(d):
            return explore(self.root,'fixture-w',instant(d+'T15:00:00-05:00'),instant(d+'T23:59:00-05:00'),now=self.now)
        self.assertEqual(query('2026-11-13')['status'], 'Scheduled')
        self.assertEqual(query('2026-11-14')['results'], [])

    def test_independent_feeds_and_unknown_direction(self):
        buffer = io.BytesIO()
        build(buffer, self.data)
        import_feed(buffer.getvalue(), feed_store(self.root,'pvta'), 'fixture:pvta', True, self.now.isoformat())
        self.assertEqual(catalog(self.root,'pvta',now=self.now)['status'], 'Scheduled')
        self.assertEqual(catalog(self.root,'cttransit',now=self.now)['status'], 'Unknown')
        self.assertEqual(board(self.root,'hartford',now=self.now)['status'], 'Scheduled')
        self.assertEqual(departures(self.root,'pvta','r','fixture-h','invalid')['status'], 'Unknown')

    def test_transfer_requires_walking_evidence_and_time(self):
        a, b = '2026-11-13T06:55:00-05:00', '2026-11-13T06:58:00-05:00'
        self.assertEqual(check_transfer(a,b)['status'],'Unknown')
        self.assertEqual(check_transfer(a,b,120,120,'fixture:path')['status'],'Infeasible')
        self.assertEqual(check_transfer(a,b,60,120,'fixture:path')['status'],'Scheduled')
