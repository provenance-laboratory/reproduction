# Finding, 26 September 2026 — the 5 September orphan-pin contradiction is repaired in one tool and not the other

⛔ **`pin_anchors.py --verify` returns rc=1 on a tree whose authority check is clean.** The two
tools implement the same rule with two different definitions, and the narrower one refuses the two
heights an anchored §2d requires to be present.

```
pin_anchors.py --verify    42 of 42 blocks our proofs name: re-fetched, matched
                           ⛔ 2 block(s) are pinned that NO PROOF NAMES: ['964878', '964881']
                           ⛔ 2 block(s) failed        rc=1
check_commitments.py       authority v22, 19 anchored versions, 30 paths, no block complaint
```

`FINDING-2026-09-05.md` recorded this three weeks ago, on exactly these two heights, and set out why
no edit to `ANCHORS.json` resolves it: §2d of an anchored version says *"every line must remain
present and unchanged"*, while the gate demanded the pinned set EQUAL the named set. **Removing the
lines violates a monotonic rule in an anchored document; keeping them failed the gate.**

## What changed since, and what did not

`check_commitments.py` was widened. Its message now reads:

```
check_commitments.py:961   "%d block(s) are pinned that NO PROOF NAMES and NO ANCHORED VERSION ..."
```

That is the resolution: a height no current proof names is legitimate when an anchored version's
§2d carries it. It is why the authority check passes today.

`pin_anchors.py` was not. It still computes the subtraction with no exemption:

```
pin_anchors.py:315-320     _recorded = set(old) if verify else set()
                           _extra = sorted(_recorded - {str(h) for h in want})
```

`want` is the set of heights the proofs name. Nothing consults the anchored versions, so the 43
heights `--add` deliberately keeps — *"43 height(s) kept that no current proof names, as section 2d
requires"* — are the same population `--verify` then counts against the tree. **The same file, in
the same run, keeps a height under one rule and fails it under another.**

⚠️ The two heights are not suspect. Both appear in v11 §2d and in every §2d since, and both were
verified against their own block headers when they were pinned. What is wrong is the second
definition of the rule, not the data.

## Why this matters more than an exit code

`OPERATOR-ACTIONS.md` §3 tells the operator to run `pin_anchors.py --check` after every anchor
round. That instruction currently produces a red result on a healthy tree. A gate that is red for a
reason the operator learns to wave past stops being a gate — and the comment beside this very code
says why the equality test was added: *"a round-7 reviewer added a fabricated block with a chosen
root and `--verify` exited 0 … unprotected against EXTENSION, which is the direction an attack
uses."* That protection is worth keeping. It needs the same exemption its sibling already has.

## A correction to my own first report

⚠️ I first reported **3** blocks failed. That count came from a run whose output was truncated when
the job was moved to the background, and one of its three was a transient header fetch. A clean run
reports **42 of 42 blocks verified and 2 failures**, both of them the orphan pins above. The number
I gave first was wrong; the diagnosis was not.

## Repair, for v24

`pin_anchors.py` takes the same exemption `check_commitments.py:961` already applies: a recorded
height is not extra when an anchored version's §2d names it. The equality test stays for everything
else, because extension is the direction an attack uses.

⚠️ Not fixed here. `pin_anchors.py` is pinned by v22 at `ca5e9d207b77f87b` and restated by v23,
which is signed and stamped and waiting on a block. Editing it now would break the pin of a document
mid-flight, exactly as editing `test_controls.py` did. **v24**, after v23 is in force.
