# ZeroSchedule v0.1

**Mission:** convert human intentions into feasible, consent-aware commitments for people, rooms, robots, vehicles, equipment, energy and staff.

## Core resources
Resource(id, type, capabilities, location, availability, maintenance_state, owner_scope); Reservation(id, resource_ids, start, end, setup_buffer, teardown_buffer, status, policy); Workflow(id, version, steps, dependency_edges, approvals); Commitment(id, request_id, deadline, owner).

## Reservation lifecycle
PROPOSED -> HELD -> CONFIRMED -> IN_PROGRESS -> COMPLETED, with explicit CANCELLED, FAILED and EXPIRED states. Holds expire; confirmation atomically verifies all resources. No partial success described as a confirmed booking.

## Scheduling constraints
Travel time, preparation, cooldown, accessibility, consent, qualifications, working hours, maintenance, charge state, resource capacity and priority. Optimize a weighted objective, but hard constraints always dominate convenience.

## Precision rituals
For coffee delivered at 06:45 and a warm towel ready at 07:00, plan backward from delivery deadlines: equipment checks, brewing, handoff, travel, towel warming, temperature safety and fallback capacity. Track planned/actual timestamps; an exact-time target is not a guarantee.

## Privacy
Two co-proprietors may maintain separate calendars and equal household authority. An availability query may return busy/free without titles, attendees or locations. Sharing and delegation require explicit scope.

## Failure handling
Replan when resources fail, escalate material changes, respect quiet hours and approved spending. Do not silently cancel or override the other proprietor's confirmed plans.

## Acceptance tests
- Reject conflicting reservations and stale holds.
- Preserve privacy across availability queries.
- Handle one clanker going offline before a delivery deadline.
- Reject unsafe temperature or unqualified transport assignments.
- Ensure cancellation compensates all held resources.
