# Paper B (`reproduction`) — internal review packet, round 12

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     187 files
  sha256 074b51f0699c138dc1679573541775380d590988c6fb54811c4ca87569f5f19b
this file
```

Repository `provenance-laboratory/reproduction`, commit `b7af331`  ⚠️ TREE DIRTY.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 12.** BOTH REVIEWERS INDEPENDENTLY DEFEATED THE UNDEFINED-NAME CONTROL WITH FOUR LINES -- `if False: REPORT_NAME = ...` binds the name for symtable and not at runtime, so the suite printed 'ok' over a function that raises NameError when called. The correction for exactly that evasion had been written in the sibling project's stress_test.py a day earlier and never carried across. A fix is not finished until you grep for the other call sites; that is the fifth time this project has recorded that sentence and the first time it has cost an evasion in the layer under review. Both reviewers also showed that the round-10 relabel repair REPORTED and did not REFUSE, and that the structured verdict introduced in round 10 was not bound to the run that produced it.
>
> - RETRACTED, from round 10's own record and from the round-11 packet: 'v9 IS NOW SIGNED AND ANCHORED' is too strong for the shipped artifact. v9 is SIGNED, and its OpenTimestamps proof carries Bitcoin attestations in blocks 965140, 965142 and 965152 whose merkle roots were checked against the live chain -- but the artifact's OWN offline verifier reports STRUCTURAL only, because those blocks are not pinned in ANCHORS.json. A claim that is true of the world and false of the shipped verifier must be stated as the second. Both reviewers reached this independently and both were right.
> - The undefined-name control is now PORTED from the census implementation rather than reimplemented, because two copies of one rule is how the evasion survived here after the other copy was fixed. It detects three shapes -- undefined, shadowed by a later local, and bound only inside a conditional -- and the reviewers' exact four-line evasion is caught by name: 'binds only inside a conditional, it may not exist when this line runs'.
> - A relabelled document carrying a commitment table is now FATAL rather than reported. Not letting it govern is not the same as refusing it, and a tree containing a document presenting itself as a higher authority is not a clean tree. Scoped to candidates that carry a table, so a stray version-shaped filename does not fail a build. Verified against an isolated green fixture: the round-10 two-cp attack now exits 1.
> - THAT FIX IMMEDIATELY FOUND A DEFECT ROUND 10 HAD INTRODUCED. `declared_version` knew one title form and the corpus has two: v2 and v3 are headed 'Confirmatory pre-registration, version N' rather than 'Pre-registration vN', so both returned None and -- since round 10 made an unversioned candidate a rejection -- two legitimate historical documents had silently stopped contributing to the composed table. Nobody noticed because they are superseded and their pins are subsets of later ones. Making the refusal fatal is what surfaced it. Both title forms are read out of the H1 now.
> - The control-suite verdict is bound to its run. The gate issues a nonce in the environment, DELETES any existing verdict before running the suite, and refuses a verdict that does not carry this run's nonce; the verdict also records a digest of the tree it examined. A reviewer pre-wrote a green verdict, crashed the suite before its own write, and the gate consumed the stale one -- the round-10 substring forgery closed and replaced by a fresher instance of the same disease, a decision read from an artifact not bound to what produced it.
>
> ⚠️ **The ANCHORS.json circularity remains the one open item and a reviewer sharpened WHY it must be closed rather than named: ots_verify returns STRUCTURAL for v9's honest not-yet-pinned blocks and for round 6's fabricated block 999999 IDENTICALLY. The tool cannot distinguish them, so the 'circularity' label is a human assertion that this instance of that verdict is the benign one -- which is the judgement the mechanism was supposed to make. The adjudicated v10 design closes it for the right reason, and the live re-fetch must compare the block's real MERKLE ROOT to the computed root; a height check alone is the same trap with a network call attached. Two further items stand: v9 does not pin the current gate bytes, so a new anchored version is needed rather than waiting; and the publishing-precondition surface is downstream of the circularity and has therefore never executed against a live tree.**

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
published as  package/ -- 64 files; OUR WEIGHTS ARE NOT IN IT, only the digest
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

