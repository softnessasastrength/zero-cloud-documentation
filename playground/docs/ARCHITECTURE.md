# Architecture

ADR 001: Keep the React/Vite app in playground/ beside the documentation. The simulation has no backend dependency and does not justify splitting the source repository. Hosted publication uses a sanitized copy of this subdirectory in the Site source repository; GitHub remains the review source.

ADR 002: Hash routing for portable static hosting. Zustand owns state, Dexie persists only user configuration. The engine uses pure cloned state transformations. React screens invoke store actions; views never send hardware commands.

```mermaid
flowchart TD
 UI[React screens] --> Store[Zustand actions]
 Store --> Engine[Deterministic engine]
 Store --> DB[IndexedDB settings]
 Engine --> Events[Structured events]
 Events --> UI
```

Role filters are illustrative local controls, not authentication. No private real data should be entered. Persistence failures are surfaced in the shell. Simulation reset intentionally leaves browser configuration intact.
