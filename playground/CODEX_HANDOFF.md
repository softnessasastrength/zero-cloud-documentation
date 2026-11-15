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

---

## Chunk log (CODEX_CHUNKS.md)

### Z-01 — Shared resort primitives · 2026-11-15 · Ember (Muse) · branch `metro-z01_muse`

- **Styled:** appended one delimited section ("Resort (ZeroCloud Metro) —
  shared primitives · chunk Z-01") at the end of `playground/src/styles.css`;
  no existing line was modified. It gives rules to the 18 classes the three
  resort screens share — `metro-panel`, `panel-kicker`, `panel-copy`,
  `metro-loading`, `metro-message`, `metro-control`, `metro-primary`,
  `metro-section`, `section-heading`, `data-tag`, `mode-switch`,
  `outbox-notice`, `outbox-entry`, `quiet-link`, `control-row`,
  `metro-events`, `metro-event`, `event-quality` — plus the two named
  variants `.metro-message.error` and `.mode-switch button.selected`.
  Only the existing `:root` tokens (`--surface`, `--line`, `--muted`,
  `--accent`) and the sheet's established type styles and colour vocabulary
  (`eyebrow`, `status`, `warning`, `event-row`, `simulation-badge`) were
  used; no new tokens, no component edits, no class renames.
- **Coverage check** (grep count of rule occurrences per class in
  `src/styles.css`, all ≥ 1): metro-panel 1, panel-kicker 1, panel-copy 1,
  metro-loading 1, metro-message 2, metro-control 1, metro-primary 1,
  metro-section 1, section-heading 2, data-tag 1, mode-switch 3,
  outbox-notice 1, outbox-entry 2, quiet-link 1, control-row 1,
  metro-events 1, metro-event 2, event-quality 1; variants
  `.metro-message.error` and `.mode-switch button.selected` both present.
- **Suites (Node v24.22.1 sandbox):** `npm run typecheck` PASS;
  `npm run lint` PASS; `npm test` PASS — 14 tests, 5 files;
  `npm run build` PASS; `npm run test:e2e` PASS — 6/6 (desktop + Pixel 7
  projects; the resort spec exercises all three routes).
- **Residual limits:** e2e ran against the full Chromium build already in
  the local browser cache (chromium-1255) via a temporary config that only
  overrode `launchOptions.executablePath`; the temporary config was deleted
  after the run and no repo file carries it — the stock headless-shell
  artifact is not downloadable in this sandbox (same caveat as the
  2026-11-14 pass), and no device result is claimed. Responsive stacking
  of the resort grids remains Z-06 and light-theme parity for the resort
  section remains Z-07; screen-specific classes remain Z-02/Z-04/Z-05.

### Z-02 — ResortMetro request screen · 2026-11-15 · Ember (Muse) · branch `metro-z02_muse`

- **Base:** stacked on `metro-z01_muse` (PR #26, open and unmerged) — the
  card declares "Depends on: Z-01", and this chunk appends its section
  directly after Z-01's in the same build-out series. This branch's PR
  targets `metro-z01_muse` so its diff is exactly the Z-02 change; it
  retargets to `main` once PR #26 lands.
- **Styled:** appended one delimited section ("Resort (ZeroCloud Metro) —
  request screen · chunk Z-02") after the Z-01 section in
  `playground/src/styles.css`; no existing line was modified. It gives
  rules to the 20 classes the card names — `resort-welcome`,
  `welcome-clock`, `metro-scenario-grid`, `booking-panel`,
  `entitlement-panel`, `entitlement-stat`, `entitlement-equation`,
  `credit-quote`, `credit-pill`, `credit-symbol`, `employee-card`,
  `employee-avatar`, `scenario-form`, `consent-note`, `request-privacy`,
  `guest-privacy-card`, `protected-banner`, `scenario-confirmed`,
  `confirm-icon`, `coverage-note`. Only the existing `:root` tokens and
  the sheet's established patterns were used: the `estate-banner`
  gradient hero for `resort-welcome`, the `data-widget` accent border
  for `booking-panel`, the `event-row` pattern for `employee-card`, the
  `simulation-badge` synthetic green for `credit-pill`/`credit-symbol`,
  and the `status` healthy green (`#32694f`/`#7be4b1`) for
  `scenario-confirmed`/`confirm-icon`/`protected-banner`. No new tokens,
  no component edits, no class renames. The scenario layout is a
  wrapping flex row (booking `flex:1 1 420px`, entitlement
  `flex:0 1 310px`, the sheet's 30px gap) so the panels sit side by
  side on desktop and stack at phone widths without taking Z-06's
  breakpoint scope; Z-06 may still convert or refine it.
- **Coverage check** (grep count of rule occurrences per class in
  `src/styles.css`, all ≥ 1, every rule inside the new section):
  resort-welcome 3, welcome-clock 3, metro-scenario-grid 1,
  booking-panel 1, entitlement-panel 1, entitlement-stat 4,
  entitlement-equation 3, credit-quote 4, credit-pill 1, credit-symbol
  2, employee-card 4, employee-avatar 2, scenario-form 1, consent-note
  1, request-privacy 1, guest-privacy-card 2, protected-banner 1,
  scenario-confirmed 3, confirm-icon 1, coverage-note 2.
- **Suites (Node v24.22.1 sandbox; baseline on the Z-01 base reproduced
  first — identical results):** `npm run typecheck` PASS; `npm run
  lint` PASS; `npm test` PASS — 14 tests, 5 files; `npm run build`
  PASS; `npm run test:e2e` PASS — 6/6 (desktop + Pixel 7 projects; the
  resort spec renders this screen at both viewports and drives the
  booking flow through `scenario-confirmed`).
- **Render check** (throwaway Playwright script, deleted after the
  run): at 1280×800 the booking and entitlement panels share the top
  row side by side, the welcome clock sits inside the banner without
  overlapping the heading text, and after confirming a booking the
  `scenario-confirmed` card and `protected-banner` render in place; at
  412×915 (Pixel 7) the panels stack vertically and the clock wraps
  below the welcome text; `/mission-control` renders `employee-card`,
  `employee-avatar`, `credit-pill` and `coverage-note` at full size.
  At rest, `documentElement.scrollWidth` equals the viewport width on
  both screens (a 3–4px transient during load traces to the app's
  pre-existing `enter` animation on `main`, not to these rules; the
  only elements extending past the viewport are the pivot nav's links
  inside its by-design horizontal scroll strip).
- **Residual limits:** e2e ran against the full Chromium build already
  in the local browser cache (chromium-1255) via a temporary config
  that only overrode `launchOptions.executablePath`; the temporary
  config was deleted after the run and no repo file carries it — the
  stock headless-shell artifact is not downloadable in this sandbox
  (same caveat as Z-01 and the 2026-11-14 pass), and no device result
  is claimed. Breakpoint refinement of the resort heroes and grids
  remains Z-06 and light-theme parity for the resort section remains
  Z-07. Observed, not acted on (named in no chunk card): `api-status`,
  `presence` and `map-dot` are used by these screens but have no rules
  anywhere in the sheet.

### Z-03 — Resort facility map · 2026-11-15 · Ember (Muse) · branch `metro-z03_muse`

- **Base:** stacked on `metro-z02_muse` (PR #27, open and unmerged) —
  the card declares "Depends on: Z-01" only, and its class set is
  disjoint from Z-02's, but the chunk appends its section directly
  after Z-02's in the same stylesheet build-out series, and the map
  renders inside a screen whose primitives (Z-01) and layout (Z-02)
  precede it. This branch's PR targets `metro-z02_muse` so its diff
  is exactly the Z-03 change; it retargets to `main` once PR #27
  lands (and #27 once #26 lands). All 62 tracked playground files
  were verified byte-identical to the base tree by git blob SHA-1
  before editing.
- **Styled:** appended one delimited section ("Resort (ZeroCloud
  Metro) — facility map · chunk Z-03") after the Z-02 section in
  `playground/src/styles.css`; no existing line was modified. It
  gives rules to the 12 classes the card names — `resort-map`,
  `dining-room`, `service-room`, `map-table`, `map-room`,
  `map-node`, `node-lobby`, `map-route`, `route-one`, `route-two`,
  `map-unit`, `map-caption`. The map renders in the Mission Control
  facility panel ("FACILITY MAP / LEVEL 01", the `ResortMetro.tsx`
  module's second screen); `map-caption` is also reused under that
  screen's events list, where the same footnote rule applies. Only
  the existing `:root` tokens and the sheet's established patterns
  were used: the plan is a two-column grid of room blocks on the
  panel (rooms recessed in the sheet's `#101112` ground with the
  `data-widget` border-top device — `--accent` for the dining
  room, the `simulation-badge` green `#2c665b` for the service
  room), the two routes are full-width bands passing behind the
  rooms (route one a solid `--accent` bar, route two a dashed
  `#63d7bd` line), `map-table` is a bordered chip in the
  `credit-quote` shape, `map-unit` rows follow the
  `employee-card`/`metro-event` row pattern with the status pushed
  right, the lobby node is a centred chip spanning the plan's foot
  with an `--accent` border, and `map-caption` is 12px
  `var(--muted)` footnote text. No new tokens, no component edits,
  no class renames.
- **Coverage check** (every class ≥ 1 rule in `src/styles.css`,
  every rule inside the new section; 18 rules in the section):
  resort-map 1, dining-room 1, service-room 1, map-table 1,
  map-room 1, map-node 1, node-lobby 1, map-route 1, route-one 1,
  route-two 1, map-unit 1, map-caption 1 (primary rules; `map-room`,
  `map-table`, `map-unit` and `map-node` carry additional
  child/descendant rules).
- **Collision check** (the card's additions-only check against the
  estate Map page): diff of `src/styles.css` against the base
  branch is +29 lines / −0 lines — additions only, all inside the
  new resort section. All 33 pre-existing estate map rules
  (`.map-intro`, `.map-toolbar`, `.map-scroll`, `.estate-map`,
  `.map-building`, `.map-zone-name`, `.map-zone-kind`,
  `.map-land-label`, `.map-agent`, `.map-inspector`, `.map-stats`,
  `.map-legend`, `.map-entry`, including their responsive
  overrides) are byte-identical before and after, and no new
  selector duplicates a pre-existing one — the resort classes only
  share the `map-` prefix.
- **Suites (Node v24.22.1 sandbox; baseline on the Z-02 base
  reproduced first — identical results):** `npm run typecheck`
  PASS; `npm run lint` PASS; `npm test` PASS — 14 tests, 5 files;
  `npm run build` PASS; `npm run test:e2e` PASS — 6/6 (desktop +
  Pixel 7 projects; the resort spec exercises all three routes,
  including the Mission Control screen that renders this map).
- **Render check** (throwaway Playwright script, deleted after the
  run): on `/mission-control` at 1280×800 the two rooms sit side by
  side (535px each) with distinct border-top colours (accent vs
  `#2c665b`), the table chip renders inside the dining room
  ("Table 04 · available"), the two clanker unit rows stack inside
  the service room with status and battery right-aligned, route one
  crosses the plan as a solid accent band behind the rooms and
  route two as a dashed green band below it, and the lobby node
  sits centred at the plan's foot; at 412×915 (Pixel 7) the same
  layout holds at 136px per room with no overlapping text.
  `documentElement.scrollWidth` equals the viewport width at both
  viewports.
- **Residual limits:** e2e ran against the full Chromium build
  already in the local browser cache (chromium-1255) via a
  temporary config that only overrode
  `launchOptions.executablePath`; the temporary config was deleted
  after the run and no repo file carries it — the stock
  headless-shell artifact is not downloadable in this sandbox (same
  caveat as Z-01 and Z-02), and no device result is claimed.
  Breakpoint refinement of the resort grids remains Z-06 and
  light-theme parity for the resort section remains Z-07 (the room
  blocks' `#101112` ground is a dark-theme literal, as in Z-01/Z-02).
  Observed, not acted on (named in no chunk card): `map-dot` — the
  status dot inside each `map-unit` — still has no rule anywhere in
  the sheet, so the unit rows read by name and status text alone;
  `api-status` and `presence` likewise remain unstyled.
