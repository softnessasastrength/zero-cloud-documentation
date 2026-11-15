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

### Z-04 — Mission Control · 2026-11-15 · Ember (Muse) · branch `metro-z04_muse`

- **Base:** stacked on `metro-z03_muse` (PR #28, open and unmerged) —
  the card declares "Depends on: Z-01" only, and its class set is
  disjoint from Z-02's and Z-03's, but the chunk appends its section
  directly after Z-03's in the same stylesheet build-out series, and
  the Mission Control screen's primitives (Z-01), people-panel
  classes (Z-02) and facility map (Z-03) precede it in that sheet.
  This branch's PR targets `metro-z03_muse` so its diff is exactly
  the Z-04 change; it retargets to `main` once PR #28 lands (and
  #28 once #27 lands, and #27 once #26 lands). All 62 tracked
  playground files were verified byte-identical to the base tree
  by git blob SHA-1 before editing.
- **Styled:** appended one delimited section ("Resort (ZeroCloud
  Metro) — mission control · chunk Z-04") after the Z-03 section in
  `playground/src/styles.css`; no existing line was modified. It
  gives rules to the 7 classes the card names — `mc-hero`,
  `mc-clock`, `mission-metrics`, `mission-metric`, `metric-icon`,
  `mission-grid`, `system-facts`. Only the existing `:root` tokens
  and the sheet's established patterns were used: the hero takes
  the `estate-banner`/`resort-welcome` recipe whole (gradient,
  accent left border, 45px headline) with the clock as its right
  cell in the `welcome-clock` shape (centred column, 34px weight-300
  time, `panel-kicker` label); the metric strip is a wrapping flex
  row of `data-widget` cards (surface, accent border-top) whose
  values take the `entitlement-stat`/`tile-number` scale (44px,
  weight 300) and whose icon takes the `credit-symbol` chip (44px,
  `#2c665b` border, `#63d7bd` glyph); the panel grid follows
  `metro-scenario-grid` (wrapping flex, panels at a 420px basis),
  so the two panels sit side by side on desktop and stack at phone
  widths without disturbing the Z-03 map layout inside the first
  panel; `system-facts` takes the sheet's existing `.facts`
  definition-list recipe (150px label column, muted `dt`, ruled
  rows). No new tokens, no component edits, no class renames.
  One wording nuance, recorded rather than silently absorbed: the
  card groups `system-facts` with the `/mission-control` classes,
  but in the code it renders in the **Engineering Console**
  (`/engineering`, the "DETERMINISTIC REPLAY" panel's seed-facts
  list) — the same kind of route-label looseness as Z-03's map.
  No chunk owns it if Z-04 does not (Z-05's card does not name it),
  so Z-04 styles it and the render check below verifies it where
  it actually renders. No stop-and-report condition was hit.
- **Coverage check** (every class ≥ 1 rule in `src/styles.css`,
  every rule inside the new section; 17 rules in the section):
  mc-hero 3, mc-clock 3, mission-metrics 1, mission-metric 3,
  metric-icon 1, mission-grid 2, system-facts 4 (selector
  occurrences; each class has exactly one primary rule, the rest
  are descendant rules). The diff against the base branch is
  +46 lines / −0 lines — additions only — and no new selector
  duplicates a pre-existing one.
- **Suites (Node v24.22.1 sandbox; baseline on the Z-03 base
  reproduced first — identical results):** `npm run typecheck`
  PASS; `npm run lint` PASS; `npm test` PASS — 14 tests, 5 files;
  `npm run build` PASS; `npm run test:e2e` PASS — 6/6 (desktop +
  Pixel 7 projects; the resort spec drives the booking flow into
  Mission Control and asserts the garden-table metric's held
  count).
- **Render check** (throwaway Playwright script against the dev
  server + simulator, deleted after the run; booking flow
  reproduced so the garden-table metric holds a reservation): on
  `/mission-control` at 1280×800 the hero spans the content width
  with the gradient ground and 45px headline, the clock sits at
  its right ("13:00" at 34px under the VIRTUAL CLOCK label), the
  four metric cards share one row (279px each, no overlap, 44px
  icon chips), the garden-table metric reads "1/2" at 44px, and
  the two panels sit side by side (574px each). At 412×915
  (Pixel 7) the clock wraps beneath the hero text, the metric
  cards stack full-width with no overlap, the panels stack, and
  "1/2" still reads at 44px. On `/engineering` the
  `system-facts` list renders its 5 facts as ruled grid rows with
  muted labels. `documentElement.scrollWidth` equals the viewport
  width on both screens at both viewports.
- **Residual limits:** e2e ran against the full Chromium build
  already in the local browser cache (chromium-1255) via a
  temporary config that only overrode
  `launchOptions.executablePath`; the temporary config was deleted
  after the run and no repo file carries it — the stock
  headless-shell artifact is not downloadable in this sandbox
  (same caveat as Z-01–Z-03), and no device result is claimed.
  Breakpoint refinement of the resort grids and heroes remains
  Z-06 (the metric strip's one-card-per-row wrap at phone widths
  is this chunk's flex basis at work, not a breakpoint rule), and
  light-theme parity for the resort section remains Z-07 (the
  hero gradient is a dark-theme literal, as in Z-01/Z-02).
  Observed, not acted on (named in no chunk card): `map-dot`,
  `api-status` and `presence` still have no rules anywhere in the
  sheet.

### Z-05 — Engineering Console · 2026-11-15 · Ember (Muse) · branch `metro-z05_muse`

- **Base:** stacked on `metro-z04_muse` (PR #29, open and unmerged) —
  the card declares "Depends on: Z-01" only, and its class set is
  disjoint from Z-02's, Z-03's and Z-04's, but the chunk appends its
  section directly after Z-04's in the same stylesheet build-out
  series, and the Engineering screen's primitives (Z-01) and its
  replay panel's facts list (Z-04) precede it in that sheet. This
  branch's PR targets `metro-z04_muse` so its diff is exactly
  the Z-05 change; it retargets to `main` once PR #29 lands (and
  #29 once #28 lands, and #28 once #27 lands, and #27 once #26
  lands). All 62 tracked playground files were verified
  byte-identical to the base tree by git blob SHA-1 before editing.
- **Styled:** appended one delimited section ("Resort (ZeroCloud
  Metro) — engineering console · chunk Z-05") after the Z-04
  section in `playground/src/styles.css`; no existing line was
  modified. It gives rules to the 7 classes the card names —
  `engineering-banner`, `engineering-grid`, `scenario-selector`,
  `clock-control`, `fault-panel`, `fleet-control-row`,
  `engineer-toggle`. Only the existing `:root` tokens and the
  sheet's established patterns were used: the banner takes the
  `estate-banner`/`resort-welcome`/`mc-hero` recipe whole
  (gradient, accent left border, 45px headline) with the wrench
  glyph in the `welcome-clock` svg colour (`#81d7d2`);
  `scenario-selector` takes `booking-panel`'s accent border-top
  as the screen's primary control panel, with a 30px bottom
  margin separating it from the grid; `engineering-grid` follows
  `mission-grid` (wrapping flex, panels at a 420px basis), so
  the clock and replay panels sit side by side on desktop and
  stack at phone widths; `clock-control` pairs the
  `mission-metric` value scale (44px, weight 300) with the
  `status`/`data-tag` label type for the running state;
  `fault-panel` takes a 30px top margin (the grid-gap rhythm);
  `fleet-control-row` follows `employee-card`/`metro-event`
  (flex row, ruled bottom border) with the name block at
  `flex: 1` and the action button at `flex: none`, so each
  row's control stays full-size and individually operable, as
  the card requires; `engineer-toggle` takes the `data-tag`
  recipe minus `white-space: nowrap` — the "engineer role
  required · choose it in settings" string is far longer than
  any `data-tag` text and would overflow the fault panel's
  heading at phone widths, so it wraps right-aligned instead.
  No new tokens, no component edits, no class renames. Unlike
  Z-03 and Z-04 there is no route-label looseness to record:
  all 7 classes render on `/engineering` exactly as the card
  describes, and `system-facts` — which renders in this
  screen's replay panel, inside the new grid — was already
  styled by Z-04 and is not restyled here; the render check
  verifies it still renders under the grid's layout. No
  stop-and-report condition was hit.
- **Coverage check** (every class ≥ 1 rule in `src/styles.css`,
  every rule inside the new section; 15 rules in the section):
  engineering-banner 4, engineering-grid 2, scenario-selector 1,
  clock-control 3, fault-panel 1, fleet-control-row 3,
  engineer-toggle 1 (selector occurrences; each class has
  exactly one primary rule, the rest are descendant rules). The
  diff against the base branch is +27 lines / −0 lines —
  additions only — and no new selector duplicates a
  pre-existing one.
- **Suites (Node v24.22.1 sandbox; baseline on the Z-04 base
  reproduced first — identical results):** `npm run typecheck`
  PASS; `npm run lint` PASS; `npm test` PASS — 14 tests, 5
  files; `npm run build` PASS; `npm run test:e2e` PASS — 6/6
  (desktop + Pixel 7 projects; the resort spec's engineering
  test drives this screen's scenario selector and clicks the
  fault button scoped to Percival's `fleet-control-row` at the
  phone viewport).
- **Render check** (throwaway Playwright script against the dev
  server + simulator, deleted after the run): on `/engineering`
  at 1280×800 the banner spans the content width with the
  gradient ground and 45px headline and the wrench glyph at its
  right, the scenario selector carries the accent top border,
  the clock and replay panels sit side by side (574px each)
  with the clock reading "13:00" at 44px, `system-facts`
  renders its 5 ruled rows inside the replay panel, the
  engineer toggle shows its full role-required text, and both
  fleet rows (Percival, Cogsworth) keep their buttons inside
  the row bounds. At 412×915 (Pixel 7) the banner holds, the
  panels stack full-width, the toggle text wraps without
  pushing the layout out, and both fleet buttons remain in-row
  and visible. `documentElement.scrollWidth` equals the
  viewport width at both viewports.
- **Residual limits:** e2e ran against the full Chromium build
  already in the local browser cache (chromium-1255) via a
  temporary config that only overrode
  `launchOptions.executablePath`; the temporary config was
  deleted after the run and no repo file carries it — the stock
  headless-shell artifact is not downloadable in this sandbox
  (same caveat as Z-01–Z-04), and no device result is claimed.
  Breakpoint refinement of the resort grids and heroes remains
  Z-06 (the panel grid's stacking at phone widths is this
  chunk's flex basis at work, not a breakpoint rule), and
  light-theme parity for the resort section remains Z-07 (the
  banner gradient is a dark-theme literal, as in Z-02/Z-04).
  Observed, not acted on (named in no chunk card): `map-dot`,
  `api-status` and `presence` still have no rules anywhere in
  the sheet; `replay-result` (the replay panel's good/bad
  verdict line) is likewise unstyled and named by no card.

### Z-06 — Resort responsive pass · 2026-11-15 · Ember (Muse) · branch `metro-z06_muse`

- **Base:** stacked on `metro-z05_muse` (PR #30, open and
  unmerged) — the card's dependencies (Z-02, Z-04, Z-05) are
  the stack below it, and this chunk's breakpoint rules must
  follow all five Z-sections in source order to take effect
  (see Placement). This branch's PR targets `metro-z05_muse`
  so its diff is exactly the Z-06 change; it retargets to
  `main` once PR #30 lands (and #30 once #29 lands, and #29
  once #28 lands, and #28 once #27 lands, and #27 once #26
  lands). All 62 tracked playground files were verified
  byte-identical to the base tree by git blob SHA-1 before
  editing.
- **Styled:** appended one delimited section ("Resort
  (ZeroCloud Metro) — responsive pass · chunk Z-06") after
  the Z-05 section in `playground/src/styles.css`. The card
  permitted edits within the earlier Z-sections; none were
  needed — the diff is +32 lines / −0 lines, additions only,
  because everything the card asks for is expressible as
  breakpoint overrides of the base rules. The section holds
  the resort rules at the sheet's two existing breakpoints:
  - `@media(max-width:1000px)` — `metro-scenario-grid`
    collapses to a single column (`flex-direction: column`;
    `booking-panel` and `entitlement-panel` reset to
    `flex: none`). The scenario grid has the estate compound
    layout's shape — a main panel beside a 310px side panel —
    and the base sheet collapses that layout at 1000px, so
    the resort grid follows its twin. This also repairs the
    wart Z-02's wrapping flex left behind: at every width
    below the wrap point the stacked entitlement panel stayed
    310px wide while the booking panel took the full column;
    it now spans the column. The heroes take no 1000px rule:
    the estate banner's only 1000px step is its 75px clock
    shrinking to 50px, and the resort clocks are already
    34px.
  - `@media(max-width:650px)` — `mission-grid` and
    `engineering-grid` collapse to a single column (same
    panel reset), following the base sheet's two-column,
    three-column and fleet layouts, which all go
    single-column at 650px. The three heroes take the estate
    banner's 650px recipe whole: `display: block`, padding
    25px (from 35px 40px), headline 34px (from 45px); and
    the hero side elements take the estate time's step below
    the text — `welcome-clock` and `mc-clock` get
    `margin-top: 30px`, and the engineering banner's glyph
    becomes a block with the same margin.
  - **Placement:** the blocks sit at the tail of the sheet,
    after the Z-01…Z-05 base rules — not inside the sheet's
    original media queries, which precede the resort
    sections; at equal specificity a breakpoint rule placed
    there could never override the later base rules. The
    estate map section is the in-file precedent: it carries
    its own media queries inside its own section, after its
    base rules. Only the existing breakpoint widths are
    used; no token was added, no component was touched, and
    no animation was added — reduced motion stays governed
    by the sheet's global reduce rule.
- **Coverage check** (the card names no new classes; the
  six it names each have rules inside the new section's
  media blocks, grep-verifiable — selector occurrences in
  the section): metro-scenario-grid 3, mission-grid 2,
  engineering-grid 2, resort-welcome 2, mc-hero 2,
  engineering-banner 3; the panel resets and hero side
  elements: booking-panel 1, entitlement-panel 1,
  welcome-clock 1, mc-clock 1.
- **Suites (Node v24.22.1 sandbox; baseline on the Z-05
  base reproduced first — identical results):**
  `npm run typecheck` PASS; `npm run lint` PASS;
  `npm test` PASS — 14 tests, 5 files; `npm run build`
  PASS; `npm run test:e2e` PASS — 6/6 (desktop + Pixel 7).
  One process note: a mid-run lint pass reported 18 errors,
  every one inside the throwaway probe scripts; with the
  probes deleted lint is clean, exactly as on the base.
- **Render check** (throwaway Playwright probe against the
  dev server + simulator, deleted after the run; viewport
  widths 1280/1024/1000/900/768/650/412/390 on all three
  routes, before and after): at 1280 and 1024 the layouts
  are the base's exactly (panels side by side, clocks beside
  the headlines). At 1000px the scenario grid is a single
  full-width column (panels 920/920, was 580/310) while the
  two-panel grids remain side by side (445/445) until their
  650px collapse; at 900 and 768 the scenario panels are
  full width (828, 707 — the entitlement panel was 310). At
  650, 412 and 390 every grid is one full-width column and
  every hero is in its block form — computed styles at 640
  and 390 confirm `display: block`, padding 25px, headline
  34px and the side elements' 30px top margin on all three
  heroes. `documentElement.scrollWidth` equals the viewport
  width at every probed width on all three routes — in
  particular at 390px on `/resort`, `/mission-control` and
  `/engineering`, the card's render check. The base already
  passed that check incidentally through flex wrapping; the
  explicit rules keep it green while making the collapse a
  deliberate step with the rest of the app.
- **Residual limits:** e2e ran against the full Chromium
  build already in the local browser cache (chromium-1255)
  via a temporary config that only overrode
  `launchOptions.executablePath`; the temporary config was
  deleted after the run and no repo file carries it — the
  stock headless-shell artifact is not downloadable in this
  sandbox (same caveat as Z-01–Z-05), and no device result
  is claimed. Light-theme parity for the resort section
  remains Z-07. Observed, not acted on (named in no chunk
  card): `map-dot`, `api-status`, `presence` and
  `replay-result` still have no rules anywhere in the sheet.

### Z-07 — Light-theme parity for resort classes · 2026-11-15 · Ember (Muse) · branch `metro-z07_muse`

- **Base:** stacked on `metro-z06_muse` (PR #31, open and
  unmerged) — the card declares "Depends on: Z-06", and the
  counterparts belong at the tail of the same build-out
  series, after all six Z-sections. This branch's PR targets
  `metro-z06_muse` so its diff is exactly the Z-07 change;
  it retargets to `main` once PR #31 lands (and #31 once #30
  lands, and #30 once #29 lands, and #29 once #28 lands, and
  #28 once #27 lands, and #27 once #26 lands). All 62 tracked
  playground files were verified byte-identical to the base
  tree by git blob SHA-1 before editing.
- **Parity audit:** every hard-coded colour in the Z-01…Z-06
  sections was listed before editing — 18 distinct colours
  across 46 declarations. Fifteen declarations sit on a
  theme-flipping ground (the page, or a `var(--surface)`
  panel) in a colour chosen for dark grounds; they get
  counterparts. The rest are both-theme by design and are
  named in the section header: the hero gradient and its
  `#40c5c6` border (the estate heroes keep theirs under
  light), the colours that sit on that gradient (paragraph
  `#a8c7c5`, clock glyphs `#81d7d2`, the mc-clock label
  `#aab6b7` — the ground is dark in both themes), `#fff` on
  `var(--accent)` grounds (the `.primary` pairing), the
  confirm-icon chip (its `#7be4b1` sits on its own `#32694f`
  in both themes), the border-only dark members `#2c665b`
  and `#32694f`, the fault/warning accents `#e76c47` and
  `#ddae50`, and the outbox tint `#5e461c30` (an alpha wash
  copied from `.warning`, which the sheet leaves unmodified
  under light).
- **Styled:** appended one delimited section ("Resort
  (ZeroCloud Metro) — light-theme parity · chunk Z-07") at
  the tail of `playground/src/styles.css`; no existing line
  was modified (the base file is a byte-exact prefix of the
  result). Eight counterpart rules, every value taken from
  the sheet's own palette: the three heroes take the estate
  banner's light recipe (`color:#fff` — the gradient stays,
  the inherited text is forced light, as on `.estate-banner`);
  `.panel-kicker` and `.map-room>span` take `#56676a`, the
  app's own light value for their `#aab6b7` (`.eyebrow`,
  `.field>span`); `.metro-message.error` takes `#91472e`,
  the error family's dark member from `.status.failed`; the
  mint text colours (`.event-quality`, `.credit-symbol`,
  `.credit-pill`, `.metric-icon`) and the dashed route band
  (`.route-two`) take `#2c665b`, the dark member of their
  own pair (`.simulation-badge`); `.protected-banner` takes
  `#32694f`, its own border's green; the pale-teal accents
  (`.metro-event time`, the privacy/coverage/map glyphs)
  take `var(--accent)`, the theme's dark teal; and
  `.map-room` — the `#101112` ground the Z-03 entry named a
  dark-theme literal — takes `var(--surface)`, so the room
  blocks step from the page in light exactly as the map
  nodes already do. No token was added, no component was
  touched, and the out-of-scope classes (`map-dot`,
  `api-status`, `presence`, `replay-result`) stay out — the
  card names none of them.
- **Coverage check** (the card's parity check, run as a
  script over the sheet): of the 46 hard-coded colour
  declarations in the Z-01…Z-06 sections, 15 are covered by
  a `[data-theme=light]` counterpart for the same selector
  and property family, 31 are the documented both-theme set
  above, and none is left over; every selector named in the
  new section exists in the base resort sections (no dead
  rules). Declarations written with theme variables were
  never in question.
- **Suites (Node v24.22.1 sandbox; baseline on the Z-06
  base reproduced first — identical results):**
  `npm run typecheck` PASS; `npm run lint` PASS;
  `npm test` PASS — 14 tests, 5 files; `npm run build`
  PASS; `npm run test:e2e` PASS — 6/6 (desktop + Pixel 7).
- **Render check** (throwaway Playwright probe against the
  dev server + simulator, deleted after the run; both
  themes, all three routes, 1280×800 and 412×915): under
  `data-theme="light"` at desktop the three heroes and their
  headlines compute to white text on the retained gradient,
  `.panel-kicker` and the map-room labels compute to
  `#56676a`, `.metric-icon` to `#2c665b`, the map rooms to
  the light `--surface`, and the booking flow completes
  with the confirm chip unchanged; under dark every probed
  value is the base's exactly (heroes `#f6f5f2`, kicker
  `#aab6b7`, metric icon `#63d7bd`, map rooms `#101112`).
  `documentElement.scrollWidth` equals the viewport width
  at both widths on all three routes in both themes, and
  the grid panel pairs (scenario, mission, engineering) do
  not overlap at either width. One process note: the first
  probe run measured during the app's `.3s` `enter`
  animation and reported 3–12px scrollWidth excesses in
  *both* themes — the load transient the Z-02 entry already
  names; the probe was fixed to wait the animation out, and
  no code changed for it.
- **Residual limits:** e2e and the render probe ran against
  the full Chromium build already in the local browser
  cache (chromium-1255) via a temporary config that only
  overrode `launchOptions.executablePath`; the temporary
  config and probe were deleted after the run and no repo
  file carries them — the stock headless-shell artifact is
  not downloadable in this sandbox (same caveat as
  Z-01–Z-06), and no device result is claimed. The resort
  stylesheet build-out is now complete (Z-01–Z-07); the
  remaining chunks are the Start-tile pair (Z-08, Z-09) and
  the documentation reconciliation (Z-10). Observed, not
  acted on (named in no chunk card): `map-dot`, `api-status`,
  `presence` and `replay-result` still have no rules anywhere
  in the sheet — under either theme.

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
