# Paper B (`reproduction`) — internal review packet, round 14

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     194 files
  sha256 813c8ba06ea52e5b3273c26bf857030aa7ff6f9c7dc1ea032b51d8c0fa63e792
this file
```

Repository `provenance-laboratory/reproduction`, commit `6964564`.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 14.** THE NEXT ORDINARY PROTOCOL ROUND WOULD HAVE BROKEN THE SHIPPING BUILD. `build_package.py` unpacked four fields from a five-field rejection, so the first legitimate PENDING successor crashed it with ValueError -- a reviewer found it by minting a synthetic v10, and nothing would have said so until it happened. NO-TABLE inferred 'is this a table' from a COUNT of raw digests, and one integer cannot carry two questions: a real three-row table in an unreadable layout escaped the threshold and was silently skipped, while a document quoting four digests in prose with no table at all was fatally rejected -- the v2/v4 shape refused by the fix for refusing the v2/v4 shape. `tree_digest` excluded caches by SUBSTRING, so any path merely containing `__pycache__` was invisible to the digest that certifies 'the verdict describes this tree'. And a reviewer objected that settling authority by live re-fetch moves the trust root from a file you write to a block explorer you query.
>
> - Rejections are a NAMED record, so widening one cannot silently break a caller -- and the two comprehensions inside `governing()` that still unpacked five positionally are converted too. Both round-14 reviewers found those by adding a sixth field: the previous round's claim was true of every caller except the module that defines the record.
> - AN ANCHOR FACT CAN NO LONGER LIE BY REPEATING A HEIGHT. `anchor_facts()` collapsed its block into a dict, so a document could commit one height twice and the second line silently replaced the first -- monotonic in shape, a lie in substance. A repeated height is refused before any collapse, and two anchored versions committing different roots for one height is refused as well: the chain has one answer, so a contradiction means the tree is broken.
> - Tables are detected structurally, and the detector and the parser now agree about the tail of a line. `_ROW` ended at a word boundary and `DIGEST_LINE` at end-of-line, so a fenced block whose rows carry trailing annotations was SEEN as four rows and PARSED as zero -- which lands in NO-TABLE and exits. A legitimate document annotating its own examples was refused outright. Backticked cells, colon separators and digest-first columns are recognised as tables too, so a layout a human reads as a table is a loud NO-TABLE rather than a silent skip.
> - `tree_digest` excludes caches by path COMPONENT, not by substring: any path merely containing `__pycache__` was invisible to the digest that certifies 'the verdict describes this tree'. Fixtures plant a decoy and assert the digest moves.
> - `pin_anchors.py` requires agreement between independent operators on both hash and merkle root, records which agreed, and REFUSES on disagreement rather than taking a majority.
> - The fixtures ship and run in the suite. The previous round's '8 fixtures / 0 findings' rested on fixtures that were not in the archive, and the reviewer was the first person ever to pass `where=`.
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

