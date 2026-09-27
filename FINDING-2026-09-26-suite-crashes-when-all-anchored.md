# Finding, 26 September 2026 — the control suite cannot run once every version is anchored

⛔ **`test_controls.py` crashes when there is no unanchored draft.** That is the steady state of a
healthy tree, so the suite cannot measure the tree in the one condition the protocol is trying to
reach.

v22 anchored in Bitcoin block **968668** at 09:50:38 UTC. `check_commitments.py` then returns
**rc=0** — *authority `PRE-REGISTRATION-v22-CONFIRMATORY.md` (v22), composed over 19 anchored
version(s): 30 path(s)*. Running `test_controls.py` against that tree raises:

```
File "test_controls.py", line 700, in p_duplicate_pin
  gov, txt, m = _declaration_target(root)
File "test_controls.py", line 843, in _declaration_target
AssertionError: no version whose declarations are checked carries a pin row
(candidates: none). Either every version is anchored, or the draft has no
commitment table -- and this attack tests nothing either way.
```

`p_duplicate_pin` needs a version that is *checked but not yet anchored* to plant a duplicate pin
row in. With v22 anchored there is no such document and the candidate list is empty.

**The function already states the right rule and then breaks it.** Its own comment reads: *"A
VERSION WHOSE DECLARATIONS ARE CHECKED BUT WHICH CARRIES NO PIN TABLE IS SKIPPED, NOT ASSERTED ON.
The first cut raised on the lowest candidate, and a tree where an early version momentarily looked
unanchored crashed the whole suite from the third attack onward — round 9's exact failure, where
one crash took five controls with it."* The empty-candidate branch is the one case that still
raises, and it reproduces round 9's failure exactly: the run aborts, the ~30 controls after
`p_duplicate_pin` never execute, and the positive control is never reached. `_Unmeasurable` already
exists for precisely this — *"a control that cannot be set up on this machine. Reported, never
scored either way"* — and `p_wrong_key_signature` uses it.

## A correction to my own first draft of this finding

⚠️ **I first wrote that the crash leaves a stale verdict a caller would consume. That is wrong,
and the error was mine.** The intended caller is defended, and was defended before I looked:

```
build_package.py:564   if _stale_verdict.exists(): _stale_verdict.unlink()
build_package.py:569   env=dict(..., CONTROL_SUITE_NONCE=_NONCE)
build_package.py:580+  reads the verdict BEFORE the branch, on every path;
                       rejects on nonce mismatch, then on tree_digest mismatch
```

That is round 11's repair, and a later round already found and fixed the follow-on bug that the
checks sat inside `if returncode != 0`. A crash now yields **no** verdict file for that gate, and
"a run that leaves no verdict cannot justify a pass" is enforced. I read `CONTROL-SUITE-VERDICT.json`
by hand after a direct run and treated what I saw as this tree's result; the file's `nonce` was
`""` precisely because no gate had issued one, which is the mechanism telling me the verdict was
not mine to read.

**The residual is narrow and real.** `OPERATOR-ACTIONS.md` §1 tells the operator to run
`python test_controls.py` directly, and on that path nothing unlinks the old verdict first. A human
who runs it, sees a crash, and opens the JSON gets the previous run's answer with no timestamp and
no indication of which tree it describes. The fix is one line at the top of `main()` — remove the
verdict before the run, so absence means "no verdict" on the hand path too, exactly as it already
does on the packaged path. It is belt-and-braces, not a hole.

## What is true of the tree right now

Established directly, not through the suite:

```
check_commitments.py   rc=0, authority v22, 19 anchored versions, 30 paths, no mismatch
anchor                 block 968668, merkle 62e24a1b11ad70b4aedc31f2eca6d15eec594db333f747ed994b2faa008f8688
                       matched against an independent block explorer, not only against our proof
pin_anchors.py --add   968668 fetched, "matches our proof"; ANCHORS.json now 44 blocks
```

## Repairs, for v23

1. `_declaration_target` raises `_Unmeasurable` instead of `AssertionError` on an empty candidate
   list, so the case reports itself and the run continues.
2. `main()` removes `CONTROL-SUITE-VERDICT.json` before the run.
3. `FINDING-2026-09-26-wrong-key-control-unmeasured.md` — the `--yes` defect, still open.

⚠️ None is fixed here. `test_controls.py` is pinned by v22 at `8249b95f69849159`, and v22 is now
**the authority**, so editing it in place breaks the pin of the document in force. v23 re-pins it
at the repaired bytes and names all three.
