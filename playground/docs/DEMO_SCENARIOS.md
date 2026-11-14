# Reproducible resort demos

All identities, schedules, fleet data and event records below are synthetic. Fixture histories persist independently by seed and can be replayed from the Engineering console.

## 1. Protected 14:00 restaurant break

1. Start both local processes with `npm run dev:stack`, then open **Resort**.
2. The fixture clock begins at 13:00. Mara Ellis has 40 eligible paid hours; `40 × 0.5` yields 20 Experience Credits.
3. Keep the 14:00 start, choose a companion, and review the 12-credit quote.
4. Confirm the request. One accepted command reserves Winter Garden Table 04, redeems credits to an 8 EC balance, protects 14:00–15:00, and schedules Percival as coverage.
5. Open **Mission Control**. Table, credit, employee-break, fleet, and event values are projections of the same accepted state.
6. Open **Engineering** (select Engineer in Settings), step to 14:00 to observe break/dispatch start, then step through 15:00 to observe the protected break and assignment complete.
7. Select **Replay and verify**. The displayed replay hash should match the live state at the same paused virtual time.

## 2. Thirty-six-hour credit fixture

In Engineering, select **36-hour entitlement**. Mara's fixture has 36 eligible paid hours, so accrual is 18 EC. A valid 12 EC break reservation leaves 6 EC. The accrual rate is unchanged; performance does not affect it.

## 3. Actuator fault recovery

Select **Actuator fault recovery**. Percival starts in a synthetic fault state; the reservation form selects Cogsworth as the available coverage unit. In Engineer mode, use **Verify repair** to clear Percival's simulated fault. The repair is logged; it does not touch hardware.

## API smoke run

`npm run test:api` creates a temporary data directory, accepts a reservation, checks remaining credits, switches fixture seeds, restarts the local server, and verifies the same selected scenario state and replay. It removes the temporary test directory afterward.
