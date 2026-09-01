# Paper B (`reproduction`) — internal review packet, round 8

*Every figure below is read from the measurement files, and every claim is lifted from `PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a figure it prints is absent from that document.*

## ⇒ SEND THESE TWO

```
paper-b-review.zip     182 files
  sha256 de69606ec0ea90217c3467909cf4b45c37178dd2e44770a3cec69948a6443b26
this file
```

Repository `provenance-laboratory/reproduction`, commit `1dbca0c`.

---

## ★ THE COVERING NOTE — paste this verbatim

> **This is round 8.** BOTH REVIEWERS BROKE THE ANCHOR FILE, IN OPPOSITE DIRECTIONS, AND BOTH WERE RIGHT. Round 6 moved the trust root from 'the shape of a proof', which two reviewers had forged, to 'a JSON file we wrote' -- and one reviewer edited that file to bless a synthetic v9, then had v9 RETIRE the very file that had blessed it, reaching exit 0 with all 21 pins matching. The other made ONE ADDITIVE CHANGE -- a fabricated block, nothing else -- and everything stayed green, because rewriting a real root breaks a real proof and everything goes red, while ADDING a block breaks nothing: every existing verification still succeeds. The file was protected against damage and unprotected against extension, which is the direction an attacker uses, and ZERO of thirty control cases touched it. Chained, that is a fabricated block, a short proof naming it, and a version retiring `train.py`. AND v9 WAS INERT: `compose()` is a monotone union, so a version whose only content is an ABSENCE removes nothing -- one reviewer forged v9's anchoring to reach the state the project was waiting for and found the pin still there, still mismatched, exit 1. `pin_anchors.py` also globbed a FILENAME PATTERN in place of 'every proof this artifact requires', so it pinned 15 blocks where the required proofs name 18: the missing one was the corpus manifest's timestamp, the document v3 section 2's non-retrofit argument rests on, which the new rule had therefore made indistinguishable from a fabrication. `anchor_status.py` CRASHED on that input -- one return path gave two values where the caller unpacks three, and it was the tampering path. And `build_package.py` crashed on an untouched tree.
>
> - THE RETIREMENT WAS THE WRONG DIRECTION AND v9 NO LONGER DOES IT. Retiring the anchor file converts a line carrying no information into no line at all and leaves the file that decides what ANCHORED means as the only unchecked input. It stays pinned. A version may not retire the anchor file that authenticated it, nor any experimental input -- `train.py`, the corpus -- refused BY NAME, because 'this file stopped being checked' can never be legitimate for those, and the old guard checked only that a retirement was well-formed, never that it was warranted.
> - THE PINNED SET MUST EQUAL WHAT THE PROOFS NAME, not merely contain it -- the same equality-not-skip rule this project already applies to distribution subsets, missing here. Checked OFFLINE inside `check_commitments.py`, so an addition cannot be silent, and the control suite has a case for it where it had none.
> - `pin_anchors.py` projects over every proof beside a file it binds plus the required list, so the corpus timestamp is ANCHORED again; every return path in `anchor_status.py` yields a verdict and names its real cause, rather than labelling a structural refusal as a proof that does not bind its document, which was false.
> - `build_package.py` runs `verify_package.py` against the bytes it just wrote. Round 6 added RUNNING the shipped controls and no gate that the shipped TREE is clean, so the package went on carrying unlisted bytecode and a SHA256SUMS disagreeing with its own proof -- both found again this round, both on the reproducer's side of the boundary, both surviving a round that fixed the source-tree half.
> - AND THE CRASH WAS MINE, IN THE FIX. Adding `PUBKEY.asc` put the filename inside the neighbouring tuple, making three elements where every consumer unpacks two, and I did not notice because the REVIEW PACKET built fine. A different tool passing is not this tool passing.
>
> ⚠️ **THE CIRCULARITY IS NOT CLOSED AND v9 SECTION 14 SAYS SO RATHER THAN CLAIMING OTHERWISE. Offline, ANCHORED remains a statement about a file we wrote, whose own caveat says a pin is an explorer's word and not a node -- and `ots_verify.py` then makes that word decisive. What is closed is the chained escalation and the addition direction. The two candidate designs are NAMED rather than chosen: stop making the file decisive, reporting height and computed root as data for a reader to settle against a chain; or anchor the file itself, accepting that this is a one-step bootstrap and not a fixed point. A known consequence is stated too: each time a version anchors, its blocks join the pinned file, so that file's digest goes stale until the next version re-pins it. v9 is stamped, signed and PENDING; until it anchors v8 governs, seven pins mismatch, all reported and counted, and the reproducer package cannot be rebuilt because its gate correctly refuses.**

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

