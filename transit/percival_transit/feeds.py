"""Independent official static feeds and route allow-lists for the personal preview."""
import hashlib
import json
import re
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from .core import SOURCE, TERMS, UTC, board, instant, load

FEEDS = {
    'rail': dict(url=SOURCE, terms=TERMS, routes=None, name='Hartford Line'),
    'cttransit': dict(url='https://www.cttransit.com/sites/default/files/gtfs/googlect_transit.zip',
        terms=TERMS, routes=['80', '81', '82', '82/84', '83', '84', '905', '905W'], name='CTtransit'),
    'pvta': dict(url='https://www.pvta.com/g_trans/google_transit.zip?t=202610281453440',
        terms='https://pvta.com/bus_service/real_time_data.php', routes=['G5', 'R10', 'R14'], name='PVTA'),
}


def feed_store(root, feed):
    if feed not in FEEDS:
        raise ValueError('unknown feed')
    return Path(root) if feed == 'rail' else Path(root) / feed


@lru_cache(maxsize=3)
def snapshot(root, digest):
    if not re.fullmatch('[a-f0-9]{64}', digest):
        raise ValueError('invalid snapshot')
    path = Path(root) / digest
    raw = (path / 'feed.zip').read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('checksum mismatch')
    meta = json.loads((path / 'metadata.json').read_text())
    return meta, load(raw, meta.get('selection'))


def catalog(root, feed, now=None):
    now = now or datetime.now(UTC)
    result = dict(api_version='v1', feed=feed, status='Unknown', routes=[], stops=[], patterns=[],
                  source=FEEDS[feed]['url'], attribution=FEEDS[feed]['name'], live=False)
    try:
        store = feed_store(root, feed)
        digest = (store / 'current').read_text().strip()
        meta, (tables, stops, trips, zone, start, end) = snapshot(str(store), digest)
        age = (now - instant(meta['fetched_at'])).total_seconds()
        result.update(snapshot=digest, snapshot_date=meta['fetched_at'], snapshot_age_seconds=age,
                      coverage_start=str(start), coverage_end=str(end), agency_timezone=str(zone), fixture=meta['fixture'])
        result['routes'] = tables['routes']
        events = {}
        for r in tables['stop_times']:
            events.setdefault(r['trip_id'], []).append(r)
        patterns = {}
        for tid, trip in trips.items():
            rows = sorted(events[tid], key=lambda r: int(r['stop_sequence']))
            ids = tuple(r['stop_id'] for r in rows)
            key = (trip['route_id'], trip.get('direction_id', ''), trip.get('trip_headsign', ''), ids)
            patterns[key] = dict(route_id=trip['route_id'], direction_id=trip.get('direction_id', ''),
                headsign=trip.get('trip_headsign', ''), stops=list(ids), destination=stops[ids[-1]]['stop_name'])
        result['patterns'] = list(patterns.values())
        served = {r['stop_id'] for r in tables['stop_times']}
        result['stops'] = [dict(stop_id=k, stop_name=r['stop_name'], stop_lat=r.get('stop_lat'), stop_lon=r.get('stop_lon')) for k, r in stops.items() if k in served]
        if not 0 <= age <= 7*86400:
            raise ValueError('stale or future snapshot')
        result.update(status='Scheduled', reason='Static timetable catalog; no live status. PVTA data is sourced from PVTA; no agency endorsement.')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result['reason'] = str(exc)
    return result


def departures(root, feed, route_id, stop_id, direction_id=None, at=None):
    status = catalog(root, feed)
    if status['status'] != 'Scheduled':
        return status | dict(departures=[], station='stop:' + stop_id)
    if route_id not in {r['route_id'] for r in status['routes']}:
        return status | dict(status='Unknown', departures=[], reason='Route absent from this snapshot')
    if not any(p['route_id'] == route_id and stop_id in p['stops'] and (direction_id is None or p['direction_id'] == direction_id) for p in status['patterns']):
        return status | dict(status='Unknown', departures=[], reason='No source pattern serves this route, stop and direction combination')
    result = board(feed_store(root, feed), 'stop:' + stop_id, at=at, route_id=route_id, direction_id=direction_id, compiled=snapshot(str(feed_store(root, feed)), status['snapshot'])[1])
    # Downstream station names are sourced from this exact trip pattern, not headsign guesses.
    result.update(feed=feed, attribution=FEEDS[feed]['name'])
    route = next(r for r in status['routes'] if r['route_id'] == route_id)
    for d in result['departures']:
        d['route_label'] = route.get('route_short_name') or route.get('route_long_name') or route_id
        _, (tables, stops, trips, _, _, _) = snapshot(str(feed_store(root, feed)), d['snapshot'])
        rows = sorted((r for r in tables['stop_times'] if r['trip_id'] == d['source_trip_id']), key=lambda r: int(r['stop_sequence']))
        index = next(i for i, r in enumerate(rows) if r['stop_id'] == d['source_stop_id'])
        d['downstream_stop_ids'] = [r['stop_id'] for r in rows[index+1:]]
        d['downstream_stop_names'] = [stops[r['stop_id']]['stop_name'] for r in rows[index+1:]]
    return result
