# Paper B (`reproduction`) — internal review packet, round 14

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     193 files
  sha256 b667f1aec1228a21204613007910fa8d7d6d88b73e177c94915b3bc67f55e8f3
this file
```

Repository `provenance-laboratory/reproduction`, commit `24af028`.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 14.** THE NEXT ORDINARY PROTOCOL ROUND WOULD HAVE BROKEN THE SHIPPING BUILD. `build_package.py` unpacked four fields from a five-field rejection, so the first legitimate PENDING successor crashed it with ValueError -- a reviewer found it by minting a synthetic v10, and nothing would have said so until it happened. NO-TABLE inferred 'is this a table' from a COUNT of raw digests, and one integer cannot carry two questions: a real three-row table in an unreadable layout escaped the threshold and was silently skipped, while a document quoting four digests in prose with no table at all was fatally rejected -- the v2/v4 shape refused by the fix for refusing the v2/v4 shape. `tree_digest` excluded caches by SUBSTRING, so any path merely containing `__pycache__` was invisible to the digest that certifies 'the verdict describes this tree'. And a reviewer objected that settling authority by live re-fetch moves the trust root from a file you write to a block explorer you query.
>
> - R
> - e
> - j
> - e
> - c
> - t
> - i
> - o
> - n
> - s
> -  
> - a
> - r
> - e
> -  
> - a
> -  
> - N
> - A
> - M
> - E
> - D
> -  
> - r
> - e
> - c
> - o
> - r
> - d
> - ,
> -  
> - s
> - o
> -  
> - w
> - i
> - d
> - e
> - n
> - i
> - n
> - g
> -  
> - o
> - n
> - e
> -  
> - c
> - a
> - n
> - n
> - o
> - t
> -  
> - s
> - i
> - l
> - e
> - n
> - t
> - l
> - y
> -  
> - b
> - r
> - e
> - a
> - k
> -  
> - a
> -  
> - c
> - a
> - l
> - l
> - e
> - r
> - ,
> -  
> - a
> - n
> - d
> -  
> - a
> -  
> - f
> - i
> - x
> - t
> - u
> - r
> - e
> -  
> - d
> - r
> - i
> - v
> - e
> - s
> -  
> - t
> - h
> - e
> -  
> - e
> - x
> - a
> - c
> - t
> -  
> - l
> - o
> - o
> - p
> -  
> - t
> - h
> - a
> - t
> -  
> - c
> - r
> - a
> - s
> - h
> - e
> - d
> - .
> -  
> - T
> - a
> - b
> - l
> - e
> - s
> -  
> - a
> - r
> - e
> -  
> - d
> - e
> - t
> - e
> - c
> - t
> - e
> - d
> -  
> - S
> - T
> - R
> - U
> - C
> - T
> - U
> - R
> - A
> - L
> - L
> - Y
> -  
> - -
> - -
> -  
> - a
> -  
> - p
> - a
> - t
> - h
> -  
> - b
> - e
> - s
> - i
> - d
> - e
> -  
> - a
> -  
> - d
> - i
> - g
> - e
> - s
> - t
> -  
> - i
> - n
> -  
> - t
> - a
> - b
> - l
> - e
> -  
> - s
> - h
> - a
> - p
> - e
> -  
> - -
> - -
> -  
> - s
> - o
> -  
> - a
> -  
> - t
> - h
> - r
> - e
> - e
> - -
> - r
> - o
> - w
> -  
> - t
> - a
> - b
> - l
> - e
> -  
> - i
> - s
> -  
> - a
> -  
> - t
> - a
> - b
> - l
> - e
> -  
> - a
> - n
> - d
> -  
> - p
> - r
> - o
> - s
> - e
> -  
> - i
> - s
> -  
> - n
> - o
> - t
> - ,
> -  
> - h
> - o
> - w
> - e
> - v
> - e
> - r
> -  
> - m
> - a
> - n
> - y
> -  
> - d
> - i
> - g
> - e
> - s
> - t
> - s
> -  
> - i
> - t
> -  
> - q
> - u
> - o
> - t
> - e
> - s
> - ;
> -  
> - u
> - p
> - p
> - e
> - r
> - c
> - a
> - s
> - e
> -  
> - d
> - i
> - g
> - e
> - s
> - t
> - s
> -  
> - p
> - a
> - r
> - s
> - e
> - ,
> -  
> - b
> - e
> - c
> - a
> - u
> - s
> - e
> -  
> - h
> - e
> - x
> -  
> - i
> - s
> -  
> - c
> - a
> - s
> - e
> - -
> - i
> - n
> - s
> - e
> - n
> - s
> - i
> - t
> - i
> - v
> - e
> - .
> -  
> - T
> - h
> - e
> -  
> - c
> - a
> - c
> - h
> - e
> -  
> - e
> - x
> - c
> - l
> - u
> - s
> - i
> - o
> - n
> -  
> - i
> - s
> -  
> - a
> -  
> - p
> - a
> - t
> - h
> -  
> - C
> - O
> - M
> - P
> - O
> - N
> - E
> - N
> - T
> - ,
> -  
> - w
> - i
> - t
> - h
> -  
> - f
> - i
> - x
> - t
> - u
> - r
> - e
> - s
> -  
> - t
> - h
> - a
> - t
> -  
> - p
> - l
> - a
> - n
> - t
> -  
> - a
> -  
> - d
> - e
> - c
> - o
> - y
> -  
> - a
> - n
> - d
> -  
> - a
> - s
> - s
> - e
> - r
> - t
> -  
> - t
> - h
> - e
> -  
> - d
> - i
> - g
> - e
> - s
> - t
> -  
> - m
> - o
> - v
> - e
> - s
> - .
> -  
> - `
> - p
> - i
> - n
> - _
> - a
> - n
> - c
> - h
> - o
> - r
> - s
> - .
> - p
> - y
> - `
> -  
> - r
> - e
> - q
> - u
> - i
> - r
> - e
> - s
> -  
> - a
> - g
> - r
> - e
> - e
> - m
> - e
> - n
> - t
> -  
> - b
> - e
> - t
> - w
> - e
> - e
> - n
> -  
> - a
> - t
> -  
> - l
> - e
> - a
> - s
> - t
> -  
> - t
> - w
> - o
> -  
> - i
> - n
> - d
> - e
> - p
> - e
> - n
> - d
> - e
> - n
> - t
> -  
> - o
> - p
> - e
> - r
> - a
> - t
> - o
> - r
> - s
> -  
> - o
> - n
> -  
> - b
> - o
> - t
> - h
> -  
> - h
> - a
> - s
> - h
> -  
> - a
> - n
> - d
> -  
> - m
> - e
> - r
> - k
> - l
> - e
> -  
> - r
> - o
> - o
> - t
> - ,
> -  
> - r
> - e
> - c
> - o
> - r
> - d
> - s
> -  
> - w
> - h
> - i
> - c
> - h
> -  
> - a
> - g
> - r
> - e
> - e
> - d
> - ,
> -  
> - a
> - n
> - d
> -  
> - R
> - E
> - F
> - U
> - S
> - E
> - S
> -  
> - o
> - n
> -  
> - d
> - i
> - s
> - a
> - g
> - r
> - e
> - e
> - m
> - e
> - n
> - t
> -  
> - r
> - a
> - t
> - h
> - e
> - r
> -  
> - t
> - h
> - a
> - n
> -  
> - t
> - a
> - k
> - i
> - n
> - g
> -  
> - a
> -  
> - m
> - a
> - j
> - o
> - r
> - i
> - t
> - y
> -  
> - -
> - -
> -  
> - t
> - w
> - o
> -  
> - o
> - f
> -  
> - t
> - h
> - e
> -  
> - t
> - h
> - r
> - e
> - e
> -  
> - s
> - h
> - a
> - r
> - e
> -  
> - t
> - h
> - e
> -  
> - E
> - s
> - p
> - l
> - o
> - r
> - a
> -  
> - c
> - o
> - d
> - e
> - b
> - a
> - s
> - e
> -  
> - a
> - n
> - d
> -  
> - o
> - n
> - e
> -  
> - d
> - o
> - e
> - s
> -  
> - n
> - o
> - t
> - ,
> -  
> - a
> - n
> - d
> -  
> - t
> - h
> - e
> -  
> - r
> - e
> - c
> - o
> - r
> - d
> -  
> - s
> - a
> - y
> - s
> -  
> - s
> - o
> - .
> -  
> - T
> - h
> - e
> -  
> - f
> - i
> - x
> - t
> - u
> - r
> - e
> - s
> -  
> - s
> - h
> - i
> - p
> -  
> - a
> - n
> - d
> -  
> - r
> - u
> - n
> -  
> - i
> - n
> -  
> - t
> - h
> - e
> -  
> - s
> - u
> - i
> - t
> - e
> - :
> -  
> - t
> - h
> - e
> -  
> - p
> - r
> - e
> - v
> - i
> - o
> - u
> - s
> -  
> - r
> - o
> - u
> - n
> - d
> - '
> - s
> -  
> - '
> - 8
> -  
> - f
> - i
> - x
> - t
> - u
> - r
> - e
> - s
> -  
> - /
> -  
> - 0
> -  
> - f
> - i
> - n
> - d
> - i
> - n
> - g
> - s
> - '
> -  
> - r
> - e
> - s
> - t
> - e
> - d
> -  
> - o
> - n
> -  
> - f
> - i
> - x
> - t
> - u
> - r
> - e
> - s
> -  
> - t
> - h
> - a
> - t
> -  
> - w
> - e
> - r
> - e
> -  
> - n
> - o
> - t
> -  
> - i
> - n
> -  
> - t
> - h
> - e
> -  
> - a
> - r
> - c
> - h
> - i
> - v
> - e
> - ,
> -  
> - a
> - n
> - d
> -  
> - t
> - h
> - e
> -  
> - r
> - e
> - v
> - i
> - e
> - w
> - e
> - r
> -  
> - w
> - a
> - s
> -  
> - t
> - h
> - e
> -  
> - f
> - i
> - r
> - s
> - t
> -  
> - p
> - e
> - r
> - s
> - o
> - n
> -  
> - e
> - v
> - e
> - r
> -  
> - t
> - o
> -  
> - p
> - a
> - s
> - s
> -  
> - `
> - w
> - h
> - e
> - r
> - e
> - =
> - `
> - .
>
> ⚠️ **v10 IS ANCHORED IN BITCOIN BLOCKS 965332 AND 965333 and governs, composed over seven anchored versions. It retires ANCHORS.json from the byte-pinned table and commits it as MONOTONIC ANCHOR FACTS instead: each height must keep its merkle root, growth is permitted. That resolves a circularity nobody could have fixed by care -- anchoring a version rewrites the file that version pins, so every version since v8 was void in that entry from the moment it took effect. v10's own anchoring added two heights and broke nothing, which is the property the digest could never have. Anchoring it also exposed `_retirement_is_permitted` reading anchor facts from a `text` parameter its only caller passed as the empty string: v10 declares 21 facts and was refused for declaring none, and it surfaced only when the retirement path first ran. v11 pins the corrected checker and is signed and PENDING; v10 governs until a calendar anchors it.**

## ⭐ CHECK THE FINDINGS, NOT ONLY THE PACKAGING

```
python reproduce_findings.py     up to five training runs, nothing timed
```

**Runtime spans an order of magnitude, and that is the finding rather than a caveat.** Measured between 26 s and over 180 s on reviewers' machines: a single-core host collapses all five thread requests into one run, a many-core host executes five. The script prints progress per run so a long one is visibly working rather than apparently hung. Do not treat any duration here as a timing measurement -- **nothing in this experiment is timed**, and the cost figures come from `measure_cost.py` under its own quiet-machine precondition.

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

