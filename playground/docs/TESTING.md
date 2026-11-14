# Testing

## Automated coverage

- `tests/engine.test.ts`: original household engine determinism, delayed completion, conflicts, role restrictions, faults, and dependencies.
- `tests/resort.test.ts`: credit accrual, atomic table/break/credit/dispatch confirmation, event replay, clock, and engineer fault policy.
- `tests/resort-api.test.ts`: disconnected reservation outbox, receipt-based synchronization, and visible reconnection rejection.
- `tests/ui.test.tsx`: tile editing plus IndexedDB persistence.
- `e2e/resort.spec.ts`: reservation to Mission Control and engineer recovery flow on desktop/mobile viewport profiles.
- `simulator/api-smoke.mjs`: service launch, reservation commit, scenario isolation, restart recovery, and deterministic replay hash.

Run `npm run test:api`, `npm run test:pwa`, `npm run typecheck`, `npm test`, `npm run lint`, `npm run build`, and, when Playwright Chromium is installed, `npm run test:e2e`.

## Verification record for this implementation draft

Passed locally: API smoke; built PWA shell/manifest/service-worker/proxy smoke; typecheck; 12 Vitest tests across four files; lint; production build. Playwright was attempted but could not launch because the Chromium executable is not installed in this environment. No hardware PWA-install test or Windows Phone smoke test has been performed. Build succeeds with a Vite advisory that the existing chart/editor JavaScript bundle exceeds 500 kB minified.
