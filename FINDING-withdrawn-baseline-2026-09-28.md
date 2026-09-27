# Open finding, 28 September 2026: a control baseline that passes alone and fails inside the suite

**Status: OPEN. Not a red tree, not an attack passing.** `test_controls.py` reports
`security_ok: true`, `liveness_ok: true`, `attacks_refused: 68`,
`attacks_passed_that_should_not_have: 0`, and the positive control passes. What is red is
`hygiene_failed: true`, which the suite defines as *a control that would crash instead of
speaking*.

## What the suite says

```
  withdrawn_claims.py -- the generator, and the record of the readings
    ⛔ BASELINE the unmutated record verifies and the file describes this folder
      ⛔ the baseline does not pass, so nothing below is measured:
      ⛔ WITHDRAWN-CLAIMS.md does not describe this folder. Regenerate it.
```

`WITHDRAWN-CLAIMS.md` was regenerated on 28 September, and the message did not change.

## What was established

The baseline is `run(HERE, "withdrawn_claims.py", "--check")` — the real folder, not a sandbox,
which the code comments say is deliberate: the generated file states how many text files were
**scanned**, and the sandbox copies a deliberate subset, so a sandbox is a folder the shipped
document correctly does not describe.

Run by hand with the suite's exact invocation — same interpreter, same `-X utf8`, same working
directory, stdout and stderr combined as the suite combines them — it **passes**:

```
rc = 0
phrase present: True
  ok   WITHDRAWN-CLAIMS.md describes this folder
```

`python withdrawn_claims.py --check` also passes immediately **before** and immediately **after** a
full suite run, and `WITHDRAWN-CLAIMS.md` is unchanged in size and mtime across that run. So the
folder is not left mutated, and the record is not stale in the state a reader would find it in.

## What was not established

**Why the same call gives a different answer inside the suite.** Reproduced three times, so it is
not intermittent. Ruled out: a stale record (regenerated), a mutated folder (byte-identical before
and after), and a sandbox path (`HERE` is `__file__.resolve().parent`).

⛔ **The obvious next step is blocked by the protocol, and that is worth saying plainly.**
Instrumenting either side means editing `withdrawn_claims.py` or `test_controls.py`, and **both are
pinned by v24**. Editing a pinned file to diagnose it turns the tree red and would need a v25 to
re-pin — the exact sequencing error v24 §1 records. A diagnosis that breaks the thing it is
diagnosing is not available here.

## What this does and does not affect

- It does **not** affect the authority chain. v24 is anchored in Bitcoin block 968848, is selected
  as authority over 21 anchored versions, and all 30 committed files hash to the digests it pins.
- It does **not** mean the withdrawal record is wrong. `--check` passes standalone.
- It **does** mean the four attacks under that baseline print `refused` while the suite also says
  nothing below the baseline is measured. **Those two statements cannot both be load-bearing**, and
  until this is settled the four refusals should be read as unconfirmed rather than as evidence.

## The route that does not break a pin

Diagnose from outside: run the suite under a filesystem watcher sampling the folder's entries, and
compare what exists at the moment the baseline runs against what exists before and after. That
needs no edit to either pinned file. It was attempted on 28 September and the probe's own shell
quoting defeated it; the approach stands.
