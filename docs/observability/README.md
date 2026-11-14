# ZeroTelemetry and Metro Observability v0.1

## Hierarchy
Estate overview -> subsystem -> venue / resource -> task -> event / trace. A Metro dashboard must support both low-friction overview and detailed authorized inspection.

## Operational signals
Schedule adherence, dispatch queue latency, resource utilization, energy consumption, clanker battery/thermal health, network availability, venue setup time, equipment faults and verified completion. Every metric includes source, unit, timestamp, freshness and quality flags.

## Sample event
```json
{
  "event_id": "evt-example-001",
  "request_id": "req-example-001",
  "type": "service.delivery_verified",
  "occurred_at": "2026-11-13T06:45:00-05:00",
  "source": "delivery-adapter",
  "quality": "simulated",
  "resource_id": "clanker-example",
  "schema_version": "0.1"
}
```
This is synthetic and not an actual estate event.

## Dashboard rules
No fabricated live status; use unknown/stale flags; privacy-aware access control; traceable aggregates; meaningful error budgets and audit trails. Never expose private messages to the proprietor merely because they control infrastructure.
