# ADR-0001: Documentation-first, safety-gated architecture

- **Status:** Proposed
- **Date:** 2026-11-13

## Context
ZeroCloud spans robotics, household automation, hospitality, communications, transport and AI research. Premature implementation risks ambiguous authority and unsafe assumptions.

## Decision
Maintain versioned specifications, subsystem boundaries, event contracts, acceptance tests and decision records before implementation. Keep experiments isolated from live safety-critical systems. Prefer local-first operation and explicit consent.

## Consequences
Slower initial implementation, but reviewable interfaces, traceability, safer incremental prototypes and clearer contribution paths.
