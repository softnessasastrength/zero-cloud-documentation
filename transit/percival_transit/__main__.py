import argparse
import json
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from .core import SOURCE, board, import_feed, instant
from .planner import round_trip, stations
from .feeds import FEEDS, catalog, departures, feed_store


def response(path, store):
    url = urlparse(path)
    segments = url.path.strip('/').split('/')
    if len(segments) == 4 and segments[:2] == ['v1', 'feeds'] and segments[2] in FEEDS:
        feed = segments[2]
        if segments[3] == 'catalog':
            return 200, catalog(store, feed)
        if segments[3] == 'departures':
            query = parse_qs(url.query)
            try:
                if set(query) - {'route_id', 'stop_id', 'direction_id', 'at'} or any(len(v) != 1 for v in query.values()):
                    raise ValueError('invalid parameters')
                result = departures(store, feed, query['route_id'][0], query['stop_id'][0], query.get('direction_id', [None])[0], instant(query['at'][0]) if 'at' in query else None)
                return (200 if result['status'] == 'Scheduled' else 503), result
            except (KeyError, ValueError) as exc:
                return 400, {'error': str(exc)}
    if url.path == '/v1/health':
        return 200, {'api_version': 'v1', 'service': 'percival-transit', 'live': False}
    if url.path == '/v1/stations':
        return 200, stations(store)
    if url.path == '/v1/round-trip':
        query = parse_qs(url.query)
        required = {'origin', 'destination', 'depart_after', 'arrive_by', 'return_after', 'return_by'}
        try:
            if not required <= set(query) or set(query) - required - {'margin_minutes'} or any(len(v) != 1 for v in query.values()):
                raise ValueError('provide origin, destination and all four offset timestamps')
            values = {k: instant(query[k][0]) for k in required - {'origin', 'destination'}}
            result = round_trip(store, query['origin'][0], query['destination'][0], **values, margin_minutes=float(query.get('margin_minutes', ['10'])[0]))
            return (503 if result['status'] == 'Unknown' else 200), result
        except ValueError as exc:
            return 400, {'error': str(exc)}
    parts = url.path.strip('/').split('/')
    if len(parts) != 4 or parts[:2] != ['v1', 'stations'] or parts[3] != 'departures':
        return 404, {'error': 'Use /v1/stations/{hartford|windsor-locks}/departures'}
    query = parse_qs(url.query)
    try:
        if set(query) - {'at', 'hours'} or any(len(v) != 1 for v in query.values()):
            raise ValueError('unsupported or repeated parameter')
        at = instant(query['at'][0]) if 'at' in query else None
        result = board(store, parts[2], at=at, hours=float(query.get('hours', ['24'])[0]))
        return (200 if result['status'] == 'Scheduled' else 503), result
    except ValueError as exc:
        return 400, {'error': str(exc)}


def main():
    parser = argparse.ArgumentParser(description='Percival: scheduled-only local Hartford Line boards')
    parser.add_argument('--store', default='.percival-transit')
    commands = parser.add_subparsers(dest='command', required=True)
    imp = commands.add_parser('import')
    imp.add_argument('file', nargs='?')
    imp.add_argument('--feed', choices=FEEDS, default='rail')
    imp.add_argument('--fixture', action='store_true')
    imp.add_argument('--accept-source-terms', action='store_true')
    bus = commands.add_parser('departures')
    bus.add_argument('feed', choices=FEEDS)
    bus.add_argument('route_id')
    bus.add_argument('stop_id')
    bus.add_argument('--direction-id')
    bus.add_argument('--at', type=instant)
    cat = commands.add_parser('catalog')
    cat.add_argument('feed', choices=FEEDS)
    dep = commands.add_parser('board')
    dep.add_argument('station', choices=['hartford', 'windsor-locks'])
    dep.add_argument('--at', type=instant)
    dep.add_argument('--hours', type=float, default=24)
    plan = commands.add_parser('plan')
    plan.add_argument('origin')
    plan.add_argument('destination')
    for name in ('depart-after', 'arrive-by', 'return-after', 'return-by'):
        plan.add_argument('--' + name, type=instant, required=True)
    plan.add_argument('--margin-minutes', type=float, default=10)
    api = commands.add_parser('serve')
    api.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    if args.command == 'import':
        try:
            if not args.fixture and not args.accept_source_terms:
                parser.error('read the source terms in README.md and pass --accept-source-terms')
            if args.fixture and not args.file:
                parser.error('--fixture requires a local fixture file')
            if args.file:
                raw = Path(args.file).read_bytes()
            else:
                with urllib.request.urlopen(FEEDS[args.feed]['url'], timeout=45) as stream:
                    raw = stream.read(20_000_001)
            if len(raw) > 20_000_000:
                raise ValueError('archive exceeds 20 MB')
            print(json.dumps(import_feed(raw, feed_store(args.store, args.feed), 'fixture:' + args.file if args.fixture else FEEDS[args.feed]['url'], args.fixture, selection=None if args.fixture else FEEDS[args.feed]['routes'], terms=FEEDS[args.feed]['terms']), indent=2))
        except Exception as exc:
            print(json.dumps({'status': 'Unknown', 'error': str(exc), 'current_snapshot_unchanged': True}))
            return 1
    elif args.command == 'catalog':
        print(json.dumps(catalog(args.store, args.feed), indent=2))
    elif args.command == 'departures':
        result = departures(args.store, args.feed, args.route_id, args.stop_id, args.direction_id, args.at)
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'Scheduled' else 1
    elif args.command == 'plan':
        result = round_trip(args.store, args.origin, args.destination, args.depart_after, args.arrive_by, args.return_after, args.return_by, args.margin_minutes)
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'Scheduled' else 1
    elif args.command == 'board':
        result = board(args.store, args.station, at=args.at, hours=args.hours)
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'Scheduled' else 1
    else:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                status, result = response(self.path, args.store)
                raw = json.dumps(result).encode()
                self.send_response(status)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Cache-Control', 'no-store')
                self.send_header('Content-Length', str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)
        server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
        print(f'Percival API: http://127.0.0.1:{server.server_port}', flush=True)
        server.serve_forever()
    return 0


if __name__ == '__main__':
    sys.exit(main())
