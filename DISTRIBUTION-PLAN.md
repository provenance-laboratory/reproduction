# The distribution plan, and the exposure floor

> ## ⛔ SUPERSEDED BY PRE-REGISTRATION v18 §1. NOTHING IN THIS DOCUMENT IS IN FORCE.
>
> **No venue below must be attempted. There is no exposure floor. There is no capture cadence.
> `INSUFFICIENT EXPOSURE` is not a reportable outcome of this study.**
>
> This plan was the first of two available repairs to a real hole a reviewer of v17 found: §2c of
> `PRE-REGISTRATION.md` made silence a finding about the ecosystem, and nothing fixed how the call
> was distributed or what would count as insufficient exposure. **v18 takes the second repair —
> it withdraws the claim**, so no exposure measurement is needed, because nothing rests on one.
>
> ⇒ **This file is retained, and pinned by digest, deliberately.** It is the record that the
> alternative was examined properly before it was set aside: §2's analysis of why the floor metric
> was ill-defined — three candidate readings differing by more than an order of magnitude, two
> already disagreeing at the baseline — and the correction of a bound that had been stated in our
> own favour, are both good work and both remain true. **A project that deletes the road it did not
> take cannot show that it looked.**
>
> ⚠️ `capture_exposure.py` and `attempts.py` remain as INSTRUMENTS. If the call is distributed, it
> is recorded honestly and the record cannot later be edited. Nothing obliges it to happen.
>
> *Read everything below as the superseded proposal it is. It is not a set of commitments.*

---

**Fixed before the first announcement. Nothing here may be revised after the window opens.**

---

## ⛔ Why this document exists

A reviewer of v17 found the one place this protocol could produce a dishonest paper without anyone
lying:

> §2c makes silence a finding about the ecosystem. The instrument can only measure "no issue was
> filed." Nothing in seventeen anchored versions fixes, in advance, how the call is distributed, to
> how many people, or what would count as insufficient exposure. … §3 of the checklist forbids
> approaching any party in a way not equally available to everyone. That is a good fairness rule,
> and there is no matching rule *requiring* broad announcement. **So minimum exposure is fully
> protocol-compliant, and it produces the sharper finding.**

⇒ *"Nobody reproduced it"* and *"nobody saw it"* are different findings and only the first is about
the ecosystem. Until now nothing in the protocol separated them. **This document makes the
separation a rule instead of a judgement**, which is what the rest of the project does everywhere.

---

## 1. ✅ The baseline, captured BEFORE any announcement

`exposure/exposure-2026-09-07.json`, OpenTimestamps-stamped.

```
unique cloners (14d)   41
unique viewers (14d)    1
clone : view ratio     41.0
referrers              github.com only
issues filed           0
forks / stars          0 / 0        watchers 1 (the owner)
```

⚠️⚠️ **THE DENOMINATOR IS NOT UNIQUE CLONERS, AND THIS BASELINE IS WHY.** Forty-one unique cloners
against **one** unique human viewer, on a repository nobody has been pointed at, is not an audience
— it is crawlers, CI mirrors and scrapers. Reporting 41 as "exposure" would let the study claim a
readership it never had.

⇒ **That is the same defect the instrument exists to prevent, arriving through the flattering
number rather than the flattering narrative.** The clone series is recorded because it is evidence;
it is not the denominator.

## 2. ⛔ THE EXPOSURE FLOOR — fixed now, before anything is posted

```
FLOOR      100
METRIC     the sum of views[].uniques over every DISTINCT DATE in the capture series
MEASURED   GitHub's own traffic record, captured on the schedule in §4 and OTS-stamped
COMPUTED   by capture_exposure.py, on every run, printed whether or not it is convenient
```

## ⛔ The metric, because fixing the threshold and leaving the metric free fixes nothing

**A first version of this document said "100 unique viewers over the window" and stopped there.
That quantity does not exist.** GitHub returns a rolling 14 days of per-day uniques plus a 14-day
total; there is no figure for uniques over 90 days, and uniques do not add — the same person on two
days is two daily uniques and one person. At least three readings were available and they differ by
more than an order of magnitude:

```
the 14-day figure in the final capture   punishes success: a launch spike on day 3 has fully
                                         decayed by day 90
sum of each capture's 14-day figure      double-counts everything -- 7-day cadence into a
                                         14-day window puts every day in two captures
sum of per-day uniques, each date once   CHOSEN. Computable, unambiguous, and an upper bound
```

⇒ **The threshold was fixed blind and the metric was left free, and the metric is the larger degree
of freedom.** Whoever computed the number in December would have been choosing, with the answer
already visible, between a rule that licenses the ecosystem claim and a rule that forbids it. That
is a bound guaranteeing its own answer, inside the instrument built to prevent one.

## ⛔ The bound was pointed the wrong way, and the error was in our favour

**A first version of this section said over-counting "makes failing the floor *harder*, which is
the right direction for a threshold that licenses a claim." That is backwards.**

⇒ Over-counting inflates the exposure figure, so the floor is **easier to clear**, so the ecosystem
claim is **easier to license**. **A gate on a claim should be hard to pass.** The sentence had
travelled from a code comment into this anchored document and then into the review brief that asked
someone to check it, which is how a convenient error propagates: each copy cited the last.

⚠️ **The metric still over-counts, and that is now stated as a cost rather than sold as a virtue.**
A returning visitor is counted once per day they return, so the figure is an **upper bound on
persons, not a count of them**. It is kept because it is unambiguous and computable from the
record — the alternatives were worse in the ways §2 lists — and because the honest response to a
bound that runs the wrong way is to *declare* it, not to reword it.

⇒ **Therefore the floor is read as an upper bound too.** Clearing it does not establish that 100
people saw the call; it establishes that no more than the counted number did, and that the number
was at least the floor. A figure that only just clears 100 is **weak evidence of exposure**, and the
paper must say so rather than treating the threshold as a line that settles the question.

⚠️ **A date appearing in two captures must carry the same value in both.** GitHub's figure for a
past day does not move. Any disagreement is reported by the tool rather than averaged away: a
changing past is a fact about the source.

**If the window closes below the floor, the outcome is reported as `INSUFFICIENT EXPOSURE` and
explicitly NOT as a null about the ecosystem.** The paper may then report the reproduction result
only as a bounded observation about this artifact, with its exposure denominator attached.

### Why 100, argued rather than asserted

A number chosen after seeing the traffic is worth nothing, so here is the reasoning while it is
still costly. One hundred unique human viewers is approximately **one modestly successful post** —
a link that reached a real audience and was not merely published. It is far below a front-page
result and far above the background this repository already produces without anyone trying.

⇒ Below it, no reasonable reader would accept that the field was given a chance to respond, and we
should not ask them to. **The floor is deliberately low enough that failing it means something went
wrong with distribution, not that the work was ignored.**

⚠️ **This is the number to argue about now.** Once the first post goes out it is fixed, and the
whole value of the instrument is that it was chosen blind.

## 3. The venues, named in advance

**Announcement is a protocol obligation, not an option.** §3 of `PUBLICATION-CHECKLIST.md` forbids
approaching any party in a way not equally available to everyone; that rule stands, and this one
sits beside it: **every venue below must be attempted, and each attempt recorded with its date.**

⇒ **The first token on each row is the venue's IDENTIFIER, and it is what `exposure/attempts.jsonl`
must use.** The list is read out of this file by `attempts.py`; it is never retyped there. A prose
list cannot be parsed without guessing where a name ends — the first draft of this block wrote
*"ML Reproducibility Challenge community channels"* with no separator, and any parser would have
had to invent one.

```
x-twitter            the prepared thread, from the project's own account
hacker-news          Show HN, linking the repository, once
r-machinelearning    the reproducibility angle, once
mastodon             ML and reproducibility instances
mlrc-channels        ML Reproducibility Challenge community channels
lobsters             lobste.rs, if an account with submit rights exists
```

## ⛔ THE ATTEMPTS ARE NOT RECORDED IN THIS FILE, and the first version of it got that wrong

**This document is pinned BY DIGEST in the pre-registration. A first version carried `[ ]` boxes and
said "each attempt recorded with its date" — so ticking one would have voided the pre-registration
it belongs to.** That is exactly the `ANCHORS.json` circularity this protocol already solved once,
recommitted on the one new document whose entire purpose is to accumulate entries.

⇒ **The rules live here and do not change. The attempts live in `exposure/attempts.jsonl`**, an
append-only log, one JSON object per line, each entry OTS-stamped when it is written:

```
{"n": 1, "venue": "...", "utc": "...", "url": "...", "outcome": "posted|removed|rejected", "prev": "..."}
```

⛔ **AND AN APPEND-ONLY FILE THAT NOTHING CHECKS IS APPEND-ONLY BY HABIT.** The first version of
this section moved the attempts out of the pinned document and stopped there, which solved the
circularity and left the record itself unprotected: a `removed` outcome could be deleted, a date
moved, an attempt inserted, and every gate in this project would still pass. **A note inside a
document is not a control** — the sentence `check_commitments.py` opens with.

⇒ **`attempts.py` is the control, and it is the same monotonic construction as the anchor facts.**
Each entry carries `prev`, the SHA-256 of the previous entry's exact line bytes (`0`×64 for the
first), so the digest of entry *k* fixes entries 1…*k* and cannot be changed by anything appended
after it. Writing entry *k* also writes `exposure/attempts-<k>.head`, holding that digest, **which
is the file that gets OpenTimestamped** — a growing log cannot be stamped, a fixed digest can.
Every exposure capture records the head and the count it saw. So:

```
python attempts.py --record <venue> <url> <outcome>    append one attempt, write its head
python attempts.py --check                             verify the chain, the heads and the captures
```

⚠️ **Growth is permitted; contradiction is not.** New entries are expected. An entry whose bytes no
longer produce a head that some Bitcoin-anchored proof or some earlier capture already recorded is
a rewritten history, and that is the only thing this check calls a failure.

⚠️ **A removed or rejected post is recorded, never retried and never deleted.** The log is evidence
about distribution, and a distribution record that only contains successes measures persistence
rather than reach.

⚠️ **One attempt per venue.** Repeated posting is spam, and a study that spams to reach its own
floor has replaced the measurement with an effort. If a venue removes the post, that is recorded as
an outcome, not retried.

⛔ **No private approaches, unchanged.** Nothing here permits messaging individuals; §2b and §3 of
the checklist still bind. **These are all public, open channels, equally available to everyone.**

## 4. The capture schedule

```
every 7 days from the first announcement, and on the close date
python capture_exposure.py    then    python ../../_ots_stamp.py exposure/<file>
```

⛔ **Seven days, not fourteen, and the margin is the point.** GitHub's traffic API returns a rolling
**14 days and keeps nothing older**, so a missed capture is data *permanently lost*, not delayed. A
seven-day cadence survives one missed capture; a fourteen-day cadence does not.

⚠️ `capture_exposure.py` records the gap in each record, so the series can never be read as
continuous when it is not.

## 5. What gets reported, whatever happens

```
the venues attempted and the date of each        from exposure/attempts.jsonl, append-only
the exposure series                              from exposure/, every record stamped
unique viewers at close, against the floor       the denominator
commitments filed and reports filed              the numerator
whether the floor was met                        which decides WHICH claim is licensed
```

⇒ **Both numbers travel together or neither is reported.** A reproduction count without its
exposure denominator is the sentence this whole document exists to make unwriteable.

---

*Related: [`PUBLICATION-CHECKLIST.md`](PUBLICATION-CHECKLIST.md) ·
[`REPRODUCTION-CALL.md`](REPRODUCTION-CALL.md) · `PRE-REGISTRATION-v18-CONFIRMATORY.md`*
