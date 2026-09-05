# Paper B — Zenodo deposit of the pre-registration and instrument

**Why this is not optional.** This experiment's central claim is that its commitments were public
*before* any result existed. Today that public location is a hosting account. If the account
lapses, is renamed, or is taken down, the pre-registration stops being publicly checkable and the
claim it supports weakens with it — while the OpenTimestamps anchors continue to prove *when* the
bytes existed to anyone who already has them.

⇒ **The anchor proves WHEN. A deposit makes the bytes RETRIEVABLE.** Neither substitutes for the
other, and right now only one of the two is durable.

⚠️ **Author-gated.** Minting a DOI is irreversible and public. Everything below is prepared;
nothing has been executed.

---

## What to deposit

A single archive containing:

```
PRE-REGISTRATION.md                     + .ots + .asc      the original commitment
PRE-REGISTRATION-v2..v11-CONFIRMATORY.md + .ots + .asc     every amended version
AMENDMENT-2026-08-30.md                 + .ots + .asc      the corpus deviation, disclosed
ANCHORS.json                                               the pinned Bitcoin blocks
PUBKEY.asc                                                 the signing key
check_commitments.py  check_signature.py  ots_verify.py    the verifiers
pin_anchors.py  anchor_status.py                           the anchor tooling
train.py  corpus/                                          the experiment and its inputs
test_controls.py                                           the control suite
PHASE-2-FINDINGS.md  MEASUREMENT-6.md                      results, including the unmeasurable one
```

**Include every superseded version and every `.superseded-*` proof.** A pre-registration that
ships only its current version is a pre-registration a reader cannot audit: the point is that
earlier commitments existed and can be checked against later ones.

## Metadata

| Field | Value |
|---|---|
| Resource type | **Dataset** (or *Software*; not *Publication* — there is no manuscript yet) |
| Title | Pre-registration, instrument and phase-2 findings for a study of bit-identical model reproduction |
| Author | Parth Mauria Saxena · Independent Researcher · ORCID 0009-0006-9409-6534 |
| Licence | CC BY 4.0 |
| Version | matches the governing protocol version at deposit time (**v11**) |
| Keywords | pre-registration; reproducibility; determinism; OpenTimestamps; machine learning; nondeterminism |

**Description** — state plainly what this is and is not:

> The pre-registered protocol, instrument, control suite and phase-2 findings for an experiment on
> the cost of bit-identical model reproduction. Every protocol version is GPG-signed and anchored
> in Bitcoin via OpenTimestamps; `check_commitments.py` verifies that the files each version pins
> by digest still hash to those digests, and `ots_verify.py` grants ANCHORED only when a proof's
> computed merkle root equals a root pinned in `ANCHORS.json`.
>
> **This deposit is not a paper and reports no completed study.** Measurement 4 requires a second
> machine and has not been performed; measurement 6 is reported as not measurable under the
> implemented design. The independent reproduction the protocol calls for cannot be produced by the
> author, by the protocol's own rule.

## Related identifiers

| Relation | Identifier |
|---|---|
| Is supplement to | the development repository (the deposit record links onward; the repository does not link back as the reference of record) |

## After the DOI exists

1. Cite the DOI as the **public location of the pre-registration** in any future manuscript, in
   place of a hosting URL.
2. Record it in `PUBLICATION-CHECKLIST.md`.
3. Re-deposit as a **new version** when a protocol version anchors, so the DOI series tracks the
   commitment series. Zenodo versioning gives a concept DOI for the series and a version DOI for
   each — cite the **version** DOI when the claim is about specific bytes, the **concept** DOI when
   it is about the line of work.

## What this does not do

It does not make the experiment complete, and it does not make the pre-registration independent.
It makes the commitment retrievable by someone who does not have the repository, which is the one
property it currently lacks.
