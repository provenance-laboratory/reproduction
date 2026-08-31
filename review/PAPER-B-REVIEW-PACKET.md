# Paper B (`reproduction`) — internal review packet, round 5

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     122 files
  sha256 3061a54e82c3b2d585f7223cb29699d24dc460c47cda7975492f489022402d00
this file
```

Repository `provenance-laboratory/reproduction`, commit `36c9db8`  ⚠️ TREE DIRTY.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 5.** Both reviewers refused the freeze and both broke BOTH new controls, nine ways between them. One gave the generalisation: every break is a control that can be satisfied by the ABSENCE, the NAME, or the DESCRIPTION of the thing it checks.
>
> - AUTHORITY WAS DISCOVERED FROM A MUTABLE FILE IN THE SAME DIRECTORY. Reading the digest table out of the protocol instead of restating it removed one hazard and introduced a worse one: whoever can change train.py can change the document saying what train.py should be. Editing both passed; minting an unanchored v6 silently moved authority. A table is authority only if its document's own proof binds its bytes and carries a Bitcoin attestation.
> - measure_hardware granted ISOLATING to SIX pairs that should not have one -- the same record as both arms, identical CPUs, Haswell vs SkylakeX, 1 thread vs 8, two absent build lines, two non-confirmatory runs -- and reported BIT-IDENTICAL: YES for an arm whose weights.npz was deleted. Every condition was satisfied by the PRESENCE or ABSENCE of a field rather than its VALUE. Conditions 0 and 4-8 added; bit-identity recomputed from the artifacts.
> - THE VERDICT IS NO LONGER ISOLATING. Both reviewers said it claimed too much; MATCHED-STACK CROSS-MACHINE is adopted. And CONFOUNDED was wrong for the first pair: arm B's record CONTAINED the BLAS library, version and build, and only the field the extractor reads was empty. That case reports RECORDING-SCHEMA INADMISSIBLE.
> - THE ROUND'S HEADLINE DEFECT WAS INSIDE THE ROUND'S OWN FIX: MEASUREMENT-4.json was excused from the packet as 'absent until measurement 4 is retaken' while on disk and being read by the packet builder. The one new result reached both reviewers with none of its evidence. An excuse claiming absence must now be true, and the packet ships the result, both run records, both artifacts and five divergence runs the same check found missing.
> - v6 commits THE INSTRUMENTS AND GATES, not only the inputs -- twelve scripts by digest. A change to any of them now requires a new anchored version, and the cost of that rule is stated in v6 rather than discovered later.
> - Every run now binds itself to what produced it: pipeline digest, every protocol document's digest and anchor state, the package's SHA256SUMS digest, and a self-reported time labelled as the weak half.
> - test_controls.py runs all eleven attacks plus the positive case, ships in package and packet, and is fatal in the publication gate. Round 3's positive controls were prose; that is why they broke.
> - The measurement-4 pair is RECLASSIFIED AS DESCRIPTIVE. Its conditions were strengthened after its result was known and it bound itself to no protocol. A confirmatory pair requires a fresh run under v6 on both machines.
> - Measurement 3's digest was two pipeline corrections old and incomparable with every other figure. Re-measured rather than annotated.
>
> ⚠️ **v6 is stamped and PENDING. Nothing may be published until it anchors, and --publishing refuses while any version is pending. A finding in train.py, the corpus, or the admissibility conditions still forces v7.**

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
m4  bit-identity, diff hw  MATCHED-STACK CROSS-MACHINE -- AMD Ryzen 9 5900HX with Radeon Gra, bit-identical True
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

- **n = 2 machines.** Intel and AMD, matched on OS, Python, numpy and the OpenBLAS build -- and BOTH SELECTED THE SAME OpenBLAS MICROKERNEL (Haswell, X86_V3). So measurement 4 shows two vendors running the SAME REDUCTION SHAPE agree, which is not vendor-independence. A machine selecting a different kernel is a different experiment and has not been run.
- **Measurement 1 was +37% in the previous revision and is +30% now.** The design was at fault, not the machine: fixed order, an "unconstrained" arm that was not a condition, and arrays sorted separately before storage. Ask whether the repaired design has its own faults.
- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS reduction order and capability is explicitly out of scope — but a reviewer may reasonably argue the finding does not transfer to attention kernels or to CUDA, where atomics add a second source of the same phenomenon.
- **Measurement 4 is DESCRIPTIVE, not confirmatory.** Its admissibility conditions were strengthened AFTER its result was known, and it bound itself to no protocol digest. Neither is repairable retroactively. A confirmatory pair needs a fresh run under v6 on both machines, and has not happened.
- **v6 pins the instruments, and authority is still not EXTERNAL.** The manifest lives in the same directory as the thing it governs; what stops last round's attack is the anchor, not the location. A reviewer asked for CI or signed release metadata to select it. Push on whether anchoring alone is enough.
- **The transitional allowance is a new escape hatch and it already swallowed one attack.** A file matching a stamped-but-pending version is reported as a transition rather than a violation, so that a freshly stamped version does not block every build. It let a deleted proof through until the control suite caught it. Attack it again — that is where a convenience rule of exactly this shape belongs under suspicion.
- **`--publishing` still does not require a public-commitment record, an address, or a close date.** v6 §7 names all three as invalidating conditions and none is enforced in code. That is a commitment written down, not a control.
- **Measurement 6 is reported NOT MEASURABLE.** Everything else is a digest or a timing a stranger can re-run. That page cannot be checked and says so.
- **The independent reproduction does not exist**, and by section 2b we may not produce one. If nobody answers the call, section 2c pre-registered that silence as a result — a reviewer should decide whether that is a finding or a rationalisation, because it was written before the window opened precisely so that question could be asked.

## ⛔ What the reviewer should NOT accept without pushing

- that a package running on the machine that built it is evidence of anything beyond completeness;
- that the unconstrained runs agreeing three times means unconstrained training is reproducible — they agreed because nothing was contending;
- that about +30% is *the* cost of determinism. It is the cost of pinning to one thread rather than requesting 16, on one configuration, at one size -- and which constraint actually buys identity is a question measurement 4 addresses only for the reduction shape both arms shared; see PHASE-2-FINDINGS section 10.

