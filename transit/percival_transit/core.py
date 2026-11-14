import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SOURCE = 'https://ctrides.com/hlgtfs.zip'
TERMS = 'https://www.cttransit.com/about/developers/terms-of-use'
UTC = timezone.utc


def instant(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timestamp must include UTC offset')
    return result.astimezone(UTC)


def day(value):
    return datetime.strptime(value, '%Y%m%d').date()


def seconds(value):
    if not re.fullmatch(r'\d{1,2}:\d{2}:\d{2}', value):
        raise ValueError('invalid GTFS time: ' + value)
    h, m, s = map(int, value.split(':'))
    if h > 47 or m > 59 or s > 59:
        raise ValueError('unsupported GTFS time: ' + value)
    return h * 3600 + m * 60 + s


def load(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if sum(i.file_size for i in z.infolist()) > 100_000_000:
            raise ValueError('feed exceeds expanded size limit')
        tables = {n[:-4]: list(csv.DictReader(io.StringIO(z.read(n).decode('utf-8-sig'))))
                  for n in z.namelist() if n.endswith('.txt') and '/' not in n}
    for name in ('agency', 'stops', 'routes', 'trips', 'stop_times'):
        if not tables.get(name):
            raise ValueError('missing or empty ' + name)
    if tables.get('frequencies'):
        raise ValueError('frequency-based feeds are not supported')
    def index(name, key):
        rows = tables[name]
        result = {r[key]: r for r in rows}
        if '' in result or len(result) != len(rows):
            raise ValueError('duplicate or empty ' + key)
        return result
    stops = index('stops', 'stop_id')
    routes = index('routes', 'route_id')
    trips = index('trips', 'trip_id')
    agencies = {r.get('agency_id', ''): r for r in tables['agency']}
    zones = {r['agency_timezone'] for r in agencies.values()}
    if len(zones) != 1:
        raise ValueError('this slice requires one agency timezone')
    zone = ZoneInfo(next(iter(zones)))
    services = set()
    dates = []
    for r in tables.get('calendar', []):
        if r['service_id'] in services:
            raise ValueError('duplicate calendar service')
        services.add(r['service_id'])
        start, end = day(r['start_date']), day(r['end_date'])
        if start > end or any(r[k] not in ('0', '1') for k in WEEK):
            raise ValueError('invalid calendar')
        dates.extend((start, end))
    seen = set()
    for r in tables.get('calendar_dates', []):
        key = (r['service_id'], r['date'])
        if key in seen or r['exception_type'] not in ('1', '2'):
            raise ValueError('invalid or duplicate calendar exception')
        seen.add(key)
        services.add(r['service_id'])
        dates.append(day(r['date']))
    if not dates:
        raise ValueError('missing service calendar')
    for r in trips.values():
        if r['route_id'] not in routes or r['service_id'] not in services:
            raise ValueError('trip foreign key')
    for r in routes.values():
        if r.get('agency_id', '') not in agencies and len(agencies) != 1:
            raise ValueError('route agency foreign key')
    sequences = {}
    for r in tables['stop_times']:
        if r['trip_id'] not in trips or r['stop_id'] not in stops:
            raise ValueError('stop_time foreign key')
        r['_seconds'] = seconds(r['departure_time'])
        arrival = seconds(r['arrival_time'])
        if arrival > r['_seconds'] or r.get('pickup_type', '0') not in ('', '0', '1', '2', '3'):
            raise ValueError('invalid stop event')
        sequences.setdefault(r['trip_id'], []).append((int(r['stop_sequence']), arrival, r['_seconds']))
    for trip in trips:
        events = sorted(sequences.get(trip, []))
        if len(events) < 2 or len({e[0] for e in events}) != len(events):
            raise ValueError('invalid trip sequence')
        if any(a[2] > b[1] for a, b in zip(events, events[1:])):
            raise ValueError('nonmonotonic trip')
    for r in tables['stop_times']:
        r['_terminal'] = int(r['stop_sequence']) == max(e[0] for e in sequences[r['trip_id']])
    start, end = min(dates), max(dates)
    for r in tables.get('feed_info', []):
        if r.get('feed_start_date'):
            start = max(start, day(r['feed_start_date']))
        if r.get('feed_end_date'):
            end = min(end, day(r['feed_end_date']))
    if start > end:
        raise ValueError('invalid feed coverage')
    return tables, stops, trips, zone, start, end


WEEK = ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday')


def active(tables, service, d):
    key = d.strftime('%Y%m%d')
    exceptions = [r for r in tables.get('calendar_dates', []) if r['service_id'] == service and r['date'] == key]
    if exceptions:
        return exceptions[0]['exception_type'] == '1'
    return any(r['service_id'] == service and r['start_date'] <= key <= r['end_date'] and
               r[WEEK[d.weekday()]] == '1' for r in tables.get('calendar', []))


def import_feed(raw, store, source, fixture=False, fetched_at=None):
    load(raw)  # validate before publishing; failed imports never replace current
    digest = hashlib.sha256(raw).hexdigest()
    root = Path(store)
    root.mkdir(parents=True, exist_ok=True)
    target = root / digest
    if not target.exists():
        import tempfile
        import os
        temp = Path(tempfile.mkdtemp(prefix='.import-', dir=root))
        (temp / 'feed.zip').write_bytes(raw)
        (temp / 'metadata.json').write_text(json.dumps(dict(snapshot=digest, source=source,
            fetched_at=fetched_at or datetime.now(UTC).isoformat(), fixture=fixture, terms=TERMS)))
        for p in temp.iterdir():
            p.chmod(0o444)
        try:
            os.rename(temp, target)
        except OSError:
            import shutil
            shutil.rmtree(temp)
            if not target.exists():
                raise
    # Re-importing identical bytes deliberately does not refresh the original acquisition time.
    pointer = root / '.current.tmp'
    pointer.write_text(digest)
    pointer.replace(root / 'current')
    return json.loads((target / 'metadata.json').read_text())


def board(store, station, at=None, now=None, hours=24, max_age_days=7):
    now = now or datetime.now(UTC)
    at = at or now
    result = dict(api_version='v1', status='Unknown', station=station, queried_at=at.isoformat(),
                  checked_at=now.isoformat(), departures=[], live=False)
    try:
        if station not in ('hartford', 'windsor-locks'):
            raise ValueError('unknown station')
        if not 0 < hours <= 48 or max_age_days <= 0:
            raise ValueError('invalid query bounds')
        root = Path(store)
        digest = (root / 'current').read_text().strip()
        if not re.fullmatch('[0-9a-f]{64}', digest):
            raise ValueError('invalid snapshot pointer')
        raw = (root / digest / 'feed.zip').read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError('snapshot checksum mismatch')
        meta = json.loads((root / digest / 'metadata.json').read_text())
        result.update(snapshot=digest, source=meta['source'], snapshot_date=meta['fetched_at'], fixture=meta['fixture'])
        age = now - instant(meta['fetched_at'])
        if age < timedelta(0) or age > timedelta(days=max_age_days):
            raise ValueError('stale or future snapshot')
        tables, stops, trips, zone, start, end = load(raw)
        result.update(agency_timezone=str(zone), coverage_start=str(start), coverage_end=str(end))
        # Exact normalized source names; never infer IDs from coordinates or fuzzy matching.
        names = {'hartford': {'hartford', 'hartford union station'},
                 'windsor-locks': {'windsor locks', 'windsor locks station'}}[station]
        ids = {sid for sid, r in stops.items() if r['stop_name'].strip().casefold() in names}
        ids |= {sid for sid, r in stops.items() if r.get('parent_station') in ids}
        if not ids:
            raise ValueError('station identity absent from feed')
        result['source_stop_ids'] = sorted(ids)
        until = at + timedelta(hours=hours)
        if at.astimezone(zone).date() < start or until.astimezone(zone).date() > end:
            raise ValueError('query window outside feed coverage')
        first = at.astimezone(zone).date() - timedelta(days=2)
        last = until.astimezone(zone).date() + timedelta(days=1)
        d = first
        while d <= last:
            if start <= d <= end:
                # GTFS service epoch is local noon minus 12 elapsed hours, including DST days.
                epoch = datetime.combine(d, time(12), zone).astimezone(UTC) - timedelta(hours=12)
                for r in tables['stop_times']:
                    trip = trips[r['trip_id']]
                    if r['_terminal'] or r['stop_id'] not in ids or r.get('pickup_type', '0') not in ('', '0'):
                        continue
                    departure = epoch + timedelta(seconds=r['_seconds'])
                    if at <= departure < until and active(tables, trip['service_id'], d):
                        result['departures'].append(dict(status='Scheduled', departure=departure.astimezone(zone).isoformat(),
                            service_date=str(d), source_trip_id=r['trip_id'], source_stop_id=r['stop_id'],
                            route_id=trip['route_id'], headsign=trip.get('trip_headsign', ''),
                            gtfs_departure_time=r['departure_time'], snapshot=digest, snapshot_date=meta['fetched_at'],
                            source=meta['source'], fixture=meta['fixture']))
            d += timedelta(days=1)
        result['departures'].sort(key=lambda r: instant(r['departure']))
        result['status'] = 'Scheduled'
        result['reason'] = 'Timetable only; operation and cancellations are not verified.'
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, UnicodeError, csv.Error, OverflowError) as exc:
        result['departures'] = []
        result['reason'] = str(exc)
    return result
