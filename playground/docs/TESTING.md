# Testing

Vitest tests engine determinism, delayed completion, correlation IDs, conflicts, guest restrictions, approval holds, fault failure, dependencies and private event filtering. React Testing Library exercises tile resizing with an IndexedDB write/read using fake-indexeddb. Playwright specifications cover navigation and ritual execution on desktop and a narrow viewport.

Local verification: TypeScript and production build passed; six Vitest tests passed. Browser QA verifies Start rendering and a ritual advancing from queued to preparing/completed. Hosted publication is verified by the deployment service. CI runs lint, typecheck, unit tests, build and Playwright. Do not report unrun CI or Playwright jobs as passing.
