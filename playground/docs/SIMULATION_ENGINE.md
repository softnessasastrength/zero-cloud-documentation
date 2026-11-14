# Simulation engine

createSimulation(seed) starts at minute 390. advance(state, minutes) clones state and advances integer minutes, capped at 1,440 per call. A seeded linear congruential generator supplies repeatable temperature variation. Idle healthy units charge below 95%; active units consume 0.6 percentage points per minute. Capacity and thermal values are synthetic assumptions.

Tasks transition queued → preparing → completed. An active fault or critically low battery fails a task. Failed dependencies fail dependents; incomplete dependencies and outstanding approvals hold tasks. Reservation conflicts reject submission. Actual completion timestamps are recorded only after execution. Retry returns failed tasks to queued. Events carry request/task/resource/correlation IDs and simulation latency. Last 2,000 events and 288 history samples are retained.

Ritual produces three preparation/delivery chains. Dinner produces preparation/service. Individual task submissions are not transactional batches: if a later submission conflicts, earlier accepted tasks remain visible. Schedules currently reserve clankers only; no spatial navigation or collision avoidance is modeled.
