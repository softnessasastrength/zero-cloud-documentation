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
               margin_minutes=10, now=None, min_dwell_minutes=None):
    result = dict(api_version='v1', status='Unknown', outbound=None, returns=[], last_return=None,
                  live=False, search_scope='This snapshot only; direct or one same-stop transfer per leg; no walking links.')
    try:
        now = now or datetime.now(UTC)
        values = (depart_after, arrive_by, return_after, return_by)
        if any(v.tzinfo is None for v in values):
            raise ValueError('all times require UTC offsets')
        if min_dwell_minutes is None and not depart_after < arrive_by <= return_after < return_by:
            raise ValueError('require depart_after < arrive_by <= return_after < return_by')
        if return_by - depart_after > timedelta(hours=48) or not 0 <= margin_minutes <= 120:
            raise ValueError('maximum search is 48 hours; transfer margin is 0–120 minutes')
        from .feeds import snapshot
        digest = (Path(store) / 'current').read_text().strip()
        meta, compiled = snapshot(str(store), digest)
        tables, stops, trips, zone, start, end = compiled
        probe_station = origin if origin in ALIASES else 'stop:' + origin
        probe = board(store, probe_station, at=depart_after, now=now,
                      hours=(return_by - depart_after).total_seconds() / 3600, compiled=compiled)
        result.update({k: v for k, v in probe.items() if k not in ('station', 'departures', 'status', 'reason')})
        if probe['status'] != 'Scheduled':
            raise ValueError(probe['reason'])
        origins, destinations = stop_ids(stops, origin), stop_ids(stops, destination)
        if not origins or not destinations or origins & destinations:
            raise ValueError('choose two distinct source-backed stations')
        result['constraints'] = dict(origin=origin, destination=destination,
            depart_after=depart_after.isoformat(), arrive_by=arrive_by.isoformat(),
            return_after=return_after.isoformat(), return_by=return_by.isoformat(), margin_minutes=margin_minutes)
        grouped = {}
        for row in tables['stop_times']:
            grouped.setdefault(row['trip_id'], []).append(row)
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
                                route_id=trips[tid]['route_id'],
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
                    required_seconds = margin_minutes * 60
                    allowed = True
                    for rule in tables.get('transfers', []):
                        if rule.get('from_stop_id') != a['to_stop_id'] or rule.get('to_stop_id') != b['from_stop_id']:
                            continue
                        if any(rule.get(k) and rule[k] != value for k, value in [('from_trip_id', a['source_trip_id']), ('to_trip_id', b['source_trip_id']), ('from_route_id', a['route_id']), ('to_route_id', b['route_id'])]):
                            continue
                        if rule.get('transfer_type') in ('3', '4', '5'):
                            allowed = False
                        required_seconds = max(required_seconds, int(rule.get('min_transfer_time') or 0))
                    if allowed and instant(b['departure']) >= instant(a['arrival']) + timedelta(seconds=required_seconds):
                        direct.append([a, b])
            unique = {tuple((s['source_trip_id'], s['service_date'], s['from_stop_id'], s['to_stop_id']) for s in j): j for j in direct}
            return sorted(unique.values(), key=lambda j: (instant(j[0]['departure']), instant(j[-1]['arrival'])))

        outbound = journeys(origins, destinations, depart_after, arrive_by)
        returns = journeys(destinations, origins, return_after, return_by)
        if min_dwell_minutes is not None:
            if not 0 <= min_dwell_minutes <= 1440:
                raise ValueError('minimum destination time must be 0–1440 minutes')
            pairs = [(a, b) for a in outbound for b in returns if instant(b[0]['departure']) - instant(a[-1]['arrival']) >= timedelta(minutes=min_dwell_minutes)]
            if pairs:
                chosen = max(pairs, key=lambda p: (instant(p[1][0]['departure']) - instant(p[0][-1]['arrival']), -len(p[0])-len(p[1])))
                outbound = [chosen[0]]
                returns = [b for b in returns if instant(b[0]['departure']) >= instant(chosen[0][-1]['arrival']) + timedelta(minutes=min_dwell_minutes)]
            else:
                outbound, returns = [], []
        result['returns'] = returns
        if outbound and returns:
            result.update(status='Scheduled', outbound=outbound[-1], last_return=returns[-1],
                reason='Scheduled round trip within the stated search. Operation and cancellations are unverified.')
        else:
            result.update(status='Infeasible', reason='No round trip satisfies these constraints in this snapshot within the stated direct/one-transfer search. Other operators and paths are unknown.')
    except (OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        result.update(status='Unknown', reason=str(exc), outbound=None, returns=[], last_return=None)
    return result


def explore(store, origin, leave_after, back_by, min_minutes=60, sort='time_there', now=None):
    from .feeds import snapshot
    result = dict(api_version='v1', status='Unknown', results=[], unknown=[
        {'destination':'NYP', 'reason':'Dated Amtrak schedule and walking links from the origin are not verified.'},
        {'destination':'BOS', 'reason':'Dated Amtrak schedule and walking links from the origin are not verified.'}],
        search_scope='Supported routes in this one feed; direct or one same-stop transfer each way. No cross-agency walking links.')
    try:
        if not leave_after < back_by or back_by-leave_after > timedelta(hours=48):
            raise ValueError('choose a positive travel window no longer than 48 hours')
        if not 0 <= min_minutes <= 1440 or sort not in ('time_there','transfers','travel_time'):
            raise ValueError('invalid Explore constraints')
        digest = (Path(store)/'current').read_text().strip()
        _, (tables, stops, trips, zone, start, end) = snapshot(str(store), digest)
        origins = stop_ids(stops, origin)
        if not origins:
            raise ValueError('origin stop is not in this snapshot')
        # Short initial destination inventory, with rail stations and principal bus stops first.
        served = {r['stop_id'] for r in tables['stop_times']}
        candidates = sorted(served-origins, key=lambda k: (not any(w in stops[k]['stop_name'].lower() for w in ('station','jewish','bright meadow','massmutual')), stops[k]['stop_name']))[:24]
        for candidate in candidates:
            plan = round_trip(store, origin, candidate, leave_after, back_by, leave_after, back_by,
                              now=now, min_dwell_minutes=min_minutes)
            if plan['status'] == 'Unknown':
                result['unknown'].append({'destination':stops[candidate]['stop_name'], 'reason':plan['reason']})
            elif plan['status'] == 'Scheduled':
                a, b = plan['outbound'], plan['last_return']
                there = (instant(b[0]['departure'])-instant(a[-1]['arrival'])).total_seconds()/60
                travel = ((instant(a[-1]['arrival'])-instant(a[0]['departure']))+(instant(b[-1]['arrival'])-instant(b[0]['departure']))).total_seconds()/60
                result['results'].append(dict(destination_id=candidate, destination=stops[candidate]['stop_name'],
                    arrival=a[-1]['arrival'], usable_minutes=there, transfers=len(a)+len(b)-2,
                    travel_minutes=travel, last_departure=b[0]['departure'], home_arrival=b[-1]['arrival'], itinerary=plan))
        key = {'time_there':lambda r:-r['usable_minutes'], 'transfers':lambda r:r['transfers'], 'travel_time':lambda r:r['travel_minutes']}[sort]
        result['results'].sort(key=key)
        result['results'] = result['results'][:6]
        result.update(status='Scheduled' if result['results'] else 'Unknown', reason='Complete scheduled returns to the exact origin stop only. Other destinations or transfer links may be Unknown.')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result['reason'] = str(exc)
    return result
