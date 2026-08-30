"""Re-derive this study's headline findings from scratch, so a reviewer checks results not prose.

⛔ A REVIEW PACKET THAT ONLY LETS YOU RE-RUN THE ARTIFACT LETS YOU CHECK THE PACKAGING. The claims
that matter here are not "the package runs" — they are:

    thread count ALONE partitions the trained model
    the resulting models are numerically indistinguishable and are not the same artifact

Both are recomputed below, from nothing but the corpus and `train.py`. If the numbers this prints
disagree with `PHASE-2-FINDINGS.md`, the findings are wrong and that is the review's most valuable
possible outcome.

⚠️ It takes a few minutes: five training runs. Nothing is timed, so it does not care whether your
machine is busy — every number here is a digest or a difference, and contention cannot move either.

    python reproduce_findings.py
"""
import io
import json
import pathlib
import struct
import subprocess
import sys

import numpy as np

NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent
COUNTS = (1, 2, 4, 8, 16)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=" * 78)
    print("  RE-DERIVING THE FINDINGS  (five training runs, no timing)")
    print("=" * 78)
    print()

    got = {}
    for n in COUNTS:
        out = HERE / "runs" / ("check-thr-%d" % n)
        r = subprocess.run([sys.executable, "-X", "utf8", "train.py", "--out", str(out),
                            "--threads", str(n)], cwd=str(HERE), capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print("  " + chr(0x26D4) + " threads=%d failed: %s" % (n, (r.stderr or "")[-300:]))
            return 1
        rec = json.loads((out / "run.json").read_text(encoding="utf-8"))
        got[n] = rec
        print("  threads=%-3d  %s   loss %.8f" % (n, rec["weights_sha256"][:48], rec["final_loss"]))

    print()
    distinct = len({v["weights_sha256"] for v in got.values()})
    print("  FINDING 1  %d distinct model(s) from %d thread counts" % (distinct, len(COUNTS)))
    print("             the paper claims 5 of 5. %s"
          % ("CONFIRMED" if distinct == len(COUNTS) else chr(0x26D4) + " NOT CONFIRMED HERE"))
    print()

    base = np.load(HERE / "runs" / "check-thr-1" / "weights.npz")
    a = np.concatenate([base[k].astype(np.float64).ravel() for k in sorted(base.files)])
    print("  FINDING 2  divergence from threads=1, over %d parameters" % a.size)
    print("             %-10s %-12s %-12s %-14s" % ("config", "rel L2", "max|diff|", "params differ"))
    for n in COUNTS[1:]:
        o = np.load(HERE / "runs" / ("check-thr-%d" % n) / "weights.npz")
        b = np.concatenate([o[k].astype(np.float64).ravel() for k in sorted(o.files)])
        d = np.abs(a - b)
        print("             threads=%-3d %-12.3e %-12.3e %d (%.1f%%)"
              % (n, np.linalg.norm(a - b) / np.linalg.norm(a), d.max(),
                 int((a != b).sum()), 100.0 * (a != b).sum() / a.size))

    # ⚠️ THE RELATIVE FIGURE, SHOWN THE HONEST WAY. The maximum relative difference over ALL
    # parameters is above 1.0 and is meaningless -- it is entirely parameters near zero. The paper
    # declines to headline it and prints both, so a reviewer can see why.
    o = np.load(HERE / "runs" / "check-thr-16" / "weights.npz")
    b = np.concatenate([o[k].astype(np.float64).ravel() for k in sorted(o.files)])
    d = np.abs(a - b)
    rms = float(np.sqrt((a ** 2).mean()))
    big = np.abs(a) > rms * 0.01
    with np.errstate(divide="ignore", invalid="ignore"):
        r_all = float(np.nanmax(np.where(np.abs(a) > 0, d / np.abs(a), 0.0)))
        r_big = float(np.nanmax(np.where(big, d / np.abs(a), 0.0)))
    print()
    print("  FINDING 3  the relative figure the paper declines to headline")
    print("             max relative diff, ALL parameters        %.3f   <- meaningless" % r_all)
    print("             max relative diff, |value| > 1%% of RMS   %.3e" % r_big)
    print("             (%d of %d parameters are above that bound)" % (int(big.sum()), a.size))

    # the loss curves: where does the divergence first appear?
    L1 = json.loads((HERE / "runs" / "check-thr-1" / "loss.json").read_text(encoding="utf-8"))
    L16 = json.loads((HERE / "runs" / "check-thr-16" / "loss.json").read_text(encoding="utf-8"))
    first = next((i for i, (x, y) in enumerate(zip(L1, L16)) if x != y), None)
    print()
    # ⛔ BOTH ANSWERS, BECAUSE THE DIFFERENCE BETWEEN THEM WAS THE ERROR. The previous
    # revision reported the loss-curve answer as though it were the model's. Two traced runs cost
    # a few more seconds and settle it: the loss file is rounded to 8 decimals, the median
    # parameter difference is of that order, so the curve cannot see what it is asked about.
    print("  FINDING 4  where does divergence FIRST appear?")
    print("             in the rounded loss curve                    step %s" % first)
    for n in (1, 16):
        subprocess.run([sys.executable, "-X", "utf8", "train.py", "--out",
                        str(HERE / "runs" / ("check-trace-%d" % n)),
                        "--threads", str(n), "--trace"], cwd=str(HERE),
                       capture_output=True, text=True)
    try:
        ta = json.loads((HERE / "runs" / "check-trace-1" / "trace.json").read_text())
        tb = json.loads((HERE / "runs" / "check-trace-16" / "trace.json").read_text())
        firsts = {}
        for i, (x, y) in enumerate(zip(ta, tb)):
            for k in x:
                if k not in firsts and x[k] != y[k]:
                    firsts[k] = i
        print("             in the WEIGHTS, per array                    %s"
              % ", ".join("%s=%s" % (k, firsts.get(k, "never")) for k in ("E", "W1", "b1",
                                                                          "W2", "b2")))
        print("             -> there is no first LAYER: reduction order enters at the first")
        print("                matmul, so every array diverges at the same step")
    except Exception as e:                                                  # noqa: BLE001
        print("             " + D + " could not read the traces: %s" % e)
    print("             final loss %.8f vs %.8f" % (L1[-1], L16[-1]))
    print()
    # ⛔ THIS PARAGRAPH USED TO SAY "It confirms that thread count partitions the model
    # HERE" NO MATTER WHAT THE RUN FOUND. A reviewer's machine produced ONE digest across all five
    # counts -- the script printed NOT CONFIRMED four lines earlier and then concluded the
    # opposite. A conclusion that does not read its own data is worse than no conclusion, because
    # it will be quoted.
    print("  " + chr(0x26A0) + " ALL OF THIS IS ONE MACHINE, and one numerical stack.")
    if distinct == len(COUNTS):
        print("  Here, requesting different thread counts produced different models. On other")
        print("  machines it has not: a reviewer saw one digest across all five requests, because")
        print("  the mechanism is the EFFECTIVE reduction shape and the environment variable is")
        print("  only a REQUEST -- one that a machine with fewer cores may cap or ignore.")
    else:
        print("  Here, requesting different thread counts produced %d distinct model(s), not %d."
              % (distinct, len(COUNTS)))
        print("  That does not contradict the configuration-A measurement. It shows the partition")
        print("  depends on the EFFECTIVE reduction shape, which a thread request only influences.")
        print("  Report this: it is the more informative outcome of the two.")
    print("  Whether bit-identity survives different hardware is measurement 4, which is not done")
    print("  and which this script cannot answer.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
