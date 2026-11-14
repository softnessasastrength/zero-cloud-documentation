# Percival Transit: local scheduled boards (v1)

First runnable P0/P1 slice for [issue #14](https://github.com/softnessasastrength/zero-cloud-documentation/issues/14), following the [mobility-first charter](https://github.com/softnessasastrength/zero-cloud-documentation/blob/docs/percival-mobility-first-charter/design/percival/mobility-first-charter-v0.1.md).

Python 3.11+ and system timezone data; no pip dependencies. The existing Metro simulator, launcher, Node dependencies, and running processes are untouched. Metro tiles, routing/return feasibility, chat, accessibility guarantees, fares, and realtime are follow-up work.

## Crostini: isolated checkout and dependencies

Run in the Linux Terminal. This creates a new directory rather than switching your Metro checkout.

```bash
git clone --branch feat/percival-transit --single-branch https://github.com/softnessasastrength/zero-cloud-documentation.git ~/percival-transit
cd ~/percival-transit/transit
sudo apt-get update
sudo apt-get install -y python3 python3-venv tzdata curl
python3 -m venv .venv
. .venv/bin/activate
python -m unittest discover -s tests -v
```

## Try the synthetic fixture first

**FICTIONAL FIXTURE: not actual trains, IDs, or service coverage.** The generated archive is deterministic and is never downloaded from an agency. Every fixture response includes `fixture: true`, a `fixture:` source, and IDs beginning with `fixture-`.

```bash
python fixtures/make_demo.py
python -m percival_transit --store /tmp/percival-demo import fixtures/demo.zip --fixture
python -m percival_transit --store /tmp/percival-demo board hartford --at 2026-11-15T00:00:00-05:00 --hours 1
python -m percival_transit --store /tmp/percival-demo board windsor-locks --at 2026-11-15T00:00:00-05:00 --hours 1
python -m percival_transit --store /tmp/percival-demo serve --port 8765
```

In a second Linux Terminal:

```bash
curl 'http://127.0.0.1:8765/v1/stations/hartford/departures?at=2026-11-15T05:00:00Z&hours=1'
curl 'http://127.0.0.1:8765/v1/stations/windsor-locks/departures?at=2026-11-15T05:00:00Z&hours=1'
```

Fixture snapshots become stale seven days after the last successful import too. Reimporting identical bytes keeps the original acquisition metadata and adds a separate successful source-check observation. Explicit `--at` timestamps query historical schedules but do not bypass freshness evaluated against the actual clock.

## Import the authoritative feed

Read the [CTtransit terms](https://www.cttransit.com/about/developers/terms-of-use) before downloading. After accepting them:

```bash
python -m percival_transit import --accept-source-terms
python -m percival_transit board hartford
python -m percival_transit board windsor-locks
python -m percival_transit serve --port 8765
```

In another terminal, query current departures:

```bash
curl 'http://127.0.0.1:8765/v1/stations/hartford/departures'
curl 'http://127.0.0.1:8765/v1/stations/windsor-locks/departures'
```

For an already downloaded, unmodified agency archive, use `python -m percival_transit import /path/to/hlgtfs.zip --accept-source-terms`. Do not import synthetic or third-party bytes as an agency archive. The importer records acquisition time, not an unverified publication time.

## Source inventory and verification (2026-11-14)

The official [CTtransit developer page](https://www.cttransit.com/about/developers) lists **https://ctrides.com/hlgtfs.zip** as the current Hartford Line static GTFS. Earlier hartfordline.com and cttransit-hosted archives are not used as silent fallbacks. The official developer page links its GTFS terms; this is an agency-specific license, not CC0. It permits limited, revocable use/reproduction/redistribution subject to its conditions, excludes trademarks and copyrighted materials, disclaims accuracy/currency, and reserves modification/revocation. Review the full terms, including the agreement/form requirement. No agency archive is redistributed in this PR.

**Real-feed smoke attempt:** download attempted on 2026-11-14 from the URL above using Python urllib, Node fetch, and the web tool. The shell could not resolve the host, Node fetch failed, and the web tool could not retrieve the ZIP. No real snapshot was acquired: snapshot date/hash, source station IDs, actual date coverage, operator/trip coverage, and real board results remain **unverified**. This is a blocked smoke check, not a pass. Run the import and both current boards above on Crostini and record their JSON provenance before relying on this slice. The API refuses absent station identities and expired calendar coverage.

Station aliases are `hartford` and `windsor-locks`; source IDs are discovered only from exact case-insensitive source names `Hartford` / `Hartford Union Station` and `Windsor Locks` / `Windsor Locks Station`, plus their declared child platforms. No production numeric IDs have been guessed. Each successful board reports its actual `source_stop_ids`; every departure reports its source stop, trip, route, service date, original GTFS time, source URL, snapshot SHA-256 and acquisition date. Exact-name mappings need confirmation against the first successfully downloaded agency snapshot. These boards cover only trips present in that snapshot; they do not claim all Amtrak or Connecticut rail services.

## Contract and limits

`GET /v1/stations/{hartford|windsor-locks}/departures?at=<ISO timestamp with offset>&hours=24`. Window is 0–48 elapsed hours. Defaults to current time and 24 hours. `Scheduled` (HTTP 200) means a valid fresh timetable, including an empty board when no service is scheduled. Calendar removal is absence of scheduled service, never a realtime cancellation claim. `Unknown` (HTTP 503) means missing, corrupt, stale, unsupported, unidentified station, or outside coverage; it has an explanatory `reason` and no departures. Bad parameter syntax returns 400; other paths 404. CLI boards exit 1 for Unknown. No endpoint emits live status; `live` is always false.

Archives live in `.percival-transit/<sha256>/feed.zip`, with read-only original bytes and metadata. Imports validate before atomically switching `current`; invalid downloads leave the last good snapshot intact. Each query rechecks SHA-256 and validation. Retention is manual; no automatic archive deletion. Acquisition metadata is first-write and identical bytes retain the original timestamp; immutable source-check observations separately record successful revalidation. A failed refresh leaves the explicitly dated last-known-good snapshot usable until seven days after its last successful source check. Seven days is a conservative application policy, not an agency refresh promise. Filesystem owners can change permissions; this is content-addressed local storage, not tamper-proof storage.

Validation covers required tables, primary/foreign keys, timezone, dates, exceptions, source times and monotonic stop sequences. Calendar-dates-only feeds work. Pickup-restricted stops are not advertised as ordinary departures. Frequency-based feeds, blank/interpolated times and GTFS times beyond 47:59:59 are rejected rather than estimated. One agency timezone is supported; no timezone is hardcoded for real data. Dates use agency-local service days; event instants use GTFS local noon minus 12 elapsed hours, then add GTFS elapsed seconds in UTC. Previous service dates are scanned for >24:00 events. Coverage bounds are calendar bounds, including exceptions; a gap inside them is a valid empty service day. A query crossing the final coverage day is Unknown rather than silently truncated. Static data cannot prove operation, delays or cancellations.

## Validation and platform status

See `VALIDATION.md` for exact executed checks. The deterministic suite includes both station boards, provenance, overnight dates, spring/fall DST, holiday addition/removal, exception-only calendars, invalid feeds, checksum corruption, immutable reimports, stale/missing snapshots and API responses. No Lumia support is claimed.

Desktop Linux uses the same Python commands. Android Termux: `pkg install python tzdata git`, clone into a separate directory, `cd percival-transit/transit`, then run the Python commands above (venv optional). Termux and Chromebook hardware, Chrome-to-Crostini localhost forwarding, package installation and real agency downloads still require device verification.

## Three-feed preview and Explore

Source verification is now recorded in [SOURCES.md](SOURCES.md), superseding the initial blocked-smoke note above. Official downloads succeeded in Actions. Bus imports maintain independent stores under the root store:

```bash
python -m percival_transit import --feed cttransit --accept-source-terms
python -m percival_transit import --feed pvta --accept-source-terms
python -m percival_transit catalog pvta
python -m percival_transit departures pvta G5 1862 --at 2026-11-13T04:00:00-05:00
python -m percival_transit departures cttransit 16545 7919 --at 2026-11-13T04:00:00-05:00
python -m percival_transit explore pvta 10006 --leave-after 2026-11-13T06:00:00-05:00 --back-by 2026-11-13T18:00:00-05:00 --min-minutes 60
```

The selected-route compiler validates the requested route subset and its source dependencies, not every unrelated route in a statewide archive. Catalogs expose actual route IDs, direction/headsign patterns and served stops. `/v1/feeds/{rail|cttransit|pvta}/catalog` and `/departures?route_id=...&stop_id=...&direction_id=...&at=...` use the same data as the CLI. `/v1/explore?feed=pvta&origin=10006&leave_after=...&back_by=...&min_minutes=60&sort=time_there` returns up to six complete same-feed round trips among an initial 24 destination candidates. Sort also accepts `transfers` and `travel_time`. Every leg resolves to a source trip, dated service and snapshot. Same-stop transfers obey the user's margin and applicable source transfer rules; no coordinate-based walking edges are inferred. NYP/BOS and cross-agency links remain Unknown with named missing evidence.
