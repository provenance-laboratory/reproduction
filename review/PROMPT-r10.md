# Internal review — Paper B, round 10

You are reviewing a pre-registered experiment on the cost of bit-identical model reproduction,
together with the authority layer that is supposed to make its commitments binding. Attached:

- `PAPER-B-REVIEW-PACKET.md` — the covering note and the command block
- `paper-b-review.zip` — the tree; extract it and run `test_controls.py` and `check_commitments.py`

Nine previous rounds are recorded in `REVIEW-ROUNDS.json`. Please read round 8 and round 9 first.
Round 8 contains a claim that round 9 had to retract — "the tree goes green the moment it
anchors" — which was false, and the retraction is kept in place rather than edited away.

## The state you will find, stated plainly

`test_controls.py` reports **31 attacks refused, 0 passed that should not have**, and then
reports separately that **the positive control is FAILING**. That is the honest state of the tree,
and the reason it fails changed on 2 September in a way worth understanding before you start.

v9 is now **signed** (good signature, required key) and **anchored** — its OpenTimestamps proof
carries Bitcoin attestations in blocks 965140, 965142 and 965152, and all three merkle roots were
checked against the live chain via an independent explorer and match. So the earlier reason for
the red tree — an unsigned, unanchored pre-registration — is gone.

**What is red now is the circularity, and it is the interesting part.** v9's own table pins
`ANCHORS.json`. `ANCHORS.json` is what makes an attestation mean anything: without a block's real
merkle root pinned there, a proof naming that block is STRUCTURAL only, which is exactly what two
round-6 reviewers exploited by minting a valid-looking attestation naming block 999999. But
anchoring v9 produces three new blocks that must be pinned into `ANCHORS.json` — which changes the
digest v9 pins. **The act of satisfying the protocol invalidates the document that demanded it.**

Round 7 already closed the obvious escape: v9 was drafted to RETIRE `ANCHORS.json`, and a reviewer
showed that converts a line carrying no information into no line at all, leaving the file that
decides what ANCHORED means as the only unchecked input — and a second reviewer chained it, editing
the local file to bless a version that then retires the file that blessed it. So retirement is not
available. The adjudicated design is v10's "report the datum", and it is deliberately **not
implemented**, so you are looking at the trap in its live form rather than at a description of it.

**We did not improvise around this.** Running `pin_anchors.py` would have made the tree green and
would have been the wrong thing: it edits a file the governing document pins, which is precisely
the move the protocol exists to forbid. The blocks were verified read-only instead, and nothing
was written.

**The most useful thing you can do is attack the separation of the two claims** — the security claim carried by the negative cases, and the liveness claim carried by the positive one. It was introduced to fix a
counter conflation flagged at rounds 6, 7 and 8 and dismissed as cosmetic each time. It stopped
being cosmetic when two correct repairs met and the build began refusing an honest tree while
citing an attack that had not happened.

- Can you make the suite report "0 PASSED THAT SHOULD NOT HAVE" while an attack has in fact
  passed — by making the positive control fail in a way that masks it?
- `build_package.py` now reads the distinguishing line out of the suite's output rather than the
  exit code. Reading a decision out of text is a proxy. Can you forge that line, or suppress it,
  or make the real one appear when it should not?
- Is separating the two claims the right repair at all, or does it give a red tree a way to look
  routine?

## The rest of the surface

**The liveness trap.** A commitment table binds only once anchored, so the interval between
stamping and anchoring is a window in which the tree is red for a reason no control can
distinguish from tampering. `check_commitments.py` diagnoses that state by name. Is naming it
enough, or is a window where tampering and honesty are indistinguishable a design fault that
should be closed rather than reported?

**The undefined-name control.** Round 9 added a `symtable` check for names a function reads from
module scope that module scope never defines — four such names had shipped, each on an error
path, each of which would raise `NameError` instead of reporting what it exists to report. Its
positive control was run by deleting a definition. Please try to defeat it: a name bound
conditionally, bound by a wildcard import, bound in a nested scope, bound by `globals()`.

**Two items are deliberately deferred to v10 and are not defects to re-report**, though argument
against the decisions is welcome: the "report the datum" semantics, and the verdict split in
section 5 between MATCHED-SHAPE and DIFFERING-SHAPE. Both are adjudicated and unimplemented.

**Where we think it is weakest.** Neither reviewer has broken the authority layer for two rounds.
That is either evidence it is sound or evidence the attacks have converged on a shape it already
anticipates. We would rather have a new class of attack that fails than another instance of one
that already fails. In particular: everything here assumes the anchor is the thing that confers
authority. If you can find a way for a table to govern that does not pass through an anchor, or
an anchor that governs a table it does not cover, that is worth more than anything on the list
above.

Please be blunt, and please prefer running to reading.
