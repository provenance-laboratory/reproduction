# Pre-registration v18 — the ecosystem claim is WITHDRAWN, and v17's repair is repaired

*Amends v17. Everything not restated here is unchanged and still governs.*

## 1. ⛔ The null was unfalsifiable, and the repair is to withdraw the claim

A reviewer of v17 found a real hole, and it is not in dispute:

> The instrument can only measure "no issue was filed." Nothing in seventeen anchored versions
> fixes, in advance, how the call is distributed, to how many people, or what would count as
> insufficient exposure. … §3 of the checklist forbids approaching any party in a way not equally
> available to everyone. That is a good fairness rule, and there is no matching rule *requiring*
> broad announcement. **So minimum exposure is fully protocol-compliant, and it produces the
> sharper finding.**

⇒ **A protocol under which doing nothing is compliant and yields the preferred result can produce
a dishonest paper without anyone lying.** Every other input to this study is committed in advance
and anchored; the one input that licensed the headline — did anyone see it — was uncommitted,
unanchored, under sole author control, and would have been written after the outcome was known.

### 1a. ⛔ Two repairs were available, and this version takes the second

```
1  BUILD THE INSTRUMENT   so "nobody reproduced it" can be separated from "nobody saw it":
                          venues named in advance, an exposure floor, a capture cadence
2  WITHDRAW THE CLAIM     so no exposure measurement is needed, because nothing rests on it
```

An earlier draft of v18 took route 1 and built the instrument. **This version takes route 2.**

⛔ **THE CLAIM BEING WITHDRAWN IS §2c OF `PRE-REGISTRATION.md`, QUOTED HERE SO THE CHANGE IS
LEGIBLE** rather than something a reader has to notice by absence:

> **If nobody reproduces the artifact within a stated window, that is a reported result and not a
> gap.**
>
> […] If an artifact published expressly to be reproduced — tiny, licensing-clean, deterministic by
> construction, with every input hashed — also goes unreproduced, then the barrier Paper A measured
> applies to a case constructed to remove every excuse for it.
>
> ⇒ That would be a finding about the ecosystem rather than about the artifact […]

**That inference is withdrawn.** The paper publishes the artifact, reports any reproductions
received, and **draws no inference from their absence.**

### 1b. ⇒ Why this costs one sentence

§4 of `PRE-REGISTRATION.md` already states the paper "is written to be publishable under either
outcome". The headline is **measurements 1–6** — the cost of determinism, and whether bit-identity
survives different hardware — and those are measured. §2c's inference from silence was a
**secondary** observation the paper does not need.

⚠️ **It is the more neutral position, not the weaker one.** An inference from silence requires
establishing that the silence means something, which requires an exposure denominator, which
requires posting obligations and a capture cadence running to December — **commitments outside the
laboratory work itself**. Withdrawing the inference removes all of that machinery and leaves the
measurements, which never depended on it.

### 1c. ⚠️ The instruments remain, as INSTRUMENTS, not as gates

```
capture_exposure.py                GitHub's own traffic record. Run it or do not; nothing turns on it
attempts.py                        the append-only distribution record, if distribution happens
exposure/exposure-2026-09-07.json  the 2026-09-07 baseline, stamped, kept as a dated observation
DISTRIBUTION-PLAN.md               SUPERSEDED. Retained as the record of the alternative examined
```

They are pinned by digest below because a tool that may be run must be the tool that was pinned.
**Nothing here obliges any of them to be run.** If the call is distributed, it is recorded honestly;
if it is not, no result depends on the difference.

⛔ **WHAT IS DROPPED, EXPLICITLY:** the exposure floor of 100 unique viewers; `INSUFFICIENT
EXPOSURE` as a reportable outcome; "announcement is an obligation, not an option"; one-attempt-
per-venue as a rule; and the seven-day capture cadence as a requirement.

⛔ **AND THE RETAINED CAPTURE CONFERS NO HEAD START.** `exposure/exposure-2026-09-07.json` is a
stamped, pre-announcement exposure baseline, and the withdrawn inference is the only thing that has
a use for it. A round-8 reviewer named the door that leaves ajar, and it is closed here: **holding
this capture buys nothing toward reinstating the claim.** Reinstating it would require a NEW
anchored protocol version, argued and judged on its own terms, which would have to establish what
v18 §1 found it could not — that the distribution was fixed in advance well enough for silence to
mean anything. A dated artifact already in hand does not supply that, does not shorten the argument,
and must never be offered as evidence that the question was left open on purpose. It is retained
because destroying an observation to make a withdrawal look tidier is the worse act.

⚠️ **`DISTRIBUTION-PLAN.md` IS RETAINED AND PINNED, NOT DELETED.** Its analysis of why the floor
metric was ill-defined — three candidate readings differing by more than an order of magnitude, two
already disagreeing at the baseline — and of the bound that pointed the wrong way, is good work and
is the evidence that route 1 was examined properly before route 2 was chosen. A project that
deletes the road it did not take cannot show that it looked.

### 1d. ⛔ The close date is KEPT, and not for the obvious reason

**The close date is unchanged: 7 December 2026, as carried by v15, v16 and v17.** All three are
signed and Bitcoin-anchored — v15 in blocks 965831/965832, v16 in 965840, v17 in 965910/965912 —
and v15 is the earliest to carry the date.

⛔ **IT IS A REPORTING CUTOFF, NOT A DEADLINE. Nothing is required to happen on or before it.**
Not publication, not distribution, not a capture. It says only which reports are counted in the
pre-cutoff number. **Reproductions received after it are still reported** — labelled post-cutoff,
and never folded into the pre-cutoff count. It must never be restated as a publication deadline:
*the paper is written when it is written.*

⛔ **AND A ROUND-6 REVIEWER ASKED THE RIGHT QUESTION ABOUT THAT SENTENCE: does it reopen, one level
up, the freedom the cutoff closes?** If nothing fixes when we stop, an author can wait for a
flattering result and write then. Their remedy was to pre-commit a submission interval. **We are
not taking one**, and the reason is not reluctance: a submission interval is a duty owed to nobody,
on a calendar, and this project does not hold those. What it holds are stopping rules.

⇒ **THE STOPPING RULE IS ALREADY HERE AND IT BINDS THE NUMBER, NOT THE CALENDAR.** The reported
pre-cutoff count is a function of the cutoff date and of nothing else. Waiting longer cannot raise
it, cannot lower it, and cannot change which reports it contains — a reproduction arriving on 8
December is reported, labelled post-cutoff, and is not in that number no matter how long we wait
before writing. **So there is nothing a later submission date can do to the result**, which is what
a pre-committed interval would have been protecting.

⚠️ **WHAT THAT DOES NOT COVER, stated rather than left.** An author who waits accumulates
post-cutoff reports, and a paper may be written more favourably for having them even though the
headline number is fixed. Labelling alone is weaker than the number's own fixity.

⛔ **SO THE REPORTING SENTENCE IS PRE-COMMITTED HERE, AND ITS ONLY FREE VARIABLE IS THE COUNT.**
A round-8 reviewer accepted that a submission interval is a calendar duty this project does not
hold, and pointed out that the residual freedom was never about the count — it was about what the
surrounding paragraphs are permitted to make of it. That is a stopping rule, not a duty, and it
costs nothing to fix now. **The paper reporting this study will report the pre-cutoff outcome in
these words, verbatim:**

> As of the pre-registered cutoff of 7 December 2026, **N** reproduction reports had
> been received. This count is a function of the cutoff date alone. No inference is drawn from its
> value in either direction: it is not evidence about the artifact, and it is not evidence about
> the ecosystem — the inference that would have made it so was withdrawn in v18 §1, before any
> value of N was known.

⛔ **THE WORD *INDEPENDENT* WAS IN THAT SENTENCE UNTIL ROUND 9, AND IT WAS A SECOND FREE
VARIABLE.** A round-9 reviewer found it, and the finding is that the paragraph above defeated
itself in its own last line. *"This count is a function of the cutoff date alone"* was false as
written: it was a function of the cutoff date **and of an admission rule nobody had committed**.
Nothing in this version or any earlier one says what makes a reproduction report independent, or
who decides. So the count could be raised by waiting — not by moving the date, but by admitting a
marginal report — which is precisely the freedom the sentence exists to close, reappearing inside
the sentence that closes it.

⛔ **AND IT CONTRADICTED A PUBLIC PROMISE ALREADY MADE.** `REPRODUCTION-CALL.md` binds this study
in front of the people it is asking: *"We do not characterise your independence. … We will not
describe any reporter as independent, or affiliated, or anything else. That is the reader's
inference to draw from the record, not ours to assert on their behalf."* The verbatim sentence did
the one thing the call promises not to do, and it would have done it in the paper.

⇒ **ONE WORD IS DELETED AND NOTHING ELSE CHANGES.** The count is of reports received; a reader
opens the public thread and judges independence for themselves, which is what the call says they
will do. That is the only version of this sentence consistent with the call, and it is the only
version under which *a function of the cutoff date alone* is true.

**N is the only thing that may change.** Any report received after the cutoff may be described
afterwards, under its own label, and may not be used to qualify, soften or strengthen the sentence
above. A paper written in March with three post-cutoff reproductions still opens this passage in
exactly these words. **This binds the narrative rather than the calendar**, which is the move
already made for the number, applied one level up to the prose.

⇒ **WHY IT SURVIVES THE CLAIM THAT MOTIVATED IT, WHICH IS THE PART A READER WILL ASK ABOUT.**
The freedom the cutoff closes has not disappeared. It has **reversed direction**:

```
BEFORE §2c was withdrawn   silence was the flattering outcome (the "sharper finding"),
                           so the pressure ran toward MINIMUM EXPOSURE
AFTER  §2c is withdrawn    a reproduction is the flattering outcome,
                           so the pressure runs toward WAITING FOR ONE
```

An open-ended stopping point would let this study run until something good arrives. A cutoff fixed
in advance closes that, and **closing it is now the only thing the cutoff does.** So the date is not
a leftover from a withdrawn claim; it is the last remaining piece of optional-stopping protection,
and it happens to be anchored already.

⛔ **AND IT IS NOT MOVED, BECAUSE MOVING IT HERE WOULD HAVE THE SHAPE THE ANCHORING EXISTS TO
PREVENT.** Changing a pre-committed parameter in the same version that withdraws the claim which
motivated it is indistinguishable from changing it because that was convenient — and
*"indistinguishable from"* is the standard this protocol applies to everything else. **Two decisions
must not be bundled where one can hide the other.** A wholly innocent change would look identical
to a self-serving one, so the innocent change is the one that does not get made.

⚠️ **IF THE DATE IS EVER TO CHANGE**, the honest route is a NEW VERSION stating the change and its
reason — never an edit to this one, and never in the same version that changes what the date is for.

## 2. ⛔ v17's repair closed the loud half and left the quiet half

The same reviewer took v17's structural strip apart, and was right three times.

**Finding 1. The two patterns disagreed about the line's tail.** The commitment pattern permitted a
trailing `# comment`; the anchor-fact pattern did not; and the strip required *every* line to match
the stricter one. **A single annotated height turned all 32 heights back into committed file
paths** — on a signed, anchored version. This file's own `_ROW` comment records that exact class,
fixed between two of the three readers and left broken between the other two.

**Finding 2. The strip was structural and the reader was still heading-located.** A renumbered heading
stripped correctly and declared **zero facts, silently** — the loud half repaired, the quiet half
untouched, in a document whose §3 says the wrong-answer case matters more than the no-answer case.

**Finding 3. And it shipped with no control at all.** The function whose failure cost three protocol
versions was never called by the control suite. That is the v10 defect verbatim: *"the rule was
violated by the document that introduced it."*

⇒ **One block-finder now serves both the strip and the reader**, so "stripped" and "read" cannot
disagree; all fenced blocks are merged rather than only the first; a tagged fence is recognised;
duplicate heights are refused across blocks as well as within one; and `commitments()` refuses
outright if blocks were stripped while the reader returned nothing. **Eleven controls cover it**,
including three negative ones proving a real commitment table still survives the strip.

⚠️ **v15 now parses correctly despite its renumbered heading** — 29 facts, 22 commitments — so the
defect that cost two protocol versions is unreachable rather than patched.

## 2.1 ⛔ Round 2 found the floor was fixed and the METRIC was not

v18 was reviewed before it was signed. The reviewer's first finding:

> The floor is 100 unique viewers "over the window", **and that quantity does not exist.** GitHub
> returns a rolling 14 days of per-day uniques and a 14-day total. Uniques do not add. … You fixed
> the threshold blind and left the *metric* free. **The metric is the larger degree of freedom.**

Three readings were available and they differ by more than an order of magnitude; two already
disagree at the baseline (clones: 41 by the 14-day figure, 43 by summing daily uniques). ⇒ Whoever
computed the number in December would have been choosing, **with the answer visible**, between a
rule that licenses the ecosystem claim and one that forbids it.

```
METRIC     the sum of views[].uniques over every DISTINCT DATE in the capture series
           -- over-counts returning visitors, so it is an UPPER BOUND on persons
COMPUTED   by capture_exposure.py on every run, printed whether or not it is convenient
```

⚠️ **And nothing computed it.** The most load-bearing number in the study was prose in one document
and enforced nowhere, which is the condition `check_commitments.py` exists because of.

## 2.2 ⛔ And the block-finder was defeated three more ways

Sharing one finder closed the two states round 1 named and **did not close the class**: a comment on
its own line inside the fence, and an indented fence, each lost every height silently. The eleven
controls were eleven shapes a reviewer had named — **enumeration standing in for projection, inside
the repair for the defect this project calls enumeration-for-projection.**

⇒ **The projection, which does not depend on knowing the shape:** every anchor-fact-shaped line in a
document must be accounted for by some block, or the document is refused. A height stated and read
by nobody is committed to nothing however its fence is written.

⚠️ **And the merge was a denial of service.** Refusing a repeated height *across* blocks meant a
version illustrating the format with a real height killed every tool that asks which document is
authority — refusing even when both blocks stated the same root. Scoped: within a block a repeat is
a lie; across blocks, only disagreement is.

## 2.3 ⛔ Round 3: four repairs, four defects, all introduced by round 2's fix

**The bound ran backwards, in our favour.** v18's first draft said over-counting *"makes failing the
floor harder, which is the right direction"*. It makes it **easier** — an inflated figure clears the
floor, so the ecosystem claim is easier to license, and a gate on a claim should be hard to pass.
⚠️ The sentence had travelled from a code comment into this document and then into the review brief
asking someone to check it, **each copy citing the last**. ⇒ Corrected in all three, and the bound
is now declared as a cost: clearing the floor shows that *no more than* N people saw the call.

**The projection projected over its own predicate.** `_raw` used the detector's own pattern, so a
`>`, `|` or `-` prefix hid a line from the check *and* from the thing it checks. This document's own
fact table, rewritten as a pipe table, parsed as 25 commitments and **zero facts, silently**. ⇒ It
counts **digests** now, which cannot be reformatted away. Ten shapes tested, two negative controls.

**The baseline proof was a calendar receipt, not an anchor** — 530 bytes, zero Bitcoin attestations,
on the one artifact whose entire claim is *"captured before any announcement"*. ⇒ Now **block
965922**, pinned and verified.

**And this plan was byte-pinned while required to grow.** It carried `[ ]` boxes and instructed that
each attempt be recorded with its date, so ticking one would have voided the pre-registration it
belongs to — **the `ANCHORS.json` circularity, recommitted on the one document whose purpose is to
accumulate entries.** ⇒ Rules stay pinned; attempts move to an append-only `exposure/attempts.jsonl`,
each entry stamped, with removals and rejections recorded rather than retried.

## 2.4 ⛔ Round 4: the projection was defeated a third time, and three rules were prose

**The projection projected over a SHAPE again, and round 3's fix is what put the shape back.**
Counting digests meant matching `^[^0-9a-fA-F]*?(\d{6,9})[^0-9a-fA-F]+([0-9a-fA-F]{64})` — *"no hex
character before the height"* — and **`0`–`9` and `a`–`f` are hex.** So any prefix containing a
digit or one of six letters was invisible: a numbered list, `Block 964534 <root>`, `height 964534:
<root>`, a row written digest-first. A reviewer produced five in one sitting and there was no reason
to think five was the number. **Three consecutive versions have written this rule so that its blind
spot is the parser's blind spot**, which is the one property it exists not to have.

⇒ **The predicate now describes neither half in terms of what surrounds it.** The digests are
removed from the line, and a height is looked for in what remains. Nothing about a prefix,
separator, bullet, cell or column order can hide either token, because the rule never looks at
anything but the two tokens. Its one bound is stated rather than assumed: a digest is a hex run of
**64 or more**, so a malformed 65-character digest — which disqualifies its block and would
otherwise vanish — is seen; runs *shorter* than 64 are excluded because these documents legitimately
abbreviate digests in prose beside heights. **The accounting is positional, not a count**: two
totals can agree while naming different lines.

**And the rule that catches every other shape had no controls, for three rounds.** It was rewritten
twice and `test_controls.py` was byte-identical across both, so each rewrite shipped having never
been attacked. ⇒ **Sixteen now**: eleven decorations that defeated some earlier version, three ways
a block is disqualified rather than missed, and five negatives proving legitimate prose still parses.

**`exposure/attempts.jsonl` was named in an anchored document, and protected by nothing.** No
writer, no reader, no control, no file. A `removed` outcome could be deleted, a date moved, an
attempt invented, and every gate here would have reported green over the record of the one thing
this version is about. ⇒ `attempts.py`, built as the **same monotonic construction as the anchor
facts**: each entry carries the digest of the one before it, that digest is written to
`exposure/attempts-<n>.head` and **stamped**, and every scheduled capture records the head and count
it saw. Growth is permitted; contradiction has to argue with Bitcoin or with an earlier stamped
capture. **Eighteen controls**, including the case a hash chain alone cannot see: a deleted tail.

⛔ **AND HERE IS WHAT "APPEND-ONLY" DOES NOT MEAN, stated where the rule is rather than only in the
implementation.** The ledger is internally chained, and it is **not** tamper-evident against
deletion of its unwitnessed tail: entries after the most recent externally witnessed head can be
removed together with that head, and the remaining chain is consistent. **Tail deletion is
detectable only back to the latest externally witnessed head** — an OpenTimestamped `.head` file,
or a count recorded by an earlier stamped capture. Until such a witness exists for a given entry,
that entry's presence rests on our word.

⚠️ A round-6 reviewer found this stated honestly in `attempts.py` and absent from the protocol, and
was right that the asymmetry matters: a reader who meets *append-only record* in an anchored
document reasonably understands a stronger protection than exists. The superseded
`DISTRIBUTION-PLAN.md` still carries the stronger historical wording, under its superseded banner,
which makes the distinction easier to miss rather than harder.

⚠️ **THE OBLIGATIONS THIS ROUND ADDED WERE REMOVED AGAIN BY §1, AND THE INSTRUMENT WAS KEPT.**
Round 4 also made `--publishing` enforce a pinned plan, a stamped baseline, and a baseline
preceding the first attempt; and it made one-attempt-per-venue a rule the record refused to break.
Those were the right rules **for a version that inferred something from silence**, and §1 withdrew
that inference. So the gates are gone and the ledger is not: `attempts.py` still refuses a rewritten
history, because a record worth keeping is worth keeping honestly, and it no longer refuses a second
post, because nothing here rations posting any more.

⚠️ **v18 also manufactured the v15 hazard by hand.** It numbered its narrative `## 2d.`, `## 2e.`,
`## 2f.` while `### 2a.`–`### 2d.` name the commitment tables, so a reader met two sections called
*2d*. It was harmless only because v17 stopped locating tables by heading at all. ⇒ Narrative
renumbered to `2.1`–`2.4`, the reservation written down in §3, and `_after_heading` now **refuses**
when a marker begins more than one line rather than silently taking the first.

## 3. ⛔ What is committed, by DIGEST

⛔ **This section commits exactly 28 file pins.** The number is written here by hand and is not maintained by any tool, which is the whole of its value: a reader can count the rows, and `prepare_anchor.py` refuses when the two disagree. A round-9 reviewer edited one character of one digest into a shape the parser could not read, and the row left the table taking the total with it — `28 pins; 28 hold … READY`, true of a document that had silently stopped committing a file. A grammar cannot count what it cannot parse, so the count comes from somewhere else.

⛔ **`2a.`–`2d.` are RESERVED for these four tables and are not available to narrative.** v18's
first draft numbered its round-2 and round-3 sections `## 2d.`, `## 2e.`, `## 2f.`, so a reader of
this document met two different sections called *2d* — the same ambiguity that, in v15, cost two
protocol versions when a renumbered heading silently emptied the fact table. It was harmless here
only because v17 stopped locating the tables by heading at all. The narrative is now numbered
`2.1`, `2.2`, `2.3`, and `check_commitments.py` **refuses outright** when a heading marker begins
more than one line, so this is a failure rather than a preference from here on.

### 2a. Experimental inputs

```
corpus/MANIFEST.json    fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py  2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json     7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30
train.py                ebd61532782573a04aca8ab5d526ab6d233c450963ac111460f2d5d86f81d2fe
runs/det-1/run.json     97a0318343b2fa60a072fd4339520b124c13e1b3fab62a5148dc5a8f60e2d816
```


⛔ **The REFERENCE RUN is committed here, and it was not before.** The digest a
reproducer is asked to arrive at is derived from this file, so leaving it uncommitted left
the one number this whole design exists to fix in advance free to be changed afterwards --
with every other commitment still verifying. `build_package.py` now derives the target
through a single function that refuses if this file is uncommitted or has moved.

### 2b. Instruments and gates

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   2e52e4bea1d0fbbc5e027d0bea226b9266e85488288fc63b4ee4f9d6e2d8e1df
build_package.py                   0c50cc172500f62c0363f124fef3e9b494e8f8ef5b3532e9371c5ae927000f9c
build_review_packet.py             f5e55b4d5190eea3fdaf724aec21472dbb00737f09189da9ae36e9a08329f6eb
check_commitments.py               94c3346085fbe9740872f5f01bd7c3219aa2b65e8e719ff54bda09e6fa6e54ff
check_signature.py                 04c16bee058b27ef3a7f44d81bcf01bc59b1505906e64d69dfe74e91d1c9681a
corpus/verify_shipped.py           943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
measure_cost.py                    4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py              d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py                9686200fc21b08e1ef0cfeb14f7ecda9733bc34296e0318b7e63c4f390b6effc
measure_storage.py                 1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
ots_verify.py                      15ca911511c6c8aff0eee0c2821203cc201d689788f4687bee63e00c8a7c2ca9
pin_anchors.py                     98ef5a2074803888da417bafc9ff6e9f01e16d5fde669acd5a54d651888ba705
reproduce_findings.py              d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
seed_sensitivity.py                1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
test_controls.py                   2823a58d1f17397d16bc8f0133942c300dcb078566bd6afac578f711849db3a5
verify_package.py                  ed4d6d2a179169720fba28ef59769dc14e59cf9d207d617ad0c4aa75e32d0410
HOW-TO-RECHECK-THE-ANCHORS.md      403526de7aeaa22a73ddcc0df24350898a43a455beb97357c63e1f1d21d04233
capture_exposure.py                4a3cd9c235b499dff5430731c0fe867147ad799d7e6b3512febd9587feb1a90d
DISTRIBUTION-PLAN.md               6a1851278f20a89328cd5ffccb0359ee97d0ebbfc6e39147feea3b734fb2cb89
exposure/exposure-2026-09-07.json  837fb43a3f9f5ddeddcd06372759c796d2df91ba958d12b269b0de2c7ccb2624
attempts.py                        1edee542a8ecfa974694a8dbc807b706bb0b0aaf767cf3213f002ffed70f36ab
REPRODUCTION-CALL.md               803e1047c9fcb186be4b4c5f8d16966db4ee4a9a00e252e42a8f01eb1d38ac83
```

⛔ **CORRECTED IN ROUND 8, BEFORE THIS VERSION WAS PUT IN FORCE.** This paragraph read *four
digests moved and four entries are new*. Four moved is right. **Seven entries were new**, and the
three it omitted were the three that most needed disclosing: `prepare_anchor.py` and
`withdrawn_claims.py` -- one of them carrying a WRITE PATH into protocol documents -- and
`runs/det-1/run.json`, the reference-run commitment, which §2a does disclose in its own bold
paragraph.

⛔ **AND IN ROUND 9 THE FIRST TWO OF THOSE THREE LEFT THIS VERSION ENTIRELY.** They are committed
by **v19**, which argues them on their own; see the split recorded at the end of this section. Five
entries are new here, and none of them is a governance change.

⚠️ §2.1's diagnosis applies to §2b: **prose in one document, enforced nowhere.** The table was
typed while the pins beside it were maintained by a tool, and nothing compared the two. A reviewer
diffed v17's pin rows against v18's and got the real number in one command.

⚠️ **Four digests moved:**

```
build_package.py                   ccbcd3b34a8be7bb -> f7b66c93bfff069f
build_review_packet.py             db18eba091a22927 -> e4eaa9b07788e99b
check_commitments.py               63c8054579615da3 -> ecb51c28c00fc187
test_controls.py                   0e38c72c43969cf7 -> 4087870ec7ac3684
```

⚠️ **Six entries are new:**

```
attempts.py                        NEW, pinned from this version
capture_exposure.py                NEW, pinned from this version
DISTRIBUTION-PLAN.md               NEW, pinned from this version
exposure/exposure-2026-09-07.json  NEW, pinned from this version
runs/det-1/run.json                NEW -- the reference run; see the bold note in 2a
REPRODUCTION-CALL.md               NEW -- and section 1d now rests on a promise it makes
```

⛔ **`REPRODUCTION-CALL.md` IS PINNED FROM THIS VERSION, AND ROUND 9 IS WHY.** §1d's verbatim
sentence used to say *N independent reproduction reports*; the word came out because the call
promises, in public and to the people it is asking, *we will not describe any reporter as
independent, or affiliated, or anything else*. The repair to a pre-registered sentence now rests on
a document that was unpinned, unsigned and unanchored -- so a reader could not check that the
promise the repair cites is the promise that was made. It is committed here for that reason.

⚠️ **Two more were new in round 8 and are not here in round 9:** `prepare_anchor.py` and
`withdrawn_claims.py` moved to v19.

⛔ **THIS VERSION BUNDLED, WHICH §1d ITSELF WARNS AGAINST, AND IN ROUND 9 IT WAS SPLIT.** §1d's
best line is that two decisions must not be bundled where one can hide the other. v18 withdrew a
claim, re-pinned four digests, added two tools, and opened a write path into protocol documents.
The re-pins are mechanical; **`--repin` is a governance change**, and it was landing inside the
version whose §1 is the thing a reviewer is meant to be weighing.

⚠️ **Round 8 recorded that rather than repairing it**, on the ground that splitting a version
about to be signed would cost more than saying so. A round-9 reviewer answered that the cost cited
was not the cost on the table: this version is unsigned, has already been redrafted once, and
`prepare_anchor.py` exists to make re-preparing cheap. They also named the asymmetry that makes
disclosure inadequate here — **the withdrawal is self-denying and `--repin` is self-empowering**,
so pairing them puts a governance change inside the version a reviewer has every reason to approve.

⇒ **`prepare_anchor.py` and `withdrawn_claims.py` are committed by v19**, which argues them on
their own and names the controls each now carries. This version withdraws a claim and re-pins. The
sentence above, written in round 8, said a future version bundling a governance change with a
substantive withdrawal should be split; that version was this one, and it was.

### 2c. ⛔ What the reproducer package contains

```
check_commitments.py
check_signature.py
corpus/MANIFEST.json
corpus/build_corpus.py
corpus/sources.json
corpus/verify_shipped.py
ots_verify.py
test_controls.py
train.py
```

### 2d. ⛔ ANCHOR FACTS — monotonic

**Every line must remain present and unchanged; new heights may be added and are not a violation.**

```
964534     018d69dc7bf4e2e8a45fdf3a89855b9b7e03027227aa14e596a91dcf320e09b9
964535     ef17461955701f9c1d296245df4ab22a71a7e3e0fd3ceeb7213de12958ba69c5
964549     e863c303c5b515da7544652b29648659c66ff2fa6ffad9fe82ccc975042eb439
964747     8a9766909969f175693a1fd85a7236e3be4d33a95cd4a0bcab3fff2e76e16857
964761     23019c9499bd74096ae1d9c4015bc4f10176900d99cb805e7252011ed7415d37
964762     ff5f6043b9883f8e8830856a16dc52783c66d1185d6ffebab5dbe3598f42c543
964775     ed2dd86c5b3c983d859139542aeced248e1f18ec030ccd550e36286a59f54f5e
964785     8aac2039e614e1557aab7264848c8b0cb1152970f2d5e7fa76170ccdfbf2a587
964789     b73d9657064cb4a9842e18ec1a007bc4702308730257cc378dd56ed3443ec0dd
964812     9cd60bdc0fdc9ba7784f8a4705c22d11b82b081a41d69ff598729522834dbd4a
964815     ac3592ef064ea4e4c7db187954f057550018a38dfa02afc7a2c3d33ad2955b76
964848     5784c7dab006cedba2172ec6cce265b83b1f75c8a27a117f4b2df1165b151d9c
964856     a2c750b72ab68db7602962f230b1e8a236633d5cef8f132fed1547b3ac6aba9e
964878     b9fef3d8dd2fc6b2945cb580525f25beaf5612b7b71e3a1b78799e22f353dce0
964881     45cb82a2d9677e318826afb6fd6f3a6be84b5cf94780ee1487b49097d5293579
964920     7f5a7092d6b342430276b08b492f1f18e8a6fa8ddb55a6245f0d93f6e70e13d3
964922     d876c661233b2de9d92f1dabebf9c1a677570711dbec02b1e5317502b2610fe6
964923     92687073de11e6fd31a71c3f6aa0c75aa60a0950dffa30b80ad91155425f4986
965140     c836cd739ba5bddf491db621fcfe76154d6002cecfb10dd4a72eecd99e039ec6
965142     df6e4b4f68795f65252340e42467d77e8e8c2a44e1e5a4ff40730848aca56eb6
965152     46e025634022f51ac766cc16d8be33c04068c0eb7e7a2f66930e022ca4185ece
965332     c20da71633ebb813cd0f4f78f6059bab6b6b06912a2eb76cc48182acf66a9d35
965333     3d4a2b7fe40ea918d1496985dce09db8395a9559f99c80b7be61b9c259b32266
965458     f4cb09e6fc3350c3ddcf0b4d64d124d1504d94a8b148f92298cf0465fc1513c9
965750     6dde0e9afe57f11f8b833e405d736ae64820acc04ef97d4bfeaffb3d089b949c
965753     a0a8bb7589ecd091de601d52e66639b755285ad688f23b43bc161f8092937586
965767     1a000e0f8b386a3d7b9af7eea508041fc818776605e5be6e5eb3fa108ea5c750
965784     5d65ae5e5a55e51cf1477df815f41cdc3486dfe25e33999361e582bdde0e9c2c
965818     6e9b364e154b594ce72804c6be577f7fb7ae9bf49d941cb71fe9c8bb9d1b2ea8
965831     84f7aba8c1732f40a3b4a6fa6845d0f1e0272bf882760122ff257a23485a3b08
965832     fe0ed8292038251f49661bc2c2674520f23510114b49b7d0089caeb9d2c28855
965840     4a817365b47122ee011d2542c01e677c3dcca3abfa04f01715de02f38bdc7b84
965910     2a7d27ba92ece6f533426c684cc7ab0bbc57a51eed4dc2e332f921a71f3836ec
965912     4c456b1d277b5969250a57052ce30a0b70f4c41cd0659e8f780e4695e3fb2504
965922     e67fe31925653d81ff315c29d2364a5023ebec76de0fc0a6ce347202b3a4edea
```

⇒ **3 height(s) added since v17**, being the block that anchored v17 itself.

## 4. ⚠️ Unchanged

v14's withholding rule; v15's shipping of the anchor pins and the statement that they are checkable
rather than independently verified; and **the close date of 7 December 2026**, carried by v15, v16
and v17 and unchanged here — a *reporting cutoff*, not a deadline, for the reasons in §1d.

## 5. ⛔ What this version does NOT do

It does not make the reproduction blind. It does not make measurement 4 confirmatory.

⛔ **And it does not replace the ecosystem claim with a safer version of the ecosystem claim.** An
earlier draft made the claim *conditional*, on a floor fixed in advance — which is a better claim,
and is still a claim resting on a measurement of who was watching. **This version does not make the
claim at all.** No reading of the result may restore it, because there is no threshold at which it
becomes available.

⚠️ **The withdrawal is not a finding.** It says nothing about whether the artifact would be
reproduced, and nothing about the ecosystem either way. It says only that this study does not
measure that, and will not report as though it had.
