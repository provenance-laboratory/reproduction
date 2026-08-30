# Paper B (`reproduction`) — internal review packet, round 4

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     41 files
  sha256 b25e2a7eeda7be8fd56bfd3945f04a2620288f0eb9c46a5921c846ad7d71a8a3
this file
```

Repository `provenance-laboratory/reproduction`, commit `f00458b`  ⚠️ TREE DIRTY.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 4.** Both reviewers refused the freeze again, and the central finding is the worst error of this project: the governing protocol was never in the package.
>
> - v3 was written, stamped, announced as governing -- and never added to CONTENTS or SEND. The package shipped v1 and a v2 whose own text says 'superseded by v3'. It ships now, and build_package refuses without it.
> - v2 and v3 were each stamped and then EDITED, so their proofs bound bytes that no longer existed. v3 was edited to say 'now anchored' -- the sentence whose truth the edit destroyed. v3 now makes no claim about its own anchoring; anchor_status.py's output is the claim.
> - anchor_status.py was a dead control: a reviewer passed it with 35 bytes of junk, with 16 bytes of a real proof, and by DELETING EVERY PROOF. It now takes an explicit required list, recomputes each digest, requires the proof to contain it, and fails closed on absence -- and states that tag presence is not path verification.
> - The packet's cross-check contained literal BACKSPACE bytes where word boundaries were meant, so it matched nothing; and its refusal used an undefined name. It now carries a canary that proves it can fire before it is trusted.
> - m5 and m7 were the last hardcoded figures and were one and two rounds stale. They are computed into MEASUREMENT-5-7.json and read as fields.
> - m7 is not separable from the seed: varying only the seed moves the differing fraction 25.4 points against a thread spread of 41.6. The doctrine 'a single timing is one sample' had been applied to m1 three times and never to divergence.
> - measurement 1 is marked DESCRIPTIVE: the schedule is fixed alternation, not randomised, so there is no design-based randomisation distribution; and its p is a magnitude-weighted sign-flip test, not the sign test it was called.
> - verify_package accepted an unlisted forged EXPECTED.json as authoritative. It now rejects any file not in SHA256SUMS and requires exactly one stage marker.
> - The packet claimed a reviewer's own run could falsify configuration A. It cannot -- it measures a different machine, and the script said so while the packet said the opposite.
>
> ⚠️ **v3 is anchored ONLY when anchor_status.py says so over its CURRENT bytes -- it is pending as this goes out, and the package carries ANCHOR-STATUS.txt saying it is not publishable in this state. A finding in train.py, the corpus or the model spec still forces v4.**

## ⭐ CHECK THE FINDINGS, NOT ONLY THE PACKAGING

```
python reproduce_findings.py     five training runs, ~2 minutes, nothing timed
```

It re-derives the thread partition and the divergence table **on YOUR stack**, from nothing but the corpus and `train.py`.

⛔ **It does not adjudicate the findings, and an earlier version of this packet said it did.** The sentence read *if its numbers disagree with PHASE-2-FINDINGS.md, the findings are wrong* — which is false, because the script measures a DIFFERENT MACHINE. A reviewer whose stack produced one digest across all five thread counts got exactly that disagreement, and the script itself said correctly that this does not contradict configuration A while the packet said it did. Both could not be true.

⇒ To audit the CONFIGURATION-A numbers rather than your own, use the reference bundle: `reference/` ships the arrays and `MEASUREMENT-5-7.json` the derived values, so the published figures can be recomputed from published bytes without training anything.

```
python verify_package.py         the package run in a directory it has never seen
```

## What is measured, and by what

```
m1  cost of pinning     ratio 1.303  95% CI [1.268, 1.343]  sign-test p=4.9e-04  12 pairs
      threads=1  median 6.02 s      threads=16 median 4.62 s
      BLOCKED alternation, paired, execution order kept; both arms PINNED.
      order effect: AB 1.3066 vs BA 1.3118 -- the design's own control, printed
      ⚠ the p is a SIGN TEST, not the randomisation distribution of a
      balanced design, whose space is C(n, n/2) rather than 2^n
      -> report as: roughly +30%, CI [+27%, +34%]. NOT as a decimal percentage
m2  apparatus           202660 bytes on 9530566 of artifact (2.126%); 167631 if train.py and
      build_corpus.py are called artifact instead -- the boundary is arguable and
      measure_storage.py reports it both ways. Timestamp proofs: 5773 bytes
      ⚠ the PERCENTAGE does not transfer: the apparatus is near-
      constant and this artifact is deliberately tiny
m3  REPEATABILITY, same hw one digest across 12 runs at threads=1
      ⛔ NOT REPORTED AS BIT-IDENTITY. Section 6 makes that an
      invalidating condition without an independent re-run. The previous revision of
      the findings said measurement 3 -HOLDS-; that was a violation and is withdrawn.
m4  bit-identity, diff hw  NOT MEASURED -- needs configurations B, C, D
m5  divergence            step 0 in EVERY array (trace records step -1 as the initial
                           state, and it is identical). relative L2 2.7084e-05, 97.55% of 804096
                           parameters differ between threads 1 and 16
m6  engineering hours     NOT MEASURABLE under this design, and reported as such.
                           The estimand never existed: nothing was made deterministic
m7  monotonicity         NOT monotone: 58.0, 56.0, 86.2, 97.6 per cent differing
      ⛔ AND NOT SEPARABLE FROM THE SEED. Varying only the seed moves the
      differing fraction by 25.4 percentage points and the relative L2 by 6.0x, against a
      thread-count spread of 41.5 points. m7's SHAPE is a claim about one trajectory.
```

## The thread sweep, read from the runs

```
threads=1    a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c597
threads=2    a23b019e05ac828aa89048b8287cd94b09ad0946da2e6799
threads=4    3fe819e501e655aa05762143fd5de3d8a83a177864809dec
threads=8    cf99a00da91d91721882eafeaad859015c16edabb6d4f4b1
threads=16   d0dcb2066db6a2f6f3a9e54e52869ce9a658a07c87e5bca0
```

⭐ **`--unconstrained` produces the threads=16 digest byte for byte**, so 'unconstrained' is not a separate condition on this machine — it is 16 threads. An identification, not an inference.

## The artifact under test

```
corpus        6312982 clean bytes, 10 texts, merkle 2006b7327c616f0ca5f9c0b9c3e766b5
model         8-byte context, d_emb 64, d_hid 1024, 300 steps, batch 256, float32
weights       sha256 a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c59721511f98f1c23d38
published as  package/ -- 39 files; OUR WEIGHTS ARE NOT IN IT, only the digest
```

## ⚠️ Known-weak, and a reviewer should push here

- **n = 1 machine.** Configuration A only. Measurement 4 is the paper's second half and is not done.
- **Measurement 1 was +37% in the previous revision and is +30% now.** The design was at fault, not the machine: fixed order, an "unconstrained" arm that was not a condition, and arrays sorted separately before storage. Ask whether the repaired design has its own faults.
- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS reduction order and capability is explicitly out of scope — but a reviewer may reasonably argue the finding does not transfer to attention kernels or to CUDA, where atomics add a second source of the same phenomenon.
- **Measurement 6 is reported NOT MEASURABLE.** Everything else is a digest or a timing a stranger can re-run. That page cannot be checked and says so.
- **The independent reproduction does not exist**, and by section 2b we may not produce one. If nobody answers the call, section 2c pre-registered that silence as a result — a reviewer should decide whether that is a finding or a rationalisation, because it was written before the window opened precisely so that question could be asked.

## ⛔ What the reviewer should NOT accept without pushing

- that a package running on the machine that built it is evidence of anything beyond completeness;
- that the unconstrained runs agreeing three times means unconstrained training is reproducible — they agreed because nothing was contending;
- that about +30% is *the* cost of determinism. It is the cost of pinning to one thread rather than requesting 16, on one configuration, at one size -- and which constraint actually buys identity is not known until measurement 4 is done.

