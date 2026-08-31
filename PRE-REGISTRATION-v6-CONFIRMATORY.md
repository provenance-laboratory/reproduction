# Pre-registration v6 — the instruments and the gates are committed too

⛔ **v3 governs, v4 amends measurement 4's admissibility, and this version replaces v5 §3 and
strengthens v4 §2.** Where this document is silent, v3 governs.

## 1. What round 4 found, in one sentence

> *The project binds the experimental inputs, but not the authority selector, the measurement
> instruments, the gates, or the evidence those instruments consume.*

Two reviewers reached that independently, and one gave the mechanical test that produces it: **for
every check, construct the input where the thing it names is absent, and see whether it passes.**
Nine attacks were built that way and all nine succeeded. Four of the nine were absences.

⇒ The defect did not recur. **It moved one layer outward.** v5 committed `train.py` and the corpus
and left every tool that reads them, judges them, and publishes them unpinned — so a change that
neuters a checker was blessed by a freshly generated `SHA256SUMS`, exactly as the original
`train.py` substitution had been.

## 2. ⛔ What is committed, by DIGEST — replacing v5 §3

### 2a. Experimental inputs

```
train.py                   22cbfeb7208c5471d0bbae89ca7da138fe55de009fd28a945c030200ade18787
corpus/MANIFEST.json       fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py     2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json        7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30

corpus merkle  2006b7327c616f0ca5f9c0b9c3e766b5ebaa2aed99f1433fc66d7560d387452b
model          804,096 parameters: 8-byte context, d_emb 64, d_hid 1024, vocab 256
training       seed 20260829, 300 steps, batch 256, lr 0.05, float32
sampling       start positions drawn uniformly from [0, len(corpus) - CONTEXT)
```

⚠️ **`train.py` moves from `1231a42a` for one reason: it now records what produced a run.** The
computation is untouched and the reference artifact is unchanged — `a4afb5c8…`, verified by running
it. §4 says what the new record contains and why the old one made a claim nobody could check.

### 2b. Instruments and gates — new in this version

```
check_commitments.py       2089c5bd7322717ca0e587ba3c23690fefd1c8dbf8f065496500e25949b7e638
anchor_status.py           b70e71f5c352eff2402a1fde5876eb449fef4ac74c9e6b2457275e47f5b8aa9b
measure_hardware.py        369f987e25d95f8df95928015574cf5898697354530ba963ab22860b780acc24
measure_cost.py            4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py      d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_storage.py         1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
seed_sensitivity.py        1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
build_package.py           42de74dc7dc3a79dd394f7d0f9c5d6cfd1e1997f02a80ec6835c15e5a617e3be
verify_package.py          bf88fd51fe247bebcd6769645eeb570f6381983decdd5867a94c04a4a5a6c87d
test_controls.py           1ab67173fc5f84b043fc7dfae955813f15bdf31b73a259de28b66652e28dfb50
corpus/verify_shipped.py   943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
reproduce_findings.py      78d570f5df51245e5d9a9b2ddeb75ef5e22cda283a06e64383ca383b80827bbf
```

⇒ **An instrument that can change silently after data exists is not an instrument, it is an
opinion with a filename.** These are held to the same rule as the inputs: a change moves the digest
and requires a new version.

⚠️ **And the cost is real, so it is stated rather than discovered.** Every repair to a checker now
requires a new anchored version. That is deliberate — round 4 exists because a checker was repaired
between rounds and nothing recorded which one produced which result — and it will make this project
slower. If that becomes an excuse for not repairing a checker, the rule has failed and should be
reported as failing, not quietly relaxed.

⛔ **A TRANSITIONAL ALLOWANCE WAS ADDED AND IMMEDIATELY SWALLOWED AN ATTACK.** A freshly
stamped version waits hours for its Bitcoin attestation, and refusing every build in the meantime
is a rule people work around — so a file matching the *pending* version rather than the anchored
one is reported as a transition instead of a violation. The control suite caught the consequence
within a minute: **deleting the anchored document's proof** dropped authority to an older version,
whereupon the pending version vouched for the changed file and the check passed. An escape hatch
that opens when the thing it trusts is *removed* is this round's own defect, committed inside the
fix for it. The allowance is now disabled by **any** protocol document lacking a binding proof.

## 3. Authority is not discovered from a directory

⛔ **`check_commitments.py` selected the highest-numbered protocol file on disk. That is not an
authority rule.** A reviewer minted an unanchored `v6`, and authority silently moved to it; another
edited `train.py` and its digest inside v5, and the check passed. Both worked because the table was
read out of a mutable file sitting beside the thing it governs.

A digest table is authority **only if the document carrying it is anchored**: its proof exists,
binds its current bytes, and carries a Bitcoin attestation. An unanchored document that carries a
digest table is a **refusal**, never a fallback — falling back to an older table would hide both a
mid-round draft and a substitution behind the same silence.

⚠️ **This is not yet external.** The manifest still lives in the same directory as the thing it
governs; what stops the attack is the anchor, not the location. A reviewer asked for authority to
be selected from outside — CI configuration, signed release metadata, or a digest given on the
command line. That remains open and is named here so it is not mistaken for solved.

## 4. A run binds itself to what produced it

⛔ **`run.json` recorded what a run produced and never what produced it** — no pipeline digest, no
protocol digest, no time. So *"this was measured under the committed pipeline, after the protocol
was anchored"* rested entirely on operator testimony, which is the kind of claim this project
refuses everywhere else.

Every run now records:

```
provenance.pipeline_sha256      the digest of train.py as it ran
provenance.protocols{}          every protocol document present, its digest, whether its proof
                                binds it, and whether that proof carries a Bitcoin attestation
provenance.package_sha256sums   the shipped package's SHA256SUMS digest, when one exists
provenance.started_utc          the machine's clock, SELF-REPORTED
```

⚠️ **The timestamp is the weak half and is labelled so in the record itself.** A self-reported clock
is worth what the machine is worth. It is recorded because an absent time cannot be checked at all,
while a present one can be compared against an anchor and found impossible. **The digests are the
load-bearing half.**

## 5. Measurement 4's admissibility — replacing v4 §2

A pair is admissible for a cross-machine claim only if **all** hold:

```
0  the two arms are DIFFERENT machines, by recorded CPU
1  operating system family and major version recorded and MATCHING
2  Python recorded and matching to major.minor
3  numpy recorded and matching exactly
4  BLAS identity -- library, version AND build line -- recorded and matching.
   Two ABSENT build lines are not a match
5  runtime microkernel OBSERVED IN BOTH AND IDENTICAL
6  effective BLAS thread count OBSERVED IN BOTH AND EQUAL, as a number
7  both arms run the confirmatory specification
8  both weights artifacts present, and the reported digest RECOMPUTED from each
```

⛔ **Conditions 0, 4, 5, 6, 7 and 8 exist because the previous version accepted their violation.**
The reviewers obtained the old `ISOLATING` verdict from: the same run record as both arms; identical
CPUs; Haswell against SkylakeX; one effective thread against eight; two absent build lines; two
non-confirmatory runs; and an arm whose artifact had been deleted, which also reported
`BIT-IDENTICAL: YES`. Every one was satisfied by the **presence or absence** of a field rather than
its **value**.

⇒ **The verdict is `MATCHED-STACK CROSS-MACHINE`, not `ISOLATING`.** It isolates nothing: microcode,
firmware and kernel scheduling differ between any two machines and are unobserved. And a pair
failing only condition 4 through an unreadable build line reports **`RECORDING-SCHEMA
INADMISSIBLE`**, because an extractor that could not read evidence which was present is not the
same event as a variable that moved.

## 6. ⛔ The existing measurement-4 pair is reclassified as DESCRIPTIVE

The Intel/AMD pair reported in `PHASE-2-FINDINGS.md` §10 meets every condition above. It was
nonetheless taken **before this version existed**, under a `run.json` that bound itself to no
pipeline or protocol, and its admissibility rules were strengthened *after* its result was known.

⇒ **It cannot be made confirmatory retroactively, and is not.** It is retained as descriptive
evidence and as the record of how the conditions were found to be insufficient. A confirmatory
measurement 4 requires a fresh pair under this version, on both machines.

⚠️ Under v5 §5 the invalidating condition — *reporting a measurement taken under a pipeline whose
digest was not committed at the time* — applies to the **first, discarded attempt**. The second
pair ran after v4 and v5 were anchored. The artifacts cannot demonstrate that, which is why §4
exists and why this section does not lean on it.

## 7. What would invalidate this version

In addition to v3 §6 and v4 §3:

- any file in §2a **or §2b** changing its digest
- selecting authority from an unanchored document
- reporting a cross-machine claim from a pair that fails any condition in §5
- reporting the §6 pair as confirmatory
- publishing with `--with-target` without a recorded public commitment
- publishing without a recorded address and close date

⚠️ **The last two are not yet enforced in code**, and are listed so the gap is a commitment rather
than a discovery. A reviewer demonstrated both: `--with-target --publishing` produced `EXPECTED.json`
with no commitment evidence, and `--publishing` succeeded with no address and no window.

---

*Replaces: v5 §3 · Strengthens: v4 §2 · Alongside: [`PRE-REGISTRATION-v3-CONFIRMATORY.md`](PRE-REGISTRATION-v3-CONFIRMATORY.md) · Enforced by [`check_commitments.py`](check_commitments.py) and [`test_controls.py`](test_controls.py)*
