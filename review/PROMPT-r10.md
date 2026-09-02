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
reports separately that **the positive control is FAILING**. That is the honest state of the
tree, not an oversight. The v9 pre-registration is stamped and timestamped but **not yet
signed**, and a table governs only once anchored, so the real tree does not currently satisfy
`check_commitments.py`. Round 9 separated these two claims precisely so that this state is
legible: the negative cases carry the security claim, the positive case carries a liveness
claim, and a liveness failure is no longer summed into a sentence asserting that a control
accepted an input it must refuse.

**The most useful thing you can do is attack that separation.** It was introduced to fix a
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
