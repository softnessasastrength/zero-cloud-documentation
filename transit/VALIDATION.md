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
