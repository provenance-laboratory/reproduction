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

---

# Second amendment, same day — the corpus changed after training

§6's first invalidating condition is *"changing the model or corpus after training has begun,
without recording the change and its date here."* This is that record.

## What changed and why

An internal reviewer found that `pg2701.txt` still contained the string *"Project Gutenberg's
archives"*, inside a transcriber's note within the extracted text. Project Gutenberg's terms make
removal of the licence **and of all references** the condition for using the underlying work
freely, so the corpus did not have the property the manifest claimed for it, and `build_corpus.py`
asserted in its own docstring that removing the boilerplate was sufficient. It is not.

**Change:** a cleaning step that drops any paragraph mentioning Project Gutenberg, records each
removal per text in the manifest, and refuses to build if a reference survives. One paragraph, 350
bytes, from one text.

```
before   merkle 814acd249a2988da…   6,313,332 bytes   30 Aug 2026, superseded
after    merkle 2006b7327c616f0c…   6,312,982 bytes   30 Aug 2026
```

## ⚠️ What it costs, stated rather than absorbed

**Every measurement taken before this change is void**, and all of them were retaken. Both
reviewers' runs were against the superseded corpus, so their digests describe an artifact that no
longer exists — their protocol findings stand, their digest observations are historical, and the
paper will say so wherever it cites them.

The superseded proof is kept as `MANIFEST.json.ots.superseded-814acd24` rather than deleted. It
attests exactly what it always attested: that corpus `814acd24…` existed before its anchor. That
remains true and is now simply a fact about a corpus we no longer use.

⛔ **A new proof was created and the new corpus was committed BEFORE any retraining**, which is the
order §2 requires. The order was preserved for the new corpus; it is the *identity* of the corpus
that changed, and that is what this amendment records.

## ⚠️ Why this is recorded as a deviation rather than as a fix

It would be easy to present this as routine maintenance completed before publication, and the
timeline permits that framing: nothing had been published, and the window had not opened. But §6
does not ask whether a change was published — it asks whether the corpus changed **after training
began**, and it did. Deciding for ourselves that a rule aimed at us does not apply because the
change was caught in time is precisely the latitude a pre-registration exists to remove.

