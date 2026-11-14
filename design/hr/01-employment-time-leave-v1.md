# ZeroCloud HR Constitution — Employment, Scheduling, Leave and Protected Time v1

**Decision status:** Accepted project design requirements, pending implementation and jurisdiction-specific legal review. Applies to fictional/simulated ZeroCloud workforce models; real deployment must comply with applicable law. **Date:** 2026-11-14.

## Core employment contract
- Each worker negotiates guaranteed **meaningful paid hours**. Full-time 40 hours per week is the standard illustrative contract, not a forced universal schedule. Part-time and custom flexible arrangements are valid.
- ZeroCloud bears demand and staffing risk. It must provide the contracted hours through normal work, reassignment, meaningful paid learning, paid exploration, alternative assignments, or guaranteed compensation. **Insufficient demand is a problem for management to solve, not a pretext to reduce the worker's guarantee.**
- No unilateral reduction in guaranteed hours, earnings, or employment classification. Changes require genuine voluntary renegotiation, documentation and lawful protections.
- Employees can arrange flexible work blocks, split shifts and independent schedules subject to legitimate safety handoffs and agreed service coverage. Scheduling must support domestic life rather than demand that life fit a rigid template.
- On-call and employer-reserved availability count as paid working time under ZeroCloud policy, even where statutory minima would be lower. If coverage is no longer needed, the employee is released from the reserved time without forfeiting contractual guarantees.
- Managers may reorganize work, add paid development, and recruit voluntary additional-hours coverage to meet demand. Coverage is the organization's responsibility, not the departing employee's.

## Employee-controlled time and leave
- Discretionary protected leave is initiated by the employee, without requiring a reason, manager approval, proof of family relationship or performance-based permission. Provide a straightforward notification mechanism; do not impose coverage-finding obligations.
- Urgent and last-minute departures are allowed. Notify when practicable and perform a minimal safety-critical handoff where feasible. Management arranges replacement coverage.
- Offer comprehensive paid leave, extended leave, and an indefinite unpaid-leave safety net without attendance punishment. Record the distinction between paid entitlement, unpaid protected status, and negotiated work-cycle arrangements.
- Enable month-long and summer-length absences by advance staffing design, voluntary extra-hours opportunities and work-cycle reorganization; never force disclosure of intimate reasons.
- **Chosen family counts:** partners, affectionate friendships, caregiving relationships and domestic bonds deserve the same scheduling and leave consideration as legal/biological family, including accompanying an important person to medical appointments.
- Leave policy may be more generous than law; statutory leave and safety protections remain floors, not ceilings.

## Off-clock privacy
- **Off-clock time is a black box.** Neither managers nor corporate scheduling systems may monitor, access, demand explanations for, or contact employees during personal time, absent the employee's voluntary initiation/opt-in.
- Exceptions are narrowly documented legal notices and imminent life-safety emergencies. No routine 'urgent' operational exception, passive tracking, or retaliation for not answering.
- Employees may voluntarily offer availability; consent must be revocable and must not silently convert into mandatory on-call status.

## HR authority and remedies
- HR is a staffed human **parallel authority**, not a subordinate mailbox for managers. It may authorize immediate leave, protective scheduling changes, and provisional relief without awaiting the direct manager's approval.
- Employees have a direct confidential HR route, written receipt, clear appeal path and anti-retaliation protections.
- Attendance and scheduling decisions must be inspectable, justified, correctable and subject to independent review.

## Architecture and test requirements
- Versioned employment agreements; guarantees separated from assignments and attendance; schedule changes require consent records.
- Paid reserved/on-call ledger; protected leave without punitive attendance points; coverage planner assigns responsibility to operations.
- Private off-clock state with no ordinary manager access or contact triggers.
- Test: 36 hours of assigned work against a 40-hour guarantee must generate 4 hours of meaningful paid alternative work or guaranteed pay, never an automatic shortfall.
- Test: last-minute chosen-family caregiving leave does not require relationship proof or manager approval; HR can immediately authorize it.
- Test: off-clock notifications are blocked absent employee opt-in or the two narrow exceptions.
- Test: manager cannot reduce guaranteed hours unilaterally or punish protected leave.

## Unresolved implementation details
Jurisdictional employment law, paid-leave funding, precise notice and safety-handoff mechanics, and scheduling algorithm selection. These may refine procedures but cannot silently negate accepted policy.

Related: ZeroCloud Metro simulation PRs #5–#7 and terminal governance PR #9. No merge authorized.
