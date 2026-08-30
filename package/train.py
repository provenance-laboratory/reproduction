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
    python train.py --out runs/t --trace              also record per-step, per-array digests
"""
import os
import sys

# ── the pin, before anything can load a BLAS ──────────────────────────────────────────────────
_UNCONSTRAINED = "--unconstrained" in sys.argv
# ⛔ MEASUREMENT 5 ASKS FOR "the first layer/step where it appears" AND THE
# PIPELINE COULD NOT ANSWER IT. What was reported as "divergence first appears at
# step 8" was the first entry at which loss.json -- written as round(x, 8) --
# differed. A reviewer perturbed one reduction at step 0 and showed the WEIGHTS
# differ from step 0 while that file notices nothing for dozens of steps. The
# rounding floor is 5e-09 and the median parameter difference is 9.3e-09, so the
# loss curve was never going to see the divergence it was being asked about.
#
# ⚠ OFF BY DEFAULT, because hashing every array every step is real work and
# measurement 1 times this loop. A tracing run and a timing run must not be the
# same run.
_TRACE = "--trace" in sys.argv
# --threads N pins to N rather than to 1. It exists so the pilot's finding can be reproduced on
# the REAL pipeline instead of on a toy sum: the claim is that thread count alone partitions the
# results, and a claim demonstrated only on the instrument that first showed it is half a claim.
_THREADS = "1"
if "--threads" in sys.argv:
    _THREADS = sys.argv[sys.argv.index("--threads") + 1]
_THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
if _UNCONSTRAINED:
    # ⛔ `--unconstrained` USED TO INHERIT WHATEVER THE CALLER HAD SET and then print
    # "threads FREE". Both reviewers found it. If the shell exported OPENBLAS_NUM_THREADS=1, the
    # "unconstrained" arm was the pinned arm wearing a different label -- and measurement 1 is a
    # comparison between those two arms.
    for _v in _THREAD_VARS:
        os.environ.pop(_v, None)
else:
    for _v in _THREAD_VARS:
        os.environ[_v] = _THREADS
# ⛔ PYTHONHASHSEED WAS SET HERE AND DID NOTHING. The interpreter reads it at start-up;
# assigning it from inside the running process cannot affect that process's hashing. The comment
# beside it claimed a determinism property the line could not deliver -- and it sat thirty lines
# under a header warning that OpenBLAS reads ITS variables at load time, which is the same
# mistake. Removed rather than moved: nothing here depends on dict iteration order, and a
# re-exec to set it would be a large mechanism for a property this pipeline does not use.

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
# ⚠ THE SEED IS PART OF THE SPECIFICATION and v3 commits to 20260829. `--seed` exists only so
# that the DEPENDENCE on the seed can be measured -- a reviewer showed the divergence magnitude
# moves substantially with it, and this project had applied "one sample is not a measurement" to
# the timing three times and never to the divergence. A run with a non-default seed is a
# SENSITIVITY probe and is not a confirmatory run; its run.json says so.
SEED = 20260829            # the pilot's date, fixed before the corpus existed
if "--seed" in sys.argv:
    SEED = int(sys.argv[sys.argv.index("--seed") + 1])
CONTEXT = 8                # bytes of context
D_EMB = 64
D_HID = 1024
STEPS = 300
BATCH = 256
LR = 0.05
DTYPE = np.float32         # float32 on purpose: this is where reduction order shows


def _cpu_model():
    """The CPU model as the OS reports it, or None. ⛔ None must STOP the run.

    The first version fell back to `platform.processor()`, which returns "x86_64" on Linux. A
    reviewer's run.json therefore reported its CPU as `x86_64` -- and section 2a says a run that
    cannot report its CPU model is not admissible. The guard did not fire because the fallback
    produced a NON-EMPTY STRING, so the check saw a value and asked no further. A placeholder
    that satisfies a presence test is worse than a missing field, because it silences the alarm.
    """
    import subprocess
    plat = sys.platform
    try:
        if plat.startswith("win"):
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                                "(Get-CimInstance Win32_Processor).Name"],
                               capture_output=True, text=True, timeout=30)
            v = [x.strip() for x in (r.stdout or "").splitlines() if x.strip()]
            return v[0] if v else None
        if plat.startswith("linux"):
            for line in pathlib.Path("/proc/cpuinfo").read_text(errors="replace").splitlines():
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
            return None
        if plat == "darwin":
            r = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                               capture_output=True, text=True, timeout=30)
            return (r.stdout or "").strip() or None
    except Exception:                                                       # noqa: BLE001
        return None
    return None


def _blas_report():
    """The FULL build config, the openblas line, and the kernel line beneath it.

    ⛔ THE KERNEL LINE WAS BEING DROPPED. The old filter kept lines containing "openblas
    configuration" or "version:", and the DYNAMIC_ARCH kernel actually selected -- here
    `Haswell MAX_THREADS=24` -- sits on the INDENTED line underneath, so it never survived.
    Section 4 names kernel selection as one of the three reasons this experiment exists, and the
    published environment could not report it.

    ⚠ The whole text is kept and hashed rather than a selection of lines. Any selection is a
    guess about what will matter later, made by the person least able to know.
    """
    import contextlib
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            np.show_config()
    except Exception:                                                       # noqa: BLE001
        pass
    full = buf.getvalue()
    lines = full.splitlines()
    ob, kernel = None, None
    for i, ln in enumerate(lines):
        if "openblas configuration" in ln.lower():
            ob = ln.split(":", 1)[-1].strip()
            indent = len(ln) - len(ln.lstrip())
            if i + 1 < len(lines):
                nxt = lines[i + 1]
                if nxt.strip() and (len(nxt) - len(nxt.lstrip())) > indent:
                    kernel = nxt.strip()
            break
    return full, ob, kernel


def _effective_threads():
    """What the BLAS is ACTUALLY using, where that can be observed.

    ⚠ A REQUEST IS NOT A SETTING. A reviewer asked for 16 threads on a machine that gave 9, and
    every digest matched anyway -- so a run reporting `threads pinned to 16` had never used 16,
    and the label was describing an intention. `threadpoolctl` reads the true count, but
    requiring it would break the property that makes this reproducible for strangers: numpy and
    nothing else. So it is used IF PRESENT, and its absence is recorded AS an absence.
    """
    try:
        import threadpoolctl
    except Exception:                                                       # noqa: BLE001
        return None, "threadpoolctl not installed - effective thread count NOT OBSERVED"
    try:
        return ([{k: v for k, v in d.items()
                  if k in ("user_api", "internal_api", "num_threads", "architecture",
                           "version", "prefix")} for d in threadpoolctl.threadpool_info()], None)
    except Exception as e:                                                  # noqa: BLE001
        return None, "threadpoolctl present but failed: %s" % e


def environment():
    """Everything a reproducer must match, and the digest of it.

    ⛔ SECTION 2A IS AN ADMISSIBILITY RULE, so this REFUSES rather than filling blanks. The
    earlier version required three fields and defaulted the rest, which is how a run reporting
    its CPU as "x86_64" with no BLAS kernel at all passed a check named for section 2a.
    """
    cpu = _cpu_model()
    full_cfg, openblas, kernel = _blas_report()
    eff, eff_why = _effective_threads()
    runtime_arch = None
    if eff:
        for _d in eff:
            if _d.get("user_api") == "blas" and _d.get("architecture"):
                runtime_arch = _d["architecture"]
                break
    runtime = ""
    try:
        import contextlib
        rb = io.StringIO()
        with contextlib.redirect_stdout(rb):
            np.show_runtime()
        runtime = rb.getvalue()
    except Exception:                                                       # noqa: BLE001
        pass
    simd = getattr(np.__config__, "CONFIG", {}).get("SIMD Extensions", {})

    env = {
        "cpu": cpu,
        "logical_processors": os.cpu_count(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        # ⛔ THIS FIELD WAS CALLED `blas_kernel_selected` AND IT IS NOT THAT. It is the line
        # np.show_config() prints under the openblas configuration -- a property of how the
        # library was BUILT. A reviewer's run recorded `Haswell MAX_THREADS=64` while the same
        # process, through threadpoolctl, reported the runtime architecture as SkylakeX. So the
        # section-2a gate was passing on a mislabelled value, and configuration A's "selected
        # kernel" was never observed at all, because threadpoolctl was absent here.
        "blas_build_config_line": kernel,
        # what the library actually selected at run time, where that can be observed
        "blas_runtime_arch": runtime_arch,
        "blas_config_sha256": hashlib.sha256(full_cfg.encode("utf-8")).hexdigest(),
        "blas_config_full": full_cfg,
        "simd_baseline": simd.get("baseline"),
        "simd_found": simd.get("found"),
        "threads_requested": ("unset (unconstrained)" if _UNCONSTRAINED else _THREADS),
        "threads_env": {k: os.environ.get(k) for k in _THREAD_VARS},
        "threads_effective": eff,
        "threads_effective_note": eff_why,
        "show_runtime": runtime,
        "unconstrained": _UNCONSTRAINED,
    }
    # ⛔ THE ADMISSIBILITY GATE, over what section 2a actually names: CPU model, thread count,
    # instruction sets, library versions and kernel selection.
    # ⛔ THE GATE REFUSED THREE COMMON INSTALLS. A reviewer fed it the show_config() shapes of
    # conda/MKL numpy, macOS Accelerate, and an OpenBLAS built without DYNAMIC_ARCH: all three
    # produce no build-config kernel line, so all three were STOPPED before training. The call
    # promises "any x86-64, python 3 and numpy, nothing else" and section 2b forbids us from
    # helping -- so those reproducers could file exactly one thing, "I could not get as far as
    # running it", and section 2c would have scored that as an ecosystem finding. It would have
    # been a finding about our gate.
    #
    # ⚠ Section 5 already settled the principle for the neighbouring field: an unobservable
    # `threads_effective` is recorded AS AN ABSENCE and the run stays admissible. Kernel selection
    # is the same situation and now gets the same treatment. What section 2a genuinely requires --
    # a run that can SAY WHAT IT IS -- is the identity of the machine and the library, not a field
    # that only one build shape can emit.
    required = {"cpu": cpu, "numpy": np.__version__, "python": sys.version.split()[0],
                "simd_baseline": simd.get("baseline")}
    missing = sorted(k for k, v in required.items() if not v)
    if missing:
        raise SystemExit(
            chr(0x26D4) + " this run cannot report %s, so section 2a makes its result "
            "INADMISSIBLE and it will not be produced." % missing + NL
            + "  Section 2a: 'If a run cannot report those, its result is not admissible.'" + NL
            + "  That is a rule about the RUN, so the run stops rather than the report noting it.")
    # Recorded, not required: their ABSENCE is data about the environment, and a run without them
    # is admissible as a reproduction and NOT admissible to kernel/thread causal attribution.
    env["admissible_for_causal_attribution"] = bool(runtime_arch and eff)
    env["_attribution_note"] = (
        "A run is admissible for kernel/thread causal attribution only if it OBSERVED the runtime "
        "architecture and the effective thread count. The build-config line is not the selected "
        "kernel and is never treated as it.")
    env["digest"] = hashlib.sha256(
        json.dumps({k: v for k, v in env.items()
                    if k not in ("unconstrained", "threads_env", "threads_requested")},
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
    # ⛔ OFF BY ONE, AND IT IS A SPECIFICATION DEFECT RATHER THAN A BUG IN THE USUAL SENSE.
    # numpy's `integers` upper bound is exclusive, so `len(data) - CONTEXT - 1` excluded the last
    # valid (context, target) pair from the training population. The effect on a 6.3 MB corpus is
    # negligible and the defect is not: the sampled population is part of the model specification,
    # so this changes every digest and belongs in a new pre-registration rather than in a patch.
    n = len(data) - CONTEXT
    order = rng.integers(0, n, size=(STEPS, BATCH), dtype=np.int64)

    losses = []
    trace = []                      # per-step, per-array digests when --trace is given
    if _TRACE:
        # ⛔ THE TRACE BEGAN AFTER THE FIRST UPDATE, so it could show that the arrays DIFFER at
        # step 0 and could not show that they STARTED the same. Without an initial state the
        # evidence supports "they differ after update 0" and not "divergence originates in the
        # first matmul" -- a reviewer drew exactly that line. Step -1 is the initialisation.
        trace.append({k: hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest()
                      for k, v in (("E", E), ("W1", W1), ("b1", b1), ("W2", W2), ("b2", b2))})
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

        if _TRACE:
            # per ARRAY, not just per step: measurement 5 asks which LAYER first differs, and a
            # single whole-model digest per step cannot answer that.
            trace.append({k: hashlib.sha256(np.ascontiguousarray(v).tobytes()).hexdigest()
                          for k, v in (("E", E), ("W1", W1), ("b1", b1),
                                       ("W2", W2), ("b2", b2))})

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

    rec = {"is_confirmatory_spec": SEED == 20260829,
           "spec": {"seed": SEED, "context": CONTEXT, "d_emb": D_EMB, "d_hid": D_HID,
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
    # ⚠ loss.json stays ROUNDED because it is a curve for reading, not evidence of
    # divergence. The full-precision values go beside it, so nothing has to be recomputed from a
    # rounded file, and the rounding can never again be mistaken for a measurement.
    (out / "loss.json").write_text(json.dumps([round(x, 8) for x in losses]) + NL,
                                   encoding="utf-8", newline=NL)
    (out / "loss-full.json").write_text(json.dumps([repr(x) for x in losses]) + NL,
                                        encoding="utf-8", newline=NL)
    if _TRACE:
        (out / "trace.json").write_text(json.dumps(trace) + NL, encoding="utf-8", newline=NL)

    print("  steps      %d in %.2f s   loss %.5f -> %.5f" % (STEPS, secs, losses[0], losses[-1]))
    print("  weights    sha256 %s" % wdigest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
