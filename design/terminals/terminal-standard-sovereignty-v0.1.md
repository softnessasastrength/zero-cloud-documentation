# ZeroCloud Terminal Standard and Sovereignty Policy — proposal v0.1

**Status:** Design proposal, not an implemented or validated security system. **Date:** 2026-11-14. **Relationship:** Complements Metro hardware/simulation design PR #5, simulation PR #6, Metro client PR #7, and Lumia research Issue #8. Preserve their existing work.

## Vision
ZeroCloud's Metro-inspired visual language spans personal devices, shared wall panels, engineering consoles, and vintage terminals. **Feature parity is explicitly not required.** Every certified terminal must provide a small complete experience suited to its location, role, and hardware. Avoid hiding primary navigation in generic hamburger drawers. Use visible information hierarchy, contextual actions, live state, accessible input and spatial navigation where feasible. Historical fidelity must not override usability.

## Minimum terminal contract (ZTS-CORE)
1. **Identity and capabilities:** Report terminal ID, software/protocol version, device class, location scope, available input/output methods and supported operations.
2. **Scoped authentication:** Support an appropriate identity/session mechanism when privileged or personal actions are available; allow safe guest controls when appropriate. Never trust client-provided role labels.
3. **Discoverability:** Clearly display available actions and current context; unavailable actions must be understandable.
4. **Commands and receipts:** Submit idempotent versioned commands with authorization checks and explicit accepted/rejected/completed states. Never display optimistic completion as verified completion.
5. **Accessibility:** Support available keyboard/touch/trackpad input, focus, legibility, contrast, and reduced motion; account for device constraints.
6. **Privacy and recovery:** Clear personal state on shared terminals, expire sessions, offer meaningful offline/degraded behavior, log consequential actions, and preserve independent safety controls.

Optional capability extensions: `lighting.scene`, `lighting.level`, `pbx.directory`, `pbx.message`, `clanker.dispatch`, `hospitality.reservation`, `engineering.telemetry`, `simulation.clock`, `simulation.replay`. Advertise extensions rather than infer from OS or class. Contract version negotiation is required.

## Example terminal profiles
- **Shared wall panel:** Sign in (or guest mode for ordinary permitted controls), identify room, choose lighting scene/brightness, receive outcome, sign out/auto-expire. Emergency egress and essential safety functions must work independently of credentials, app, or network. Never display another user's preferences without authorization.
- **BlackBerry Bold (legacy Java):** Keyboard/optical-trackpad-first directory, messaging and read-only synthetic status. Investigate OS 6/7 Java SDK, COD/JAD packaging, simulators and obsolete TLS constraints. No capability claim until tested.
- **BlackBerry Priv (Android):** Touch-first Metro tiles with optional physical-keyboard communication mode. Investigate reliable keyboard-open detection; offer manual mode switching if unavailable. Legacy Android support requires isolated protocol gateway.
- **Lumia 640 XL (Windows 10 Mobile):** Native UWP/APPX feasibility, ARM package, emulator and device test matrix. Verify actual installed OS build before selecting SDK/minimum target.
- **Ubuntu Touch:** Research native Qt/QML Metro-style client, Click packaging, OpenStore distribution and supported device versions.
- **Modern Android/PWA, Engineering and Mission Control:** Richer role-scoped workspaces on shared backend; no requirement to replicate every feature on smaller devices.

## Distribution and verification
A unified GitHub Releases download center may use playful historical badges such as 'Windows Phone' or 'BlackBerry World' **only with unambiguous labels that the historical stores are defunct**; links must point to actual hosted binaries/docs, not pretend store availability. Publish per-platform status: proposed, buildable, emulator-tested, hardware-tested. Track version, target architecture, minimum OS, install procedure, signing dependencies, known limitations, checksum and reproducible CI/manual build provenance. No untested compatibility claims.

## Owner sovereignty, delegation and non-aggression
**Design intent:** Maximize owner's authority over owner-controlled software, synthetic worlds and infrastructure while respecting others' autonomy, consent, property, privacy and safety. The non-aggression principle is a proposed normative policy, not a complete legal decision procedure. Shared ownership, employment relationships, emergencies, conflicting claims, and applicable law require explicit governance rules.

- **Owner master mode:** Full inspection, modification, simulation reset/replay, and configuration of owned resources, subject to independently enforced safety boundaries and rights of others.
- **Delegation:** Explicit scoped permissions, expiry and revocation, with least authority needed for the purpose. A physical terminal's location alone does not establish permission.
- **Protected boundaries:** Master credentials do not authorize covert surveillance, disclosure of private messages, coercive interference with individuals, or bypass of physical safety interlocks.
- **Emergency intervention:** Narrow, logged, time-limited, proportionate actions with documented reason and review; no blanket unlimited emergency mode.
- **Shared control:** Equal owners' domains and shared assets require clear policy and dispute resolution; owner sovereignty is not unilateral control over another proprietor's rights.
- **Audit and appeals:** Consequential actions record actor, resource, policy decision, reason, event ID and result; provide independent review of disputed decisions. Avoid collecting unnecessary personal information.

## Security architecture notes
Keep the existing unauthenticated loopback-only simulator API on loopback. Do not expose it to the LAN or old devices. Introduce a separate authenticated, rate-limited, versioned gateway with per-capability authorization, command receipts, secure transport and revocation. Devices unable to satisfy contemporary security requirements may be restricted to isolated synthetic/offline modes. Treat physical controls as safety-critical and subject to independent validated controllers. This document does not certify the NAP, authentication or any device.

## Proposed acceptance tests
1. Guest wall panel can adjust only explicitly permitted local lighting; signed-in user sees only own saved preferences.
2. Session timeout clears user information; network outage cannot disable independent emergency lighting/egress.
3. Unsupported capabilities are omitted or clearly disabled; no false command-success status.
4. Owner can pause/reset/replay synthetic simulation; cannot use master override to read another user's protected messages.
5. Revoked delegation blocks further actions and is logged.
6. Keyboard-only and optical-trackpad navigation, reduced-motion behavior and screen-reader access are verified on actual supported platforms.
7. Legacy devices cannot directly reach an unauthenticated operations API.
8. Each release badge links to a verified artifact or explicitly labeled research documentation.

## Open decisions
- Ownership and dispute rules for jointly owned property.
- Consent and revocation semantics for personal preferences.
- Which wall controls remain available to anonymous guests.
- What PBX and dispatch actions legacy terminals may request.
- Terminal discovery and pairing mechanism.
- Exact SDK/device availability and compatibility verification.

## Next stages (separate draft PRs, no merges without explicit authorization)
A. Protocol schemas and terminal conformance fixtures.
B. Wall panel Metro prototype with scoped authentication and lighting simulation.
C. BlackBerry Priv Android compatibility client and keyboard tests.
D. BlackBerry Bold / Ubuntu Touch / Lumia feasibility spikes with documented emulator and hardware results.
E. Authorization policy engine, audit trail and threat model.
