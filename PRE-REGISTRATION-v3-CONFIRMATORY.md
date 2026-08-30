# Confirmatory pre-registration, version 3 — 30 August 2026

**Version 2 is superseded before it was ever executed.** Round-2 review found defects in the
pipeline and in v2's own publication order, and a pre-registration you cannot follow is not one.

⛔ **The pilot remains the pilot.** Nothing below re-labels pilot measurements as confirmatory
results. What changes is that the confirmatory study can now actually be run in the order it
specifies.

---

## 1. What v2 got wrong

```
the ordering it exists to fix   v2 puts a public commitment BEFORE the reference run -- and the
                                package shipped EXPECTED.json, so the target went out at step 3,
                                before the commitment at step 4. The reference run also predated
                                v2 itself. The document ordered an experiment the package undid

it committed to filenames       "train.py is fixed" with no digest. A timestamped filename does
                                not commit its bytes, so a post-stamp change to the pipeline was
                                undetectable from the pre-registration

the §2a gate refused honest     `blas_kernel_selected` was REQUIRED, and only a DYNAMIC_ARCH
installs                        OpenBLAS emits it. conda/MKL, macOS Accelerate and plain OpenBLAS
                                were stopped before training -- reproducers who could file
                                nothing but "I could not run it", which §2c would have scored as
                                an ecosystem finding about our own gate

the field was mislabelled       it is the BUILD configuration line, not the selected kernel. A
                                reviewer's run recorded `Haswell MAX_THREADS=64` while the same
                                process reported a SkylakeX runtime architecture
```

## 2. ⛔ What is committed, by DIGEST

```
train.py                   aa893adb175e5d05fcd82d3007f673426ac93105393f4ea80759b87e44817f12
corpus/MANIFEST.json       fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py     2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json        7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30

corpus merkle  2006b7327c616f0ca5f9c0b9c3e766b5ebaa2aed99f1433fc66d7560d387452b
model          804,096 parameters: 8-byte context, d_emb 64, d_hid 1024, vocab 256
training       seed 20260829, 300 steps, batch 256, lr 0.05, float32
sampling       start positions drawn uniformly from [0, len(corpus) - CONTEXT)
```

⚠️ **The sampling range is stated because it was wrong.** v2's pipeline used
`len(data) - CONTEXT - 1` with an exclusive bound, silently excluding the last valid
(context, target) pair. Negligible in effect and part of the specification, so it changes every
digest and belongs here rather than in a patch note.

⇒ **Any change to a file above changes its digest and voids this pre-registration.** That is the
property v2 lacked: it named files, and a name is not a commitment.

## 3. The publication order, with the flaw v2 could not survive

```
1  this document is frozen, OpenTimestamped, and ANCHORED IN A BITCOIN BLOCK
2  the TARGET-FREE input package is published: train.py, the corpus, the call. No digest of any
   trained artifact is in it, because the target cannot precede the commitment
3  at least one reproducer COMMITS PUBLICLY through the open call
4  the confirmatory reference run is performed
5  the reference bundle and EXPECTED.json are published as a SEPARATE, signed, timestamped artifact
6  reproducers run and file reports
7  the window closes on the date stated at step 2, and everything filed is reported
```

⛔ **Step 1 says ANCHORED and means it.** v2 was timestamped and called anchored in three
documents while both of its proofs carried calendar attestations only -- the retired v1 proof was
the only Bitcoin-anchored one in the study, so the superseded protocol had the stronger guarantee.
`anchor_status.py` decides this by reading the proof bytes, and publication waits for it.

⚠️ **And it waits for a second reason.** The proofs are covered by the package's `SHA256SUMS`.
Upgrading one after publication changes a file every reproducer has already checksummed, so
`sha256sum -c` would fail for all of them on a file that grew for the right reason. Waiting a few
hours removes the choice between a broken checksum and a weak proof.

## 4. Admissibility, corrected

A run is **admissible as a reproduction** if it reports its CPU model, Python and numpy versions,
and its SIMD baseline. That is what identifies the machine and the library.

A run is **admissible for kernel or thread causal attribution** only if it additionally OBSERVED
the runtime BLAS architecture and the effective thread count -- which requires `threadpoolctl`.

⛔ **Configuration A's pilot runs are NOT admissible for causal attribution**, because
`threadpoolctl` was absent and the runtime architecture was never observed. The pilot's own
`run.json` now records `admissible_for_causal_attribution: false`. So *"reduction shape is
provenance-critical"* remains a plausible mechanism rather than a measured one until a
confirmatory run observes it.

⚠️ **The absence of an optional observation is recorded, never fatal.** A reproducer with numpy
alone can still file a result; they simply cannot be cited for a claim about kernels. This is the
principle v1 §5 already applied to the effective thread count, applied consistently.

## 5. Measurements

As v2 §4, with three corrections:

```
m1  the design is BLOCKED, not shuffled: orders alternate, so a warm-up cannot sit entirely in
    one arm. The bootstrap resamples WITHIN each order stratum. The reported p is named an exact
    two-sided SIGN TEST -- it is not the randomisation distribution of a balanced design, whose
    space is C(n, n/2) and not 2^n. The order effect is PRINTED, not merely controlled for
m5  the trace records the initial state as step -1, so it can establish that two runs STARTED
    identically. Locating divergence at the first matmul needs step-0 intermediate digests, which
    this trace does not record -- so that claim is stated as consistent-with, not measured
m2  a declared file that is absent is FATAL, and the boundary is stated: this measures the
    provenance overhead of ONE RELEASE, not the size of this study's apparatus
```

## 6. What would invalidate this pre-registration

- any file in §2 changing its digest
- publishing any trained artifact's digest before a public commitment exists
- reporting bit-identity without an independent party's re-run
- citing a run for kernel or thread causal attribution when it did not observe them
- reporting a tolerance without quantifying it
- benchmarking the model's capability anywhere in the paper
- any measurement going unreported because it was inconvenient
- describing any reproducer as independent, or as anything else

**All seven measurements are reported whatever they say.**

## 7. Retained unchanged

⛔ **WE DO NOT ASSIST.** ⛔ **WE DO NOT CHARACTERISE INDEPENDENCE.** And §2c's null outcome, which
now applies at the commitment step as well as at the window's close.

---

⚠️ **Status: the pilot is complete; nothing is published; no reproducer has been approached; no
confirmatory run exists.**

⭐ **This document's proof now carries a Bitcoin attestation, and so does the corpus manifest's**
-- verify with `python anchor_status.py`, which reads the proof bytes rather than a log line.
The precondition in §3 step 1 is therefore met, and step 2 may proceed when the author chooses
to open the window.

**NOT a product, and not a recommendation.**
