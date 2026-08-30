"""The deterministic training run. One file, numpy only, no network.

⛔ THREAD PINNING HAPPENS BEFORE numpy IS IMPORTED, and that ordering is the whole point of putting
it at the top of this file rather than in a wrapper. OpenBLAS reads these variables once, at load
time; setting them after `import numpy` changes nothing and looks like it worked. The pilot of
29 August measured four different bit-patterns from four thread counts on one machine, so this is
not a precaution, it is the finding applied.

⚠️ WHY AN MLP AND NOT A TRANSFORMER. The pre-registration says capability is irrelevant and will
not be benchmarked; what has to be exercised is the MECHANISM the pilot identified -- threaded BLAS
reduction order in large matmuls. An MLP over a fixed context does that with backprop simple enough
to be read and checked by a stranger in an afternoon. A hand-written transformer would add hundreds
of lines whose only effect on this measurement is more places for a bug that is not the subject.

    python train.py --out runs/det-1                 deterministic, threads pinned to 1
    python train.py --out runs/free-1 --unconstrained  threads free, no pinning
"""
import os
import sys

# ── the pin, before anything can load a BLAS ──────────────────────────────────────────────────
_UNCONSTRAINED = "--unconstrained" in sys.argv
# --threads N pins to N rather than to 1. It exists so the pilot's finding can be reproduced on
# the REAL pipeline instead of on a toy sum: the claim is that thread count alone partitions the
# results, and a claim demonstrated only on the instrument that first showed it is half a claim.
_THREADS = "1"
if "--threads" in sys.argv:
    _THREADS = sys.argv[sys.argv.index("--threads") + 1]
if not _UNCONSTRAINED:
    for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[_v] = _THREADS
    # Python's own hash randomisation does not touch these arrays, but it does touch any dict
    # iteration order that reaches a filename or a manifest, so it is pinned too.
    os.environ.setdefault("PYTHONHASHSEED", "0")

import hashlib                                                              # noqa: E402
import io                                                                   # noqa: E402
import json                                                                 # noqa: E402
import pathlib                                                              # noqa: E402
import platform                                                             # noqa: E402
import time                                                                 # noqa: E402

import numpy as np                                                          # noqa: E402

NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent

# ── the specification. Every number here is part of the published artifact ────────────────────
SEED = 20260829            # the pilot's date, fixed before the corpus existed
CONTEXT = 8                # bytes of context
D_EMB = 64
D_HID = 1024
STEPS = 300
BATCH = 256
LR = 0.05
DTYPE = np.float32         # float32 on purpose: this is where reduction order shows


def environment():
    """Everything a reproducer must match, and the digest of it.

    ⚠️ A run that cannot report these is not admissible -- the pre-registration says so, so this
    refuses rather than filling in blanks.
    """
    import subprocess
    cpu = platform.processor() or "unknown"
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-CimInstance Win32_Processor).Name"],
                           capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and r.stdout.strip():
            cpu = r.stdout.strip().splitlines()[0].strip()
    except Exception:                                                       # noqa: BLE001
        pass
    cfg = io.StringIO()
    try:
        import contextlib
        with contextlib.redirect_stdout(cfg):
            np.show_config()
    except Exception:                                                       # noqa: BLE001
        pass
    blas = [ln.strip() for ln in cfg.getvalue().splitlines()
            if "openblas configuration" in ln.lower() or "version:" in ln.lower()]
    env = {
        "cpu": cpu,
        "logical_processors": os.cpu_count(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "blas": sorted(set(blas))[:6],
        "simd_baseline": getattr(np.__config__, "CONFIG", {}).get(
            "SIMD Extensions", {}).get("baseline", []),
        "simd_found": getattr(np.__config__, "CONFIG", {}).get(
            "SIMD Extensions", {}).get("found", []),
        "threads_env": {k: os.environ.get(k) for k in
                        ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")},
        "unconstrained": _UNCONSTRAINED,
    }
    missing = [k for k in ("cpu", "numpy", "python") if not env.get(k)]
    if missing:
        raise SystemExit(chr(0x26D4) + " the run cannot report %s, so its result is not "
                         "admissible under section 2a" % missing)
    env["digest"] = hashlib.sha256(
        json.dumps({k: v for k, v in env.items() if k != "unconstrained"},
                   sort_keys=True).encode("utf-8")).hexdigest()
    return env


def corpus_ids():
    """The corpus, as byte ids, in the order the committed manifest fixes.

    ⛔ THE ORDER COMES FROM THE MANIFEST, not from a directory listing. A filesystem enumerates in
    whatever order it likes, and a training set assembled from `iterdir()` is a different training
    set on a different machine while every file digest still matches.
    """
    man = json.loads((HERE / "corpus" / "MANIFEST.json").read_text(encoding="utf-8"))
    blob = bytearray()
    for entry in man["texts"]:                       # manifest order, not directory order
        p = HERE / "corpus" / entry["file"]
        b = p.read_bytes()
        got = hashlib.sha256(b).hexdigest()
        if got != entry["clean_sha256"]:
            raise SystemExit(chr(0x26D4) + " %s does not match the committed manifest "
                             "(%s vs %s)" % (entry["file"], got[:16], entry["clean_sha256"][:16]))
        blob += b
    return np.frombuffer(bytes(blob), dtype=np.uint8), man["merkle_root"]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv \
        else HERE / "runs" / "adhoc"
    out.mkdir(parents=True, exist_ok=True)

    env = environment()
    data, merkle = corpus_ids()
    vocab = 256

    print("  corpus     %d bytes, merkle %s" % (len(data), merkle[:16]))
    print("  cpu        %s (%d logical)" % (env["cpu"], env["logical_processors"]))
    print("  threads    %s" % ("FREE (unconstrained)" if _UNCONSTRAINED
                                     else "pinned to " + _THREADS))
    print("  env digest %s" % env["digest"][:16])

    rng = np.random.Generator(np.random.PCG64(SEED))
    E = (rng.standard_normal((vocab, D_EMB)) * 0.02).astype(DTYPE)
    W1 = (rng.standard_normal((CONTEXT * D_EMB, D_HID)) * (1.0 / np.sqrt(CONTEXT * D_EMB))).astype(DTYPE)
    b1 = np.zeros(D_HID, dtype=DTYPE)
    W2 = (rng.standard_normal((D_HID, vocab)) * (1.0 / np.sqrt(D_HID))).astype(DTYPE)
    b2 = np.zeros(vocab, dtype=DTYPE)

    # ⛔ THE DATA ORDER IS DRAWN ONCE, FROM THE SEED, AND STORED. Sampling a fresh batch inside the
    # loop makes the order depend on how many times the RNG was touched elsewhere -- which changes
    # the moment anyone adds a diagnostic that draws a random number.
    n = len(data) - CONTEXT - 1
    order = rng.integers(0, n, size=(STEPS, BATCH), dtype=np.int64)

    losses = []
    t0 = time.perf_counter()
    for step in range(STEPS):
        idx = order[step]
        ctx = np.stack([data[i:i + CONTEXT] for i in idx]).astype(np.int64)
        y = data[idx + CONTEXT].astype(np.int64)

        h0 = E[ctx].reshape(BATCH, CONTEXT * D_EMB)
        z1 = h0 @ W1 + b1
        a1 = np.maximum(z1, 0)
        z2 = a1 @ W2 + b2

        z2 -= z2.max(axis=1, keepdims=True)
        ex = np.exp(z2)
        p = ex / ex.sum(axis=1, keepdims=True)
        loss = float(-np.log(p[np.arange(BATCH), y] + 1e-9).mean())
        losses.append(loss)

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
        np.add.at(dE, ctx, dh0)          # deterministic scatter-add, unlike a threaded reduction

        for prm, grad in ((W1, dW1), (b1, db1), (W2, dW2), (b2, db2), (E, dE)):
            prm -= LR * grad.astype(DTYPE)

    secs = time.perf_counter() - t0

    weights = {"E": E, "W1": W1, "b1": b1, "W2": W2, "b2": b2}
    npz = out / "weights.npz"
    # ⚠️ savez writes a zip whose entries carry a timestamp, so the FILE digest is not stable even
    # when the numbers are. The artifact that is compared is the digest over the raw arrays in a
    # fixed order -- a property of the weights, not of the container that holds them.
    np.savez(npz, **weights)
    h = hashlib.sha256()
    for k in sorted(weights):
        h.update(k.encode())
        h.update(np.ascontiguousarray(weights[k]).tobytes())
    wdigest = h.hexdigest()

    rec = {"spec": {"seed": SEED, "context": CONTEXT, "d_emb": D_EMB, "d_hid": D_HID,
                    "steps": STEPS, "batch": BATCH, "lr": LR, "dtype": str(np.dtype(DTYPE)),
                    "vocab": vocab},
           "corpus_merkle_root": merkle,
           "environment": env,
           "wall_clock_seconds": round(secs, 4),
           "final_loss": round(losses[-1], 8),
           "loss_first": round(losses[0], 8),
           "weights_sha256": wdigest,
           "weights_npz_bytes": npz.stat().st_size}
    (out / "run.json").write_text(json.dumps(rec, indent=2) + NL, encoding="utf-8", newline=NL)
    (out / "loss.json").write_text(json.dumps([round(x, 8) for x in losses]) + NL,
                                   encoding="utf-8", newline=NL)

    print("  steps      %d in %.2f s   loss %.5f -> %.5f" % (STEPS, secs, losses[0], losses[-1]))
    print("  weights    sha256 %s" % wdigest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
