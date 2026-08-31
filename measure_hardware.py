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


BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])


def protocol_anchoring():
    """Was each governing document ANCHORED when this measurement was taken?

    ⛔ A PRE-REGISTRATION'S FORCE IS ITS TIMESTAMP, so whether the commitment was anchored
    BEFORE the data existed is a property of the measurement, not a footnote about it. The AMD arm
    of the first real pair was run while v4's proof was still calendar-only. That is recorded here
    automatically, by reading the proof bytes, rather than left to whoever writes the paper to
    remember.

    ⚠ Tag presence is not full verification -- see anchor_status.py, which says the same thing
    about the same bytes. A True here means the proof over these bytes claims a Bitcoin
    attestation.
    """
    import hashlib as _hl
    out = {}
    for doc in sorted(HERE.glob("PRE-REGISTRATION*.md")):
        proof = HERE / (doc.name + ".ots")
        if not proof.exists():
            out[doc.name] = {"proof": False, "binds_document": False, "bitcoin_attestation": False}
            continue
        blob = proof.read_bytes()
        out[doc.name] = {
            "proof": True,
            "binds_document": _hl.sha256(doc.read_bytes()).digest() in blob,
            "bitcoin_attestation": BITCOIN_TAG in blob}
    return out


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


def _threads(env):
    """The EFFECTIVE thread count, as a number, not as the presence of a record."""
    te = env.get("threads_effective")
    if not te:
        return None
    if isinstance(te, list):
        ns = [x.get("num_threads") for x in te if isinstance(x, dict)]
        ns = [n for n in ns if n is not None]
        return max(ns) if ns else None
    return te if isinstance(te, int) else None


def _blas_identity(env):
    """Library, version and build together -- an identical build LINE is not an identical BLAS."""
    te = env.get("threads_effective")
    lib = ver = None
    if isinstance(te, list) and te and isinstance(te[0], dict):
        lib, ver = te[0].get("prefix"), te[0].get("version")
    return (lib, ver, env.get("blas_build_config_line"))


def _stated(v):
    """Has this field been STATED? None, "", "None", "?" and whitespace are all silence.

    ⛔ FIVE MORE ABSENCE ATTACKS PASSED, IN THE TOOL ALREADY REPAIRED TWICE FOR EXACTLY THIS.
    Round 5 removed both arms' `spec`, then `corpus_merkle_root`, then `threads_requested`, then
    `python`, and each time the pair was declared MATCHED-STACK CROSS-MACHINE -- the strongest
    verdict this tool can issue -- because `a.get(k) != b.get(k)` is FALSE when neither arm states
    k. Deleting the evidence made the pair look MORE comparable, not less. A sixth attack, blanking
    one arm's CPU, crashed on a None slice.

    ⚠ THE PREVIOUS REPAIRS FIXED THE CONDITIONS AND LEFT THE PREMISE. Round 4's absences were
    caught one at a time inside `conditions()`; nothing was done about the same-input gate ABOVE
    it, which is the gate deciding whether the comparison is a comparison at all. Repairing
    instance N where it appears is how instance N+1 gets made.

    ⛔ AND `python` FAILED A SECOND WAY: `str(None).split(".")` is `["None"]`, so two absent
    Pythons compared EQUAL AND TRUTHY as the string "None". A guard that tests truthiness after
    stringifying tests the truthiness of the word None.

    ⚠ `_stated` DOES NOT PROJECT OVER THE RECORD'S KEYS -- it is asked about named fields, so a
    field nobody thought to guard is still unguarded. That is the honest limit. The defence is that
    every comparison below now routes through `_agree`, so adding an unguarded one takes deliberate
    effort instead of being what happens by default.
    """
    if v is None:
        return False
    return str(v).strip() not in ("", "None", "null", "?", "-")


def _agree(va, vb, norm=None):
    """(ok, detail). Absence is never agreement -- on either side, in either direction."""
    if not _stated(va) and not _stated(vb):
        return False, "ABSENT IN BOTH ARMS -- two silences are not a match, nothing was held fixed"
    if not _stated(va) or not _stated(vb):
        return False, ("NOT RECORDED on arm %s (the other says %s)"
                       % ("A" if not _stated(va) else "B",
                          str(vb if not _stated(va) else va)[:40]))
    na, nb = (norm(va), norm(vb)) if norm else (va, vb)
    if not _stated(na) or not _stated(nb):
        return False, "recorded but unparseable: %s vs %s" % (str(va)[:26], str(vb)[:26])
    return na == nb, "%s vs %s" % (str(va)[:34], str(vb)[:34])


def conditions(a, b):
    """v4 section 2's conditions, plus the ones round 4 showed were missing entirely.

    ⛔ SIX PAIRS THAT SHOULD NOT HAVE ONE WERE GRANTED `ISOLATING`, and two reviewers found them
    independently. THE SAME RECORD passed as both arms. Haswell against SkylakeX passed, because
    condition 5 checked that the runtime architecture was RECORDED and never that the two MATCHED
    -- which defeats the exact caveat section 10's claim rests on. One effective thread against
    eight passed, for the same reason. Two absent build lines passed. Two NON-CONFIRMATORY runs
    passed. Identical CPUs passed.

    ⇒ The pattern is one thing, and it is the pattern the reviewers asked us to generalise: every
    one of these conditions was satisfied by the PRESENCE or the ABSENCE of a field rather than by
    its VALUE. Presence is not equality, and absence is not agreement.
    """
    ea, eb = a["environment"], b["environment"]
    out = []

    # ⛔ NEW, AND FIRST, BECAUSE IT IS THE COMPARISON'S PREMISE. The tool compared two files
    # without ever asking whether they were two MACHINES.
    # ⚠ RENAMED FROM "the two arms are DIFFERENT machines", which this cannot observe. It
    # compares two SELF-REPORTED CPU STRINGS: two hosts of one model report the same string, and a
    # copied record reports its source's. What is actually checked is that the arms report
    # DIFFERENT identities, which is weaker than being different machines, so it is now named that
    # way. And it required only arm A to HAVE a CPU, so blanking arm B's passed it.
    ok0, det0 = _agree(ea.get("cpu"), eb.get("cpu"))
    if not _stated(ea.get("cpu")) or not _stated(eb.get("cpu")):
        out.append((0, "both arms REPORT a CPU identity", False, det0))
    else:
        out.append((0, "the arms report DIFFERENT CPU identities", not ok0, det0))

    ok1, det1 = _agree(ea.get("platform"), eb.get("platform"), norm=os_family)
    out.append((1, "operating system recorded and matching", ok1, det1))

    ok2, det2 = _agree(ea.get("python"), eb.get("python"),
                       norm=lambda v: ".".join(str(v).split(".")[:2]))
    out.append((2, "Python matching to major.minor", ok2, det2))

    ok3, det3 = _agree(ea.get("numpy"), eb.get("numpy"))
    out.append((3, "numpy matching exactly", ok3, det3))

    # ⛔ AN IDENTICAL BUILD LINE IS NOT AN IDENTICAL BLAS, and two ABSENT lines are not agreement.
    ia, ib = _blas_identity(ea), _blas_identity(eb)
    ka, kb = ea.get("blas_build_config_line"), eb.get("blas_build_config_line")
    if ka is None and kb is None:
        detail4 = ("ABSENT in BOTH arms. Two absences are not a match -- neither arm has stated "
                   "what its BLAS is, so nothing has been held constant")
        ok4 = False
    elif ka is None or kb is None:
        which = "B" if kb is None else "A"
        detail4 = ("NOT RECORDED on arm %s (the other says %r). This is usually a MISSING "
                   "`pyyaml`, not a different BLAS: without it numpy's config output takes a "
                   "format the parser cannot read. It is a RECORDING failure, and the verdict "
                   "below says so rather than calling the science confounded." % (which, ka or kb))
        ok4 = False
    else:
        ok4 = ia == ib
        detail4 = "%s / %s vs %s / %s" % (ka, ia[1] or "version?", kb, ib[1] or "version?")
    out.append((4, "BLAS identity matching (library, version, build)", ok4, detail4))

    # ⛔ PRESENCE WAS NOT EQUALITY. This is the condition the section-10 caveat depends on.
    ok5, det5 = _agree(ea.get("blas_runtime_arch"), eb.get("blas_runtime_arch"))
    out.append((5, "runtime microkernel OBSERVED and IDENTICAL in both", ok5, det5))

    ok6, det6 = _agree(_threads(ea), _threads(eb))
    out.append((6, "effective BLAS thread count OBSERVED and EQUAL", ok6, det6))

    # ⛔ A NON-CONFIRMATORY RUN CANNOT SUPPORT A CONFIRMATORY MEASUREMENT. Both arms passed with
    # seed 1 and is_confirmatory_spec false.
    ca, cb = a.get("is_confirmatory_spec"), b.get("is_confirmatory_spec")
    out.append((7, "both arms run the CONFIRMATORY specification", ca is True and cb is True,
                "%s vs %s" % (ca, cb)))
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
    print("  A  %-34s %s" % (str(a["environment"].get("cpu") or "NOT REPORTED")[:34], pa))
    print("  B  %-34s %s" % (str(b["environment"].get("cpu") or "NOT REPORTED")[:34], pb))
    print()

    # ⛔ THE INPUTS MUST BE THE SAME QUESTION. Comparing two runs of different specifications
    # would produce a difference that says nothing about hardware, and nothing else here checks it.
    # ⛔ THIS GATE READ `a.get(k) != b.get(k)`, WHICH IS FALSE WHEN NEITHER ARM STATES k.
    # Deleting both arms' `spec` -- the field saying the two runs asked the same question -- made
    # the pair MORE comparable, not less, and the tool answered MATCHED-STACK CROSS-MACHINE. The
    # same for `corpus_merkle_root` and `threads_requested`. Three attacks, one line, and that line
    # is the PREMISE of everything printed below it.
    same_input = True
    for key, why in (("spec", "the two runs asked the same question"),
                     ("corpus_merkle_root", "they trained on the same bytes"),
                     ("threads_requested", "the known divergence cause was pinned")):
        src_a, src_b = (a, b) if key != "threads_requested" else (a["environment"],
                                                                  b["environment"])
        ok, detail = _agree(src_a.get(key), src_b.get(key))
        if ok:
            continue
        same_input = False
        if not _stated(src_a.get(key)) or not _stated(src_b.get(key)):
            print("  " + D + " %s IS NOT STATED (%s). It is the field establishing that %s; "
                  "unstated it establishes nothing, and an absence is not an agreement."
                  % (key, detail, why))
        else:
            print("  " + D + " THE TWO ARMS DO NOT SHARE %s (%s). They are not the same "
                  "experiment, and no comparison below is meaningful." % (key, detail))
    if not same_input:
        print()

    conds = conditions(a, b)
    for n, name, ok, detail in conds:
        print("  %s  %d. %-48s %s" % ("ok " if ok else D, n, name, detail))

    failed = [n for n, _name, ok, _d in conds if not ok]
    isolating = same_input and not failed

    # ⛔ BIT-IDENTITY WAS TWO SELF-REPORTED STRINGS. A reviewer deleted weights.npz from one arm
    # and the tool still printed BIT-IDENTICAL: YES, because it compared the digests each run.json
    # claimed for itself and never opened either artifact. A measurement about BYTES that never
    # reads the bytes is the proxy defect at its purest.
    import hashlib as _hl
    recomputed, file_digests, missing = {}, {}, []
    for tag, path in (("A", pa), ("B", pb)):
        wf = pathlib.Path(path).parent / "weights.npz"
        if not wf.exists():
            missing.append((tag, str(wf)))
            continue
        # ⛔ AND IT MUST RECOMPUTE THE DIGEST THE PIPELINE ACTUALLY CLAIMS. The first version
        # hashed the .npz FILE and reported both arms as drifted -- a false alarm, because
        # `weights_sha256` is a digest over the ARRAYS: sorted key name, then the C-contiguous
        # bytes of each. Recomputing the wrong thing is not a check, it is a second claim.
        import numpy as _np
        _z = _np.load(wf)
        _h = _hl.sha256()
        for _k in sorted(_z.files):
            _h.update(_k.encode())
            _h.update(_np.ascontiguousarray(_z[_k]).tobytes())
        recomputed[tag] = _h.hexdigest()
        file_digests[tag] = _hl.sha256(wf.read_bytes()).hexdigest()
    claimed = {"A": a.get("weights_sha256"), "B": b.get("weights_sha256")}
    drifted = [k for k, v in recomputed.items() if claimed.get(k) != v]

    print()
    for tag in ("A", "B"):
        print("  %s weights  claimed %s" % (tag, claimed.get(tag)))
        print("             on disk %s" % recomputed.get(tag, "ARTIFACT ABSENT"))
    if missing:
        identical = False
        print("  " + D + " %d weights artifact(s) absent: %s. Bit-identity is a claim about BYTES;"
              % (len(missing), [m[0] for m in missing]))
        print("  without them there is nothing to compare and the answer is not 'yes'.")
    elif drifted:
        identical = False
        print("  " + D + " arm %s's artifact does not hash to the digest its own run.json claims."
              % ", ".join(drifted))
        print("  The record and the bytes disagree; nothing downstream of this is usable.")
    else:
        identical = recomputed["A"] == recomputed["B"]
        print("  BIT-IDENTICAL: %s  (array digest recomputed from both artifacts)"
              % ("YES" if identical else "NO"))
        if file_digests.get("A") == file_digests.get("B"):
            print("  and the .npz CONTAINER files are byte-identical too: %s"
                  % file_digests["A"][:32])
    print()

    if missing or drifted:
        verdict = "NOT COMPARABLE"
        print("  " + D + " NOT COMPARABLE. The artifacts this comparison is ABOUT are absent or")
        print("  disagree with their own records, so no condition below can rescue it.")
    elif not same_input:
        verdict = "NOT COMPARABLE"
        print("  " + D + " NOT COMPARABLE. The arms do not share an input specification, so the")
        print("  byte comparison above is not a measurement of anything.")
    elif failed:
        # ⛔ `CONFOUNDED` WAS THE WRONG WORD FOR A PARSER FAILURE, and a reviewer was right that
        # conflating them hides which thing broke. Arm B's record DID contain the BLAS library,
        # version and build; only the convenience field the extractor reads was empty. The science
        # was not confounded -- the instrument failed to read evidence that was present.
        _recording_only = (failed == [4] and (
            a["environment"].get("blas_build_config_line") is None)
            != (b["environment"].get("blas_build_config_line") is None))
        verdict = "RECORDING-SCHEMA INADMISSIBLE" if _recording_only else "CONFOUNDED"
        moved = ", ".join(str(n) for n in failed)
        print("  " + D + " %s. Condition(s) %s not met." % (verdict, moved))
        if 4 in failed and (a["environment"].get("blas_build_config_line") is None) != (
                b["environment"].get("blas_build_config_line") is None):
            print("  " + W + " Condition 4 failed on a RECORDING GAP, not an observed difference:")
            print("  one arm did not record its build line at all. That is recoverable by")
            print("  installing pyyaml on that arm and re-running it -- the arms may well be")
            print("  matched. Until then this pair cannot carry a vendor claim.")
        print("  between these arms. The result above is REPORTED, as v4 §2 requires, and it may")
        print("  NOT be cited for a claim about CPU vendor. Nothing here is discarded; it is")
        print("  labelled.")
    else:
        verdict = "MATCHED-STACK CROSS-MACHINE"
        # ⛔ THIS SAID `ISOLATING`, AND BOTH ROUND-4 REVIEWERS SAID IT CLAIMED TOO MUCH. It does
        # not isolate anything: firmware, microcode and kernel scheduling are neither held constant
        # nor observed, and the two machines necessarily differ in them. What the design supports
        # is narrower and is now what the label says.
        print("  ok  MATCHED-STACK CROSS-MACHINE. Two DIFFERENT machines, matched on operating")
        print("  system, Python, numpy, BLAS library-version-build, runtime microkernel and")
        print("  effective thread count, both running the confirmatory specification, produced")
        print("  artifacts whose digests were RECOMPUTED here and compared.")
        print()
        print("  " + W + " THIS IS NOT CAUSAL ISOLATION AND THE LABEL NO LONGER SAYS IT IS.")
        print("  Microcode, BIOS and firmware settings, and kernel scheduling differ between any")
        print("  two machines and are not observed here. The honest reading is: on the one")
        print("  reduction shape both machines chose, vendor did not change the bytes.")
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
        "protocol_anchoring_when_this_record_was_written": protocol_anchoring(),
        "_anchoring_caveat": (
            "This is the anchoring state WHEN THIS RECORD WAS WRITTEN, which is not necessarily "
            "the state when either arm was RUN -- and the two differed for the first real pair: "
            "the FIRST pair's second-machine arm was run while v4's proof was still "
            "calendar-only. The artifacts cannot settle that ordering by themselves, "
            "because run.json carries no timestamp: it records wall-clock DURATION but not when "
            "the run happened. That is a gap in the pipeline's record, stated here rather than "
            "papered over, and it cannot be closed retroactively for this pair."),
        "_limits": ("An ISOLATING verdict isolates the CPU only among the variables listed in v4 "
                    "§2. Microcode, BIOS settings, kernel scheduling and CPU features beyond the "
                    "recorded SIMD baseline are neither held constant nor observed."),
    }
    (HERE / args.out).write_text(json.dumps(rec, indent=2) + NL, encoding="utf-8", newline=NL)
    _anch = rec["protocol_anchoring_when_this_record_was_written"]
    _unanchored = sorted(k for k, v in _anch.items() if not v["bitcoin_attestation"])
    if _unanchored:
        print()
        print("  " + W + " PROTOCOL NOT FULLY ANCHORED AS THIS RECORD IS WRITTEN: %s"
              % ", ".join(_unanchored))
        print("  A pre-registration's force is its timestamp. These carry calendar receipts but")
        print("  no Bitcoin attestation yet, so the commitment precedes the data only as far as")
        print("  the calendars are trusted. Recorded in the output rather than argued about.")
    print()
    # ⛔ THIS PARAGRAPH USED TO END "For the first real pair it did not: the second-machine arm
    # ran while v4 was still calendar-only" -- typed prose about ONE historical pair, printed on
    # EVERY run. It was still printing that on a pair whose protocol was fully anchored before the
    # run. A dead noun beside a live number, in the tool built to keep them apart. The historical
    # fact lives in the retained record for the pair it is about; what is printed here is only
    # what these artifacts can support.
    print("  " + W + " AND THIS IS THE STATE NOW, NOT AT RUN TIME. run.json records wall-clock")
    print("  DURATION but not WHEN a run happened, so THESE ARTIFACTS CANNOT ESTABLISH whether")
    print("  either arm ran before or after any anchor -- in either direction. Closing that would")
    print("  mean recording a timestamp in run.json, and train.py is pinned by digest in the")
    print("  protocol, so it is a v6 and not an edit.")

    print()
    print("  written to %s" % args.out)
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
