# Paper B (`reproduction`) — internal review packet, round 1

*Every figure below is read from the measurement files by `build_review_packet.py`. It refuses to write if one is missing.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     22 files
  sha256 92a82ee538a20dba735f3a71d1c743f31436487973f792e035b4da8bed5b990c
this file
```

Repository `provenance-laboratory/reproduction`, commit `7e607c5`  ⚠️ TREE DIRTY.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This paper has no manuscript yet, and that is what the review is for.** Phase 1 fixed the corpus and pre-registered the protocol; phase 2 built the pipeline and took every measurement that one machine can take. Reviewing it now, before a word of the paper is written, is deliberate: the expensive mistake would be to write the argument first and discover the measurements do not carry it.
>
> ⭐ **The headline arrived from a direction the pre-registration did not predict.** Section 4 expected bit-identity to fail ACROSS hardware, for principled reasons. It fails **within one machine, on thread count alone** — five thread counts, five distinct models, with 83% of parameters differing between 1 and 16. The conclusion the paper was written to be publishable under therefore holds *a fortiori*, and with a far smaller apparatus than the argument needed.
>
> ⚠️ **And the two models are numerically indistinguishable.** Relative L2 8e-06, final loss agreeing to seven significant figures. Any tolerance-based provenance claim passes; the bit-identity claim fails on 83% of the parameters. **That gap is the paper.**
>
> ⛔ **Measurement 1 took three attempts and the first two are reported, not replaced.** The first was contaminated by a build running in another window. The guard written to prevent that failed the same way — it checked once, found the machine quiet, and a build started a second later. A precondition checked once at the start is not a precondition held throughout.

## ⭐ CHECK THE FINDINGS, NOT ONLY THE PACKAGING

```
python reproduce_findings.py     five training runs, ~2 minutes, nothing timed
```

It re-derives the thread partition, the divergence table, the relative figure this paper declines to headline, and the step at which the loss curves first differ — from nothing but the corpus and `train.py`. **If its numbers disagree with `PHASE-2-FINDINGS.md`, the findings are wrong**, and that is the most valuable outcome this review could have. Contention cannot move any of it: every number is a digest or a difference, and nothing in that script is timed.

```
python verify_package.py         the package run in a directory it has never seen
```

## What is measured, and by what

```
m1  cost of pinning     ratio 1.102  95% CI [1.072, 1.192]  p=4.9e-04  12 pairs
      threads=1  median 5.95 s      threads=16 median 5.40 s
      counterbalanced, paired, stored in execution order; both arms PINNED
      -> report as: roughly +10%, CI [+7%, +19%]. NOT as a decimal percentage
m2  apparatus           182542 bytes on 9530566 of artifact (1.915%); 152726 if train.py and
      build_corpus.py are called artifact instead -- the boundary is arguable and
      measure_storage.py reports it both ways. Timestamp proofs: 4171 bytes
      ⚠ the PERCENTAGE does not transfer: the apparatus is near-
      constant and this artifact is deliberately tiny
m3  REPEATABILITY, same hw one digest across 12 runs at threads=1
      ⛔ NOT REPORTED AS BIT-IDENTITY. Section 6 makes that an
      invalidating condition without an independent re-run. The previous revision of
      the findings said measurement 3 -HOLDS-; that was a violation and is withdrawn.
m4  bit-identity, diff hw  NOT MEASURED -- needs configurations B, C, D
m5  divergence             first differs at step 8; relative L2 8.0e-06;
                           83% of 804,096 parameters differ between threads 1 and 16
m6  engineering hours     NOT MEASURABLE under this design, and reported as such.
                           The estimand never existed: nothing was made deterministic
m7  monotonicity          NOT monotone: 97.3, 97.6, 97.5, 96.8 per cent differing
```

## The thread sweep, read from the runs

```
threads=1    59d07fa0811667df8a9dd606f9ff7842265fd0cac605812f
threads=2    48b1241b245931126edcc57ec3f3fb80971e38fa204b3bbf
threads=4    63a77c3c178c9b33d9be5768b81bf50250b3007ffc167ed0
threads=8    53e63c7c05544cecb0ac0cf8c17ac9d94fa00f2bc47de984
threads=16   e2d154eb756fc8e9e45544f243b54a9f5ff0a03bdac9a074
```

⭐ **`--unconstrained` produces the threads=16 digest byte for byte**, so 'unconstrained' is not a separate condition on this machine — it is 16 threads. An identification, not an inference.

## The artifact under test

```
corpus        6312982 clean bytes, 10 texts, merkle 2006b7327c616f0ca5f9c0b9c3e766b5
model         8-byte context, d_emb 64, d_hid 1024, 300 steps, batch 256, float32
weights       sha256 59d07fa0811667df8a9dd606f9ff7842265fd0cac605812f96981d6b04ded8b5
published as  package/ -- 30 files; OUR WEIGHTS ARE NOT IN IT, only the digest
```

## ⚠️ Known-weak, and a reviewer should push here

- **n = 1 machine.** Configuration A only. Measurement 4 is the paper's second half and is not done.
- **Measurement 1 was +37% in the previous revision and is +10% now.** The design was at fault, not the machine: fixed order, an "unconstrained" arm that was not a condition, and arrays sorted separately before storage. Ask whether the repaired design has its own faults.
- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS reduction order and capability is explicitly out of scope — but a reviewer may reasonably argue the finding does not transfer to attention kernels or to CUDA, where atomics add a second source of the same phenomenon.
- **Measurement 6 is a memory.** Everything else is a digest or a timing a stranger can re-run. That page cannot be checked and says so.
- **The independent reproduction does not exist**, and by section 2b we may not produce one. If nobody answers the call, section 2c pre-registered that silence as a result — a reviewer should decide whether that is a finding or a rationalisation, because it was written before the window opened precisely so that question could be asked.

## ⛔ What the reviewer should NOT accept without pushing

- that a package running on the machine that built it is evidence of anything beyond completeness;
- that the unconstrained runs agreeing three times means unconstrained training is reproducible — they agreed because nothing was contending;
- that about +10% is *the* cost of determinism. It is the cost of pinning to one thread rather than requesting 16, on one configuration, at one size -- and which constraint actually buys identity is not known until measurement 4 is done.

