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

## Verification record — 2026-11-14 (Muse verification pass, branch `metro-verification_muse`)

Re-run from a clean `npm ci` (Node v24.22.1). Initially failing: typecheck and lint (5 dead imports) and Playwright e2e (2 passed / 4 failed — the resort, mission-control, and engineering routes were not wired into the router). After the fixes recorded in `CODEX_HANDOFF.md`: typecheck, lint, production build, PWA smoke, and API smoke (replay hash `29176a953324…`) pass; 14 Vitest tests across five files pass; Playwright e2e passes 6/6 on desktop and phone viewports. E2E caveat: the sandbox cannot download Playwright's headless-shell artifact, so e2e ran against the full Chromium build in the local browser cache via a temporary executable-path override (deleted after the run); the stock `npx playwright install chromium && npm run test:e2e` path stands for normal development environments. No hardware PWA-install test or Windows Phone smoke test has been performed.
