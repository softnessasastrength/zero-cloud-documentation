# ZeroCloud Metro: Hardware & Simulation Design v1.0

**Status:** Proposed / design review  
**Version:** 1.0.0-draft  
**Date:** 2026-11-14  
**Related:** #4 (Metro Universal Control Experience / ZeroFlow orchestration)  
**Nature:** Fictional resort, real software prototypes. A possible future, not a prediction.

## 1. Intent

Build an interactive, installable, hardware-agnostic Metro experience for operating a deeply simulated fictional ZeroCloud resort. The experience must be useful on real handheld devices, while simulation data is always labeled as synthetic. Optimize for engineering depth, extensibility, and documented behavior, not a superficial dashboard mockup.

### Principles
- **One world, many clients:** Shared simulation state; handheld, desktop, command center and experimental legacy clients.
- **No invented telemetry:** Every metric derives from a simulated entity, event, calculation, or explicitly labeled fixture.
- **Human-first operations:** Protected employee breaks, earned hospitality credits, equitable access, and human-clanker service parity are first-class invariants.
- **Theatrical presentation, reliable operation:** Clanker personality must not obscure real faults, guest consent, or safety.
- **Speculative rigor:** Separate canon, requirements, simulations, prototypes, and validated real-world claims.
- **Infinite zoom:** From resort overview to individual tables, clanker actuators, scheduling decisions, accounting entries and fault traces.

## 2. Experiences

### 2.1 Metro Handheld
Windows Phone/Metro-inspired design language: bold typography, panoramic navigation, live tiles, legible motion, touch-first interaction and accessible reduced-motion alternatives. Guest Mode: bookings, preferences, service requests, privacy, receipts. Employee Mode: shifts, protected breaks, training, earned credits, resort access. Engineering Mode: permitted fleet status, diagnostics and simulation actions. Role-based authorization and identity boundaries must be enforced by backend services, not by UI hiding.

### 2.2 Metro Mission Control
Facility map and selectable floors/venues; occupancy and capacity; reservation timeline; restaurant throughput; clanker dispatch and service parity; staffing coverage and protected breaks; utility demand; ZeroPay and experience-credit liability; friction observatory; synthetic incident stream. Drill-down from every aggregate into grounded entities and contributing events.

### 2.3 Metro Engineering
Virtual clock controls (pause, resume, speed, step); scenario selection; deterministic replay; seed/configuration visibility; fault injection with safety guards; clanker hardware abstraction, battery/actuator state, maintenance predictions; performance traces and event logs; comparative scheduling policy experiments. Simulation controls must never connect to physical equipment by default.

## 3. Architecture

```text
Android / PWA / Chromebook / Desktop / Legacy experiment
                         |
                Metro Client API
                         |
           Authentication + policy layer
                         |
          Simulation Kernel / Virtual Clock
                Event log + snapshots
                         |
     +---------+---------+---------+---------+
     |         |         |         |         |
  ZeroFlow  Temporal  ZeroFleet  ZeroPay  Facilities
     |         |         |         |         |
  Hospitality   Workforce   Restaurants   Transit
                         |
          Metrics projections / read models
                         |
          Metro dashboards and replay tools
```

Prefer explicit versioned API contracts and stable domain identifiers. Use event-driven modeling with reproducible scenarios. Store timestamps in a documented canonical format, distinguish virtual from wall time, and track scenario seed, configuration revision, schema version and application commit.

## 4. Hardware target matrix

| Target | Initial strategy | Status |
|---|---|---|
| Modern Android / Pixel | Installable PWA, optional native wrapper for hardware integration | Proposed |
| Chromebook / Crostini | Browser/PWA; local dev backend and CLI | Proposed |
| Desktop | Responsive browser; optional packaged shell | Proposed |
| Dedicated kiosk | Browser kiosk mode on supported hardware | Proposed |
| Windows Phone 8.x / Windows 10 Mobile | Device-specific feasibility study, legacy API client if toolchain, signing and connectivity permit | Research only |

**Windows Phone constraint:** Do not claim installability without identifying device model, OS/build, supported SDK, app packaging/signing/developer unlock, TLS support, and realistic networking capabilities. Prefer a thin compatible client rather than porting the simulation kernel. No requirement to depend on obsolete Microsoft services.

## 5. Core simulated domains

1. **World and facilities:** buildings, rooms, maps, paths, capacities, HVAC, energy and maintenance.
2. **Hospitality:** reservations, tables, suites, guest journeys, preparation and recovery.
3. **Temporal Engine:** allocation, dependencies, breaks, travel buffers, resource conflicts and confirmed commitments.
4. **Workforce:** paid hours, employee entitlements, training, protected breaks and fair staffing coverage.
5. **ZeroPay:** explicit price/credit quotes, ledgers, experience-credit accrual at 0.5 per eligible paid hour, redemptions, liabilities and dispute records.
6. **Clanker Fleet:** individual identity, capability, location, availability, battery, mechanical state, maintenance, dispatch, handoff and theatrical persona.
7. **Friction Observatory:** time lost, unnecessary interactions, failed handoffs and who bears shifted burden.
8. **ZeroTransit:** simulated arrivals, dispatch, movement and accessible routing.

Do not assert that a software simulation validates physical robotics performance.

## 6. Example end-to-end scenario: 14:00 steakhouse break

Employee requests 14:00–15:00 protected break with a guest; system checks staffing coverage, actual simulated table inventory and travel buffer; returns a priced Experience Credit quote; on confirmation, atomically reserves dependent resources or returns a comprehensible alternative. At break start, employee enters Guest Mode and routine work messages are deferred. Fleet dispatch absorbs permissible demand peaks while preserving equivalent service standards and other workers' breaks. A simulated clanker actuator fault triggers safe task suspension, alternate dispatch, guest-visible recovery and traceable incident accounting. No theatrical dialogue delays safety response.

## 7. Event and observability contracts

Minimum event fields: `event_id`, `scenario_id`, `simulation_time`, `recorded_at`, `event_type`, `schema_version`, `actor_id`, `subject_id`, `correlation_id`, `causation_id`, `payload`. Document idempotency, ordering, replay and redaction rules.

Every dashboard panel must document:
- Entity/source and query definition
- Units, aggregation window and virtual/wall-clock semantics
- Staleness, missing-data and error states
- Drill-down provenance and accessibility behavior
- Whether data is simulated, fixture-based or real test telemetry

## 8. Security and privacy

Isolate guest, employee, operator and engineering capabilities. Explicitly gate fault injection and administrative operations. Separate personal booking information from employer scheduling visibility. Support disposable guest sessions and consent-based persistent preferences. Treat all simulated personally identifying records as synthetic. Never expose control endpoints to actual devices without separate physical safety review.

## 9. Verification plan

- Deterministic replay produces identical state hashes for identical seed/configuration/build.
- Event schemas validate; rejected events cannot corrupt projections.
- Booking conflicts never produce double reservations.
- Employee credits accrue exactly 0.5 per eligible paid hour, independent of performance.
- Confirmed breaks are protected against routine reassignment; violations are surfaced as failures.
- Clanker substitution does not silently downgrade a specifically purchased experience.
- Dashboard metrics reconcile to domain events and ledger entries.
- Offline, reconnect, stale-state, reduced-motion and small-screen tests.
- Fault injection cannot bypass safety and authorization checks.
- Legacy device support claims require a real hardware smoke test.

## 10. Suggested staged implementation

**Stage A:** Design tokens, live tiles, responsive navigation, mock-but-traceable fixture data, installable PWA and accessible interaction patterns.

**Stage B:** Local deterministic simulation kernel, scenario fixtures, virtual clock, event log, basic entity API, persistent snapshots and replay.

**Stage C:** Restaurant bookings, workforce scheduling, protected break scenario, earned-credit ledger and clanker dispatch.

**Stage D:** Facility maps, operational drill-down, diagnostics, fault injection, incident replay and scenario comparisons.

**Stage E:** Android wrapper and hardware integrations where justified; Windows Phone feasibility spike with device inventory and explicit go/no-go.

## 11. Acceptance criteria for v1 design

- Working specification checked into the repository and linked from design review.
- No claim of existing deployed resort or validated physical clankers.
- Clear modular boundaries, API/event contracts, hardware matrix and testable invariants.
- One fully described cross-domain scenario, with traceability to human-first operating principles.
- Implementation remains separate and requires its own reviewed PRs and tests.

## 12. Open decisions

- Client framework and component system
- Simulation language/runtime and persistence
- Scenario authoring format
- Live-tile refresh semantics and offline synchronization
- Map representation and asset pipeline
- Windows Phone target model and OS version
- Formal verification scope and performance budgets
