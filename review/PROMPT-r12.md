# Internal review — Paper B, round 12

You are reviewing a pre-registered experiment on the cost of bit-identical model reproduction,
together with the authority layer that decides which protocol version governs it. Attached:

- `PAPER-B-REVIEW-PACKET.md` — the covering note and the command block
- `paper-b-review.zip` — the tree; extract it and run things

Rounds 1 to 11 are in `REVIEW-ROUNDS.json`. Please read rounds 10 and 11 first.

## The state you will find, stated exactly

`test_controls.py` reports **31 attacks refused, 0 passed that should not have**, hygiene clean,
and the **positive control FAILING**. That last is honest and it is the whole open question.

**A correction to what the last packet told you.** It said "v9 IS NOW SIGNED AND ANCHORED". Both
round-11 reviewers said that is too strong and both were right. v9 **is signed**, and its
OpenTimestamps proof carries Bitcoin attestations in blocks 965140, 965142 and 965152 whose merkle
roots were checked against the live chain. But **the artifact's own offline verifier reports
STRUCTURAL only**, because those blocks are not pinned in `ANCHORS.json`. A claim true of the world
and false of the shipped verifier has to be stated as the second one. That wording is retracted in
round 11's record rather than edited out of round 10's.

## What the circularity actually is, now that a reviewer sharpened it

`ots_verify` returns STRUCTURAL for v9's honest not-yet-pinned blocks and for round 6's
**fabricated block 999999** — *identically*. The tool cannot tell them apart. So calling this
state "the circularity" is a human asserting that this instance of that verdict is the benign one,
which is exactly the judgement the mechanism was supposed to make. **That is why naming it is not
sufficient and it is a fault to close.** The adjudicated v10 design — report height and computed
root as data, let a live re-fetch settle authority — closes it for the right reason. If you attack
one thing, attack that design before it is built.

## What changed this round

- **The undefined-name control was defeated by four lines and is now ported, not reimplemented.**
  `if False: X = ...` binds for symtable and not at runtime. The corrected three-shape version had
  existed in the sibling project for a day and was never carried across — two copies of one rule,
  which is how the evasion survived. It now catches undefined, shadowed-by-a-later-local, and
  conditional-only bindings. `globals()["x"] = ...` remains undecidable and is disclosed.
- **A relabelled document carrying a commitment table is FATAL, not reported.** Round 10 stopped
  it governing; a reviewer showed the checker printed `NOT AUTHORITY [RELABELLED]` and exited 0.
- **That fix immediately found a defect round 10 introduced.** `declared_version` knew one title
  form; v2 and v3 use another, so both had silently stopped contributing to the composed table
  since round 10. Making the refusal fatal is what surfaced it.
- **The verdict is bound to its run.** The gate issues a nonce, deletes any existing verdict first,
  and refuses one that does not carry this run's nonce. A reviewer had pre-written a green verdict,
  crashed the suite before its own write, and the gate consumed the stale file.

## What would help most

**Attack the freshness binding.** It is one round old and this project's record on one-round-old
controls is poor. Can you make the gate accept a verdict the suite did not write — a race, a
symlink, a suite that writes the nonce before doing the work?

**Attack the fatal-rejection scope.** It fires only on candidates carrying a commitment table.
Is there a document that should be refused and carries no table, or one that carries a table the
parser does not recognise as one?

**The publishing surface has never run.** `publication_preconditions()` calls `governing()`, which
raises on the circularity, so the report_to checks, the window-close date check and all five §2c
rule cases are downstream of an unresolved state and have only ever passed fixtures. A reviewer
identified this and it is worth confirming independently — it means the publishing path is the
least-tested code in the artifact.

**Two items we owe and have not done**: v9 does not pin the current gate bytes, so a new anchored
version is required rather than waiting; and the counterfactual figures in the sibling paper are
subtractions across two runs.

Please be blunt, and prefer running to reading. Every round that changed something here began with
a reviewer executing a command.
