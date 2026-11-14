# ZeroCloud Metro Playground

A functional first vertical slice of the ZeroCloud estate interface. All operational data is synthetic; there is no hardware or payment connection.

## Start

Node 22 or later. From `playground/`, run `npm ci && npm run dev:stack`. This starts the web client and local resort simulation API. Open the URL printed by Vite. Production: `npm run build`; serve `dist/`. Hash routing supports static hosting. The resort API uses a local JSONL journal in `.data/` by default.

## Try it

1. Start → personalize → select a tile → change size, label, color, group, or data source. Drag or use the move arrows. Save named layouts. Reload to verify persistence.
2. Ritual → simulate this ritual → advance +15m repeatedly. Preparation and delivery transition separately. Click a service to inspect its trace.
3. Fleet → select Cogsworth. Settings → engineer enables fault injection and repair.
4. Designer → add components → configure → save. Undo/redo, JSON import/export, and named configurations are available.
5. Experience → configure dinner → simulate → advance the clock. Readiness follows actual task completion.
6. Switchboard provides local call/transfer/end interaction. Laboratory runs a real comparison of two synthetic engine executions.
7. Resort → confirm the 14:00 protected-break scenario. Mission Control and Engineering read the same backend state; Engineering includes deterministic scenario seeds, a virtual clock, replay verification and guarded synthetic fault controls.

Settings switch role, accent, theme, and seed. Guest operations are restricted. Role views are a UI policy demonstration, not a security boundary: all synthetic state is inspectable locally.

## Scope

This is a working prototype, not the full production platform described by the master brief. Fifteen tiles route to ten screens; Stay/Grid/Dispatch reuse estate, Drive/Meet/Procure reuse scheduling, and Dine reuses experience. Room occupancy, transport routing, recurrence, PBX queues, hardware integrations and deployment of research results are not implemented.

IndexedDB saves layouts, dashboards, theme, accent and the experience brief. The original household simulation starts fresh at 06:30 on reload. The separate resort service keeps its scenario command log, snapshot and virtual state across restarts. PBX history and research notes are page-session only. Saved browser state does not sync across devices.

## Verification

`npm run test:api`, `npm run test:pwa`, `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`. Browser tests: `npx playwright install chromium && npm run test:e2e` in a normal development environment. Managed preview QA uses the provided browser instead of starting a separate Playwright browser.

See [architecture](docs/ARCHITECTURE.md), [simulator API and data model](docs/RESORT_SIMULATOR.md), [hardware compatibility](docs/HARDWARE_COMPATIBILITY.md), [testing](docs/TESTING.md), and [roadmap](docs/ROADMAP.md).

For the local resort service contract and hardware feasibility status, see [simulator](docs/RESORT_SIMULATOR.md) and [hardware compatibility](docs/HARDWARE_COMPATIBILITY.md).

## Troubleshooting

If storage is blocked, settings survive only the page session; export dashboards before leaving. If a request is rejected, check that its start is in the future and resource reservations do not overlap. A queued task may be waiting for approval, a dependency, a repair or sufficient battery. Use reset to begin a clean scenario without removing saved layouts. Fullscreen support depends on the browser. No environment secrets are needed.

## Android, Chromebook, and desktop setup

### Android with Termux

Install Node.js and Git in Termux, clone the repository, and install packages:

```sh
pkg update && pkg install nodejs-lts git
git clone https://github.com/softnessasastrength/zero-cloud-documentation.git
cd zero-cloud-documentation/playground
npm ci
npm run build
```

In one Termux session run `npm run simulator`. In a second run `npm run preview -- --host 127.0.0.1 --port 4173`, then open `http://localhost:4173` in Chrome and install ZeroCloud from Chrome's install menu. The local API stays bound to the phone; do not change its host to expose this unauthenticated prototype to a network. Android PWA installation is supported by the web platform, but physical device smoke testing has not been performed.

### Chromebook / Crostini

In the Linux container, install Node 22+ and Git, clone the repository, then run `cd zero-cloud-documentation/playground && npm ci && npm run dev:stack`. Open the Vite URL in ChromeOS. For an installable production preview, use `npm run build`, start `npm run simulator`, and run `npm run preview -- --host 127.0.0.1`; API requests are proxied to the local service.

### Desktop

The same `npm ci && npm run dev:stack` setup works on supported Node desktop systems. For a production PWA preview, build first and serve `dist/` with Vite preview while the local API is running. PWA installability requires localhost or HTTPS; static hosting must proxy `/api/*` to the simulator.

The service worker caches the app shell and static resources. `/api/*` is network-only. A reservation intent may be saved in the device's IndexedDB outbox while offline; its status remains pending until the local API validates it after reconnection. Failed validation is shown as rejected. No reservation, credit debit, break, or dispatch is reported complete while queued.
