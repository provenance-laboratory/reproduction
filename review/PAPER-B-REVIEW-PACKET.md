# Paper B (`reproduction`) — internal review packet, round 6

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     173 files
  sha256 2aff91f669b5c85cbb9e9ea7a0704e9b38c7b56a1c025564ea55de593199c05a
this file
```

Repository `provenance-laboratory/reproduction`, commit `8375ac6`  ⚠️ TREE DIRTY.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 6.** Both reviewers independently built the SAME forty-byte file -- SHA256(document) followed by the eight-byte Bitcoin attestation tag -- and it was accepted as an OpenTimestamps proof. It moved authority in check_commitments.py and let a substituted train.py through with exit 0, while `ots info` on the same file says it is not a timestamp file at all. ROUND 4 HAD FOUND THIS ATTACK AND THE REPAIR DID NOT FIX IT: a round-4 reviewer passed 35 bytes of junk containing the tag, the repair added BINDING (require the document's digest to appear) and never added PARSING, so the next reviewer supplied 40 bytes containing both strings and was believed. Two rounds, one defect, because the repair addressed the instance rather than the class. AND ANCHORING ANSWERS WHEN, NEVER WHO: stamping is free, public and unilateral, so anyone with write access can compose a successor, stamp it and wait two hours -- timestamping was the whole of these documents' authenticity story. FIVE MORE ABSENCE ATTACKS PASSED in the tool already repaired twice for absences: deleting BOTH arms' spec, corpus_merkle_root, threads_requested or python each returned MATCHED-STACK CROSS-MACHINE, the strongest verdict the tool can issue, because `a.get(k) != b.get(k)` is FALSE when neither arm states k. `started_utc` WAS AN END TIME: measured at shell-before 09:12:38, recorded 'started' 09:12:42, shell-after 09:12:42, wall clock 3.8s -- the only field saying WHEN was wrong by the duration of the run. `--publishing` enforced NONE of v6 section 7's conditions, and build_package.py did not even forward the flag to check_commitments.py. (This round was reviewed before v6 was anchored, so some of it was read against a pre-registration still pending.)
>
> - PROOFS ARE PARSED NOW. ots_verify.py walks the OpenTimestamps serialisation and EVALUATES the operation tree, so the attestation's merkle root is computed from the document's own bytes and reported. An earlier draft parsed the structure without evaluating it, and a byte flipped inside an append argument still passed -- the same substring-instead-of-parse defect one level in, caught by testing the module rather than reading it. It refuses the 40-byte forgery, 35 bytes of junk, a digest alone, a REAL Bitcoin-anchored proof over a DIFFERENT document, truncation, and trailing bytes.
> - AND THE REPAIR EXPOSED A WORSE DEFECT, which is this round's real result. Once forgeries were refused, forging v6's proof did not promote anything: v6 simply dropped out of the candidate set and authority FELL BACK TO v5, WHICH PINS FOUR FILES WHERE v6 PINS SIXTEEN, and all four still matched. Exit 0. The attack never beat the proof check -- it beat the SELECTION RULE by deleting the strongest candidate, and a smaller table is not a smaller authority but a different one. Three variants (forge, truncate, append) passed this way and only the deletion variant was caught, by an unrelated path.
> - The fix cannot refuse every unanchored document above the authority, or the project stops: for the hours between stamping a successor and its anchor, a legitimately pending document sits above the version in force -- which is the state v8 is in as this goes out. So anchored() returns a STATE, and PENDING is a value rather than a phrase matched in the reason text; TAMPERED and MISSING above the authority are refused.
> - SIGNATURES ANSWER WHO. Anchoring is free, public and unilateral: anyone with write access can compose a successor, stamp it and wait two hours. check_signature.py verifies a detached signature over every protocol document found by GLOB, parsing gpg's machine-readable status rather than its prose -- 'Good signature' is printed for untrusted keys and exit 0 covers an expired one. It gates publication, not review. A signature alone would be weaker than the pair: signing is as backdatable as stamping, and it is the anchor that fixes it in time.
> - THE PACKAGE SHIPPED CONTROLS THAT COULD NOT PASS INSIDE IT. check_commitments.py imported a module the package did not contain, and test_controls.py died with a FileNotFoundError -- the two files the reproduction call tells a stranger to run -- because every gate ran the checker against the SOURCE tree and nothing ever ran it where a reproducer runs it. The build now derives shipped dependencies from imports, ships the signatures, and RUNS the shipped controls instead of importing them, because importing is not running.
> - v8 section 2c declares the distribution subset and the rule is an EQUALITY -- the absent set must be exactly the pinned set minus the subset -- because 'ignore files that are not there' would make deleting a file the way to avoid its digest being checked.
> - ABSENCE IS NOT AGREEMENT, AT THE PREMISE THIS TIME. Round 4's absences were repaired one at a time inside conditions(); round 5's four were read by the same-input gate ABOVE it, where a.get(k) != b.get(k) is FALSE when neither arm states k. Deleting the field that says the two runs asked the same question made the pair look MORE comparable. Every comparison now routes through one _agree(), and condition 0 is renamed to what it can observe: 'the arms report DIFFERENT CPU identities'.
> - train.py captures provenance BEFORE training -- started_utc was an end time -- and refuses a package binding whose manifest does not list the running pipeline. Weights are unchanged at a4afb5c8 under both pipelines, verified by running both.
> - --publishing enforces v6 section 7 at last: an anchored protocol must govern before EXPECTED.json ships, and a reporting address and an OPEN close date must be recorded. The first version of that gate accepted its own template's 'FILL IN:' placeholder, catching only the date and only because a date must parse. A declared gap is still a gap.
> - THREE MORE HAND-KEPT LISTS OF PROTOCOL DOCUMENTS were removed, in anchor_status.py, build_package.py and this packet builder. v7 had recorded editing one of them as a COST of v6's rule rather than as the enumeration defect it was: fixing instance N by enumerating is how instance N+1 gets made. Attacks 11 -> 30, all refused.
>
> ⚠️ **v7 anchored at Bitcoin block 964856. v8 is STAMPED AND PENDING -- it governs nothing until a calendar anchors it, which is why check_commitments.py and test_controls.py exit non-zero INSIDE the package and the build says so instead of hiding it. v8 is also NOT YET SIGNED, so check_signature.py exits 2, which is a publication-gate failure and deliberately not a review-build failure. v8 was re-stamped several times while being drafted; every superseded proof is retained beside it under a .superseded- name and travels in this packet, and section 11 states the rule it relies on: AUTHORITY ATTACHES AT ANCHORING, NOT AT STAMPING. Nothing may be published until v8 anchors, is signed, and a confirmatory measurement-4 pair is run on both machines under it.**

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
published as  package/ -- 63 files; OUR WEIGHTS ARE NOT IN IT, only the digest
```

## ⚠️ Known-weak, and a reviewer should push here

- **n = 2 machines.** Intel and AMD, matched on OS, Python, numpy and the OpenBLAS build -- and BOTH SELECTED THE SAME OpenBLAS MICROKERNEL (Haswell, X86_V3). So measurement 4 shows two vendors running the SAME REDUCTION SHAPE agree, which is not vendor-independence. A machine selecting a different kernel is a different experiment and has not been run.
- **Measurement 1 was +37% in the previous revision and is +30% now.** The design was at fault, not the machine: fixed order, an "unconstrained" arm that was not a condition, and arrays sorted separately before storage. Ask whether the repaired design has its own faults.
- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS reduction order and capability is explicitly out of scope — but a reviewer may reasonably argue the finding does not transfer to attention kernels or to CUDA, where atomics add a second source of the same phenomenon.
- **Measurement 4 is DESCRIPTIVE, not confirmatory.** Its admissibility conditions were strengthened AFTER its result was known, and it bound itself to no protocol digest. Neither is repairable retroactively. A confirmatory pair needs a fresh run on both machines under the ANCHORED successor, and has not happened -- and train.py's digest moved this round (22cbfeb7 -> f44a74f0) for two recording defects, so the existing pair was produced by a pipeline the current protocol does not pin. The trained weights are identical under both, verified by running both, so no result changes; the RECORD does.
- **Authority is still not EXTERNAL.** The manifest lives in the same directory as the thing it governs; what stops the substitution attack is the anchor and now the signature, not the location. A reviewer asked for CI or signed release metadata to select it. Push on whether an anchor plus a signature by a key WE distribute is enough.
- **⛔ THE `PENDING` BRANCH IS THIS ROUND'S NEW ESCAPE HATCH, and it exists because the obvious strict rule was unusable.** Destroying a higher version's proof is refused now, because falling back to an older document would enforce a SMALLER table. But a document that PARSES, commits to its own bytes and carries only a calendar attestation is allowed to sit above the authority unrefused — otherwise every build would fail for the hours between stamping a successor and its anchor, which is the state v8 is in as this goes out. **That is a convenience rule of exactly the shape the transitional allowance had, and the transitional allowance swallowed an attack last round.** Attack this one.
- **v8 was re-stamped several times while being drafted, and the rule licensing that is stated rather than derived.** §11 says authority attaches at ANCHORING, not at stamping, so a document that has never governed anything may be revised. Every superseded proof is retained under a `.superseded-` name and ships in this packet. Decide whether that is a principled line or a two-hour window in which anything can be quietly rewritten.
- **A signature says a KEY asserted these bytes, and the fingerprint you will check it against comes from us.** `check_signature.py --require` refuses a valid signature by any other key, and prints the fingerprint precisely because this tool cannot establish whose it is. Key distribution is outside the artifact, and the packet does not solve it.
- **`--publishing` now enforces v6 §7's last two conditions, and its first version accepted its own template's placeholder.** `report_to` reading `FILL IN: the URL a reproducer files at...` passed, because the check refused only "", None, TBD and ?; only the close date was caught, and only because a date must PARSE. Look for the same shape elsewhere: a gate that tests the SHAPE of a value rather than the claim it makes.
- **§2c's distribution subset is a new rule with a branch no live input has taken.** It declares which pinned files a reproducer package contains, and the test is an EQUALITY — absent must equal the complement — because a skip would make deletion the way to avoid a digest check. It cannot take effect until v8 anchors, so in THIS package `check_commitments.py` still refuses. The five rule cases in `test_controls.py` are exercised against the declaration rather than the authority, which is honest but is not the same as having run in anger.
- **Measurement 6 is reported NOT MEASURABLE.** Everything else is a digest or a timing a stranger can re-run. That page cannot be checked and says so.
- **The independent reproduction does not exist**, and by section 2b we may not produce one. If nobody answers the call, section 2c pre-registered that silence as a result — a reviewer should decide whether that is a finding or a rationalisation, because it was written before the window opened precisely so that question could be asked.

## ⛔ What the reviewer should NOT accept without pushing

- that a package running on the machine that built it is evidence of anything beyond completeness;
- that the unconstrained runs agreeing three times means unconstrained training is reproducible — they agreed because nothing was contending;
- that about +30% is *the* cost of determinism. It is the cost of pinning to one thread rather than requesting 16, on one configuration, at one size -- and which constraint actually buys identity is a question measurement 4 addresses only for the reduction shape both arms shared; see PHASE-2-FINDINGS section 10.

