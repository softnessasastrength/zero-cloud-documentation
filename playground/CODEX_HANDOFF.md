# Codex Handoff — ZeroCloud Metro Playground Verification Pass

**Date:** 2026-11-14 · **Agent:** Muse (Ember) · **Branch:** `metro-verification_muse`
**Scope:** verification and small fixes only. No Priority C feature build-out was started.

## Verification results (this pass, Node v24.22.1 sandbox, `npm ci` from the committed lockfile)

| Suite | Command | Before | After fixes |
| --- | --- | --- | --- |
| Typecheck | `npm run typecheck` | **FAIL** — 5 × TS6133 dead imports | PASS |
| Lint | `npm run lint` | **FAIL** — same 5 unused vars | PASS |
| Unit/integration | `npm test` (Vitest) | PASS — 14 tests, 5 files | PASS — 14 tests, 5 files |
| Resort engine | `npm run test:sim` | PASS — 4 tests | PASS — 4 tests |
| API smoke | `npm run test:api` | PASS — replay hash `29176a953324…` | PASS — same hash |
| PWA smoke | `npm run test:pwa` | PASS | PASS |
| Production build | `npm run build` | not run pre-fix (blocked by typecheck in `tsc -b`) | PASS |
| E2E | `npm run test:e2e` (Playwright) | **FAIL** — 2 passed / 4 failed | **PASS — 6/6** (see caveat) |

**E2E caveat:** Playwright's headless-shell artifact is not downloadable in the
sandbox (`npx playwright install chromium` fails on the CDN fetch), so e2e was
run against the full Chromium build already present in the local browser cache
via a temporary config that only overrode `launchOptions.executablePath`. The
temporary config was deleted after the run; no repo file carries it. On a
normal development machine the stock path stands:
`npx playwright install chromium && npm run test:e2e`.

## Fixes in this branch (each verified by re-running the affected suites)

1. **Dead imports removed** — `src/App.tsx` (`lazy`, `Suspense`) and
   `src/pages/Start.tsx` (`useEffect`, `getResortSnapshot`, `ResortState`).
   These were the sole cause of the typecheck and lint failures.
2. **Resort screens wired into the router** — `src/pages/ResortMetro.tsx`
   exports complete `ResortMetro`, `MissionControl`, and `EngineeringConsole`
   components, but `App.tsx` never imported them; `/resort`, `/engineering`,
   and the Mission Control link all fell through to "Page not found." This
   broke the documented user flow (README "Try it" step 7;
   `scripts/percival-chromebook.sh` directs users to `/#/resort`) and 4 of 6
   e2e tests. Added routes `/resort`, `/mission-control`, `/engineering` and
   matching pivot-nav entries.
3. **Mission Control garden-table metric** — `src/pages/ResortMetro.tsx`:
   the metric counted only reservations whose window contains the current
   virtual minute, so a confirmed 14:00 booking viewed at the fixture's 13:00
   start rendered `0/2`, contradicting its own "live reservation state" label
   and every sibling metric (breaks protected, clanker assignment, credits all
   reflect the booking immediately). It now counts the table's held
   reservations; the facility map still distinguishes occupied vs booked.
4. **Ambiguous e2e locator scoped (test-side fix)** — `e2e/resort.spec.ts`:
   the Fault Lab renders one fault button per clanker by design, so after
   Percival's repair two `inject fault` buttons exist and the bare locator
   strict-mode-fails. The assertion is now scoped to Percival's
   `.fleet-control-row`. The app's per-clanker fault controls were left as
   designed; the domain fault policy is covered by `tests/resort.test.ts`.

## Reproduce

```bash
cd playground
npm ci
npm run typecheck && npm run lint && npm test && npm run test:sim
npm run test:api && npm run test:pwa && npm run build
npx playwright install chromium && npm run test:e2e   # needs Playwright CDN access
```

## Scoped for Codex (found during this pass — deliberately NOT built here)

1. **Resort stylesheet is missing entirely.** None of the ~60 class names used
   by `ResortMetro` / `MissionControl` / `EngineeringConsole` (`metro-panel`,
   `mc-hero`, `engineering-grid`, `fault-panel`, `booking-panel`, …) have any
   rule in `src/styles.css`. The screens are functional but render unstyled.
   This is design + CSS work against `design/metro/metro-hardware-simulation-v1.md`.
2. **Start-page resort tiles do not consume the resort API.**
   `docs/METRO_V1_IMPLEMENTATION.md` states Start tiles display values derived
   from resort API entities; `Start.tsx` does not call `resort-api` at all
   (its unused imports, removed above, were the residue). Implement the wiring
   or correct the doc.
3. **Bundle size / code-splitting.** Production JS: `index` 491.75 kB +
   `ChartView` 368.85 kB minified. `App.tsx` imports every page eagerly; the
   dead `lazy`/`Suspense` imports suggest splitting was intended. ROADMAP
   already lists lazy-loaded charts as next work.
4. **ROADMAP "Next" features remain unimplemented** (per README scope):
   recurrence/date calendars, genuine room and vehicle reservations, PBX
   queues, persistent research notes, occupancy/event-readiness models,
   richer experiment registry, full keyboard/touch audit, broader e2e.
5. **Accessibility validation backlog** (from `docs/ACCESSIBILITY.md`):
   screen-reader audit, automated contrast audit across custom accents,
   browser-zoom testing, real-device touch testing. Reduced-motion support
   exists (`@media (prefers-reduced-motion: reduce)` in `styles.css`).
6. **Hardware: no claims.** Per `docs/HARDWARE_COMPATIBILITY.md`, Android PWA,
   Chromebook/Crostini, and desktop have no device smoke tests; Windows Phone
   8.x / Windows 10 Mobile are research-only with no handset, OS build, SDK,
   signing, or TLS validation. Lumia/KaiOS investigation needs named hardware
   and a separate plan — nothing in this pass changes that.

## Priority C state, as found in code (for planning)

- **Panoramic navigation:** implemented — Start renders grouped tile
  panoramas; the pivot nav and panorama scroll horizontally; tile editing,
  drag + keyboard/touch move alternatives, named persistent layouts.
- **Live tiles:** implemented with clearly labelled synthetic data — tiles
  render live simulation metrics with a `SIM` tag; resort tiles are the
  exception (see scoped item 2).
- **Responsive layouts:** implemented — breakpoints at 650px / 1000px /
  1550px; e2e passes on desktop and Pixel 7 viewports.
- **Accessibility / reduced-motion:** baseline implemented (skip link,
  semantic landmarks, labelled controls, focus outlines, reduced-motion
  media query); audit-level validation outstanding (scoped item 5).
- **Resort simulation:** implemented and deterministic — seeded fixtures
  (20261114/15/16), versioned commands, JSONL journal, replay hash verified
  identical across runs in this pass; UI screens were unrouted until fix 2
  and are unstyled until scoped item 1.

## Chunk log (CODEX_CHUNKS.md)

### Z-08 — Resort-sourced tile metrics · 2026-11-15 · Ember (Muse) · branch `metro-z08_muse`

- **Base:** `main` (this PR targets `main` directly; no
  stack, no retarget cascade). The card declares "Depends
  on: None" and the chunk book's ordering note calls Z-08
  independent; the files it names (`src/domain/models.ts`,
  `src/pages/Start.tsx`, `tests/ui.test.tsx`) were verified
  byte-identical between `main` and the stack head
  `metro-z07_muse` by git blob SHA-1 — across the whole
  repo the two trees differ only in `src/styles.css` and
  this log. This entry therefore opens the chunk-log
  section on `main`; when PR #26 lands, its Z-01 entry
  appends under the same heading (a possible one-line
  merge adjacency in this log file, flagged in the PR
  body). All 62 tracked playground files were verified
  byte-identical to the `main` tree by git blob SHA-1
  before editing (100 tracked blobs repo-wide, 0
  mismatches).
- **Before this chunk:** `Start.tsx` derived every tile
  value from the household simulation store (`metric()`
  over `clock`, `fleet`, `tasks`, `alerts`, `energy`) and
  never called the resort API — the gap
  `docs/METRO_V1_IMPLEMENTATION.md` glosses over and Z-10
  reconciles. The tile metric enum had no resort kinds,
  so no tile could name resort state at all.
- **Wired:** `tileSchema`'s metric enum gains
  `resort-reservations` and `resort-clankers`.
  `Start.tsx` polls `getResortSnapshot()` from
  `src/domain/resort-api.ts` on mount and every 2.5s
  (the `useResort` cadence) and resolves resort tiles
  from that snapshot with Mission Control's own
  derivations, so a tile cannot disagree with
  `/mission-control`: held reservations = reservation
  IDs held on tables that resolve in
  `state.reservations`; available clankers =
  `status==='available'`. The tile editor's "Live
  content" select offers the new kinds.
- **Honesty states (the chunk's point):** a fresh
  snapshot shows the derived count under the tile's
  existing `SIM` tag; a cached snapshot (simulator
  unreachable, cache present — `getResortSnapshot()`'s
  `stale` path) shows the count with `· cached`
  appended to the caption, so the stale state is
  visible on the tile; a failed poll after a value was
  shown keeps the last value but flips it to the same
  `· cached` marking rather than presenting it as
  live; with no snapshot at all the tile shows the
  explicit label `unavailable` ("resort data
  unavailable") and no numeric value — never a
  fabricated number. Household metrics are untouched.
- **Suites (baseline on unmodified `main` reproduced
  first — identical results):** `npm run typecheck`
  PASS; `npm run lint` PASS; `npm test` PASS — 17
  tests, 5 files (14 baseline + 3 new in
  `tests/ui.test.tsx`: a stubbed snapshot renders the
  derived counts, 2 held / 1 available; API failing
  with no cache renders `unavailable` with no digit
  anywhere in the tile's number block; API failing
  with a seeded cache renders the cached count with
  `· cached`). The existing Start tile-editing test
  passes unmodified. `npm run build` PASS.
  `npm run test:e2e` PASS — 6/6 (desktop + Pixel 7).
  A throwaway browser probe (deleted after the run)
  drove the real editor against the seeded simulator:
  a tile rebound to `resort-reservations` showed
  `0reservations held`; rebound to `resort-clankers`
  it showed `2resort clankers available` — the
  seed-20261114 state, derived live.
- **Residual limits:** e2e and the probe ran against
  the full Chromium build already in the local browser
  cache (chromium-1255) via a temporary config that
  only overrode `launchOptions.executablePath`; the
  temporary config and probe were deleted after their
  runs and no repo file carries them — no device
  result is claimed. No default layout gains resort
  tiles here (that is Z-09, which also owns the
  saved-layout guarantee); a resort tile exists only
  when a user assigns one in the editor. The doc
  sentence that overclaims this wiring is Z-10's to
  fix.

### Z-09 — Resort tiles in the default Start layout · 2026-11-15 · Ember (Muse) · branch `metro-z09_muse`

- **Base:** `metro-z08_muse` (PR #33; this PR targets
  it and lands after it). The card declares "Depends
  on: Z-08", and the dependency is real in the code:
  the seeded tiles bind the `resort-reservations` /
  `resort-clankers` metrics Z-08 added to the tile
  enum and resolves in `Start.tsx`; a default layout
  naming them cannot exist on any earlier tree. All
  62 tracked playground files were verified
  byte-identical to the `metro-z08_muse` tree by git
  blob SHA-1 before editing (100 tracked blobs
  repo-wide, 0 mismatches).
- **Before this chunk:** the seeded default tile set
  (`initialTiles` in `src/domain/seed.ts`) held 15
  household / hospitality / infrastructure tiles and
  no resort tile; a resort tile existed only when a
  user assigned one in the editor (Z-08).
- **Seeded:** the `modules` table in `seed.ts` gains
  two entries, appended after the existing 15 (which
  keep their ids, order, and every field):
  `Reservations` (id `reservations`, label
  `ZeroReservations`, metric `resort-reservations`)
  and `ResortFleet` (id `resortfleet`, label
  `ZeroResortFleet`, metric `resort-clankers`), both
  group `Resort`, both routing to `/resort`, size
  `medium`, colours from the existing palette
  (`#a36a16`, `#6845b8`). The `Resort` group renders
  after Infrastructure on a fresh Start page.
- **Fresh vs saved (the chunk's guarantee):** no
  store change was needed and none was made. The
  persist middleware (zustand, `src/state/store.ts`)
  distinguishes the two states by construction: with
  no stored `workspace` record, the store is created
  with `tiles: initialTiles`, so fresh state gets the
  new seed; with a stored record, rehydration
  replaces `tiles` wholesale with the saved array —
  there is no merge, migration, or injection path
  anywhere in the store. The card's stop condition
  (the store cannot distinguish fresh state from a
  saved layout) does not arise.
- **Suites (baseline on unmodified `metro-z08_muse`
  reproduced first — typecheck PASS, lint PASS,
  Vitest 17/17, build PASS, e2e 6/6):** `npm run
  typecheck` PASS; `npm run lint` PASS; `npm test`
  PASS — 19 tests, 5 files (17 baseline + 2 new in
  `tests/ui.test.tsx`: fresh state — the seed's id
  list is pinned (the 15 existing ids plus
  `reservations` and `resortfleet`), the `Resort`
  group renders, and a stubbed snapshot (per Z-08)
  drives the seeded tiles to `2reservations held` /
  `1resort clankers available`, both linking to
  `#/resort`; saved layout — a pre-existing
  `workspace` record holding a two-tile layout with
  no resort tiles is written to the store's own
  storage and rehydrated through the real persist
  path, and the loaded `tiles` are byte-identical
  (`JSON.stringify` equality) to what was saved,
  with no resort tile injected). The existing tests
  pass unmodified. `npm run build` PASS.
  `npm run test:e2e` PASS — 6/6 (desktop + Pixel 7).
  A throwaway browser probe (deleted after the run)
  opened Start on a fresh browser profile against
  the seeded simulator: the `Resort` group shows `0`
  reservations held and `2` resort clankers
  available — the seed-20261114 state, derived
  live — both tiles linking to `#/resort`.
- **Residual limits:** e2e and the probe ran against
  the full Chromium build already in the local
  browser cache (chromium-1255) via a temporary
  config that only overrode
  `launchOptions.executablePath`; the temporary
  config and probe were deleted after their runs and
  no repo file carries them — no device result is
  claimed. One nuance, recorded not absorbed: the
  card's "a stored layout must load exactly as
  saved" is proven here for the persisted `tiles`
  array — the Start layout the store owns; named
  layouts saved via `saveLayout` ride the same
  verbatim round-trip (`structuredClone` in,
  `structuredClone` out) and were not separately
  re-proven. The doc reconciliation of the default
  layout's claims remains Z-10's.

### Z-10 — Reconcile the implementation doc · 2026-11-15 · Ember (Muse) · branch `metro-z10_muse`

- **Base:** `metro-z09_muse` (PR #34; this PR targets
  it and lands after it). The card declares "Depends
  on: Z-08; Z-09 if it lands" — Z-09 has landed as a
  branch, so the doc is reconciled against the
  post-Z-09 tree. All 62 tracked playground files
  were verified byte-identical to the
  `metro-z09_muse` tree by git blob SHA-1 before
  editing (100 tracked blobs repo-wide, 0
  mismatches).
- **Before this chunk:** the Boundaries section of
  `docs/METRO_V1_IMPLEMENTATION.md` said "Resort
  tiles in `Start.tsx` display values derived from
  these same API entities." That was the doc's only
  Start-tiles claim, and it was overbroad: it implied
  Start tiles generally derive from the resort API,
  when only two metric kinds do.
- **Reconciled (that bullet only — the card's
  acceptance is that no other section of the doc
  changes):** the bullet now states that only tiles
  bound to a resort metric derive from the resort
  API entities — `resort-reservations` (the
  reservation IDs held on tables that resolve in
  `state.reservations`) and `resort-clankers`
  (clankers whose status is `available`) — computed
  in `Start.tsx` from the `getResortSnapshot()`
  snapshot it polls on mount and every 2.5 seconds,
  with one seeded tile of each kind in the default
  layout's `Resort` group and any tile bindable to a
  resort metric in the editor. It states that every
  other metric (`clock`, `fleet`, `tasks`, `alerts`,
  `energy`) derives from the household simulation
  store — including `fleet`, whose "clankers
  available" caption counts the household fleet, not
  the resort fleet. And it states the unavailable
  behaviour exactly as coded: above the small tile
  size, a resort tile shows "connecting to resort
  data" before any snapshot, "unavailable" /
  "resort data unavailable" (never a number) if
  polling fails before any snapshot arrives, and the
  last value with "· cached" appended to its caption
  when the snapshot is served from the client's
  local cache or a poll fails after a value was
  shown. Every sentence is checkable against
  `Start.tsx`, `src/domain/resort-api.ts`,
  `src/domain/seed.ts`, and `src/domain/engine.ts`.
- **Suites (baseline on unmodified `metro-z09_muse`
  reproduced first — typecheck PASS, lint PASS,
  Vitest 19/19, build PASS, e2e 6/6):** `npm run
  typecheck` PASS; `npm run lint` PASS; `npm test`
  PASS — 19 tests, 5 files; `npm run build` PASS;
  `npm run test:e2e` PASS — 6/6 (desktop + Pixel 7).
  Documentation only: no code, styles, or tests
  changed.
- **Residual limits:** e2e ran against the cached
  full Chromium build (chromium-1255) via a
  temporary config that only overrode
  `launchOptions.executablePath`; the temp config
  was deleted after the run and no repo file carries
  it — **no device result is claimed**. The
  symlinked `node_modules` caveat from prior chunks
  applies unchanged. Sandbox timings are not
  performance evidence. Two nuances, recorded not
  absorbed: (1) the `SIM` tag renders unconditionally
  on every tile (Z-08's flagged nuance), so resort
  staleness is carried by the caption, as the
  reconciled paragraph states; (2) the wider doc
  updates contemplated when this chunk was
  commissioned (resort styling, light-theme parity,
  the responsive pass) were NOT made — the card
  scopes Z-10 to the Start-tiles paragraph and
  forbids other sections changing.
- **Plan complete:** Z-10 is the last chunk in
  `CODEX_CHUNKS.md`. With this entry, chunks Z-01
  through Z-10 are all implemented, each as an
  unmerged PR.
