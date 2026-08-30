# Amendment, 30 August 2026 — a deviation from §2b, recorded on the day it happened

*Section 6 says a change made after training begins must be recorded here **with its date**. This
is that record. It is written before any paper text exists, so that it is a disclosure rather than
a defence.*

---

## The deviation

§2b says:

> the second party must be secured **before** training starts, not recruited afterwards to bless a
> result.

**Phase-2 training ran on 30 August 2026 and no second party had been secured.** The order the
pre-registration specified was not followed.

## Why it matters, stated at full strength before any mitigation

The rule exists because a reproducer recruited *after* a result is known can be chosen — knowingly
or not — for the likelihood of confirming it. **The protection the rule offers is against the
authors' own selection, and we have given that protection up.** Nothing below restores it; the
mitigations below are weaker instruments than the rule was.

## What does still hold

```
THE ARTIFACT IS FROZEN FIRST     the corpus manifest and its Merkle root were committed and
                                 OpenTimestamped BEFORE the first training step, and that proof
                                 is now ANCHORED in a Bitcoin block. Whoever reproduces it cannot
                                 be handed a different corpus than the one committed on 29 Aug

THE TARGET IS PUBLISHED FIRST    EXPECTED.json fixes the digest to be matched. It goes out with
                                 the package, before any report arrives, so the bar cannot move
                                 to meet a result

THE CALL IS OPEN                 §2b's other half is intact: the request is public, anyone may
                                 file against it, and nobody is approached in a way not equally
                                 available to everyone

EVERY REPORT IS REPORTED         including failures, divergences, and reports we dislike. A
                                 reproducer chosen badly can still file a result we did not want
```

⚠️ **What none of that fixes:** a party approached by us, after the fact, is a party we chose. A
reader should weigh the reproduction accordingly, and **the paper will state this deviation in the
same place it states the reproduction**, not in an appendix.

## The §6 constraint that is unaffected and binding

> reporting bit-identity without an independent party's re-run *invalidates the pre-registration*

⛔ **So measurement 3 is not yet a finding of this paper.** `PHASE-2-FINDINGS.md` records that
bit-identity held across three of our own pinned runs; that is an internal phase record. **The
paper may not report bit-identity as established until an independent re-run exists**, and if none
arrives, §2c's null outcome is what gets reported instead. That constraint is unchanged by this
amendment and is not negotiable by us afterwards.

## ⚠️ And one thing that is *not* a mitigation

**A run by anyone connected to this project is not the independent re-run** — it is measurement 4.
Running the package on a second machine of our own is a legitimate and wanted measurement of
cross-hardware bit-identity, and it satisfies §3 measurement 4. It satisfies nothing in §2b, and
presenting it as though it did would be the substitution this project spends its time detecting in
other people's work.

---

*Recorded 30 August 2026, before the reproduction window opened and before any paper text was
written. Related: [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) §2b, §2c, §6.*
