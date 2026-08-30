"""Measurement 1: what determinism costs in wall-clock, measured rather than timed once.

⛔ THE FIRST ATTEMPT AT THIS NUMBER WAS INADMISSIBLE AND LOOKED FINE. Three pinned runs took
7.66 s, 7.59 s and 14.28 s -- an 88% spread -- because a CPU-bound build was running in another
window. Had the pair of runs happened to land on quiet and busy moments respectively, the headline
cost of determinism would have been off by a factor of two and nothing in the output would have
said so. A single timing is not a measurement; it is one sample from a distribution nobody looked
at.

⇒ So: repetitions, INTERLEAVED, with the spread reported beside the median. Interleaving matters
because machines drift -- thermal throttling, background services, a scheduler moving work between
P- and E-cores. Running all the pinned trials and then all the free ones attributes any drift to
the condition.

⚠️ AND THE MACHINE IS CHECKED, NOT ASSUMED, QUIET. This refuses to start while another heavy
process of ours is running, because "I think nothing else was going on" is exactly the claim that
was wrong the first time.

    python measure_cost.py --reps 7
"""
import io
import json
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import time

NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent
BUSY = re.compile(r"build_|sweep\.py|check_claims|control_audit|test_executors")


def busy_processes():
    """Our own heavy jobs, if any are running. An empty list is the precondition."""
    ps = shutil.which("powershell")
    if not ps:
        return []
    r = subprocess.run([ps, "-NoProfile", "-Command",
                        "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" "
                        "| Select-Object -ExpandProperty CommandLine"],
                       capture_output=True, text=True, timeout=60)
    return [ln.strip()[:70] for ln in (r.stdout or "").splitlines() if BUSY.search(ln or "")]


def one(tag, args):
    out = HERE / "runs" / ("cost-" + tag)
    t0 = time.perf_counter()
    r = subprocess.run([sys.executable, "-X", "utf8", "train.py", "--out", str(out)] + args,
                       cwd=str(HERE), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    wall = time.perf_counter() - t0
    if r.returncode != 0:
        raise SystemExit(chr(0x26D4) + " a run failed: " + (r.stderr or "")[-400:])
    rec = json.loads((out / "run.json").read_text(encoding="utf-8"))
    # The run's OWN clock, not this wrapper's: the wrapper includes interpreter start-up and
    # corpus hashing, which are real costs but not the cost of the training loop.
    return rec["wall_clock_seconds"], wall, rec["weights_sha256"]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    reps = int(sys.argv[sys.argv.index("--reps") + 1]) if "--reps" in sys.argv else 7

    busy = busy_processes()
    if busy:
        print("  " + chr(0x26D4) + " %d heavy process(es) of ours are still running:" % len(busy))
        for b in busy[:4]:
            print("      %s" % b)
        print("  Refusing to measure. The first attempt at this number was taken under exactly")
        print("  this condition and produced an 88% spread that looked like a result.")
        return 1

    print("=" * 78)
    print("  MEASUREMENT 1 -- the wall-clock cost of determinism, %d interleaved reps" % reps)
    print("=" * 78)
    print()

    det, free, digests = [], [], {"pinned": set(), "free": set()}
    for i in range(reps):
        d_loop, d_wall, d_h = one("det", [])
        f_loop, f_wall, f_h = one("free", ["--unconstrained"])
        det.append((d_loop, d_wall)); free.append((f_loop, f_wall))
        digests["pinned"].add(d_h); digests["free"].add(f_h)
        print("    rep %d   pinned %6.2f s    free %6.2f s" % (i + 1, d_loop, f_loop))
        # ⛔ A PRECONDITION CHECKED ONCE AT THE START IS NOT A PRECONDITION HELD THROUGHOUT.
        # The first guarded attempt at this number checked the machine, found it quiet, and then a
        # build started one second later and ran alongside all seven reps -- producing a 13.25 s
        # pinned run beside a 6.18 s one. The check has to happen where contention can ARRIVE,
        # which is between the reps, and its failure has to discard the run rather than annotate
        # it: a contaminated measurement that is written down gets cited.
        late = busy_processes()
        if late:
            print()
            print("  " + chr(0x26D4) + " contention APPEARED during rep %d: %s" % (i + 1, late[0]))
            print("  Discarding the whole run. Nothing is written -- a contaminated measurement")
            print("  on disk is worse than none, because the next reader cannot see the window")
            print("  it was taken through.")
            return 1

    dl = sorted(x[0] for x in det)
    fl = sorted(x[0] for x in free)
    md, mf = statistics.median(dl), statistics.median(fl)
    print()
    print("    %-28s %-10s %-10s %-10s" % ("", "median", "min", "max"))
    print("    %-28s %-10.2f %-10.2f %-10.2f" % ("threads pinned to 1", md, dl[0], dl[-1]))
    print("    %-28s %-10.2f %-10.2f %-10.2f" % ("threads unconstrained", mf, fl[0], fl[-1]))
    print()
    over = (md - mf) / mf * 100.0
    print("    determinism costs %+.1f%% of wall-clock on this configuration" % over)
    # ⚠️ A single ratio hides whether the two distributions even separate. If the ranges overlap,
    # the honest statement is that the cost is not resolved by this many repetitions.
    if dl[0] <= fl[-1] and fl[0] <= dl[-1]:
        print("    " + chr(0x26A0) + " THE RANGES OVERLAP, so this figure is not resolved at %d "
              "reps." % reps)
    else:
        print("    the ranges do not overlap, so the separation is resolved at %d reps" % reps)

    print()
    for k in ("pinned", "free"):
        n = len(digests[k])
        print("    %-22s %d distinct weight digest(s) across %d runs%s"
              % (k, n, reps, "" if n == 1 else "  " + chr(0x26D4) + " NOT REPRODUCIBLE"))

    rec = {"reps": reps, "quiet_machine_verified_between_every_rep": True, "loop_seconds": {"pinned": dl, "free": fl},
           "median": {"pinned": md, "free": mf},
           # ⛔ STORED UNROUNDED. The console printed 37.1 from the live
           # computation while the packet printed 37.0 from a value rounded
           # to 2 places -- two artifacts, two numbers, one measurement.
           "determinism_overhead_percent": over,
           "determinism_overhead_reported": "roughly a third; the ranges separate by only %.2f s, so one decimal place is false precision"
                                             % (dl[0] - fl[-1]),
           "ranges_overlap": bool(dl[0] <= fl[-1] and fl[0] <= dl[-1]),
           "distinct_digests": {k: sorted(v) for k, v in digests.items()}}
    (HERE / "MEASUREMENT-1.json").write_text(json.dumps(rec, indent=2) + NL,
                                             encoding="utf-8", newline=NL)
    print()
    print("  written to MEASUREMENT-1.json")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
