# Paper B (`reproduction`) — internal review packet, round 1

*Every figure below is read from the measurement files by `build_review_packet.py`. It refuses to write if one is missing.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     18 files, sha256 3c34cbce3c07962f41e961347ed4170a
this file
```

Repository `provenance-laboratory/reproduction`, commit `c6949a7`.

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
m1  cost of determinism   about +37% (37.05%)   11 interleaved reps, ranges do not overlap
      pinned  median 6.59 s   min 5.87   max 9.52
      free    median 4.80 s   min 4.66   max 5.75
m2  apparatus             48555 bytes on 9530916 bytes of artifact (0.509%)
      of which timestamp proofs   7387 bytes
m3  bit-identity, same hw  one digest across 11 runs -- but see below
      ⛔ NOT YET A FINDING OF THIS PAPER. Section 6 makes reporting
      bit-identity without an independent party's re-run an invalidating condition.
      Three of OUR OWN runs agreeing is an internal phase record, nothing more.
m4  bit-identity, diff hw  NOT MEASURED -- needs configurations B, C, D
m5  divergence             first differs at step 8; relative L2 8.0e-06;
                           83% of 804,096 parameters differ between threads 1 and 16
m6  engineering hours      self-reported; flagged as the weakest evidence in the study
```

## The thread sweep, read from the runs

```
threads=1    ccf303f04e8ab1f02723f199137f9eb237bd042bd754bb87
threads=2    639bc3afab0add2aea194f82a0bb110a1a3c7526ede565f8
threads=4    9aef82f7a8400bddc12e8f9f1c0e6969977867f26984ab1f
threads=8    3d73f3c2c76fc828c2d8a8577a2a64b8b072b9013b9f8201
threads=16   479add43eee1ae443fe2f4038ac322cf8e7bcad09356de8c
```

⭐ **`--unconstrained` produces the threads=16 digest byte for byte**, so 'unconstrained' is not a separate condition on this machine — it is 16 threads. An identification, not an inference.

## The artifact under test

```
corpus        6313332 clean bytes, 10 texts, merkle 814acd249a2988da156438d4fda68066
model         8-byte context, d_emb 64, d_hid 1024, 300 steps, batch 256, float32
weights       sha256 ccf303f04e8ab1f02723f199137f9eb237bd042bd754bb87e09a0333a19e18cd
published as  package/ -- 27 files; OUR WEIGHTS ARE NOT IN IT, only the digest
```

## ⚠️ Known-weak, and a reviewer should push here

- **n = 1 machine.** Configuration A only. Measurement 4 is the paper's second half and is not done.
- **The m1 ranges separate by 0.12 s.** Non-overlapping, but thin enough that a twelfth repetition landing badly would close it. Read it as *roughly a third*, not as 37.1%.
- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS reduction order and capability is explicitly out of scope — but a reviewer may reasonably argue the finding does not transfer to attention kernels or to CUDA, where atomics add a second source of the same phenomenon.
- **Measurement 6 is a memory.** Everything else is a digest or a timing a stranger can re-run. That page cannot be checked and says so.
- **The independent reproduction does not exist**, and by section 2b we may not produce one. If nobody answers the call, section 2c pre-registered that silence as a result — a reviewer should decide whether that is a finding or a rationalisation, because it was written before the window opened precisely so that question could be asked.

## ⛔ What the reviewer should NOT accept without pushing

- that a package running on the machine that built it is evidence of anything beyond completeness;
- that the unconstrained runs agreeing three times means unconstrained training is reproducible — they agreed because nothing was contending;
- that about +37% is *the* cost of determinism rather than the cost on one configuration, on one pipeline, at one size.

