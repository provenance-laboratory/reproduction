# ⛔ THIS PACKAGE IS MID-REBUILD AND MUST NOT BE USED

`SHA256SUMS` is absent, so nothing here can be checked — and the first step of
`REPRODUCTION-CALL.md` is `sha256sum -c SHA256SUMS`. A package you cannot verify is not a package.

**Why it is in this state.** Two defects were found on 6 September 2026 by running the published
procedure as a stranger would:

1. the shipped package had gone **stale** — 7 files no longer matched their recorded digests;
2. three signed protocol documents in it **quoted the reference weights digest**, so a reproducer
   opening the package held the answer they were meant to arrive at.

`build_package.py` was changed to withhold any protocol document containing the target. That file
is committed by digest in the pre-registration, so the change required a new protocol version —
**v14** — and the build correctly refuses to run until v14 carries a Bitcoin attestation.

⇒ **Nothing is wrong with the experiment.** `train.py` was run from this package on a clean copy
and reproduced the reference weights digest exactly. What failed was the packaging around it.

**This file disappears when the package is rebuilt.** If you are reading it, the rebuild has not
happened yet and no reproduction should be attempted from these bytes.
