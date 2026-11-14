# Chromebook Transit preview

Review the stacked drafts: engine/source #18, Metro/launcher #20. The original ZeroCloud menu options and simulator are preserved. Transit uses a separate checkout and ports 4183 (Metro) / 8765 (read-only API), with no Ollama dependency.

## One-command launcher

The delivery message provides an immutable commit-pinned command. To review the current draft branch from Crostini:

```bash
curl -fsSL https://raw.githubusercontent.com/softnessasastrength/zero-cloud-documentation/feat/percival-metro-preview/playground/scripts/percival-chromebook.sh -o /tmp/percival-transit-preview-launcher.sh && bash /tmp/percival-transit-preview-launcher.sh
```

Choose **4) Launch Transit preview**. Review the linked CTtransit and PVTA terms before accepting the feed refresh. Terminal may request sudo for missing Debian packages. The script validates each feed independently; a failed refresh preserves its last valid snapshot. It prints and attempts to open **http://localhost:4183/#/transit** in Chrome. Keep Terminal open; Ctrl+C stops only the two servers started by this Transit session. Existing services on either port are preserved and cause a clear startup refusal.

Code checkouts live under `~/.local/share/percival-chromebook/transit-previews/<version>/`; durable GTFS data under `~/.local/share/percival-chromebook/transit-data/`. Existing resort data and `$ROOT/metro` are untouched. Rerunning a pinned version reuses its clean checkout, dependencies and saved data; edits or a wrong pinned HEAD cause a refusal, never a reset. For code upgrades, use the new commit-pinned delivery command to get a new version directory. Feed data remains shared across preview versions. Failed refreshes never become synthetic trains.

The pinned preferred stops are based on the exact agency IDs in SOURCES.md. New feeds with changed stop/route IDs yield Unknown until reverified. Bright Meadow has no campus bus service on the sampled Saturday; Jewish Home still has G5 service. Each row displays the actual downstream-campus pattern, destination, trip/service date and hash. Some G5 morning trips bypass Jewish Home; some terminate there. Do not infer continuation from the route number alone.

## Explicit commands (no launcher, no Ollama)

From a separate clone of this preview branch:

```bash
sudo apt-get update
sudo apt-get install -y git curl python3 python3-venv tzdata
cd transit
python3 -m venv .venv
. .venv/bin/activate
python -m unittest discover -s tests -v
python -m percival_transit import --accept-source-terms
python -m percival_transit import --feed cttransit --accept-source-terms
python -m percival_transit import --feed pvta --accept-source-terms
python -m percival_transit board hartford --at 2026-11-13T05:00:00-05:00
python -m percival_transit board windsor-locks --at 2026-11-13T05:00:00-05:00
python -m percival_transit departures cttransit 16545 13577 --at 2026-11-13T04:00:00-05:00
python -m percival_transit departures pvta G5 1862 --at 2026-11-13T04:00:00-05:00
python -m percival_transit explore pvta 10006 --leave-after 2026-11-13T06:00:00-05:00 --back-by 2026-11-13T18:00:00-05:00 --min-minutes 60
python -m percival_transit serve --port 8765
```

In a second terminal with Node 22 installed:

```bash
cd playground
npm ci
npm run build
PERCIVAL_TRANSIT_PORT=8765 npm run preview -- --host 127.0.0.1 --port 4183 --strictPort
```

Query either API path through the same-origin Metro proxy:

```bash
curl 'http://127.0.0.1:4183/transit-api/v1/stations/hartford/departures?at=2026-11-13T10:00:00Z'
curl 'http://127.0.0.1:4183/transit-api/v1/stations/windsor-locks/departures?at=2026-11-13T10:00:00Z'
curl 'http://127.0.0.1:4183/transit-api/v1/feeds/pvta/departures?route_id=G5&stop_id=1862&at=2026-11-13T09:00:00Z'
```

## Explore and limits

Explore defaults to the exact Bright Meadow or Jewish Home G5 stop. Enter the leave-after and back-by timestamps with an explicit offset for the chosen date, and a minimum usable time at the destination. The deterministic planner checks both legs and any same-stop transfer margins, including the final trip to that exact origin. It searches the initial 24 supported same-feed destination candidates and returns up to six, sorted by usable time, transfers or travel time. Expand any result to see the source legs and last usable return.

The intercity controls allow switching NYP/BOS, origin and leave-after/arrive-by constraints, but return **Unknown**, naming missing Amtrak schedule/terms and pedestrian links. No complete intercity itinerary, fare, seat availability, booking or proof of impossibility is claimed. Ticket information links to Amtrak. Cross-agency walking transfers at Bright Meadow and Windsor Locks are also Unknown pending exact path/time verification, despite agency statements that connections exist. These remain unfinished release work, not simulated successes.

Offline: the production service worker caches the Metro shell, never transit API responses. The app separately stores exact-query last-known boards and catalogs. Cached rows are labelled with their query time, original snapshot and last source check. A new query cannot reuse an unrelated response. Expired source checks or query windows become Unknown. Cached data cannot verify cancellation or current operation.

## Reproducible checks

```bash
cd transit
python3 -m unittest discover -s tests -v
python3 -m percival_transit.smoke --fixture --output /tmp/fixture-smoke.json
python3 -m percival_transit.smoke --accept-source-terms --at 2026-11-13T05:00:00-05:00 --output /tmp/rail-smoke.json
python3 -m percival_transit.bus_smoke cttransit
python3 -m percival_transit.bus_smoke pvta
cd ../playground
npm run lint
npm run typecheck
npm test
npm run build
npx playwright install --with-deps chromium
npm run test:e2e
npm run test:api
node simulator/pwa-smoke.mjs
python3 scripts/transit-launcher-smoke.py
node scripts/transit-real-smoke.mjs
```

The local restricted sandbox can run deterministic Python/TypeScript/unit/build checks but cannot bind servers or resolve feed hosts. Actions is used for real downloads, loopback API checks, launcher process lifecycle and Chromium. `transit/SOURCES.md` records dated source evidence and known PDF conflicts. Physical Chromebook checks remain: package installation on the actual Debian container, ChromeOS localhost forwarding, xdg-open launching Chrome, touch/keyboard use, app installation, offline recovery and suspend/resume. Linux/Chromium results are not hardware validation.
