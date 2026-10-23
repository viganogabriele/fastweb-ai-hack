# Recorded source-backed Core candidate

This nested directory contains real response envelopes on synthetic dev sources,
the exact RunSpec, source/config inventory, a scripted synthetic local decision,
one positive POST-investigate job recording (`investigate-job/`) and verification
evidence. It is not DTO fixture input and is not loaded by `fixtures load`.

Rebuild sources from empty projections, and replay the investigate job, with
networking denied, using the commands in
[`scripts/core_demo.md`](../../../../scripts/core_demo.md). No credentials or mock
server are needed for replay. Check `asset-manifest.json` for byte hashes.

Keep the disclosed `degraded` outcomes, both tool-budget fallbacks and the
unapplied NYC01 correction visible. This package does not certify a release freeze,
hold-out performance, a genuine operator decision or real human/stock dispatch.
