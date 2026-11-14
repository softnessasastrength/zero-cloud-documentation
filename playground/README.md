# ZeroCloud Metro Playground

A functional first vertical slice of the ZeroCloud estate interface. All operational data is synthetic; there is no hardware or payment connection.

## Start

Node 22 or later. From `playground/`, run `npm ci && npm run dev`. Open the URL printed by Vite. Production: `npm run build`; serve `dist/`. Hash routing supports static hosting.

## Try it

1. Start → personalize → select a tile → change size, label, color, group, or data source. Drag or use the move arrows. Save named layouts. Reload to verify persistence.
2. Ritual → simulate this ritual → advance +15m repeatedly. Preparation and delivery transition separately. Click a service to inspect its trace.
3. Fleet → select Cogsworth. Settings → engineer enables fault injection and repair.
4. Designer → add components → configure → save. Undo/redo, JSON import/export, and named configurations are available.
5. Experience → configure dinner → simulate → advance the clock. Readiness follows actual task completion.
6. Switchboard provides local call/transfer/end interaction. Laboratory runs a real comparison of two synthetic engine executions.

Settings switch role, accent, theme, and seed. Guest operations are restricted. Role views are a UI policy demonstration, not a security boundary: all synthetic state is inspectable locally.

## Scope

This is a working prototype, not the full production platform described by the master brief. Fifteen tiles route to ten screens; Stay/Grid/Dispatch reuse estate, Drive/Meet/Procure reuse scheduling, and Dine reuses experience. Room occupancy, transport routing, recurrence, PBX queues, hardware integrations and deployment of research results are not implemented.

IndexedDB saves layouts, dashboards, theme, accent and the experience brief. Simulation starts fresh at 06:30 on reload. PBX history and research notes are page-session only. Saved browser state does not sync across devices.

## Verification

`npm run typecheck`, `npm run lint`, `npm test`, `npm run build`. Browser tests: `npx playwright install chromium && npm run test:e2e` in a normal development environment. Managed preview QA uses the provided browser instead of starting a separate Playwright browser.

See [architecture](docs/ARCHITECTURE.md), [testing](docs/TESTING.md), and [roadmap](docs/ROADMAP.md).

## Troubleshooting

If storage is blocked, settings survive only the page session; export dashboards before leaving. If a request is rejected, check that its start is in the future and resource reservations do not overlap. A queued task may be waiting for approval, a dependency, a repair or sufficient battery. Use reset to begin a clean scenario without removing saved layouts. Fullscreen support depends on the browser. No environment secrets are needed.
