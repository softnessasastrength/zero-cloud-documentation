# Local resort simulation service

The Metro prototype now includes a local HTTP service for a versioned fictional-resort state. It is a development simulator, not a production service, and it does not connect to physical devices, payroll, payments, or real guest records.

## Run it

From `playground/`:

```sh
npm ci
npm run dev:stack
```

The web client runs at Vite's printed URL. The API listens on `127.0.0.1:4174`. To run only the API use `npm run simulator`. Set `ZERO_CLOUD_DATA_DIR` to choose the local persistence directory and `ZERO_CLOUD_SEED` to start a fresh scenario with another seed. The default `.data/` directory is ignored by Git.

## API v1

| Method and path | Purpose |
| --- | --- |
| `GET /api/health` | Reports service availability and synthetic-data status. |
| `GET /api/state` | Returns current domain state, virtual time, scenario seed and events. |
| `GET /api/events` | Returns the append-only projected event list. |
| `POST /api/commands` | Validates and applies one versioned simulation command. |
| `GET /api/replay` | Rebuilds state from the initial seed and command journal and returns a SHA-256 state hash. |

Commands have stable IDs for idempotency and include `recordedAt` wall time separately from virtual `simulation_time`. The journal is newline-delimited JSON. After each accepted command, a snapshot is written through a temporary file and atomic rename. On startup, the append-only journal is replayed and validated; the journal remains authoritative if the snapshot write was interrupted.

The event envelope carries `event_id`, `scenario_id`, `simulation_time`, `recorded_at`, `event_type`, `schema_version`, `actor_id`, `subject_id`, `correlation_id`, `causation_id`, and a typed domain payload. The seed payroll projection explicitly records 40 synthetic eligible hours at 0.5 Experience Credits per hour. A break reservation validates employee, table, credit balance and clanker availability before committing reservation, credit redemption, protected break and dispatch together. A conflict rejects the command without changing the input state.

## Boundaries and limits

This initial vertical slice contains one employee, one two-seat table and two synthetic clankers. The scenario is deterministic for a fixed seed and ordered command journal. `recordedAt` is included in replay, so replays of a stored journal reproduce the same state and event envelope. The JSONL journal is suitable for a single local process, not concurrent writers or multi-user internet hosting. There is no authentication; the server binds to loopback by default. Do not expose it to a LAN or public network.

The browser's original estate simulation remains intact. It still models household service tasks independently. The new local service introduces explicit restaurant, workforce, ZeroPay credit, and dispatch entities; the Metro screens are connected in the following implementation stage.
