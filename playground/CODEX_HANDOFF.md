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
