"""Record official selected-route inventories and weekday/weekend scheduled samples."""
import json
import tempfile
import urllib.request
from datetime import datetime
from pathlib import Path
from .core import UTC, import_feed, instant
from .feeds import FEEDS, catalog, departures, feed_store


def run(feed):
    now = datetime.now(UTC)
    report = dict(feed=feed, source=FEEDS[feed]['url'], terms=FEEDS[feed]['terms'], checked_at=now.isoformat(), result='Unknown')
    try:
        with urllib.request.urlopen(report['source'], timeout=45) as response:
            raw = response.read(20_000_001)
        if len(raw) > 20_000_000:
            raise ValueError('archive exceeds limit')
        with tempfile.TemporaryDirectory() as root:
            report['snapshot'] = import_feed(raw, feed_store(root, feed), report['source'], fetched_at=now.isoformat(), selection=FEEDS[feed]['routes'], terms=report['terms'])
            info = catalog(root, feed)
            report['catalog'] = info
            samples = []
            for route in info['routes']:
                rid = route['route_id']
                patterns = [p for p in info['patterns'] if p['route_id'] == rid]
                for d in ('2026-11-13', '2026-11-14'):
                    for direction in sorted({p['direction_id'] for p in patterns}):
                        candidates = [p for p in patterns if p['direction_id'] == direction]
                        sid = candidates[0]['stops'][0]
                        r = departures(root, feed, rid, sid, direction, instant(d+'T04:00:00-05:00'))
                        samples.append(dict(date=d, route=route, stop_id=sid, direction_id=direction, board=r))
            report['samples'] = samples
            pins = [s for s in info['stops'] if any(k in s['stop_name'].casefold() for k in ('bright meadow', 'jewish', 'massmutual', 'railroad station', 'rr station'))]
            report['preferred_stop_candidates'] = pins
            report['pinned_samples'] = []
            for stop in pins:
                for route in info['routes']:
                    if any(p['route_id'] == route['route_id'] and stop['stop_id'] in p['stops'] for p in info['patterns']):
                        for date in ('2026-11-13', '2026-11-14'):
                            report['pinned_samples'].append(dict(date=date, stop=stop, route=route, board=departures(root, feed, route['route_id'], stop['stop_id'], at=instant(date+'T04:00:00-05:00'))))
            if info['status'] != 'Scheduled' or any(s['board']['status'] != 'Scheduled' for s in samples):
                raise ValueError('one or more boards are Unknown')
            report['result'] = 'Passed'
    except Exception as exc:
        report['error'] = str(exc)
    return report


if __name__ == '__main__':
    import sys
    result = run(sys.argv[1])
    Path(sys.argv[1] + '-smoke.json').write_text(json.dumps(result, indent=2))
    # Full report is an artifact; logs retain compact evidence.
    print(json.dumps({k: v for k, v in result.items() if k != 'catalog'}, indent=2))
    sys.exit(0 if result['result'] == 'Passed' else 1)
