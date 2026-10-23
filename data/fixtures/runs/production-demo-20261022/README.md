# Recorded production demo

Source-backed synthetic run for the redesign UI. Start it with `make demo`.
See [the runbook](../../../../docs/production-demo.md) for inputs, click path,
data-quality details and recording commands.

`mode=recorded`, product namespace, no authorized fixture projections. The
`profile.yaml` file declares the selected dev sources, two supplemental emails
and one planned logistics calendar. Preparation rebuilds the hashed input tree
from existing sources plus those declared inputs.

The package contains actual Fastweb and systems response envelopes, the frozen
RunSpec and verification evidence. It contains no database or credentials.
The original Core bundle remains separate in `../core-dev-20261023/`.
