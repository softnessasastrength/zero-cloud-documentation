"""Reproducible source and HTTP smoke report; never substitutes fixture data."""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import csv
import io
import zipfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from .core import SOURCE, TERMS, board, import_feed, instant, load


def http_boards(store, at):
    # Port 0 lets the OS choose a free loopback port. Read it from the child.
    process = subprocess.Popen([sys.executable, '-m', 'percival_transit', '--store', str(store),
                                'serve', '--port', '0'], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True)
    try:
        line = process.stdout.readline().strip()
        if not line.startswith('Percival API: http://127.0.0.1:'):
            raise RuntimeError('API startup failed: ' + process.stderr.read()[-2000:])
        base = line.split('Percival API: ', 1)[1]
        result = {}
        for station in ('hartford', 'windsor-locks'):
            url = base + '/v1/stations/' + station + '/departures?hours=1&at=' + at.isoformat().replace('+00:00', 'Z')
            try:
                response = urllib.request.urlopen(url, timeout=10)
            except urllib.error.HTTPError as exc:
                response = exc
            with response:
                result[station] = {'http_status': response.code, 'body': json.load(response)}
        return result
    finally:
        process.terminate()
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()


def run(fixture=False, raw=None):
    now = datetime.now(timezone.utc)
    report = dict(checked_at=now.isoformat(), source='fixture:generated-demo' if fixture else SOURCE,
                  terms=None if fixture else TERMS, fixture=fixture, result='Unknown')
    try:
        if raw is None:
            if fixture:
                import io
                from fixtures.make_demo import build
                buffer = io.BytesIO()
                build(buffer)
                raw = buffer.getvalue()
            else:
                with urllib.request.urlopen(SOURCE, timeout=30) as response:
                    report['resolved_url'] = response.url
                    raw = response.read(20_000_001)
        report['sha256'] = hashlib.sha256(raw).hexdigest()
        report['snapshot_date'] = now.isoformat()
        if len(raw) > 20_000_000:
            raise ValueError('archive exceeds 20 MB')
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            report['archive_files'] = archive.namelist()
            report['source_inventory'] = {name: list(csv.DictReader(io.StringIO(archive.read(name).decode('utf-8-sig'))))
                for name in ('stops.txt', 'agency.txt', 'routes.txt', 'feed_info.txt') if name in archive.namelist()}
        tables, stops, trips, zone, start, end = load(raw)
        report.update(agency_timezone=str(zone), coverage_start=str(start), coverage_end=str(end),
                      agencies=tables['agency'], routes=tables['routes'], trip_count=len(trips),
                      source_stops=[{'stop_id': k, 'stop_name': r['stop_name'],
                                     'parent_station': r.get('parent_station', '')} for k, r in stops.items()])
        at = instant('2026-11-15T05:00:00Z') if fixture else now
        with tempfile.TemporaryDirectory(prefix='percival-smoke-') as temp:
            import_feed(raw, temp, report['source'], fixture, now.isoformat())
            report['boards'] = {s: board(temp, s, at=at, now=now, hours=1)
                                for s in ('hartford', 'windsor-locks')}
            report['http'] = http_boards(temp, at)
            for station, direct in report['boards'].items():
                wire = report['http'][station]
                if direct['status'] != 'Scheduled' or wire['http_status'] != 200:
                    raise ValueError(station + ': ' + direct['reason'])
                if wire['body']['departures'] != direct['departures']:
                    raise ValueError('HTTP/direct departure mismatch: ' + station)
                if not fixture and direct['fixture']:
                    raise ValueError('fixture substitution')
        report['result'] = 'Passed'
    except Exception as exc:
        report['error'] = str(exc)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', action='store_true')
    parser.add_argument('--accept-source-terms', action='store_true')
    parser.add_argument('--output', default='smoke-report.json')
    args = parser.parse_args()
    if not args.fixture and not args.accept_source_terms:
        parser.error('read source terms, then pass --accept-source-terms')
    report = run(args.fixture)
    Path(args.output).write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['result'] == 'Passed' else 1


if __name__ == '__main__':
    sys.exit(main())
