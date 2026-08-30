"""Measurement 4 — bit-identity across hardware, under v4's admissibility conditions.

⛔ WHY THIS FILE EXISTS. v3 carried measurement 4 forward as *configuration A against configuration
B*, an Intel machine against an AMD one. As specified it could not isolate anything: in the runs
available, CPU vendor, operating system, Python version, numpy version and the OpenBLAS build all
moved AT ONCE, so a difference in the output bytes was attributable to any of five things and the
measurement was designed to attribute it to one.

`PRE-REGISTRATION-v4-CONFIRMATORY.md` adds the conditions, and this is the step that applies them.
It was written and anchored while measurement 4 had NO DATA -- no second-machine run existed under
this protocol -- which is the difference between a condition and an excuse.

⚠️ WHAT A PASS MEANS, AND WHAT IT DOES NOT. If both arms meet conditions 1-5 and the bytes differ,
that isolates the CPU only among the variables listed. Microcode, BIOS settings, kernel scheduling
and CPU features beyond the recorded SIMD baseline are neither held constant nor observed. This
answers *"do these two machines, matched on software, produce the same bytes"*. It does not answer
*"is CPU vendor the cause"*, and the record it writes says so in its own text.

⇒ A pair failing any condition is STILL REPORTED, labelled CONFOUNDED, naming every variable that
moved. That mirrors v3 §4 exactly: an absent observation is recorded, never fatal, and never
silently upgraded into a result.

    python measure_hardware.py --a runs/tpc-thr-1 --b runs/amd-thr-1
"""
import argparse
import io
import json
import pathlib
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent


def load(where):
    p = pathlib.Path(where)
    if p.is_dir():
        p = p / "run.json"
    if not p.exists():
        raise SystemExit(D + " no run record at %s" % p)
    return json.loads(p.read_text(encoding="utf-8")), p


def os_family(plat):
    """The family and major version, e.g. Windows-11 or Linux-5. Not the full string.

    ⚠ `platform.platform()` carries a build number that changes with every patch Tuesday. Matching
    on the whole string would call two identical systems different; matching on family alone would
    call Windows 10 and Windows 11 the same. Family plus major version is the honest granularity,
    and it is stated here rather than left to whoever reads the output.
    """
    if not plat:
        return None
    bits = str(plat).split("-")
    return "-".join(bits[:2]) if len(bits) > 1 else bits[0]


def conditions(a, b):
    """v4 §2 conditions 1-5. Returns [(n, name, ok, detail)]."""
    ea, eb = a["environment"], b["environment"]
    out = []

    fa, fb = os_family(ea.get("platform")), os_family(eb.get("platform"))
    out.append((1, "operating system recorded and matching", bool(fa and fb) and fa == fb,
                "%s vs %s" % (fa or "NOT RECORDED", fb or "NOT RECORDED")))

    pa = ".".join(str(ea.get("python", "")).split(".")[:2])
    pb = ".".join(str(eb.get("python", "")).split(".")[:2])
    out.append((2, "Python matching to major.minor", bool(pa and pb) and pa == pb,
                "%s vs %s" % (ea.get("python"), eb.get("python"))))

    out.append((3, "numpy matching exactly",
                bool(ea.get("numpy")) and ea.get("numpy") == eb.get("numpy"),
                "%s vs %s" % (ea.get("numpy"), eb.get("numpy"))))

    ka, kb = ea.get("blas_build_config_line"), eb.get("blas_build_config_line")
    # both-absent is admissible only if both say so; one absent is a moved variable
    out.append((4, "OpenBLAS build configuration matching",
                (ka == kb) and (ka is not None or kb is None),
                "%s vs %s" % (ka or "ABSENT", kb or "ABSENT")))

    obs_a = ea.get("blas_runtime_arch") is not None and ea.get("threads_effective") is not None
    obs_b = eb.get("blas_runtime_arch") is not None and eb.get("threads_effective") is not None
    out.append((5, "runtime architecture and effective threads OBSERVED in both", obs_a and obs_b,
                "A %s / B %s" % ("observed" if obs_a else "NOT OBSERVED",
                                 "observed" if obs_b else "NOT OBSERVED")))
    return out


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="configuration A run directory or run.json")
    ap.add_argument("--b", required=True, help="configuration B run directory or run.json")
    ap.add_argument("--out", default="MEASUREMENT-4.json")
    args = ap.parse_args()

    a, pa = load(args.a)
    b, pb = load(args.b)

    print("=" * 78)
    print("  MEASUREMENT 4 — bit-identity across hardware")
    print("=" * 78)
    print()
    print("  A  %-34s %s" % (a["environment"].get("cpu", "?")[:34], pa))
    print("  B  %-34s %s" % (b["environment"].get("cpu", "?")[:34], pb))
    print()

    # {D} THE INPUTS MUST BE THE SAME QUESTION. Comparing two runs of different specifications
    # would produce a difference that says nothing about hardware, and nothing else here checks it.
    same_input = True
    for key in ("spec", "corpus_merkle_root"):
        if a.get(key) != b.get(key):
            same_input = False
            print("  " + D + " THE TWO ARMS DO NOT SHARE %s. They are not the same experiment, "
                  "and no comparison below is meaningful." % key)
    if a["environment"].get("threads_requested") != b["environment"].get("threads_requested"):
        same_input = False
        print("  " + D + " the arms pinned different thread counts (%s vs %s). Thread count is a "
              "known cause of divergence in this pipeline; holding it fixed is not optional."
              % (a["environment"].get("threads_requested"),
                 b["environment"].get("threads_requested")))
    if not same_input:
        print()

    conds = conditions(a, b)
    for n, name, ok, detail in conds:
        print("  %s  %d. %-48s %s" % ("ok " if ok else D, n, name, detail))

    failed = [n for n, _name, ok, _d in conds if not ok]
    isolating = same_input and not failed

    identical = a.get("weights_sha256") == b.get("weights_sha256")
    print()
    print("  A weights  %s" % a.get("weights_sha256"))
    print("  B weights  %s" % b.get("weights_sha256"))
    print("  BIT-IDENTICAL: %s" % ("YES" if identical else "NO"))
    print()

    if not same_input:
        verdict = "NOT COMPARABLE"
        print("  " + D + " NOT COMPARABLE. The arms do not share an input specification, so the")
        print("  byte comparison above is not a measurement of anything.")
    elif failed:
        verdict = "CONFOUNDED"
        moved = ", ".join(str(n) for n in failed)
        print("  " + D + " CONFOUNDED. Condition(s) %s failed, so more than the CPU differs" % moved)
        print("  between these arms. The result above is REPORTED, as v4 §2 requires, and it may")
        print("  NOT be cited for a claim about CPU vendor. Nothing here is discarded; it is")
        print("  labelled.")
    else:
        verdict = "ISOLATING"
        print("  ok  ISOLATING, within the stated limits. Both arms meet conditions 1-5 and share")
        print("  an input specification, so among the variables this protocol observes, the CPU")
        print("  is what differs.")
        print()
        print("  " + W + " Microcode, BIOS settings, kernel scheduling and CPU features beyond the")
        print("  recorded SIMD baseline are NOT held constant and NOT observed. This answers")
        print("  'do these two machines, matched on software, produce the same bytes'. It does")
        print("  not establish that CPU vendor is the cause, and must not be written as though")
        print("  it did.")

    rec = {
        "_what": ("Measurement 4 under PRE-REGISTRATION-v4-CONFIRMATORY.md. The verdict labels "
                  "the COMPARISON, not the result: a confounded pair is reported, never dropped."),
        "verdict": verdict,
        "bit_identical": identical,
        "conditions": [{"n": n, "condition": name, "met": ok, "observed": detail}
                       for n, name, ok, detail in conds],
        "conditions_failed": failed,
        "same_input_specification": same_input,
        "arms": {
            "A": {"run": str(pa), "cpu": a["environment"].get("cpu"),
                  "weights_sha256": a.get("weights_sha256"), "environment": a["environment"]},
            "B": {"run": str(pb), "cpu": b["environment"].get("cpu"),
                  "weights_sha256": b.get("weights_sha256"), "environment": b["environment"]}},
        "_limits": ("An ISOLATING verdict isolates the CPU only among the variables listed in v4 "
                    "§2. Microcode, BIOS settings, kernel scheduling and CPU features beyond the "
                    "recorded SIMD baseline are neither held constant nor observed."),
    }
    (HERE / args.out).write_text(json.dumps(rec, indent=2) + NL, encoding="utf-8", newline=NL)
    print()
    print("  written to %s" % args.out)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
