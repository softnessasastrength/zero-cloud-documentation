# Validation record — 2026-11-14

Environment: available Linux sandbox, Python 3.13. Existing Metro checkout and Chromebook launcher worktree were inspected and left unchanged. Remote branch inventory and open PR search were read before edits; the open compound-map PR #3 remains separate. Base: main `8d71c15`. New worktree: `/home/brandenalgo/percival-transit`, branch `feat/percival-transit`.

Executed from `transit/`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m unittest discover -s tests -v
python fixtures/make_demo.py
python -m percival_transit --store /tmp/percival-demo-v2 import fixtures/demo.zip --fixture
python -m percival_transit --store /tmp/percival-demo-v2 board hartford --at 2026-11-15T00:00:00-05:00 --hours 1
python -m percival_transit --store /tmp/percival-demo-v2 board windsor-locks --at 2026-11-15T00:00:00-05:00 --hours 1
```

Result: all 8 tests passed. Synthetic snapshot SHA-256 `d075a5450db0587cd951c450f78280d82d1b6c0486e464b3d02b797fc4342caf`, acquired `2026-11-14T21:40:25.357249+00:00`. Hartford: Scheduled 00:30 -05:00; Windsor Locks: Scheduled 00:50 -05:00; both source trip `fixture-overnight`, service date 2026-11-14. These are fictional test results, not agency trains.

`python -m percival_transit --store /tmp/percival-demo serve --port 8765` was attempted. Sandbox socket creation failed with `PermissionError: Operation not permitted`. Both documented curl URLs were attempted and failed to connect. API route, status, query parsing, and both response payloads passed direct deterministic handler tests; network-level API serving is **not verified** here.

The authoritative `https://ctrides.com/hlgtfs.zip` download was attempted via Python urllib, Node fetch and web retrieval. DNS/network access failed; no authoritative snapshot/date/hash or real-feed board result exists. The production import command also fails explicitly with Unknown and preserves the current pointer. Feed URL and linked licensing were checked on CTtransit's official developer/terms pages. Real station IDs and actual coverage remain unverified pending a successful download.

Dependencies were already available and venv creation succeeded. System package installation requires the user's Crostini environment; sudo/package management is not available for this sandbox validation. The documented clone uses a new directory and must be run after the branch is published. Chrome localhost forwarding, both actual HTTP queries, agency archive compatibility, production stop-name mappings and current service coverage require Chromebook verification. Termux and Python 3.11 compatibility have not been device-tested.

## Published timetable precedence

Use the agency PDF timetable applicable to the travel date as the preferred
schedule evidence. Check the agency's date-specific exceptions and service
notices before applying the regular PDF. Preserve day-of-week restrictions,
train or bus numbers, direction, boarding locations, and substitution notes.
Record the PDF URL, effective dates, page and service section for each
cross-check. GTFS can supply machine-readable schedules and stop identifiers.
When an applicable PDF and GTFS disagree, use the published timetable for
verified entries and show Unknown where the discrepancy cannot be resolved.
A static timetable establishes scheduled service only.

### Hartford Line sample check

For Friday, November 13, 2026, compare the
[applicable Hartford Line PDF, page 1](https://hartfordline.com/wp-content/uploads/2026/11/HL-112-1115-End-Bus-Substitutions_v2.pdf)
with the [source and HTTP smoke report](https://github.com/softnessasastrength/zero-cloud-documentation/actions/runs/43644898840).

| Station | Sample scheduled departure | PDF section | GTFS stop | API |
| --- | --- | --- | --- | --- |
| Hartford Union Station | 5:35 a.m. | Weekday southbound | 6 | HTTP 200, 17 departures |
| Windsor Locks | 8:49 a.m. | Weekday northbound | 8 | HTTP 200, 12 departures |

The smoke queried a 24-hour window starting at 5:00 a.m. Eastern. The two
sample times agree. Counts describe the GTFS-backed board and do not establish
full parity with the PDF, which lists multiple operators and substitutions.
The download was acquired November 14, 2026, from
`https://ctrides.com/hlgtfs.zip` with SHA-256
`03e8bc27defd6b3a501c760592ad0ed196b5b88db0a5380ba855e55c999f9d0d`.

Use the [official schedule index](https://hartfordline.com/fares-schedules/)
to select the PDF for a new travel date. The agency publishes a separate
[November 16 timetable](https://hartfordline.com/wp-content/uploads/2026/11/HL-1116-New-Service-Portal-North-Bridge-Outage-Ends_v1.pdf).
The current CLI and API still read GTFS. PDF ingestion and runtime precedence
remain implementation work.

### Discrepancies to cover in the PDF-backed boards

The same weekday southbound PDF table lists a 5:59 a.m. Windsor Locks
departure. The GTFS smoke query began at 5:00 a.m. Eastern, but its board
has no 5:59 a.m. entry. The 8:49 a.m. Windsor Locks time is in the PDF's
northbound table, whose column continues to Springfield. The corresponding
GTFS smoke row says “Northbound to Hartford,” and its trip ID also appears
at Windsor Locks after the Hartford stop. A board should derive the trip's
onward destination from the applicable timetable or verified stop sequence
when the feed headsign conflicts. Copying the feed headsign into that board
would give riders the wrong destination.

The PDF-backed acceptance check should exercise both differences, preserve
the effective-period boundary on November 16, and check published
substitution notes before treating a timetable column as a train.
