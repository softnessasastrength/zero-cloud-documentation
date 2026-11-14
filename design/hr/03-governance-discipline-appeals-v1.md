# ZeroCloud HR Constitution — Governance, Discipline, Accountability and Appeals v1

**Decision status:** Accepted project design requirements, pending implementation and legal review. **Date:** 2026-11-14.

## Equal accountability
- Managers are **not exempt** from the rules governing employees. Rank confers responsibility, not immunity or presumption of correctness.
- Employee and manager claims are evaluated using the same evidence and procedural standards. Conflicts of interest require recusal and independent review.
- Transparency is the default for the rationale and process of decisions affecting an employee; protect third-party privacy and legitimate confidential evidence without allowing secrecy to defeat meaningful appeal.

## Justified discipline
- Every corrective action requires a specific allegation, policy or contract provision, documented supporting facts, proportional reasoning, employee opportunity to respond, named decision authority and written notice.
- No vague 'attitude', unexplained productivity judgment, manager preference, or retaliation masquerading as discipline.
- Distinguish skill mismatch, insufficient training, systemic staffing defects and disability/accommodation issues from culpable misconduct. Investigate reassignment, coaching, paid learning and process improvement before punitive responses when appropriate.
- Keep objective work measures contextual: a failed packing metric does not establish overall worker incompetence.
- Corrective actions must be reviewable, time-bounded where appropriate, and capable of correction or removal when overturned.

## Genuine open-door and appeals process
- Any employee can bypass their direct manager and seek independent HR review without retaliation.
- HR is staffed, empowered and organizationally parallel to operations; it can authorize immediate protective leave/schedule adjustments, preserve evidence and pause disputed non-safety-critical actions.
- Appeals must be substantive: independent reviewer, clear timelines, evidence access consistent with privacy law, employee statement, written reasoned outcome and meaningful remedies.
- Managers face equivalent accountability, including corrective action, removal from decision authority or employment consequences when justified by the same standards.
- Track case intake, decisions, appeal state, remedies, implementation and independent audit without exposing sensitive case details to unrelated personnel.

## NAP and sovereignty alignment
- Owner/master system authority is not a license to coerce, retaliate, monitor off-clock life or bypass employee consent, privacy and protected rights.
- Delegation, oversight and emergency authority remain scoped and logged. Safety-critical action is narrowly permitted when justified and subject to review.
- Do not use automation or experimental AI as a silent final arbiter of discipline, leave, wages or termination. AI may provide inspectable decision support, with human responsibility and appeal.
- The proposed non-aggression principle needs explicit adjudication rules for conflicting rights, shared property and emergencies; it does not supersede applicable law.

## Technical governance and test cases
- Event-sourced case lifecycle: allegation -> notice -> response -> independent review -> decision -> appeal -> remedy/closure.
- Role-scoped access, tamper-evident audit trails, employee-visible decision records, documented redactions, retention/deletion policy, and anti-retaliation alerts with human oversight.
- Test: a manager cannot unilaterally approve their own misconduct investigation.
- Test: a disciplinary record without concrete facts and cited policy fails validation.
- Test: employee appeals a productivity-based action and receives a reasoned review considering training and alternative roles.
- Test: HR can grant protective leave independently of the employee's manager.
- Test: owner master credentials cannot bypass protected personnel confidentiality.
- Test: overturned discipline triggers documented correction and remedy, not merely an advisory note.

## Implementation boundaries
These are design commitments, not a representation that an employment-law-compliant HRIS or appeals board exists. Before any real deployment, review labor, disability, leave, privacy, wage, intellectual-property and recordkeeping requirements in the relevant jurisdiction.

Related: terminal sovereignty PR #9; employment/time and learning/benefits HR drafts. No merge authorized.
