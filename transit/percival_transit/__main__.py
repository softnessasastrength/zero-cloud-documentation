import argparse
import json
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from .core import SOURCE, board, import_feed, instant


def response(path, store):
    url = urlparse(path)
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
    imp.add_argument('--fixture', action='store_true')
    imp.add_argument('--accept-source-terms', action='store_true')
    dep = commands.add_parser('board')
    dep.add_argument('station', choices=['hartford', 'windsor-locks'])
    dep.add_argument('--at', type=instant)
    dep.add_argument('--hours', type=float, default=24)
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
                with urllib.request.urlopen(SOURCE, timeout=30) as stream:
                    raw = stream.read(20_000_001)
            if len(raw) > 20_000_000:
                raise ValueError('archive exceeds 20 MB')
            print(json.dumps(import_feed(raw, args.store, 'fixture:' + args.file if args.fixture else SOURCE, args.fixture), indent=2))
        except Exception as exc:
            print(json.dumps({'status': 'Unknown', 'error': str(exc), 'current_snapshot_unchanged': True}))
            return 1
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
