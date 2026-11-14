"""Bounded deterministic timetable search: direct or one same-stop transfer per leg."""
from datetime import datetime, timedelta, time
from pathlib import Path
from .core import UTC, active, board, instant, load

ALIASES = {'hartford': {'hartford', 'hartford union station'},
           'windsor-locks': {'windsor locks', 'windsor locks station'}}


def stop_ids(stops, value):
    ids = {value} if value in stops else {k for k, r in stops.items()
        if r['stop_name'].strip().casefold() in ALIASES.get(value, set())}
    return ids | {k for k, r in stops.items() if r.get('parent_station') in ids}


def stations(store):
    probe = board(store, 'hartford', hours=1)
    result = {**probe, 'stations': []}
    if probe.get('snapshot'):
        try:
            _, stops, _, _, _, _ = load((Path(store) / probe['snapshot'] / 'feed.zip').read_bytes())
            result['stations'] = [{'id': k, 'name': r['stop_name']} for k, r in stops.items()
                                  if r.get('location_type', '0') in ('', '0', '1')]
        except (OSError, ValueError, KeyError):
            pass
    return result


def round_trip(store, origin, destination, depart_after, arrive_by, return_after, return_by,
               margin_minutes=10, now=None):
    result = dict(api_version='v1', status='Unknown', outbound=None, returns=[], last_return=None,
                  live=False, search_scope='This snapshot only; direct or one same-stop transfer per leg; no walking links.')
    try:
        now = now or datetime.now(UTC)
        values = (depart_after, arrive_by, return_after, return_by)
        if any(v.tzinfo is None for v in values):
            raise ValueError('all times require UTC offsets')
        if not depart_after < arrive_by <= return_after < return_by:
            raise ValueError('require depart_after < arrive_by <= return_after < return_by')
        if return_by - depart_after > timedelta(hours=48) or not 0 <= margin_minutes <= 120:
            raise ValueError('maximum search is 48 hours; transfer margin is 0–120 minutes')
        probe = board(store, 'hartford', at=depart_after, now=now,
                      hours=(return_by - depart_after).total_seconds() / 3600)
        result.update({k: v for k, v in probe.items() if k not in ('station', 'departures', 'status', 'reason')})
        if probe['status'] != 'Scheduled':
            raise ValueError(probe['reason'])
        raw = (Path(store) / probe['snapshot'] / 'feed.zip').read_bytes()
        tables, stops, trips, zone, start, end = load(raw)
        origins, destinations = stop_ids(stops, origin), stop_ids(stops, destination)
        if not origins or not destinations or origins & destinations:
            raise ValueError('choose two distinct source-backed stations')
        result['constraints'] = dict(origin=origin, destination=destination,
            depart_after=depart_after.isoformat(), arrive_by=arrive_by.isoformat(),
            return_after=return_after.isoformat(), return_by=return_by.isoformat(), margin_minutes=margin_minutes)
        grouped = {}
        for row in tables['stop_times']:
            grouped.setdefault(row['trip_id'], []).append(row)
        if tables.get('transfers'):
            raise ValueError('Feed transfer rules need separate validation; this preview cannot prove transfers for this feed.')
        instances = []
        d = depart_after.astimezone(zone).date() - timedelta(days=2)
        last = return_by.astimezone(zone).date() + timedelta(days=1)
        while d <= last:
            if start <= d <= end:
                epoch = datetime.combine(d, time(12), zone).astimezone(UTC) - timedelta(hours=12)
                for tid, rows in grouped.items():
                    trip = trips[tid]
                    if active(tables, trip['service_id'], d):
                        instances.append((tid, str(d), sorted(rows, key=lambda r: int(r['stop_sequence'])), epoch))
            d += timedelta(days=1)

        def segments(source, target, earliest, latest):
            found = []
            for tid, service_date, rows, epoch in instances:
                for i, a in enumerate(rows):
                    if source is not None and a['stop_id'] not in source:
                        continue
                    if a.get('pickup_type', '0') not in ('', '0'):
                        continue
                    departure = epoch + timedelta(seconds=a['_seconds'])
                    if departure < earliest or departure >= latest:
                        continue
                    for b in rows[i+1:]:
                        if target is not None and b['stop_id'] not in target:
                            continue
                        if b.get('drop_off_type', '0') not in ('', '0'):
                            continue
                        from .core import seconds
                        arrival = epoch + timedelta(seconds=seconds(b['arrival_time']))
                        if arrival <= latest:
                            found.append(dict(status='Scheduled', source_trip_id=tid, service_date=service_date,
                                from_stop_id=a['stop_id'], to_stop_id=b['stop_id'],
                                from_name=stops[a['stop_id']]['stop_name'], to_name=stops[b['stop_id']]['stop_name'],
                                departure=departure.astimezone(zone).isoformat(), arrival=arrival.astimezone(zone).isoformat(),
                                snapshot=probe['snapshot'], snapshot_date=probe['snapshot_date'],
                                source=probe['source'], fixture=probe['fixture']))
            return found

        def journeys(source, target, earliest, latest):
            direct = [[s] for s in segments(source, target, earliest, latest)]
            first = segments(source, None, earliest, latest)
            second = segments(None, target, earliest, latest)
            by_stop = {}
            for s in second:
                by_stop.setdefault(s['from_stop_id'], []).append(s)
            for a in first:
                for b in by_stop.get(a['to_stop_id'], []):
                    if (a['source_trip_id'], a['service_date']) == (b['source_trip_id'], b['service_date']):
                        continue
                    if instant(b['departure']) >= instant(a['arrival']) + timedelta(minutes=margin_minutes):
                        direct.append([a, b])
            unique = {tuple((s['source_trip_id'], s['service_date'], s['from_stop_id'], s['to_stop_id']) for s in j): j for j in direct}
            return sorted(unique.values(), key=lambda j: (instant(j[0]['departure']), instant(j[-1]['arrival'])))

        outbound = journeys(origins, destinations, depart_after, arrive_by)
        returns = journeys(destinations, origins, return_after, return_by)
        result['returns'] = returns
        if outbound and returns:
            result.update(status='Scheduled', outbound=outbound[-1], last_return=returns[-1],
                reason='Scheduled round trip within the stated search. Operation and cancellations are unverified.')
        else:
            result.update(status='Infeasible', reason='No round trip satisfies these constraints in this snapshot within the stated direct/one-transfer search. Other operators and paths are unknown.')
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        result.update(status='Unknown', reason=str(exc), outbound=None, returns=[], last_return=None)
    return result
