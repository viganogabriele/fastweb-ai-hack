# Recorded source-backed Core candidate

This nested directory contains real response envelopes on synthetic dev sources,
the exact RunSpec, source/config inventory, frozen local decision and verification
evidence. It is not DTO fixture input and is not loaded by `fixtures load`.

Rebuild sources from empty projections with networking denied using the commands
in [`scripts/core_demo.md`](../../../../scripts/core_demo.md). No credentials or
mock server are needed for replay. Check `asset-manifest.json` for byte hashes.

Keep the disclosed `degraded` outcomes, D1 budget fallback and conservative
correction limitations visible. This package does not certify a release freeze,
hold-out performance or real human/stock dispatch.
