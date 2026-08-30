# Pre-registration v5 — §2 was violated for a day, and nothing noticed

⛔ **v3 governs, v4 amends measurement 4's admissibility, and this version replaces v3 §2 only.**
Everything else in both stands unaltered and is not restated here.

## 1. What happened

v3 §2 pins four files by SHA-256 and says:

> *"Any change to a file above changes its digest and voids this pre-registration. That is the
> property v2 lacked: it named files, and a name is not a commitment."*

⛔ **That sentence was never enforced by anything, and it was broken the day after it was written.**
`train.py` was modified in commit `23df27d` — the round-3 commit — moving its digest from
`aa893adb` to `1231a42a`. v3 §2 was not updated. **The pre-registration has been void since
2026-08-30**, and every tool in this project reported success throughout: the package rebuilt,
`verify_package.py` passed, and `SHA256SUMS` was regenerated over the new bytes — which is how a
substitution passes a checksum derived from the thing it is meant to police.

⚠️ **It was found on 2026-08-31 by writing the control**, `check_commitments.py`, after a second
and separate violation: `corpus/build_corpus.py` was edited to add a verification mode, and
nothing objected to that either. That edit has been reverted; its file is byte-for-byte the
committed `2d3ce23b` again. `train.py`'s cannot be reverted, for the reason in §2.

## 2. What the change to `train.py` was, and why it is not reverted

The round-3 edit added `--seed`, and an `is_confirmatory_spec` field recording whether the seed is
the committed one. It exists because a round-2 reviewer required it: the divergence magnitude moves
substantially with the seed, and this project had applied *"one sample is not a measurement"* to the
timing three times and never to the divergence. Measurement 7's seed-sensitivity arm calls it.
Reverting `train.py` would delete a measurement a review round demanded.

⭐ **The change is numerically inert on the confirmatory path, and that is demonstrated rather than
argued.** The committed pipeline `aa893adb` was checked out of git and run:

```
train.py @ aa893adb  --threads 1        weights a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c59721511f98f1c23d38
train.py @ 1231a42a  --threads 1        weights a4afb5c86dd88ae5ce7a475d448ee6bab18f6bc4e3c6c59721511f98f1c23d38
```

Bit-identical. With no `--seed` argument the seed remains 20260829 and the computation is
unchanged; the only difference in output is one added key in `run.json`. **No measurement taken
under either version is affected.**

⚠️ **This does not make the violation harmless, and it must not be filed as though it were.** The
digest commitment exists precisely so that nobody has to take *"the change was inert"* on trust. It
was inert here; the point is that for a day nothing in this project could have told the difference,
and the same silence would have covered a change that was not.

## 3. ⛔ What is committed, by DIGEST — replacing v3 §2

```
train.py                   1231a42a09125a5cdc2d339cef8b08a78000a66b04a972a220b736acedd0e7a4
corpus/MANIFEST.json       fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py     2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json        7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30

corpus merkle  2006b7327c616f0ca5f9c0b9c3e766b5ebaa2aed99f1433fc66d7560d387452b
model          804,096 parameters: 8-byte context, d_emb 64, d_hid 1024, vocab 256
training       seed 20260829, 300 steps, batch 256, lr 0.05, float32
sampling       start positions drawn uniformly from [0, len(corpus) - CONTEXT)
```

⇒ Three of the four digests are unchanged from v3. Only `train.py` moves, and only to the version
that has been in use since round 3.

## 4. The control, which is the part that matters

`check_commitments.py` **parses this table out of the anchored document** — it does not restate it,
because a hand-copied list drifts from the protocol and the drift looks authoritative on both
sides. It recomputes each digest and fails closed, including on an empty parse: if the table's
format changes and the regex matches nothing, that is a broken check, not a clean bill of health.

⛔ **It runs inside `build_package.py`, which refuses to build when it fails.** A commitment nobody
verifies is the thing v2 had and v3 was written to remove; v3 removed it in prose and this removes
it in code.

## 5. What would invalidate this version

In addition to everything in v3 §6 and v4 §3:

- any file in §3 changing its digest, as before — now detectable
- re-committing a digest to accommodate a change instead of restoring the file, where the change
  is not independently required and its inertness not demonstrated
- reporting a measurement taken under a pipeline whose digest was not committed at the time

⚠️ **The third is the honest limitation of this document.** Measurement 4's second-machine arm was
run on 2026-08-31, while `train.py`'s committed digest was stale — under the pipeline this version
commits, but before this version existed. That is recorded in `MEASUREMENT-4.json` rather than
smoothed over, and it is the reason the demonstration in §2 was run at all.

---

*Replaces: v3 §2 · Alongside: [`PRE-REGISTRATION-v3-CONFIRMATORY.md`](PRE-REGISTRATION-v3-CONFIRMATORY.md) and [`PRE-REGISTRATION-v4-CONFIRMATORY.md`](PRE-REGISTRATION-v4-CONFIRMATORY.md) · Enforced by [`check_commitments.py`](check_commitments.py)*
