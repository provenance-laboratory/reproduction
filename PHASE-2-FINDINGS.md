# Phase 2 — what one machine can measure, and what it turned out not to show

*Revised 30 August 2026 after two internal reviews. Configuration **A**: Intel Core i5-1240P,
hybrid 4 P-cores + 8 E-cores, 16 logical, AVX2 without AVX-512; numpy 2.5.1 on OpenBLAS 0.3.33
`DYNAMIC_ARCH`, kernel `Haswell MAX_THREADS=24`.*

⛔ **Both reviewers rejected the previous revision, and its headline number was wrong by nearly a
factor of four.** Section 1 is the list.

---

## 1. What the reviews changed

| previously reported | now reported |
|---|---|
| determinism costs **+37.05%** | pinning to one thread costs **roughly 10%**, 95% CI [+7%, +19%] |
| divergence first appears at **step 8** | divergence appears at **step 0**, in **every array** |
| apparatus is **0.509%** of the artifact | **1.92%**, from a shipped script with a declared boundary |
| bit-identity **holds** on identical hardware | **internal repeatability only** — §6 forbids the other claim |
| five thread counts, five distinct models | true *here*; a reviewer got **one** model from five counts |
| the corpus is licensing-clean | it was not — one text still named Project Gutenberg |
| measurement 7 | was simply missing, which §6 also forbids |

**Every one was found by someone running the artifact rather than reading about it.**

## 2. ⛔ The corpus was wrong, and fixing it made everything downstream historical

`pg2701.txt` still contained *"one from Project Gutenberg's archives"* in a transcriber's note.
Project Gutenberg's terms make removing the licence **and all references** the condition for
redistributing the underlying work freely, so the corpus did not have the property the manifest
claimed — while the cleaning step's own docstring asserted that removing the boilerplate sufficed.

The fix is a rule over the class rather than a patch for the file that failed: **any paragraph
mentioning Project Gutenberg is dropped after marker extraction, each removal is recorded per text
in the manifest, and the build refuses if a reference survives.** One 350-byte editorial paragraph
was removed.

```
merkle root   814acd249a2988da…  ->  2006b7327c616f0ca5f9c0b9c3e766b5ebaa2aed99f1433fc66d7560d387452b
clean bytes   6,313,332          ->  6,312,982
```

⚠️ **This makes every earlier figure historical, including both reviewers' runs.** Their digests
were computed against corpus `814acd24…`, which no longer exists — so their protocol findings all
stand, and their digest observations describe a superseded artifact and are reported as such. The
old proof is kept as `MANIFEST.json.ots.superseded-814acd24`; it still attests exactly what it
always attested.

⚠️ **For several hours it was the STRONGER proof** -- the superseded corpus proof carried a
Bitcoin attestation while the proof over the corpus actually in use did not, and three documents
said 'anchored' regardless. Both round-2 reviewers caught it. Both are anchored now, and
`anchor_status.py` decides the question by reading the proof bytes so that the prose cannot drift
from it again.

## 3. Measurement 1 — and the number has now moved twice

```
                  median     min      max
threads=1          6.02 s    5.55 s   6.47 s
threads=16         4.62 s    3.80 s   4.90 s

order effect       AB median ratio 1.3066 (n=6)   BA 1.3118 (n=6)
paired differences positive in 12 of 12 pairs
sign-test p        4.88e-04   exact two-sided, all 4,096 sign assignments
ratio of medians   1.303
bootstrap 95%      [1.268, 1.343]  -- stratified within each order
```

⇒ **Pinning to one thread costs roughly 30% here, 95% CI [+27%, +34%].**

⛔ **This estimate has been +37%, then +10%, and is now +30%. Those are not three measurements of
one quantity; they are one quantity measured by three designs, two of which were faulty.**

```
+37%   fixed order, an "unconstrained" arm that was not a condition, arrays sorted separately
+10%   counterbalanced but SHUFFLED -- the seeded shuffle put BA BA BA first, so the warm-up sat
       entirely in one arm's order, and the two orders then disagreed by six points
       (AB 1.114 against BA 1.177). The design's own control had failed and nothing printed it
+30%   blocked alternation, stratified bootstrap, order effect printed
```

⭐ **The evidence that the third design is the sound one is that its order effect nearly
vanished**: 1.3066 against 1.3118, a gap of 0.5 points where the shuffled design's was six. A
counterbalanced design that can place half its blocks consecutively is counterbalanced in name,
and the +10% figure was distorted by exactly the imbalance it was meant to remove.

⚠ **A reader should still treat 30% as a pilot figure.** It is one machine, one pipeline, one
size, and the history above is a reason for caution rather than a story of convergence. What is
robust across all three designs is the direction and the fact of a cost, not its magnitude.

⚠ **And it is not "the cost of determinism."** It is the cost of pinning to one thread rather
than requesting sixteen -- two stated constraints. Which minimum constraint actually achieves
bit-identity is unknown until measurement 4 is done, and an unknown constraint cannot be costed.

## 4. Measurement 5 — divergence at step 0, from a trace that now starts earlier

```
initial state (step -1)                                    IDENTICAL in both runs
first step at which E, W1, b1, W2, b2 differ                0, 0, 0, 0, 0
first step at which the ROUNDED loss curve differs          21
```

⛔ **The trace used to begin after the first update**, so it could show the arrays *differ* at step
0 and could not show they *started* the same. A reviewer drew that line precisely: the evidence
supported "they differ after update 0" and not "divergence originates at the first matmul". It now
records the initialisation as step −1, and the two runs are confirmed identical there.

⚠️ **Even so, the stronger claim is not made.** That every array differs after the first update is
*consistent with* reduction order entering at the first matmul; **locating the source** would need
digests of the step-0 intermediates or gradients, which this trace does not record. The findings
say consistent-with, and `reproduce_findings.py` prints the same qualification.

⛔ **"Divergence first appears at step 8" was a fact about `loss.json`**, which is written as
`round(x, 8)` — a floor of 5 × 10⁻⁹, the same order as the median parameter difference. The loss
curve could never see what it was asked about.

**Magnitude on the v3 pipeline, threads=1 against threads=16, over 804096 parameters:**

```
relative L2            2.7084e-05
max |difference|       1.8023e-04
parameters differing   97.55%
final loss             3.25522614 vs 3.25522804   -- agree to 5 decimals, NOT identical
sign-test p (m1)       4.9e-04
```

⛔ **An earlier revision said the final losses were identical to eight decimals. They are not.** It
was the sentence written to *replace* a claim withdrawn in round 1 — a correction that introduced a
new overstatement.

⚠️ **"Numerically indistinguishable" stays withdrawn.** No behavioural equivalence was tested and
capability testing is out of scope.

⚠️ **A number this study declines to headline.** The maximum *relative* difference over all
parameters is meaningless — entirely parameters near zero. Reporting it would be a true number
selected to mislead.

## 5. Measurement 3 — internal repeatability, and not more

Three runs at threads=1 produced one digest, `59d07fa0…`.

⛔ **Not reported as bit-identity.** §6 makes *"reporting bit-identity without an independent
party's re-run"* an invalidating condition, and the previous revision said measurement 3 "holds"
and was "now measured". That was a violation of the pre-registration by this document, and it is
withdrawn. Three of our own runs agreeing is **internal repeatability**. It becomes evidence about
bit-identity when someone unconnected to this project reproduces it, and not before.

## 6. Measurement 7 — not monotone, and not separable from the seed

```
threads     2       4       8       16     
differing   58.0%   56.0%   86.2%   97.6%  
```

⇒ **Not monotone.** But that shape is a claim about **one trajectory**, and it should not be read
as more:

```
spread across thread counts (this seed)   41.5 percentage points
spread across five seeds, threads 1 vs 16 25.4 percentage points
relative L2 across those seeds            varies 6.0x
```

⛔ **The seed spread is 61% of the thread spread**, so m7's shape at one seed cannot be
distinguished from trajectory noise. A reviewer found this by varying only the seed and observing
that a one-index change to the sampling range had already moved m7 from `97.3/97.6/97.5/96.8` to
its present values between two pipeline revisions.

⚠️ **This project applied "a single timing is one sample from a distribution nobody looked at" to
measurement 1 three times, and never once to the divergence measurements.** The doctrine was
available the whole time and was not carried across. `measure_divergence.py` now reports both
spreads, and m7 is stated as *not monotone at this seed, with the seed accounting for most of the
range* rather than as a property of thread count.

## 7. ⛔ The headline claim, narrowed by a laptop

The previous revision said *five thread counts, five distinct models*. On configuration A that
still holds. **On a reviewer's machine, five thread counts produced one model** — the request for
16 was granted as 9, and the mechanism is the **effective reduction shape**, which an environment
variable only requests.

⇒ The defensible claim is narrower and more useful:

> **Reduction shape is provenance-critical, and thread count is one dial that changes it — but
> whether turning that dial changes the artifact is itself implementation-dependent.**

That is a better finding than the universal it replaces, because it says where to look instead of
asserting something a single laptop can refute.

## 8. Measurement 6 — not measurable under this design

⛔ **Reported as not measurable rather than estimated.** The estimand never existed: no ordinary
pipeline was later made deterministic, so there is no delta; and no contemporaneous time log was
kept, so a retrospective figure would be inadmissible. The "afternoon" and "two days" of the
earlier revision are withdrawn as quantitative evidence and remain in
[`MEASUREMENT-6.md`](MEASUREMENT-6.md) as process history, labelled as such.

## 9. ⛔ The pre-registration was void for a day, and every tool reported success

v3 §2 pins four files by SHA-256 and states that a change to any of them voids the
pre-registration — *"it named files, and a name is not a commitment"*. **Nothing enforced that
sentence.**

It was found on 2026-08-31 by writing the control that should always have existed. Two violations
were standing at that moment:

```
corpus/build_corpus.py   edited minutes earlier, to add a verification mode.
                         Digest 2d3ce23b -> d9fd717e. REVERTED; it is the committed file again
train.py                 edited on 2026-08-30 in the round-3 commit, which added --seed and
                         is_confirmatory_spec and left §2 untouched. Digest aa893adb -> 1231a42a.
                         THE PRE-REGISTRATION HAD BEEN VOID FOR A DAY
```

⚠️ **Throughout that day the package rebuilt, `verify_package.py` passed, and `SHA256SUMS` was
regenerated over the new bytes.** A checksum derived from the bytes it polices cannot notice a
substitution — which is the whole reason the digests were written into an anchored document in the
first place, and exactly the property that document was unable to enforce about itself.

⭐ **`train.py` is not reverted, and the change is shown to be numerically inert rather than
asserted to be.** `--seed` exists because a round-2 reviewer required measurement 7's
seed-sensitivity arm; reverting would delete a measurement a review demanded. So the committed
pipeline was checked out of git and run:

```
train.py @ aa893adb (committed)   weights a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c59721511f98f1c23d38
train.py @ 1231a42a (in use)      weights a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c59721511f98f1c23d38
```

Bit-identical. Without `--seed` the computation is unchanged and one key is added to `run.json`. **No
measurement in this document is affected.**

⛔ **That does not make the violation harmless, and it is not filed as though it were.** The
commitment exists precisely so nobody has to take *"the change was inert"* on trust. It was inert
here; the point is that for a day nothing in this project could have told the difference, and the
same silence would have covered a change that was not.

`PRE-REGISTRATION-v5-CONFIRMATORY.md` re-commits the digests and discloses all of it.
`check_commitments.py` **parses the table out of the anchored document** rather than restating it,
derives the governing version from what is on disk rather than naming one in a constant, fails
closed on an empty parse, and is fatal inside `build_package.py`. Four positive controls, including
one that deletes v5 to confirm v3 does not silently resume governing.

## 10. Measurement 4 — ISOLATING, and bit-identical

⛔ **As v3 specified it, this comparison could not isolate anything.** CPU vendor, operating
system, Python, numpy and the OpenBLAS build all moved at once, so a byte difference was
attributable to any of five things and the measurement was designed to attribute it to one. An
earlier revision of this section said the condition *"has to be added to §2a before measurement 4 is
run"*. It never was. `PRE-REGISTRATION-v4-CONFIRMATORY.md` adds it, and was written and anchored
while measurement 4 had **no data at all** — which is the difference between a condition and an
excuse.

The pair, under v4's conditions and with every protocol version carrying a Bitcoin attestation:

```
arm A   Intel Core i5-1240P      Windows-11  Python 3.14.3  numpy 2.5.1  OpenBLAS Haswell MAX_THREADS=24
arm B   AMD Ryzen 9 5900HX       Windows-11  Python 3.14.7  numpy 2.5.1  OpenBLAS Haswell MAX_THREADS=24

conditions 1-5          all met
weights, both arms      a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c59721511f98f1c23d38
BIT-IDENTICAL           yes
VERDICT                 ISOLATING
```

⇒ **Two machines of different CPU vendors, matched on operating system, Python, numpy and the
OpenBLAS build, produced the same bytes.** Within the variables this protocol observes, the CPU is
what differed, and it did not change the artifact.

⚠️ **What that does NOT establish, stated because the sentence is easy to over-read.** It isolates
the CPU *only among the variables v4 §2 lists*. Microcode revision, BIOS and firmware settings,
kernel scheduling and CPU feature availability beyond the recorded SIMD baseline are neither held
constant nor observed. And both arms selected the **same OpenBLAS microkernel** — `Haswell` — so
what is shown is that two vendors running the same reduction shape agree, not that vendor is
irrelevant to bit-identity in general. A machine selecting a different kernel is a different
experiment, and §7's finding says that is where divergence lives.

⛔ **The first attempt at this pair was CONFOUNDED, and it is retained rather than deleted.** Arm B
recorded no OpenBLAS build line — `pyyaml` was absent, so numpy's configuration output took a
format the parser cannot read. A **recording gap**, not a different BLAS: the pair was
bit-identical *and* confounded, which is why the verdict labels the comparison rather than the
result. It survives as `runs/amd-thr-1-no-pyyaml` with its own record, because keeping only the
clean answer would leave no trace of how it was reached. The dependency list that omitted `pyyaml`
was hand-written from what seemed relevant rather than derived from what arm A depends on, and was
wrong the first time it was used.

⚠️ **A limit these artifacts cannot close.** `run.json` records wall-clock *duration* but not
*when* a run happened, so nothing in the package establishes whether an arm ran before or after a
given anchor, in either direction. For the first pair it demonstrably ran early; for this one the
protocol was anchored first, and the artifacts cannot show it. Closing that means recording a
timestamp in `run.json` — and `train.py` is pinned by digest in `PRE-REGISTRATION-v5-CONFIRMATORY.md`
§3, so it is a v6 and not an edit.

## 11. What one machine still cannot say

```
§2b            the independent re-run does not exist, and by §2b we may not produce one
MEASUREMENT 4  isolates the CPU only among the variables v4 §2 lists, and both arms
               selected the SAME OpenBLAS microkernel. Microcode, BIOS settings, kernel
               scheduling and CPU features beyond the recorded SIMD baseline are neither
               held constant nor observed
ORDERING       run.json carries no timestamp, so no artifact here shows whether a run
               preceded or followed an anchor
```

⇒ The ISOLATING result answers *"do these two machines, matched on software, produce the same
bytes"*. It does not establish that CPU vendor is irrelevant to bit-identity, and nothing in this
document may be written as though it did. **Two vendors agreeing on one microkernel is not the same
claim as vendor-independence**, and §7 already locates divergence in the reduction shape rather than
in the hardware.

---

*Related: [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) · [`AMENDMENT-2026-08-30.md`](AMENDMENT-2026-08-30.md) · [`PILOT-2026-08-29.md`](PILOT-2026-08-29.md) · [`MEASUREMENT-6.md`](MEASUREMENT-6.md)*
