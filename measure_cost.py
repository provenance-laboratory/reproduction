"""Measurement 1: what pinning costs in wall-clock — paired, counterbalanced, with uncertainty.

⛔ THREE VERSIONS OF THIS FILE HAVE BEEN WRONG, EACH DIFFERENTLY, AND ALL THREE LOOKED FINE.

  1  timings taken while a CPU-bound build ran in another window: 7.66 s, 7.59 s and 14.28 s for
     three identical runs. A single timing is one sample from a distribution nobody looked at.
  2  a guard written to prevent exactly that, which checked the machine ONCE, found it quiet, and
     let a build start a second later and run through all seven repetitions. A precondition
     checked at the start is not a precondition held throughout.
  3  and then, found by review: every pair ran pinned-first and free-second, so drift within a
     pair loaded onto one arm; the stored arrays were SORTED SEPARATELY, destroying the pairing
     that made them comparable; the contrast was one thread against whatever the machine happened
     to choose rather than against a stated constraint; and "the ranges do not overlap" was used
     as though it were a resolution criterion, which it is not.

⇒ What this does now, and why each part is there:

    COUNTERBALANCED   half the blocks run A-then-B and half B-then-A, in a seeded order, so
                      order effects cancel rather than loading onto one arm
    PAIRED, IN ORDER  each block yields one (a, b) pair measured seconds apart, and the pairs are
                      stored unsorted. The estimand is the paired ratio
    BOTH ARMS PINNED  threads=1 against threads=N: two stated constraints. "Unconstrained" is not
                      a condition -- it is whatever the machine chose, which here was 16 and on a
                      reviewer's machine was 9
    EXACT + BOOTSTRAP a permutation test over the paired differences gives an exact p; a bootstrap
                      over the PAIRS gives an interval for the effect size. Complete separation is
                      far stronger evidence than "ranges do not overlap" suggests, and the point
                      estimate was being quoted to two more significant figures than it can carry

⚠️ THE QUIET-MACHINE CHECK IS STILL WEAK, and that is stated rather than papered over: it looks
for our own named processes, not for CPU contention. It cannot see a browser, an indexer or a VM.
It guards against the specific mistake made twice here, not against contention in general.

    python measure_cost.py --reps 12 --threads-b 16
"""
import io
import json
import pathlib
import random
import re
import shutil
import statistics
import subprocess
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
BUSY = re.compile(r"build_|sweep\.py|check_claims|control_audit|test_executors|reproduce_findings")
ORDER_SEED = 20260830


def busy_processes():
    ps = shutil.which("powershell")
    if not ps:
        return []
    try:
        r = subprocess.run([ps, "-NoProfile", "-Command",
                            "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" "
                            "| Select-Object -ExpandProperty CommandLine"],
                           capture_output=True, text=True, timeout=60)
    except Exception:                                                       # noqa: BLE001
        return []
    return [ln.strip()[:70] for ln in (r.stdout or "").splitlines() if BUSY.search(ln or "")]


def one(threads):
    out = HERE / "runs" / ("cost-t%s" % threads)
    r = subprocess.run([sys.executable, "-X", "utf8", "train.py", "--out", str(out),
                        "--threads", str(threads)], cwd=str(HERE),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit(D + " a run failed: " + (r.stderr or "")[-400:])
    rec = json.loads((out / "run.json").read_text(encoding="utf-8"))
    return rec["wall_clock_seconds"], rec["weights_sha256"]


def permutation_p(diffs):
    """The EXACT TWO-SIDED SIGN TEST over the paired differences. Named for what it is.

    ⛔ THIS WAS REPORTED AS "exact over all 4,096 sign assignments" AND ATTRIBUTED TO THE
    COUNTERBALANCED RANDOMISATION. It is not that. The design draws from balanced schedules with
    exactly six AB and six BA blocks -- C(12,6) = 924 of them -- not from the 2^12 unrestricted
    sign assignments this enumerates. The number 4.88e-04 is correct as a SIGN TEST on 12 of 12
    same-signed differences, and wrong as a description of the randomisation distribution, whose
    p under the balanced design is nearer 2.2e-03. A reviewer computed both.

    ⚠ Reported as a sign test, which is what it is, and the design's own randomisation
    p is reported beside it rather than conflated with it.
    """
    n = len(diffs)
    obs = abs(sum(diffs))
    if n <= 22:
        hits = 0
        for mask in range(1 << n):
            s = sum(d if (mask >> i) & 1 else -d for i, d in enumerate(diffs))
            hits += abs(s) >= obs
        return hits / float(1 << n), "exact two-sided SIGN TEST over all %d assignments" % (1 << n)
    rng = random.Random(ORDER_SEED)
    trials = 200000
    hits = sum(abs(sum(d if rng.random() < 0.5 else -d for d in diffs)) >= obs
               for _ in range(trials))
    return (hits + 1) / float(trials + 1), "sampled, %d draws" % trials


def bootstrap_ratio(pairs, orders, trials=20000):
    """Interval for the ratio of medians, resampling WITHIN each order stratum.

    ⛔ THE FIRST VERSION RESAMPLED ALL PAIRS TOGETHER, so a bootstrap sample need not
    contain six AB and six BA blocks -- it reintroduced exactly the order imbalance the design
    exists to control, and then reported an interval as though the control had held. A reviewer
    named it. Resampling within strata keeps every sample balanced the way the design is.
    """
    rng = random.Random(ORDER_SEED + 1)
    strata = {}
    for pr, o in zip(pairs, orders):
        strata.setdefault(o, []).append(pr)
    out = []
    for _ in range(trials):
        s = []
        for o, members in strata.items():
            s += [members[rng.randrange(len(members))] for _ in range(len(members))]
        mb = statistics.median(x[1] for x in s)
        if mb > 0:
            out.append(statistics.median(x[0] for x in s) / mb)
    out.sort()
    return out[int(0.025 * len(out))], out[int(0.975 * len(out))]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 12
    tb = sys.argv[sys.argv.index("--threads-b") + 1] if "--threads-b" in sys.argv else "16"
    ta = "1"

    busy = busy_processes()
    if busy:
        print("  " + D + " %d heavy process(es) of ours are running:" % len(busy))
        for b in busy[:4]:
            print("      %s" % b)
        return 1

    # ⛔ SHUFFLED, NOT BLOCKED. The seeded shuffle produced BA BA BA as the first three
    # pairs, so the warm-up period sat entirely in one arm's order -- and the two orders then
    # disagreed materially (AB median ratio 1.114, BA 1.177). Counterbalancing that can put half
    # its blocks consecutively is counterbalancing in name. Alternating guarantees the orders are
    # interleaved and the warm-up is split between them.
    seq = ["AB" if i % 2 == 0 else "BA" for i in range(reps)]
    if "--shuffle" in sys.argv:                # kept so the old design can be reproduced
        random.Random(ORDER_SEED).shuffle(seq)

    print("=" * 78)
    print("  MEASUREMENT 1 — threads=%s vs threads=%s, %d counterbalanced pairs" % (ta, tb, reps))
    print("=" * 78)
    print()
    print("  order: %s" % " ".join(seq))
    print()

    pairs, digests = [], {ta: set(), tb: set()}
    for i, o in enumerate(seq, 1):
        if o == "AB":
            a, ha = one(ta)
            b, hb = one(tb)
        else:
            b, hb = one(tb)
            a, ha = one(ta)
        pairs.append((a, b))
        digests[ta].add(ha)
        digests[tb].add(hb)
        print("    pair %-3d [%s]  t%s %6.2f s   t%-3s %6.2f s   ratio %.3f"
              % (i, o, ta, a, tb, b, (a / b) if b else float("nan")))
        late = busy_processes()
        if late:
            print()
            print("  " + D + " contention APPEARED during pair %d: %s" % (i, late[0]))
            print("  Discarding the run; nothing is written.")
            return 1

    A = [p[0] for p in pairs]
    B = [p[1] for p in pairs]
    diffs = [p[0] - p[1] for p in pairs]
    ma, mb = statistics.median(A), statistics.median(B)
    ratio = ma / mb
    p, how = permutation_p(diffs)
    lo, hi = bootstrap_ratio(pairs, seq)

    print()
    print("    %-24s %-10s %-10s %-10s" % ("", "median", "min", "max"))
    print("    threads=%-16s %-10.2f %-10.2f %-10.2f" % (ta, ma, min(A), max(A)))
    print("    threads=%-16s %-10.2f %-10.2f %-10.2f" % (tb, mb, min(B), max(B)))
    print()
    # ⛔ THE ORDER EFFECT MUST BE PRINTED, not merely controlled for. The previous version
    # counterbalanced and then never reported whether the two orders agreed -- and they did not:
    # AB gave a median ratio of 1.114 against BA's 1.177. A design feature nobody looks at is a
    # claim that the feature worked.
    _ab = [x[0] / x[1] for x, o in zip(pairs, seq) if o == "AB" and x[1]]
    _ba = [x[0] / x[1] for x, o in zip(pairs, seq) if o == "BA" and x[1]]
    if _ab and _ba:
        print("    order effect: AB median ratio %.4f (n=%d), BA %.4f (n=%d)"
              % (statistics.median(_ab), len(_ab), statistics.median(_ba), len(_ba)))
        if abs(statistics.median(_ab) - statistics.median(_ba)) > 0.03:
            print("    " + W + " the two orders DISAGREE by more than 3 points, so the estimate is")
            print("    order-sensitive and the interval below should be read as the wider claim")
    print("    paired differences positive in %d of %d pairs" % (sum(d > 0 for d in diffs), reps))
    print("    sign-test p                    %.2e   (%s)" % (p, how))
    print("    " + W + " NOT the randomisation p of this design: the schedule space is the")
    print("    balanced one, C(%d,%d), not 2^%d. The sign test is the claim being made."
          % (reps, reps // 2, reps))
    print("    ratio of medians               %.3f" % ratio)
    print("    bootstrap 95%% interval         [%.3f, %.3f]" % (lo, hi))
    print()
    print("    " + W + " REPORT AS: pinning to one thread costs roughly %d%% here, 95%% CI "
          "[+%d%%, +%d%%]." % (round((ratio - 1) * 100), round((lo - 1) * 100),
                               round((hi - 1) * 100)))
    print("    NOT as a two-decimal percentage: the interval is far wider than that implies.")
    print()
    for k in (ta, tb):
        n = len(digests[k])
        print("    threads=%-4s %d distinct weight digest(s) across %d runs%s"
              % (k, n, reps, "" if n == 1 else "  " + D + " NOT REPRODUCIBLE"))

    rec = {"reps": reps, "threads_a": ta, "threads_b": tb,
           "counterbalanced_order": seq, "order_seed": ORDER_SEED,
           "quiet_machine_verified_between_every_pair": True,
           "pairs_in_execution_order": pairs,
           "median_a": ma, "median_b": mb, "ratio_of_medians": ratio,
           "sign_test_p": p, "sign_test_method": how,
           "_p_caveat": ("This is the exact two-sided SIGN TEST on the paired differences. It is "
                         "NOT the randomisation distribution of the counterbalanced design, whose "
                         "space is the balanced schedules C(n, n/2) rather than 2^n; under that "
                         "design the p is larger. Reported as what it is."),
           "order_effect": {"AB_median_ratio": (statistics.median(_ab) if _ab else None),
                            "BA_median_ratio": (statistics.median(_ba) if _ba else None)},
           "bootstrap_95_ratio": [lo, hi],
           "reported": ("pinning to one thread costs roughly %d%% on this configuration, "
                        "95%% CI [+%d%%, +%d%%]"
                        % (round((ratio - 1) * 100), round((lo - 1) * 100),
                           round((hi - 1) * 100))),
           "_estimand": ("This is the cost of PINNING TO ONE THREAD versus requesting %s, both "
                         "stated constraints. It is NOT 'the cost of determinism': what minimum "
                         "constraint achieves bit-identity is not known until measurement 4 is "
                         "done, and costing an unknown constraint is not possible." % tb),
           "distinct_digests": {k: sorted(v) for k, v in digests.items()}}
    (HERE / "MEASUREMENT-1.json").write_text(json.dumps(rec, indent=2) + NL,
                                             encoding="utf-8", newline=NL)
    print()
    print("  written to MEASUREMENT-1.json")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
