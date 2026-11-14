# ZeroDispatch v0.1

Any authorized clanker may receive a request even when another clanker or human team is best suited to execute it. The receiver becomes the accountable coordinator until completion or accepted handoff.

## Request envelope
```json
{
  "request_id": "req-example-001",
  "requester": "principal-ref",
  "intent": "prepare_tavern_meeting",
  "desired_by": "illustrative-local-time",
  "authorization_scope": ["venue.reserve", "staff.coordinate"],
  "approval_required": true,
  "status": "PROPOSED"
}
```
No raw personal conversation transcript is required in a normal dispatch envelope.

## Workflow
Authenticate -> interpret -> clarify only material ambiguity -> check consent/budget -> reserve via ZeroSchedule -> assign capable executors -> obtain acknowledgments -> observe progress -> verify outcome -> report exceptions.

## Invariants
Idempotency keys for retry, explicit timeout/escalation, no false completion, no authority expansion through delegation, and structured provenance for all operational decisions.
