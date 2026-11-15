# ZeroCloud Metro Playground — Luna-sized Codex chunks

These chunks decompose the two pieces of work scoped in
`CODEX_HANDOFF.md` — (1) the missing resort stylesheet and (2) the
Start-page resort tiles that do not consume the resort API — into
pieces a mid-tier coding model can complete in one sitting without
frontier-level design judgment. They are work orders, not a redesign.

**Design discipline:** the screens are styled against the design
system that already exists — the `:root` tokens in `src/styles.css`
(`--accent`, `--surface`, `--line`, `--muted`, the dark background,
the `#f5cd65` focus colour, breakpoints at 650px / 1000px / 1550px,
and the `[data-theme=light]` theme) and Stage A of
`design/metro/metro-hardware-simulation-v1.md` (design tokens, live
tiles, responsive navigation). Chunks **apply** those tokens; they do
not invent a new palette, type scale, or layout language. Inventing
one is design work and is listed under NOT CHUNKED.

## How to consume a chunk

1. Take the earliest chunk whose dependencies are complete. Do not
   combine chunks merely because they touch `src/styles.css`.
2. Read the chunk card, the relevant component in
   `src/pages/ResortMetro.tsx`, and the existing rules in
   `src/styles.css` before editing. The stylesheet is minified into
   long lines; append resort rules as a new, clearly delimited
   section rather than rewriting existing lines.
3. A chunk is **done** only when all of the following are true:
   - its acceptance check passes (each card names one — a class
     coverage check, a named suite, or a named screen render);
   - `npm run typecheck`, `npm run lint`, `npm test`, and
     `npm run build` all pass;
   - the e2e suite passes where the card names it:
     `npm run test:e2e` (on a machine where
     `npx playwright install chromium` works);
   - a dated entry appended to `CODEX_HANDOFF.md` records the chunk
     ID, what was styled or wired, the suites run, and any residual
     limit.
4. Resort data is synthetic and labelled; no chunk may present a
   simulated value as real telemetry, and no tile may display a
   number that does not derive from the state it claims to derive
   from.

## Stop-and-report rule

Stop the chunk and report the blocker instead of improvising if:

- styling a class honestly requires a new design token, a layout
  change to the component, or a class rename in the component;
- a class in the card no longer exists in `ResortMetro.tsx`, or a
  rule would collide with the estate Map page's existing `.map-*`
  rules in `src/styles.css`;
- the Start-tile wiring would require fabricating a value, changing
  the resort API contract, or migrating existing users' saved
  layouts in a way that could lose their tiles;
- an existing test fails for an unrelated reason; or
- the card's factual premise no longer matches the code.

The report should name the chunk, the exact failed premise, the
evidence, and the smallest decision needed from Ember or the owner. A
stopped chunk is useful information, not a failed sitting.

## Consumption order

Z-01 → Z-02; Z-03 after Z-01; Z-04 and Z-05 after Z-01; Z-06 after
Z-02, Z-04, and Z-05; Z-07 after Z-06; Z-08 independent; Z-09 after
Z-08; Z-10 after Z-08 (and after Z-09 if it lands).

---

## The resort stylesheet

`src/pages/ResortMetro.tsx` exports three screens — `ResortMetro`
(route `/resort`), `MissionControl` (`/mission-control`), and
`EngineeringConsole` (`/engineering`) — using ~65 class names that
have no rules anywhere in `src/styles.css`. The screens are
functional but render unstyled. Chunks Z-01–Z-07 give every one of
those classes a rule, screen by screen. Classes that already have
global rules (`eyebrow`, `primary`, `form-grid`, `field`) are reused,
never redefined.

### Z-01 — Shared resort primitives

**Objective:** Style the classes all three resort screens share:
`metro-panel`, `panel-kicker`, `panel-copy`, `metro-loading`,
`metro-message` (including its `error` variant), `metro-control`,
`metro-primary`, `metro-section`, `section-heading`, `data-tag`,
`mode-switch` (including the `selected` state), `outbox-notice`,
`outbox-entry`, `quiet-link`, `control-row`, and the shared event
list: `metro-events`, `metro-event`, `event-quality`. Use only the
existing `:root` tokens and type styles.

**Files:** `src/styles.css` (append one delimited resort section).

**Acceptance:** A coverage check — every class named in this card
has at least one rule in `src/styles.css` (grep-verifiable) — plus
typecheck, lint, unit tests, and build green, and
`npm run test:e2e` passing (the resort spec exercises all three
routes). Record the coverage-check output in the handoff entry.

**Depends on:** None.

### Z-02 — ResortMetro request screen

**Objective:** Style the `/resort` request screen's own classes:
`resort-welcome`, `welcome-clock`, `metro-scenario-grid`,
`booking-panel`, `entitlement-panel`, `entitlement-stat`,
`entitlement-equation`, `credit-quote`, `credit-pill`,
`credit-symbol`, `employee-card`, `employee-avatar`,
`scenario-form`, `consent-note`, `request-privacy`,
`guest-privacy-card`, `protected-banner`, `scenario-confirmed`,
`confirm-icon`, `coverage-note`.

**Files:** `src/styles.css`.

**Acceptance:** Coverage check for the named classes; typecheck,
lint, unit tests, build green; e2e resort spec passes at both
configured viewports (desktop and Pixel 7), which render this
screen. The screen must read as a coherent panel layout at both
viewports — panels stacked/grid per the existing layout conventions
in `styles.css`, no overlapping text.

**Depends on:** Z-01.

### Z-03 — Resort facility map

**Objective:** Style the facility map rendered inside the
`ResortMetro` screen: `resort-map`, `dining-room`, `service-room`,
`map-table`, `map-room`, `map-node`, `node-lobby`, `map-route`,
`route-one`, `route-two`, `map-unit`, `map-caption`. These are
resort-specific classes; the estate Map page's `.map-*` rules
already in `styles.css` (`.map-scroll`, `.estate-map`,
`.map-building`, …) belong to a different screen and must not be
altered or relied on.

**Files:** `src/styles.css`.

**Acceptance:** Coverage check for the named classes; a collision
check — no existing estate-map rule is modified (diff of
`styles.css` shows additions only in the resort section);
typecheck, lint, unit tests, build, and e2e green; the `/resort`
screen's map renders rooms, tables, and routes as visually distinct
elements at both e2e viewports.

**Depends on:** Z-01.

### Z-04 — Mission Control

**Objective:** Style the `/mission-control` screen's own classes:
`mc-hero`, `mc-clock`, `mission-metrics`, `mission-metric`,
`metric-icon`, `mission-grid`, `system-facts`. (Its event section
reuses Z-01's event-list classes.)

**Files:** `src/styles.css`.

**Acceptance:** Coverage check for the named classes; typecheck,
lint, unit tests, build green; e2e passes, and the Mission Control
screen renders its hero, clock, and metric grid as a coherent
layout at both e2e viewports — the garden-table metric fixed in the
verification pass must remain legible as a held-reservation count.

**Depends on:** Z-01.

### Z-05 — Engineering Console

**Objective:** Style the `/engineering` screen's own classes:
`engineering-banner`, `engineering-grid`, `scenario-selector`,
`clock-control`, `fault-panel`, `fleet-control-row`,
`engineer-toggle`.

**Files:** `src/styles.css`.

**Acceptance:** Coverage check for the named classes; typecheck,
lint, unit tests, build green; e2e resort spec passes — it drives
this screen's scenario selector and per-clanker fault controls, so
the styled `fleet-control-row` layout must keep each row's controls
individually operable (the spec scopes its locator to Percival's
row).

**Depends on:** Z-01.

### Z-06 — Resort responsive pass

**Objective:** Add the resort section's rules at the stylesheet's
existing breakpoints (1000px and 650px): the resort grids
(`metro-scenario-grid`, `mission-grid`, `engineering-grid`) and
heroes (`mc-hero`, `engineering-banner`, `resort-welcome`) collapse
to a single column in step with the rest of the app, and no resort
screen overflows horizontally at the Pixel 7 viewport. Reduced
motion is already handled globally; do not add resort animations
that bypass it.

**Files:** `src/styles.css`.

**Acceptance:** Typecheck, lint, unit tests, build green; e2e
passes at both viewports; a render check at 390px-wide viewport
shows no horizontal scrollbar on `/resort`, `/mission-control`,
and `/engineering`.

**Depends on:** Z-02, Z-04, Z-05.

### Z-07 — Light-theme parity for resort classes

**Objective:** Bring the resort section to parity with the app's
`[data-theme=light]` theme: any resort rule that hard-codes a
dark-only colour gets a light-theme counterpart, or is rewritten
to use the theme variables (`--surface`, `--line`, `--muted`) so
both themes work from one rule.

**Files:** `src/styles.css`.

**Acceptance:** A check that every colour/background in the resort
section is either a theme variable or has a `[data-theme=light]`
counterpart (grep-verifiable); typecheck, lint, unit tests, build,
and e2e green; all three resort screens render legibly under
`data-theme="light"` at the desktop viewport.

**Depends on:** Z-06.

---

## Start tiles and the resort API

`docs/METRO_V1_IMPLEMENTATION.md` states: "Resort tiles in
`Start.tsx` display values derived from these same API entities."
That is not true today: `Start.tsx` derives every tile value from
the household simulation store (`metric()` over `clock`, `fleet`,
`tasks`, `alerts`, `energy`), and never calls the resort API. Z-08
and Z-09 make the claim true for resort tiles; Z-10 reconciles the
document with whatever is actually true afterwards.

### Z-08 — Resort-sourced tile metrics

**Objective:** Extend the tile metric system so a tile can derive
its value from resort API state. Add resort metric kinds to the
`tileSchema` metric enum in `src/domain/models.ts` (at minimum:
held reservations count and available clankers count, both derived
from `ResortState`), and a resolver in `Start.tsx` that reads the
latest resort snapshot via `getResortSnapshot()` from
`src/domain/resort-api.ts`. When the simulator is unreachable and
no cached state exists, the tile shows an explicit unavailable
label — never a fabricated or stale-as-live number; cached state
is shown with the tile's existing `SIM` tag and the stale state
visible.

**Files:** `src/domain/models.ts`; `src/pages/Start.tsx`;
`tests/ui.test.tsx`.

**Acceptance:** A new Vitest case renders `Start` with a stubbed
resort snapshot and asserts a resort-metric tile displays the
derived count; a second case with the API failing and no cache
asserts the unavailable label and no numeric value. The existing
Start tile-editing test passes unmodified. Typecheck, lint, full
Vitest, and build green.

**Depends on:** None.

### Z-09 — Resort tiles in the default Start layout

**Objective:** Add default Start tiles bound to Z-08's resort
metrics — at minimum a reservations tile and a resort-fleet tile,
grouped under a "Resort" group and routing to `/resort` — in the
seeded default tile set (`src/domain/seed.ts`). Existing saved
layouts are user data: fresh state gets the new tiles; a stored
layout must load exactly as saved, with no tiles added, removed,
or reordered. If the store cannot distinguish fresh state from a
saved layout, stop and report rather than migrating silently.

**Files:** `src/domain/seed.ts`; `src/state/store.ts` (only if
fresh-state detection needs it); `tests/ui.test.tsx`.

**Acceptance:** A Vitest case with fresh state asserts the resort
tiles render with API-derived values (stubbed snapshot, per Z-08);
a case with a pre-existing saved layout asserts the layout loads
byte-identical with no resort tiles injected. Typecheck, lint,
full Vitest, and build green.

**Depends on:** Z-08.

### Z-10 — Reconcile the implementation doc

**Objective:** Documentation only. Correct
`docs/METRO_V1_IMPLEMENTATION.md`'s Start-tiles sentence (and any
directly dependent claim in the same paragraph) so it states
exactly which Start tile values derive from resort API entities
after Z-08/Z-09, which still derive from the household simulation
store, and how unavailable resort state is displayed. If any part
of the original claim could not be made true, the doc says so
plainly instead of implying the wiring exists.

**Files:** `docs/METRO_V1_IMPLEMENTATION.md`.

**Acceptance:** Every sentence in the corrected paragraph is
verifiable against `Start.tsx`'s actual behaviour (a reviewer can
point each claim at the code path that makes it true); no other
section of the doc changes; typecheck/lint/test/build unaffected
and green.

**Depends on:** Z-08; Z-09 if it lands.

---

## NOT CHUNKED — and why

- **Visual design beyond the existing tokens.** A new palette,
  type scale, tile/layout redesign, or a fresh interpretation of
  the Metro design language against
  `design/metro/metro-hardware-simulation-v1.md` is design
  judgment for an owner/design session. Z-01–Z-07 deliberately
  constrain Luna to applying the system that exists.
- **Accessibility audits.** The screen-reader audit, automated
  contrast audit across custom accents, browser-zoom testing, and
  real-device touch testing scoped in `CODEX_HANDOFF.md` require
  assistive technology, measurement tooling, and judgment calls
  about acceptable thresholds — not honestly reducible to a
  coverage check.
- **Bundle size / code-splitting.** The eager-import split scoped
  in the handoff is a performance-architecture decision (which
  pages split, what the loading states are) and is outside this
  task's two scoped items.
- **Hardware and device smoke tests.** Android PWA, Chromebook,
  and desktop device validation needs named physical hardware;
  Windows Phone remains research-only per
  `docs/HARDWARE_COMPATIBILITY.md`. No chunk may claim a device
  result.
- **ROADMAP "Next" feature build-out.** Recurrence calendars,
  genuine reservations, PBX queues, and the rest of the unbuilt
  feature list are product work, not part of the two scoped items
  decomposed here.
