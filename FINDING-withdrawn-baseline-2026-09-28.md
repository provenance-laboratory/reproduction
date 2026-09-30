# DIAGNOSED 30 September 2026: the suite deletes a file the record counts

**Status: CAUSE ESTABLISHED. The repair needs a new protocol version.** This document was opened on
28 September saying the cause was not understood, and that reporting the consequence honestly was
not the same as understanding it. The cause is now understood and is recorded here in place of the
speculation.

## What was observed

`test_controls.py` reported `hygiene_failed: true` on every run, from this block:

```
  withdrawn_claims.py -- the generator, and the record of the readings
    ⛔ BASELINE the unmutated record verifies and the file describes this folder
      ⛔ the baseline does not pass, so nothing below is measured:
      ⛔ WITHDRAWN-CLAIMS.md does not describe this folder. Regenerate it.
```

Run by hand with the suite's exact invocation — same interpreter, same `-X utf8`, same working
directory, streams combined the same way — `withdrawn_claims.py --check` **passed**, before the
suite and after it, with `WITHDRAWN-CLAIMS.md` unchanged in size and mtime across the run.
Regenerating the record changed nothing. Reproduced on four runs across three days, including with
the tree red and with it green, so it was not the pin state.

## The cause

**`WITHDRAWN-CLAIMS.md` records how many text files the folder holds, and
`CONTROL-SUITE-VERDICT.json` is one of them.** The suite deletes that file at the start of its own
run, so that a stale verdict can never be mistaken for a fresh one — the nonce discipline
`build_package.py` documents.

So for the duration of a run the folder holds one text file fewer than the record describes, the
check correctly reports a mismatch, and the file is back before anyone looks.

Measured rather than argued:

| state of the folder | text files scanned | `--check` |
|---|---:|---|
| `CONTROL-SUITE-VERDICT.json` present, as a person finds it | **151** | passes |
| the same file absent, as it is during a suite run | **150** | refuses |

The difference is exactly that one file.

⚠️ **Nothing was wrong with the record, the generator, or the check.** Each behaved correctly
throughout. What was wrong was an assumption nobody had written down: that the folder a record
describes holds still while the record is being checked. **The suite's own output file is inside the
subject it measures, and the suite removes it in order to measure.**

## Why it was hard to see

Every instinct was to test it by hand, and by hand it always passed — the observation and the
condition could not coexist. The earlier write-up recorded the right constraint for the wrong
reason: it said the obvious next step was blocked because the files are pinned. In fact the step
that settled it needed no edit at all, only running the check against the folder **in the state the
suite puts it in**, which is one `mv` and one command.

⇒ **A check that cannot be reproduced by hand is not thereby unreproducible.** It may be measuring a
state a person never occupies.

## The repair, and why it is not applied here

`CONTROL-SUITE-VERDICT.json` should be outside the scan. It is a run artifact, not a document that
could carry a withdrawn claim, and no reading of the withdrawal record is served by counting it.

⛔ **`withdrawn_claims.py` is pinned by v25**, so that one-line change needs a v26 — which is the
cost v25 itself reduced for findings and did not reduce for tools. The repair is queued rather than
made, and this document is the record of why the queue exists.

⚠️ **Until then the four attacks below that baseline remain `unmeasured`, and that is now known to be
a reporting artifact rather than a gap in coverage.** v25 §2z made them say `unmeasured` instead of
`refused`, which was the right change on the evidence then available and is still right: they did
test nothing. What is new is that we know why, and that the security property they guard was never
in question.
