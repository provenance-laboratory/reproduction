"""Are the m5 magnitude and the m7 differing-fraction properties of the pipeline, or of one seed?

PHASE-2-FINDINGS reports m5 (relative L2, % of parameters differing) and m7 (the differing
fraction across thread counts) from ONE trajectory: seed 20260829, one corpus, one run per arm.
Between the v2 and v3 pipelines, an off-by-one that shifted the sampling range by a single index
moved m7 from 97.3 / 97.6 / 97.5 / 96.8 to 58.0 / 56.0 / 86.2 / 97.6.

If a one-index change does that, the quantity may be a property of the trajectory rather than of
the thread count. This varies the seed and holds everything else fixed, using a fixed alternative
reduction order (reversed k in the first matmul) in place of a thread change -- the same class of
arithmetic difference, available on a single-core machine.
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
import hashlib
import json
import pathlib

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
CONTEXT, D_EMB, D_HID, STEPS, BATCH, LR = 8, 64, 1024, 300, 256, 0.05
DTYPE = np.float32


def corpus():
    man = json.loads((HERE / "corpus" / "MANIFEST.json").read_text(encoding="utf-8"))
    blob = bytearray()
    for e in man["texts"]:
        blob += (HERE / "corpus" / e["file"]).read_bytes()
    return np.frombuffer(bytes(blob), dtype=np.uint8)


DATA = corpus()


def run(seed, reversed_reduction):
    data = DATA
    vocab = 256
    rng = np.random.Generator(np.random.PCG64(seed))
    E = (rng.standard_normal((vocab, D_EMB)) * 0.02).astype(DTYPE)
    W1 = (rng.standard_normal((CONTEXT * D_EMB, D_HID)) * (1.0 / np.sqrt(CONTEXT * D_EMB))).astype(DTYPE)
    b1 = np.zeros(D_HID, dtype=DTYPE)
    W2 = (rng.standard_normal((D_HID, vocab)) * (1.0 / np.sqrt(D_HID))).astype(DTYPE)
    b2 = np.zeros(vocab, dtype=DTYPE)
    n = len(data) - CONTEXT                      # the v3 range
    order = rng.integers(0, n, size=(STEPS, BATCH), dtype=np.int64)

    for step in range(STEPS):
        idx = order[step]
        ctx = np.stack([data[i:i + CONTEXT] for i in idx]).astype(np.int64)
        y = data[idx + CONTEXT].astype(np.int64)
        h0 = E[ctx].reshape(BATCH, CONTEXT * D_EMB)
        if reversed_reduction:
            z1 = (np.ascontiguousarray(h0[:, ::-1]) @ np.ascontiguousarray(W1[::-1])) + b1
        else:
            z1 = h0 @ W1 + b1
        a1 = np.maximum(z1, 0)
        z2 = a1 @ W2 + b2
        z2 -= z2.max(axis=1, keepdims=True)
        ex = np.exp(z2)
        p = ex / ex.sum(axis=1, keepdims=True)
        dz2 = p
        dz2[np.arange(BATCH), y] -= 1.0
        dz2 /= BATCH
        dW2 = a1.T @ dz2
        db2 = dz2.sum(axis=0)
        da1 = dz2 @ W2.T
        dz1 = da1 * (z1 > 0)
        dW1 = h0.T @ dz1
        db1 = dz1.sum(axis=0)
        dh0 = (dz1 @ W1.T).reshape(BATCH, CONTEXT, D_EMB)
        dE = np.zeros_like(E)
        np.add.at(dE, ctx, dh0)
        for prm, grad in ((W1, dW1), (b1, db1), (W2, dW2), (b2, db2), (E, dE)):
            prm -= LR * grad.astype(DTYPE)
    return np.concatenate([np.asarray(v, dtype=np.float64).ravel()
                           for v in (E, W1, W2, b1, b2)])


print("=" * 74)
print("  ONE FIXED ALTERNATIVE REDUCTION ORDER, ACROSS SEEDS")
print("=" * 74)
print("  %-12s %-12s %-12s %-14s" % ("seed", "rel L2", "max|diff|", "params differ"))
rows = []
for seed in (20260829, 1, 2, 3, 4):
    a = run(seed, False)
    b = run(seed, True)
    d = np.abs(a - b)
    rel = np.linalg.norm(a - b) / np.linalg.norm(a)
    frac = 100.0 * (a != b).mean()
    rows.append((rel, frac))
    print("  %-12d %-12.3e %-12.3e %.1f%%" % (seed, rel, d.max(), frac))
rels = np.array([r[0] for r in rows])
fracs = np.array([r[1] for r in rows])
print()
print("  relative L2   min %.3e  max %.3e  ratio max/min %.1fx"
      % (rels.min(), rels.max(), rels.max() / rels.min()))
print("  %% differing   min %.1f%%     max %.1f%%     spread %.1f points"
      % (fracs.min(), fracs.max(), fracs.max() - fracs.min()))
print()
print("  PHASE-2-FINDINGS reports one seed: rel L2 2.708e-05, 97.6%% differing (threads 1 vs 16)")
print("  and m7 as 58.0 / 56.0 / 86.2 / 97.6, called NOT MONOTONE.")
print("=" * 74)
