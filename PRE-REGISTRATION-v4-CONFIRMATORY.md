# Pre-registration v4 — the hardware comparison, made isolating before it is run

⛔ **v3 governs everything except measurement 4.** This version changes exactly one thing, adds
nothing else, and exists because measurement 4 has not been run yet. Every other section of v3
stands unaltered and is not restated here; where this document is silent, v3 is the protocol.

⚠️ **Why this is a pre-registration and not a revision.** Measurement 4 has **no data**. No
second-machine run exists, none has been attempted under this protocol, and the two runs that do
exist are disclaimed in `PHASE-2-FINDINGS.md` as early, confounded and predating the corpus
correction. A condition added to an unmeasured measurement is a commitment. The same words added
after a result would be an excuse, and the difference is the timestamp on this file — which is why
it is stamped and anchored before the run rather than described in a commit message.

## 1. The defect in v3

v3 §5 carries measurement 4 forward from v2 as *bit-identity across hardware*: configuration A
against configuration B, an Intel machine against an AMD one, asking whether the same pipeline on
the same corpus produces the same bytes.

⛔ **As specified, that comparison cannot isolate anything.** In the runs available, CPU vendor,
operating system, Python version, numpy version and the OpenBLAS build all differ **at once**. A
difference in the output bytes is then attributable to any of five things, and the measurement was
designed to attribute it to one. `PHASE-2-FINDINGS.md` states this and says the condition "has to
be added to §2a before measurement 4 is run". It was never added. This document adds it.

⚠️ **v3 already contains the principle and did not apply it here.** §4 refuses to credit a run for
*kernel or thread causal attribution* unless it observed the runtime BLAS architecture and the
effective thread count — because an unobserved variable cannot carry a causal claim. Vendor is the
same kind of variable, and measurement 4 is the same kind of claim.

## 2. What is added to admissibility

A run is **admissible for VENDOR causal attribution** — that is, for measurement 4's comparison of
configuration A against configuration B — only if, in addition to v3 §4's requirements:

```
1  the operating system family and major version are recorded and MATCH the other arm
2  the Python version is recorded and MATCHES the other arm to major.minor
3  the numpy version is recorded and MATCHES the other arm exactly
4  the OpenBLAS build-configuration line is recorded and MATCHES the other arm,
   or both arms record its absence for the same stated reason
5  the runtime BLAS architecture and effective thread count are OBSERVED in both arms
   (v3 §4 already requires this for kernel and thread claims; it is restated because
   measurement 4 cannot be read without it)
```

⇒ **A pair of runs failing any of 1–5 is still reported.** It is reported as a
**CONFOUNDED** comparison, naming every variable that moved, and it may not be cited for a claim
about CPU vendor. This mirrors v3 §4 exactly: the absence of an observation is recorded, never
fatal, and never silently upgraded into a result.

⛔ **`train.py` is not changed by this, and every input to conditions 1–5 is already
recorded.** It writes CPU model, `platform.platform()` — which carries the operating system family
and version — the Python and numpy versions, the SIMD baseline, `blas_build_config_line` and,
where observable, `blas_runtime_arch`. What does not exist is the **comparison step**: nothing
reads two runs, checks 1–5 against each other and applies the label. That is an addition to the
*reporting*, not to the pipeline, so **no committed digest in v3 §2 changes** — which v3 §6 makes
the condition for this pre-registration surviving at all.

⚠️ **Two drafts of this section were corrected before it was anchored, and both proofs are
retained beside this file rather than deleted.** The first said the operating system was not
recorded; it is, by `platform.platform()`, and the claim was withdrawn by reading `train.py`
instead of trusting the sentence (`.ots.superseded-os-claim`). The second asked only that the
operating system be *recorded*, which would have let the two arms run different systems and still
be called isolating — the exact confound this document exists to remove, left in condition 1 while
conditions 2, 3 and 4 all required a match (`.ots.superseded-os-recorded-only`). A retired proof is
part of the record; deleting it would hide that the correction happened.

## 3. What would invalidate this version

In addition to everything in v3 §6:

- reporting measurement 4 as a vendor comparison when conditions 1–5 were not met
- adjusting conditions 1–5 after seeing either arm's output
- reporting only one arm

⚠️ **And the honest limitation, stated now rather than discovered later.** If both arms are held to
1–5 and the bytes still differ, that isolates *vendor* only among the variables listed. Microcode,
BIOS settings, kernel scheduling and CPU feature availability beyond the recorded SIMD baseline are
not held constant and are not observed. Measurement 4 answers *"do these two machines, matched on
software, produce the same bytes"*. It does not answer *"is CPU vendor the cause"*, and this
document does not let it be written as though it did.

## 4. Retained unchanged

Everything in v3, including its §2 commitments by digest, its §3 publication order, its §4
admissibility rules, its §5 measurements 1, 2, 3, 5, 6 and 7, and its §7. This document supersedes
v3 **only** on the admissibility of measurement 4.

⇒ **All seven measurements are reported whatever they say.**

---

*Governs: measurement 4 only · Governed by: [`PRE-REGISTRATION-v3-CONFIRMATORY.md`](PRE-REGISTRATION-v3-CONFIRMATORY.md) in every other respect · Status: see `ANCHOR-STATUS.txt`*
