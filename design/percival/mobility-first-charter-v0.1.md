# Percival: Mobility-First Experience Coordination Charter (Draft v0.1)

**Status:** Proposed design direction, not deployed functionality. **Priority:** First useful personal vertical slice before enterprise/resort expansion.

## Mission
Percival helps people exercise autonomy within real-world constraints. It coordinates chosen experiences without presuming the meaning of relationships, requiring disclosure of private origins, or overriding transportation preferences. Start with an authentic Windows Phone Metro-inspired Connecticut transit application that solves the owner's real journeys; generalize the same verified operations engine to shared experiences and later ZeroCloud enterprise workflows.

## Non-negotiable principles
1. **Mobility is foundational:** Before representing an outing as transportation-feasible, validate outbound **and** return travel for each participant. Optimize usable time together while honoring hard constraints.
2. **No fabricated operational reality:** No invented trains, stops, fares, delays, accessibility, venue hours, reservations, or route feasibility. Separate VERIFIED (with source/time), SCHEDULED (not live), INFEASIBLE (proved within stated coverage/constraints), UNKNOWN (insufficient data), and SOLVER_TIMEOUT. An LLM may interpret requests but never override deterministic validation.
3. **Constraints are instructions:** Hard constraints (e.g., Amtrak-only intercity travel, latest return, accessibility, no pickup) must not be relaxed silently. Preferences and negotiable limits remain separately modeled; changes require consent.
4. **Independent, symmetric privacy:** Two people can agree on a public destination and time while privately planning origins, routes, schedules, budgets, and departures. Sharing is granular, revocable, minimized, and never assumed. Avoid leaking origin via precise ETA or repeated suggestions.
5. **Relationships are not input requirements:** Dinner, friendship, dates, and shared activities need no relationship classification. The people determine what the experience means.
6. **Simplicity is a right; complexity is an invitation:** Metro UI for effortless daily use, optional engineering console exposing provenance, rejected alternatives, assumptions, trace, and reproducible scenarios.
7. **Failure is explicit:** If the trip cannot be proven possible, explain why or identify missing evidence. Never present a simulated journey as a real operational recommendation.

## Initial scope
- Rail: Hartford Line, Metro-North New Haven Line (and relevant branches), Shore Line East; later CTtransit and other Connecticut operators, Amtrak intercity, walking and scooter last-mile.
- Pin Hartford Union Station and Windsor Locks station; scheduled arrivals/departures, source timestamps, offline last-known-good cache, later realtime updates where verified.
- Real geographic Metro map, semantic zoom, panoramas/pivots, live tiles, accessible motion; responsive Android/Chromebook/desktop. Native Lumia/Windows Phone is a separate feasibility/testing track, not claimed supported.
- Experience planning: independent participant itineraries, mutually agreed meeting point/time, private preferences, round-trip assurance, optional budget and split proposal requiring both parties' consent.
- Geographic reachability and complex multi-stop itinerary solver with hard constraints, dwell times, deadlines, and auditable infeasibility reports.

## Data-to-operations pipeline
1. Acquire source GTFS archives, licensing/metadata, checksums, coverage, and refresh cadence. Store immutable raw versions.
2. Validate tables, foreign keys, service calendars, exceptions, timezones, GTFS times beyond 24:00, trip patterns, and agency-specific stop identities.
3. Compile dated service instances, stop events, station equivalences, footpaths, transfer edges, spatial indexes, and versioned network snapshots atomically.
4. Merge GTFS-Realtime only where available and correctly mapped; never assume CTtransit bus realtime covers rail. Retain scheduled vs observed/predicted distinctions.
5. Expose versioned APIs for station boards, reachability, itinerary solving, and provenance; cache offline with visible freshness.
6. Route using a deterministic transit algorithm (RAPTOR/CSA candidate), adding multi-stop constraint optimization only after a validated baseline.

## Reliability and safety tests
- Last-service-of-day and return feasibility; short/long transfers; missed connections and cancellations; overnight GTFS service dates; DST transitions; holidays; stale/broken feeds; station identity conflicts; accessibility constraints; disconnected/offline operation; transfer walk times; conflicting operators; route changes mid-trip; solver timeout; multi-failure combinations.
- Property/invariant tests: every recommended leg resolves to a dated source trip; every transfer meets constraints; every plan has an independently checked return; no UNKNOWN result is presented as feasible; no participant origin leaks into shared payload.
- Synthetic failure lab and deterministic replay isolated from real operational outputs. Keep immutable trace IDs and feed snapshot hashes.
- Human-friendly messaging for unverified information and verified alternatives; never guarantee real-world service operation.

## Implementation sequence / acceptance gates
**P0:** Source inventory, licenses, GTFS importer, validator, immutable snapshots, reproducible fixtures and tests.
**P1:** Accurate scheduled departure boards for Hartford and Windsor Locks with service-date handling and provenance; no invented data.
**P2:** Metro map + pinned station live tiles; cross-platform browser/PWA smoke tests; offline stale-state labels.
**P3:** Verified outbound/return journey planner and constrained solver; deterministic edge-case suite.
**P4:** Privacy-preserving collaborative Meet workflow, consent and expense negotiation (no payment execution).
**P5:** Statewide network expansion, reachability and engineering Failure Lab.
**P6:** Windows Phone native feasibility, separately verified on emulator and Lumia hardware.

**Definition of first success:** The owner can open Percival, check when a train is scheduled to leave Hartford or Windsor Locks, plan an outing and return, and clearly see when data is missing or uncertain. No production or real-time integration is claimed by this document.

## Relationship to existing ZeroCloud work
Preserve the existing resort Metro playground and simulation draft PRs. This charter defines the personal-first operational vertical slice and a shared data/solver contract, not a replacement for existing simulation code. Keep changes in draft PRs; do not merge without explicit authorization.
