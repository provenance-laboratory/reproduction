"""Measurements 5 and 7, computed from the reference arrays into structured records.

⛔ WHY THIS EXISTS. m5 and m7 were the last two figures the review packet carried as typed string
literals, and they were the two that went stale -- shipped one and two rounds behind the findings
they claimed to summarise, past a cross-check that could not fire. A reviewer's summary was exact:
*"m5 and m7 are the only two figures still hardcoded, and they are the two that are stale."*

⇒ They are now computed here and written as JSON, so the packet reads fields instead of retyping
prose, and a stale figure becomes a stale FILE -- which the anchor and digest checks can see.

⛔ AND THE SECOND FINDING, WHICH IS SHARPER. Both are reported from ONE trajectory: one seed, one
corpus, one run per arm. Between the v2 and v3 pipelines an off-by-one that shifted the sampling
range by a single index moved m7 from 97.3/97.6/97.5/96.8 to 58.0/56.0/86.2/97.6. If one index
does that, the quantity may be a property of the trajectory rather than of the thread count.

⚠️ This project's own doctrine -- *a single timing is one sample from a distribution nobody looked
at* -- was applied to measurement 1 three times and never to the divergence measurements. So the
seed is varied here too, and the spread is reported beside the headline.

    python measure_divergence.py
"""
import hashlib
import io
import json
import pathlib
import subprocess
import sys

import numpy as np

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
COUNTS = (1, 2, 4, 8, 16)
SEEDS = (20260829, 1, 2, 3, 4)


def flat(run_dir):
    z = np.load(HERE / "runs" / run_dir / "weights.npz")
    return np.concatenate([z[k].astype(np.float64).ravel() for k in sorted(z.files)])


def compare(a, b):
    d = np.abs(a - b)
    return {"relative_l2": float(np.linalg.norm(a - b) / np.linalg.norm(a)),
            "max_abs_diff": float(d.max()),
            "params_differing": int((a != b).sum()),
            "params_total": int(a.size),
            "percent_differing": round(100.0 * float((a != b).sum()) / a.size, 4)}


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    missing = [n for n in COUNTS if not (HERE / "runs" / ("thr-%d" % n) / "weights.npz").exists()]
    if missing:
        raise SystemExit(D + " reference runs missing for threads %s. Train them first." % missing)

    base = flat("thr-1")
    print("=" * 78)
    print("  MEASUREMENTS 5 AND 7 — from the reference arrays")
    print("=" * 78)
    print()
    per_thread = {}
    for n in COUNTS[1:]:
        per_thread[n] = compare(base, flat("thr-%d" % n))
        c = per_thread[n]
        print("  threads=%-3d relL2 %.4e  max %.4e  %.2f%% of %d differ"
              % (n, c["relative_l2"], c["max_abs_diff"], c["percent_differing"],
                 c["params_total"]))

    fr = [per_thread[n]["percent_differing"] for n in COUNTS[1:]]
    monotone = all(fr[i] <= fr[i + 1] for i in range(len(fr) - 1))
    print()
    print("  m7  differing fraction across thread counts: %s"
          % " / ".join("%.1f%%" % x for x in fr))
    print("      monotone in thread count: %s" % ("yes" if monotone else "NO"))

    # ── the trajectory question ──────────────────────────────────────────────────────
    print()
    print("  " + W + " IS THIS A PROPERTY OF THE THREAD COUNT OR OF THE SEED?")
    print("  Varying the seed, holding everything else fixed, threads=1 against threads=16:")
    seedwise = {}
    for s in SEEDS:
        outs = []
        for n in (1, 16):
            o = HERE / "runs" / ("seed%s-t%d" % (s, n))
            if not (o / "weights.npz").exists():
                r = subprocess.run([sys.executable, "-X", "utf8", "train.py", "--out", str(o),
                                    "--threads", str(n), "--seed", str(s)], cwd=str(HERE),
                                   capture_output=True, text=True)
                if r.returncode != 0:
                    print("      " + D + " seed %s threads %d failed: %s"
                          % (s, n, (r.stderr or "")[-160:]))
                    outs = None
                    break
            outs.append("seed%s-t%d" % (s, n))
        if not outs:
            continue
        c = compare(flat(outs[0]), flat(outs[1]))
        seedwise[s] = c
        print("      seed %-9s relL2 %.4e   %.2f%% differ" % (s, c["relative_l2"],
                                                              c["percent_differing"]))

    rec = {"reference_seed": SEEDS[0],
           "m5_threads_1_vs_16": per_thread[16],
           "m7_percent_differing_by_thread_count":
               {str(n): per_thread[n]["percent_differing"] for n in COUNTS[1:]},
           "m7_monotone_in_thread_count": monotone,
           "seed_sensitivity": {str(s): c for s, c in seedwise.items()},
           "reference_digests": {("thr-%d" % n): hashlib.sha256(
               (HERE / "runs" / ("thr-%d" % n) / "weights.npz").read_bytes()).hexdigest()
               for n in COUNTS}}
    if seedwise:
        pcts = [c["percent_differing"] for c in seedwise.values()]
        l2s = [c["relative_l2"] for c in seedwise.values()]
        rec["seed_spread_percent_points"] = round(max(pcts) - min(pcts), 4)
        rec["seed_relative_l2_ratio"] = round(max(l2s) / min(l2s), 4)
        print()
        print("      spread across seeds: %.1f percentage points, relative L2 varies %.1fx"
              % (rec["seed_spread_percent_points"], rec["seed_relative_l2_ratio"]))
        print()
        print("  " + D + " REPORT BOTH. The thread-count spread and the seed spread are the same")
        print("  kind of number, and if the second is a large fraction of the first then m7's")
        print("  SHAPE is not separable from trajectory noise at one seed. That is a limit on")
        print("  what m7 can claim, not a defect in the pipeline.")
    (HERE / "MEASUREMENT-5-7.json").write_text(json.dumps(rec, indent=2) + NL,
                                               encoding="utf-8", newline=NL)
    print()
    print("  written to MEASUREMENT-5-7.json")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
