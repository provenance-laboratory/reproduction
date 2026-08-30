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

## 3. Measurement 1 — roughly 10%, not 37%

Twelve **counterbalanced** pairs (half threads-1-first, half threads-16-first, in a seeded order),
both arms explicitly pinned, the machine re-checked between every pair, and the pairs stored **in
execution order**:

```
                  median     min      max
threads=1          5.95 s    5.21 s   6.30 s
threads=16         5.40 s    4.21 s   5.73 s

paired differences positive in 12 of 12 pairs
permutation p          4.88e-04   exact, over all 4,096 sign assignments
ratio of medians       1.102
bootstrap 95% CI       [1.072, 1.192]
```

⇒ **Pinning to one thread costs roughly 10% here, 95% CI [+7%, +19%].**

⛔ **The +37% was an artifact of the design, and three faults produced it.** Every pair ran
pinned-first, so drift inside a pair loaded onto one arm. The comparison arm was *unconstrained* —
not a condition at all, but whatever the machine chose. And the two timing arrays were **sorted
separately** before being stored, destroying the pairing that made them comparable.

⭐ **Repairing the design moved the estimate from 37% to 10% and made the evidence far stronger.**
Complete separation across 12 pairs is an exact p of 4.88 × 10⁻⁴ — where the previous revision had
worried about a 0.12 s gap and called it "thin", which was the wrong statistic to be nervous about.

⚠️ **It is not "the cost of determinism."** It is the cost of pinning to one thread rather than
requesting sixteen: two stated constraints. Which minimum constraint actually achieves bit-identity
is unknown until measurement 4 is done, and an unknown constraint cannot be costed.

## 4. Measurement 5 — divergence appears at step 0, in every array

```
first step at which E, W1, b1, W2, b2 differ (threads 1 vs 16)     0, 0, 0, 0, 0
first step at which the ROUNDED loss curve differs                 64
```

⛔ **"Divergence first appears at step 8" was a fact about `loss.json`.** It is written as
`round(x, 8)`; that rounding floor is 5 × 10⁻⁹, the same order as the median parameter difference,
so the loss curve could never see what it was being asked about. A reviewer demonstrated it by
perturbing one reduction at step 0 — the weights differ from step 0, the recorded loss notices
nothing for dozens of steps.

⇒ `train.py --trace` now records a digest **per array, per step**, and full-precision losses ship
beside the rounded ones. §3 asked for *"the first layer/step where it appears"*; the answer is that
there is no first layer. Reduction order enters at the first matmul, so everything diverges at once.

**Magnitude, threads=1 against threads=16, over 804,096 parameters:**

```
relative L2            2.008e-05
max |difference|       1.369e-04
parameters differing   778,597 of 804,096   (96.8%)
final loss             identical to 8 decimals
```

⚠️ **"Numerically indistinguishable" is withdrawn.** No behavioural equivalence was tested and
capability testing is out of scope by §5. The defensible statement is *close under the reported
parameter metrics, with identical final loss to eight decimals* — a different claim that licenses
a different inference.

⚠️ **A number this study declines to headline.** The maximum *relative* difference over all
parameters is **17.0**, and it is meaningless — entirely parameters near zero. Above 1% of RMS the
maximum is 1.03 × 10⁻¹. Reporting 17.0 would be a true number selected to mislead, which is the
failure mode this pair of papers exists to measure in other people's work.

## 5. Measurement 3 — internal repeatability, and not more

Three runs at threads=1 produced one digest, `59d07fa0…`.

⛔ **Not reported as bit-identity.** §6 makes *"reporting bit-identity without an independent
party's re-run"* an invalidating condition, and the previous revision said measurement 3 "holds"
and was "now measured". That was a violation of the pre-registration by this document, and it is
withdrawn. Three of our own runs agreeing is **internal repeatability**. It becomes evidence about
bit-identity when someone unconnected to this project reproduces it, and not before.

## 6. Measurement 7 — divergence is NOT monotone in thread count

Added by the pilot; omitted entirely from the previous revision, which §6 forbids.

```
threads     2       4       8       16
differing   97.3%   97.6%   97.5%   96.8%
```

⇒ **Not monotone**, and the last step goes the "wrong" way — *fewer* differing parameters at more
threads. Whatever governs the magnitude, it is not "more threads, more disagreement".

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

## 9. What one machine still cannot say

```
MEASUREMENT 4   bit-identity across hardware. NOT DONE. The two reviewer runs are early and
                confounded -- CPU, OS, Python, numpy and OpenBLAS all differ at once -- and they
                predate the corpus correction, so they cannot be compared to current digests
§2b            the independent re-run does not exist, and by §2b we may not produce one
```

⚠️ **A vs B is not an isolating comparison unless OS, Python, numpy and the BLAS build are held
constant too.** Otherwise vendor, operating system, library version and selected microkernel move
together, and the matrix's one clean contrast is lost. That condition has to be added to §2a before
measurement 4 is run, or the comparison it was designed to make cannot be made.

---

*Related: [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) · [`AMENDMENT-2026-08-30.md`](AMENDMENT-2026-08-30.md) · [`PILOT-2026-08-29.md`](PILOT-2026-08-29.md) · [`MEASUREMENT-6.md`](MEASUREMENT-6.md)*
