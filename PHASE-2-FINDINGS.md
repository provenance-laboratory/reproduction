# Phase 2 — the pipeline runs, and the model is reproducible under a stated constraint

*30 August 2026. Configuration **A** of the pre-registered matrix: Intel Core i5-1240P, hybrid
4 P-cores + 8 E-cores, 16 logical, AVX2 without AVX-512. numpy 2.5.1 on
OpenBLAS 0.3.33 built `DYNAMIC_ARCH`.*

---

## 1. What exists now

```
train.py           one file, numpy only, no network. ~1.85M parameters over a fixed 8-byte
                   context. 300 steps, batch 256, float32, seed 20260829
measure_cost.py    measurement 1, interleaved and with a quiet-machine precondition
corpus/            10 texts, 6,313,332 clean bytes, merkle root 814acd24..., committed and
                   OpenTimestamped BEFORE any of this ran -- now ANCHORED in a Bitcoin block
```

⚠️ **An MLP, not a transformer, and that is a choice with a reason.** The pre-registration says
capability is irrelevant and will not be benchmarked. What must be exercised is the mechanism the
pilot identified — threaded BLAS reduction order in large matmuls — and an MLP does that with
backprop a stranger can read and check in an afternoon. A hand-written transformer would add
hundreds of lines whose only effect on *this* measurement is more places for a bug that is not the
subject.

⛔ **Two ordering hazards are handled in the code rather than in a README**, because both produce
correct-looking runs that are not reproducible:

- **The thread pin happens before `import numpy`.** OpenBLAS reads those variables once, at load
  time. Setting them afterwards changes nothing and looks like it worked.
- **The corpus is assembled in MANIFEST order, not directory order.** A training set built from
  `iterdir()` is a different training set on a different filesystem while every file digest still
  matches — substitution passing an integrity check, one level up from the bytes.

## 2. Measurement 3 — bit-identity on identical hardware: **it holds**

Three runs, threads pinned to 1, same machine:

```
det-1  det-2  det-3     weights sha256 ccf303f04e8ab1f02723f199137f9eb237bd042bd754bb87e09a0333a19e18cd
```

One digest across three runs. **Under a stated constraint, bit-identical reproduction of a trained
model is achievable.** That is the first half of the claim in section 1 of the pre-registration, and
it is now measured rather than assumed.

## 3. The pilot's finding, reproduced on the real pipeline

The 29 August pilot partitioned a toy `numpy` sum by thread count. The same partition appears in
the trained model, and it is not subtle:

```
threads=1     ccf303f04e8ab1f0…      --
threads=2     639bc3afab0add2a…      39.3% of parameters differ from threads=1
threads=4     9aef82f7a8400bdd…      37.6%
threads=8     3d73f3c2c76fc828…      39.7%
threads=16    479add43eee1ae44…      83.0%
```

⭐ **Five thread counts, five distinct models.** A claim demonstrated only on the instrument that
first showed it is half a claim; this is the other half.

⭐ **And "unconstrained" is not a separate condition on this machine.** Three unconstrained runs
produced `479add43…` — byte-identical to `threads=16`. That is an identification, not an inference,
and it changes how the contrast should be described: the honest comparison is pinned-versus-16, not
pinned-versus-chaotic.

⚠️ **The unconstrained runs agreed with each other, and that must not be read as reproducibility.**
Three runs on an otherwise idle machine chose 16 threads three times. Under contention OpenBLAS may
choose differently, and nothing in the artifact would record that it had. The pinned runs agree
*because the pin makes them*; the free runs agreed *because nothing interfered*. Only one of those
is a property of the artifact.

## 4. Measurement 5 — the divergence, measured

Divergence first appears at **training step 8** in every configuration. Between the threads=1 and
threads=16 models, over all 804,096 parameters:

```
relative L2, ||a-b|| / ||a||            8.0e-06
max |difference|                        6.5e-05      0.16% of the parameter RMS
mean |difference| among differing        7.1e-08
median |difference| among differing      9.3e-09
final loss                              3.27143717  vs  3.27143621
```

⇒ **The two models are numerically indistinguishable and are not the same artifact.** The loss
agrees to seven significant figures; 83% of the parameters differ in their bits; no digest matches.

⛔ **This is exactly the reframing section 4 pre-registered, arriving from a direction it did not
predict.** Section 4 expected bit-identity to fail *across hardware*. It fails **within one
machine**, on nothing but thread count — so the conclusion holds a fortiori and with a smaller
apparatus than the argument needed.

⚠️ **A number this record declines to headline.** The maximum *relative* difference is 1.08 — over
100%, which sounds like a catastrophe and means nothing. It is entirely parameters near zero
(|value| ≤ 4.0e-04), where relative error is undefined in any useful sense. Among the 797,295
parameters above 1% of RMS, the maximum relative difference is **2.3e-02**. Reporting the 1.08
would have been a true number selected to mislead, which is the failure mode this pair of papers
exists to measure in other people's releases.

## 5. ⛔ A measurement that was inadmissible and looked fine

The first timings of measurement 1 read **7.66 s, 7.59 s and 14.28 s** for three identical pinned
runs — an 88% spread — because a CPU-bound build was running in another window. Had the pinned and
free trials landed on quiet and busy moments respectively, the headline cost of determinism would
have been wrong by a factor of two and **nothing in the output would have said so**.

`measure_cost.py` therefore: refuses to start while our own heavy jobs are running, interleaves
the two conditions rather than running all of one and then all of the other (machines drift —
thermal throttling, a scheduler migrating work between P- and E-cores), reports median with min and
max, and states explicitly whether the two ranges overlap.

⛔ **And then the guarded version failed the same way, which is the part worth recording.** It
checked the machine, found it quiet, and a build started one second later and ran alongside all
seven repetitions — producing a 13.25 s pinned run beside a 6.18 s one. **A precondition checked
once at the start is not a precondition held throughout.** The check now runs *between every
repetition*, where contention can actually arrive, and its failure **discards the whole run without
writing anything**: a contaminated measurement left on disk gets cited, and the next reader cannot
see the window it was taken through.

⭐ **What did work was the overlap test.** That contaminated run reported `determinism costs +38.5%`
and, immediately beneath it, `THE RANGES OVERLAP, so this figure is not resolved at 7 reps`. The
headline number was wrong and the tool said so in the same breath — because it was built to report
whether the two distributions separate rather than to report a ratio. **A ratio between two
distributions nobody characterised is the same error as a single timing, one level up.**

## 6. Measurement 1 — the cost of determinism: **about +37%**

Eleven interleaved repetitions, the machine verified quiet **between every repetition**:

```
                        median      min       max
threads pinned to 1      6.59 s     5.87 s    9.52 s
threads unconstrained    4.80 s     4.66 s    5.75 s

determinism costs 37.05% of wall-clock on configuration A
```

**The ranges do not overlap, so the separation is resolved at 11 repetitions** — and only just:
the slowest unconstrained run (5.75 s) is 0.12 s faster than the fastest pinned one (5.87 s).
⚠️ **That margin is thin enough to report as thin.** A twelfth repetition landing badly would close
it, and the honest reading is *the cost is real and is roughly a third*, not *the cost is
37.05%*.

⛔ **One decimal place of that figure was already inconsistent across two artifacts.** The
measurement tool printed `+37.1%` from the live computation while the review packet printed
`+37.0%` from a value the same tool had rounded to two places before storing it. One measurement,
two numbers, neither wrong. The stored value is now unrounded and both consumers round it once, at
the point of display — but the deeper point is that **at a 0.12 s margin the first decimal was
never meaningful**, and printing it invited exactly this.

⇒ **What is being bought for that third is the only thing that makes the artifact checkable at
all.** The unconstrained runs were faster and produced a model no third party can confirm they
reproduced. The pinned runs are slower and produce one digest, every time.

## 7. The package, and the one control it can pass

`build_package.py` assembles what a reproducer receives: the pipeline, the corpus and its manifest,
the pre-registration and both OpenTimestamps proofs, the pilot, the reproduction call and the
report template — 22 files, 6.37 MB.

⚠️ **Our trained weights are deliberately NOT in it.** Only the digest, in `EXPECTED.json`. A
reproducer holding our `weights.npz` can compare digests without training anything and, worse,
cannot be certain they did not compare our file with itself. The artifact under test is the
procedure.

**The packaging control:** the package was copied to an empty directory and run there as a stranger
would.

```
sha256sum -c SHA256SUMS          21 of 21 OK
python train.py --out my-run     300 steps, 8.61 s
weights sha256                   ccf303f0…  == EXPECTED.json
```

⛔ **What that control does and does not establish.** It establishes that the package is COMPLETE —
nothing needed was left behind in the working tree, which is the confound section 2b makes
expensive, since a reproducer who fails for want of a missing file would be measuring our
packaging. It establishes **nothing about reproducibility across machines**: it ran on
configuration A, the machine that produced the expected digest. Calling this a successful
reproduction would be the error the whole paper is about.

## 8. What remains

```
MEASUREMENT 2   DONE: 48,555 bytes of apparatus on 9,530,916 bytes of artifact (0.509%),
                of which 7,387 bytes are the two OpenTimestamps proofs. The ratio does NOT
                transfer -- the apparatus is near-constant and this artifact is tiny, so the
                absolute figure is the one that carries
MEASUREMENT 4   needs configurations B, C and D. A vs B is the isolating comparison and it needs
                a second physical machine; nothing here can substitute for it
MEASUREMENT 6   engineering hours, self-reported, honestly -- to be written at the end and not
                reconstructed from memory
PUBLICATION     the package, then the public reproduction call. The window opens when the
                artifacts are published and its close date is fixed then
```

⛔ **The independent re-run cannot be produced from this workspace, by construction.** Section 2b
binds us: the reproducer receives the published package and nothing else, we do not assist, and any
assistance is logged and reported. That is a human dependency and it is supposed to be one.

---

Related: [`PRE-REGISTRATION.md`](PRE-REGISTRATION.md) · [`PILOT-2026-08-29.md`](PILOT-2026-08-29.md)
