# Confirmatory pre-registration, version 2 — 30 August 2026

**Everything done before this document is hereby reclassified as a PILOT.** Its measurements are
reported as pilot evidence and are not the study's result.

⛔ **This is not a rescue.** It is issued because two internal reviewers, independently, found that
the executed study had deviated from version 1 in two ways that cannot be undone by disclosure, and
because the honest response to *"you did not follow your protocol"* is a protocol you can follow —
not a paragraph explaining why the old one still counts.

---

## 1. Why version 1 could not be executed as written

```
§2b  the second party must be secured BEFORE training starts
     -> training ran 30 Aug with no second party secured. Recorded in AMENDMENT-2026-08-30

§6   no change to the corpus after training begins without recording it
     -> the corpus changed 30 Aug: a Project Gutenberg reference survived cleaning in one text
        and had to be removed. Recorded in the same amendment
```

⚠️ **Both were disclosed and neither is repaired by disclosure.** §2b protects against the authors
selecting a reproducer once the result is known; stating that we gave that protection up does not
restore it. So version 1 is retired as a pilot protocol, and this document is what the confirmatory
study runs under.

⇒ **What the pilot bought is real and is kept:** the instrumentation, the failure modes, and the
knowledge of what to measure. A pilot whose purpose is to find out that your measurement design is
wrong has succeeded when it does.

## 2. The order, which is the whole point of this version

```
1  this document is frozen and OpenTimestamped                          <- before anything else
2  the corpus manifest is frozen and TIMESTAMPED                           done: 2006b732...
   ⛔ Bitcoin anchoring PENDING. Do not proceed to step 3 until it is not.
3  the package and the reproduction call are PUBLISHED
4  at least one reproducer COMMITS PUBLICLY, through the open call, before any reference run
5  the reference run is performed and its digest published
6  reproducers run and file reports
7  the window closes on the stated date and everything filed is reported
```

⛔ **Step 4 precedes step 5 and that ordering is the correction.** A reference digest published
before anyone has committed is a target that reproducers self-select against. A commitment made
before the target exists cannot be.

⚠️ **We cannot perform step 4.** It requires a person who is not us, responding to a public call.
If nobody commits, §2c's null outcome applies and is reported — but it is now a null outcome about
a *commitment*, which is a sharper measurement than silence after publication, because committing
costs nothing but attention.

## 3. What is fixed and may not change after this document is anchored

```
corpus        merkle 2006b7327c616f0ca5f9c0b9c3e766b5ebaa2aed99f1433fc66d7560d387452b
              10 texts, 6,312,982 clean bytes, cleaning rule in corpus/build_corpus.py
model         804,096 parameters: 8-byte context, d_emb 64, d_hid 1024, vocab 256
training      seed 20260829, 300 steps, batch 256, lr 0.05, float32
pipeline      train.py, numpy only, no network, thread pin before the numpy import
```

⛔ **Changing any of these after anchoring voids the confirmatory study**, exactly as §6 said and
exactly as happened to version 1. The pilot exists so that this list is now believed to be correct
rather than hoped to be.

## 4. Measurements, restated with the pilot's corrections built in

```
m1  cost of pinning        PAIRED and COUNTERBALANCED: half the blocks threads-1-first, half
                           threads-16-first, seeded order recorded. Both arms explicitly pinned --
                           "unconstrained" is not a condition. Pairs stored IN EXECUTION ORDER.
                           Reported as a ratio with an exact permutation p and a bootstrap
                           interval, to the precision the interval supports
m2  storage overhead       computed by measure_storage.py, with both populations defined by rule
                           and the arguable boundary reported both ways
m3  repeatability          our own runs agreeing is INTERNAL REPEATABILITY. It is not reported as
                           bit-identity, ever, without an independent re-run (§6)
m4  across hardware        the matrix in §5. NOT the same as an independent reproduction
m5  divergence             from per-array, per-step digests (train.py --trace), never from the
                           rounded loss curve. Report the first STEP and the first ARRAY
m6  engineering hours      NOT MEASURABLE under this design and reported as such. The estimand
                           does not exist: the pipeline was deterministic from inception
m7  monotonicity           divergence as a function of thread count, and whether it is monotone.
                           In the pilot it was NOT
```

## 5. ⛔ The hardware matrix, with the condition version 1 omitted

```
A  Intel Core i5-1240P     hybrid 4P+8E, 16 threads, AVX2, no AVX-512
B  AMD Ryzen 9 5900HX      8 homogeneous cores, 16 threads, AVX2, no AVX-512
C  cloud instance          server-class x86, ISA recorded at run time
D  second cloud instance   different provider, ISA recorded at run time
```

⛔ **A vs B is only an isolating comparison if the OS, Python, numpy and the BLAS build are held
constant.** Version 1 omitted that condition, so vendor, operating system, library version and
selected microkernel would all have moved together and the design's one clean contrast would have
been lost. A reviewer's run demonstrated the hazard: different CPU, OS, Python, numpy and OpenBLAS
at once, producing a different digest that cannot be attributed to any of them.

⇒ **Each configuration records, and a run that cannot is inadmissible:** CPU model as the OS
reports it, effective thread count where observable, the selected BLAS kernel, the full build
configuration and its digest, SIMD baseline and found sets, and the Python and numpy versions.
`train.py` enforces this and stops rather than filling blanks.

⚠️ **Where the effective thread count cannot be observed** — `threadpoolctl` absent — that is
recorded as an absence and the run is still admissible, because requiring the dependency would
break the property that a stranger can run this with numpy alone. A request is not a setting, and
the record now distinguishes them.

## 6. What would invalidate THIS pre-registration

- changing the corpus, model or pipeline after this document is anchored
- reporting bit-identity without an independent party's re-run
- performing the reference run before a public commitment exists (§2, step 4)
- reporting a tolerance without quantifying it
- benchmarking the model's capability anywhere in the paper
- any measurement in §4 going unreported because it was inconvenient
- describing any reproducer as independent, or as anything else (§2b of version 1, retained)

**All seven measurements are reported whatever they say.** A measurement omitted is a result.

## 7. What is retained unchanged from version 1

§2b's two binding rules, which were never the problem:

⛔ **WE DO NOT ASSIST.** A reproducer receives the published package and nothing else. Any
assistance is logged and reported, and a run that received it is reported separately.

⛔ **WE DO NOT CHARACTERISE INDEPENDENCE.** The paper reports what was filed and at what public
address. A reader opens the thread and judges. Asserting independence on a reporter's behalf is
asserting the thing the reader should be checking.

And §2c's null outcome, now sharpened to apply at step 4 as well as step 6.

---

⚠️ **Status at signing: the pilot is complete, the corpus is frozen and TIMESTAMPED, and nothing
has been published.**

⛔ **NOT ANCHORED. Both active proofs -- this document's and the corpus manifest's -- carry
calendar attestations only.** The sole Bitcoin attestations in this study belong to the SUPERSEDED
corpus proof and the RETIRED v1 pre-registration, so the pilot currently has a stronger guarantee
than the protocol replacing it. Both round-2 reviewers found this while three documents said
'anchored'. `anchor_status.py` decides the question by reading the proof bytes; the prose follows it. No reproducer has been approached. No confirmatory reference run exists.

**NOT a product, and not a recommendation.**
