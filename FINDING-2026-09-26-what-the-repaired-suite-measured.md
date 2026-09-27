# Finding, 26 September 2026 — what the repaired suite measured, and the one control it cannot

v23 is in force. `check_commitments.py` returns **rc=0** — *authority
`PRE-REGISTRATION-v23-CONFIRMATORY.md` (v23), composed over 20 anchored version(s): 30 path(s)*,
anchored in Bitcoin block **968689** (merkle `a78a9847…`, matched against an independent explorer).
The baseline passes, so the control suite is measurable for the first time since v22 anchored.

```
attacks_refused                     68
positive_control_failed          False        <- liveness_ok TRUE, the first time
attacks_passed_that_should_not_have  1
hygiene_failed                    True
security_ok                      False
```

## What the §2t repair bought

**The wrong-key control runs, and it holds.**

```
ok  verify() names the wrong key, not merely a bad one
    BAD: WRONG KEY: a valid signature by 8C0C0F471ABC9227
```

That case had been reporting `unmeasured`. It now exercises the bypass v22 §2g was written to
repair, and the repair refuses it. The subkey control signs the same way and is measurable on the
same change. The refused count moving 74 → 68 is these two arriving while eight others leave, for
the reason below.

## What §2s repaired, and the ninth case it did not reach

Eight `_declaration_target` cases report `unmeasured` instead of ending the run — the §2s repair
doing its job. They are unmeasurable for a stated reason: **they need a version that is checked but
not yet anchored, and in a healthy tree there is none.**

⛔ **A ninth control has the same dependency and does not detect it.** `p_forged_restatement`
mutates `_newest(root)`:

```
  ⛔ WRONG  a restatement row forged to a tampered train.py   (wanted 'do not restate')
      got:  ⛔ 2 file(s) no longer match the pin the highest version in force gives them.
```

When the newest document was an unsigned draft, editing it was legitimate and `prepare_anchor.py`
reached the restatement rule — the round-16 repair — and said *"do not restate"*. Now the newest
document is signed and anchored, so the same mutation is an edit to a document in force, and the
general pin-mismatch rule fires first.

⚠️ **The tree refused: `rc != 0`, no bypass.** The security property held. What did not hold is the
coverage: the restatement defence v22 §2r installed was not the thing exercised, and the control
reports WRONG rather than reporting that it could not be set up. It is the §2s shape one control
over — a case whose precondition has quietly stopped being true.

⚠️ **And three sibling controls share the precondition without being examined here.** Four attacks
call `_newest(root)`; three of them are counted `refused` in this run. Whether each was refused by
the rule it targets, or by the same general rule that caught this one, is not established by a
`refused` line. A pass for the wrong reason reads exactly like a pass.

## What is and is not claimed

- **Established:** the tree is green; liveness is true; the wrong-key control runs and refuses; no
  attack in this run got through.
- **Not established:** that `security_ok: false` reflects a defence that is missing. It reflects
  one control reporting WRONG and eight reporting unmeasured, and on this evidence both are
  precondition problems rather than holes.
- **Open:** which rule actually refused each of the three sibling `_newest` controls.

## Repairs, for v24

1. `p_forged_restatement`, and any attack mutating `_newest(root)`, checks whether that document is
   signed or anchored and raises `_Unmeasurable` when it is — the treatment `_declaration_target`
   now gets.
2. `pin_anchors.py` takes the anchored-version exemption `check_commitments.py:961` already has, per
   `FINDING-2026-09-26-orphan-pins-half-repaired.md`.
3. Worth considering with them: a control whose precondition is an unsigned draft can only run
   while one exists. Either the suite synthesises one, or the steady state leaves nine cases
   unmeasurable and says so in the verdict rather than in prose.

⚠️ Not fixed here. `test_controls.py` is pinned by v23, which went in force today.
