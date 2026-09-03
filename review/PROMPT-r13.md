# Internal review — Paper B, round 13

A pre-registered experiment on the cost of bit-identical model reproduction, and the authority
layer that decides which protocol version governs it. Attached:

- `PAPER-B-REVIEW-PACKET.md` — the covering note and the command block
- `paper-b-review.zip` — the tree; extract it and run things

Rounds 1 to 12 are in `REVIEW-ROUNDS.json`. Please read round 12 first.

## The state you will find

`test_controls.py`: **31 attacks refused, 0 passed that should not have**, hygiene clean, and the
**positive control FAILING**. That last is honest and it is still the open question.

To be exact about v9, because a previous packet overstated it: v9 **is signed**, and its
OpenTimestamps proof carries Bitcoin attestations in blocks 965140, 965142 and 965152 whose merkle
roots match the live chain. **The artifact's own offline verifier reports STRUCTURAL only**,
because those blocks are not pinned in `ANCHORS.json`.

## What round 12 found, because it sets the standard

**Every protection built in round 11 was dead on the path a shipping build takes.** The whole
verdict-consumption block — the nonce check included — sat inside `if _tc.returncode != 0`. On the
green path the gate never opened the verdict file. The structured verdict was consulted to explain
a failure and never to justify a pass. Beside it, `tree_digest` was **written and never read**, and
even as written covered 16 files of 320 — excluding the protocol documents, the proofs, the
signatures and the corpus.

**A versioned document whose table the parser cannot read was silently skipped.** `DIGEST_LINE`
matches only `path<space>64hex`, so a markdown pipe-table parsed as zero commitments, hit a silent
`continue`, and appeared in neither `found` nor `rejected` — no output at all. Round 11's fatal
scope fires on `1 <= pinned < MIN_EXPECTED`, and zero pins escaped it, because the scope test was
the output of the parser under test.

**And the first version of that fix refused two legitimate documents** — v2 mentions one digest in
prose and pins nothing, which is the whole reason v3 exists. The v2/v3 defect repeating inside the
fix for the v2/v3 defect, caught by running it.

## What would help most

**Attack the verdict binding again.** It is now checked on every path, with the tree digest
recomputed by the gate from a function the suite exports. That is two rounds old in design and one
round old in this form. Can you make the gate accept a verdict describing different bytes — a race
between the digest computation and the package build, a file the digest walk skips, a suite that
computes the digest before doing the work?

**Attack the NO-TABLE rule.** It fires when a document carries at least `MIN_EXPECTED` 64-hex
digests and the parser reads none. Is there a real table that carries fewer, or a document that
carries many digests and legitimately pins nothing? The threshold is the project's own and it is
still a threshold.

**The publishing surface has never run.** `publication_preconditions()` is downstream of
`governing()`, which raises on the circularity, so the `report_to` check, the window-date check and
all five §2c cases have only ever passed fixtures. A round-12 reviewer established this
independently. It is the least-tested code in the artifact and it first executes in anger the
moment the circularity resolves.

**The circularity, stated as sharply as we can.** `ots_verify` returns STRUCTURAL for v9's honest
not-yet-pinned blocks and for round 6's fabricated block 999999 — *identically*. The tool cannot
tell them apart, so calling this state "the circularity" is a human asserting that this instance of
that verdict is the benign one, which is the judgement the mechanism was supposed to make. That is
why naming it is not enough. The adjudicated v10 design is: report height and computed root as
data, verdict unverified-here, and let a live re-fetch settle authority — comparing the block's
real **merkle root** to the computed root, because a height check alone is the same trap with a
network call attached. **Attack that design before it is built.**

**Two items we owe.** v9 does not pin the current gate bytes, so this resolves by anchoring a NEW
version rather than by waiting. And `reproduce_findings.py` did not complete inside a reviewer's
180-second bound while the packet claims roughly two minutes; the claim needs slack or the tool
needs progress output.

Please be blunt, and prefer running to reading. Every round that changed something here began with
a reviewer executing a command, and round 12's headline finding was a control that had never been
executed on the path that matters.
