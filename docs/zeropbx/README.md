# ZeroPBX and ZeroVoice v0.1

ZeroPBX is a proposed SIP-compatible estate PBX supporting extensions, presence, transfers, conferencing, priority queues and authenticated household calls. ZeroVoice provides opt-in voice intent routing.

## Pennington Direct
A headset press may invoke an Android companion through supported call/assistant controls, connecting to Pennington via authenticated ZeroPBX routing. Bluetooth headset button interception is vendor- and OS-dependent; arbitrary remapping must not be assumed.

## Security
End-to-end identity binding, scoped permissions, encrypted media where supported, private-zone microphone kill switches, opt-in room microphones, short retention, and no hidden ambient surveillance. Calls are not automatically available for model training.

## Routing
Pennington can coordinate through ZeroDispatch, transfer to qualified staff, and preserve a request ID across transfers. Network loss should produce a clear failure or local fallback, not a fabricated connection.
