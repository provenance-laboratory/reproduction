# Paper B (`reproduction`) — internal review packet, round 3

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     25 files
  sha256 b545684563d9eade0ca7729512f974e0433aaa1808db45c6cc081035b1cb8c57
this file
```

Repository `provenance-laboratory/reproduction`, commit `eb4a4fd`  ⚠️ TREE DIRTY.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 3.** Both reviewers required a v3 pre-registration, and both were right again. Round 2's repairs each needed their own repair.
>
> - `blas_kernel_selected` was NOT the selected kernel -- it is the build-configuration line, and a reviewer's run recorded `Haswell MAX_THREADS=64` while the same process reported a SkylakeX runtime architecture. Renamed to `blas_build_config_line`, with `blas_runtime_arch` recorded where observable.
> - That field was also REQUIRED by the §2a gate, which refused conda/MKL, macOS Accelerate and non-DYNAMIC_ARCH OpenBLAS outright -- three honest installs that could file nothing but 'I could not run it', which §2c would have scored as an ecosystem finding about our own gate. Now recorded as an absence, exactly as §5 already settled for the effective thread count.
> - An off-by-one in the sampling range excluded the last valid (context, target) pair. Negligible in effect, and part of the model specification, so it changes every digest.
> - The trace began after the first update, so it could show the arrays DIFFER at step 0 but not that they STARTED identical. It now records the initialisation as step -1.
> - 'Final loss identical to eight decimals' was false: 3.21813250 against 3.21812963. It was the sentence written to replace a claim withdrawn in round 1.
> - Nothing is anchored: both active OpenTimestamps proofs carry calendar attestations only, while three documents said 'anchored'. The retired pilot's proof is the stronger one. `anchor_status.py` now decides this by reading the proof bytes.
> - The v2 ordering was defeated by the package: the reference run predates the document that orders it, and EXPECTED.json shipped the target inside the package handed out before the commitment step.
>
> ⚠️ **v3 is required. The corpus, model and pipeline are NOT frozen until v3 is anchored and its proofs carry a Bitcoin attestation -- so a finding in any of them is still cheap to act on, and is wanted now rather than after publication.**

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

