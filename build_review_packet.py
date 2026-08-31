"""Assemble the internal-review packet for Paper B, with every figure measured here.

⛔ WHY THIS IS NOT A TEMPLATE WITH THE NUMBERS TYPED IN. Paper A's review packet opened with the
sentence "every number here is measured at build time" and carried `round 9` as a string literal
through two further rounds of work, with a covering note describing a finding from the round before
that. The live numbers were live and the noun beside them was dead. This reads the measurement
files and refuses to write if one is missing.

    python build_review_packet.py
"""
import hashlib
import io
import json
import pathlib
import subprocess
import sys
import zipfile

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "review"

SEND = (
    ("PRE-REGISTRATION-v3-CONFIRMATORY.md", "THE CONFIRMATORY PROTOCOL -- READ THIS FIRST"),
    ("PRE-REGISTRATION-v3-CONFIRMATORY.md.ots", "its proof"),
    ("PRE-REGISTRATION-v2-CONFIRMATORY.md", "version 2, superseded, retained as record"),
    ("PRE-REGISTRATION-v2-CONFIRMATORY.md.ots", "its proof"),
    ("anchor_status.py", "the proof check -- run it; a pass is narrower than it sounds"),
    ("ENVIRONMENT-LOCK.json", "interpreter and library, recorded not locked"),
    ("MEASUREMENT-2.json", "storage overhead, from measure_storage.py"),
    ("measure_storage.py", "measurement 2's derivation, with its boundary declared"),
    ("PRE-REGISTRATION.md", "version 1, now the PILOT protocol"),
    ("PRE-REGISTRATION.md.ots", "its proof, ANCHORED in a Bitcoin block"),
    ("PILOT-2026-08-29.md", "the observation that made the thread pin part of the protocol"),
    ("AMENDMENT-2026-08-30.md", "a deviation from section 2b, recorded on the day"),
    ("PHASE-2-FINDINGS.md", "what the pipeline found"),
    ("MEASUREMENT-1.json", "the cost of determinism, 11 interleaved reps"),
    ("MEASUREMENT-6.md", "engineering hours, self-reported and flagged as the weakest evidence"),
    ("REPRODUCTION-CALL.md", "the open request, written to section 2b"),
    ("PUBLICATION-CHECKLIST.md", "the decisions that must be made in the act of publishing"),
    ("train.py", "the pipeline"),
    ("build_package.py", "what a reproducer receives"),
    ("verify_package.py", "the package run as a stranger would"),
    ("build_review_packet.py", "this packet's own builder -- a reviewer asked for it"),
    ("REVIEW-ROUNDS.json", "the round record the covering note is generated from"),
    ("measure_cost.py", "measurement 1's instrument"),
    ("reproduce_findings.py",
     "re-derives the headline findings from scratch -- five runs, no timing, so a"
     " reviewer checks the RESULTS rather than the prose"),
    ("corpus/MANIFEST.json", "the corpus and its Merkle root"),
    ("corpus/MANIFEST.json.ots", "committed BEFORE the first training step, now anchored"),
    ("corpus/build_corpus.py", "the corpus derivation, pinned by digest"),
    ("corpus/sources.json", "the ten texts and where they came from, pinned by digest"),
    ("corpus/verify_shipped.py",
     "checks a SHIPPED corpus using only what a package contains -- build_corpus.py --verify "
     "cannot, because it re-derives from raw/ and raw/ is not shipped"),
    ("PRE-REGISTRATION-v4-CONFIRMATORY.md",
     "measurement 4's admissibility, committed while measurement 4 had NO data"),
    ("PRE-REGISTRATION-v4-CONFIRMATORY.md.ots", "its proof"),
    ("PRE-REGISTRATION-v5-CONFIRMATORY.md",
     "THE DIGEST COMMITMENTS, re-committed after v3 §2 went unenforced for a day"),
    ("PRE-REGISTRATION-v5-CONFIRMATORY.md.ots", "its proof"),
    ("check_commitments.py",
     "the control that enforces the digest commitments -- v3 §2 was prose, and was broken the "
     "next day without anything noticing"),
    ("measure_hardware.py", "measurement 4's instrument, which labels the COMPARISON"),
    ("MEASUREMENT-4-confounded-no-pyyaml.json",
     "the first hardware pair: bit-identical AND confounded, retained as record"),
    ("MEASUREMENT-4-RUNBOOK.md", "the second-machine procedure, and the two errors it contained"),
    ("MEASUREMENT-5-7.json", "measurements 5 and 7, computed rather than typed"),
    ("measure_divergence.py", "their instrument, including the seed-sensitivity arm"),
    ("seed_sensitivity.py", "the seed arm's driver"),
    # ⛔ THE ROUND'S ONE NEW RESULT SHIPPED WITH NONE OF ITS EVIDENCE. The packet printed
    # "m4 ... MATCHED-STACK ... bit-identical True" from MEASUREMENT-4.json while that file was
    # EXCLUDED with the reason "absent until measurement 4 is retaken" -- false, it was on disk and
    # the packet could only print from it by opening it. Neither arm's run.json shipped either,
    # because unclassified() globbed *.py/*.md/*.json beside the builder and never looked in
    # runs/. A reviewer found all of it and called it round 4's own headline defect inside round
    # 4's own fix. They were right.
    ("MEASUREMENT-4.json", "THE RESULT, with both arms' environments and every condition"),
    ("runs/tpc-thr-1/run.json", "arm A's run record -- rehash it"),
    ("runs/amd-thr-1/run.json", "arm B's run record -- rehash it"),
    ("runs/tpc-thr-1/weights.npz", "arm A's artifact, so bit-identity can be recomputed"),
    ("runs/amd-thr-1/weights.npz", "arm B's artifact, so bit-identity can be recomputed"),
    ("runs/amd-thr-1-no-pyyaml/run.json",
     "the first pair's arm B, retained: bit-identical AND inadmissible"),
    # the divergence runs MEASUREMENT-5-7.json is computed from -- found by the same coverage
    # check, one layer down: a measurement that names a run and does not ship it is the same
    # defect as m4's, and there were five more of them.
    ("runs/thr-1/run.json", "measurement 5/7 reference arm, 1 thread"),
    ("runs/thr-2/run.json", "measurement 5/7, 2 threads"),
    ("runs/thr-4/run.json", "measurement 5/7, 4 threads"),
    ("runs/thr-8/run.json", "measurement 5/7, 8 threads"),
    ("runs/thr-16/run.json", "measurement 5/7, 16 threads"),
    ("test_controls.py",
     "every attack round 4 used, as a suite -- the positive controls were prose and both "
     "reviewers broke the tools they described"),
)

# {D} SEND WAS A HAND-KEPT LIST AND IT HAD ALREADY DRIFTED TWICE OVER: `anchor_status.py` appeared
# in it TWICE, so the zip carried a duplicate entry -- silently, because zipfile only warns -- and
# every file added by two rounds of work was missing from a packet whose entire job is to show a
# reviewer everything. A reader would have judged the round on an artifact that omitted the
# governing protocol version, the control enforcing its digests, and the measurement instrument.
#
# ⇒ The descriptions stay curated, because they carry judgement a projection cannot. What is
# PROJECTED is the coverage check: every candidate file must be named in SEND or excused by name.
EXCLUDED = {
    "REVIEW-ROUNDS.json": "listed above; kept here so the excuse list is exhaustive",
}

# ⛔ AN EXCUSE THAT CLAIMS ABSENCE MUST BE TRUE. MEASUREMENT-4.json was excused as "absent until
# measurement 4 is retaken" while sitting on disk and being READ by this very script eighty lines
# later. The coverage check verified that every file was NAMED and never that the naming was
# accurate -- a control satisfied by the DESCRIPTION of the thing it checks, which is the exact
# generalisation a round-4 reviewer drew from the round's other defects.
_ABSENCE_WORDS = ("absent", "does not exist", "not yet", "pending", "until ")


def false_excuses(here):
    """Excuses that claim a file is absent while it sits on disk."""
    bad = []
    for rel, why in EXCLUDED.items():
        if (here / rel).exists() and any(w in why.lower() for w in _ABSENCE_WORDS):
            bad.append("%s is excused as %r and EXISTS" % (rel, why[:60]))
    return bad


def unclassified(here):
    """Files a reviewer could reasonably expect, that SEND neither ships nor excuses.

    ⚠ THIS GLOBBED BESIDE THE BUILDER AND NEVER LOOKED IN runs/, so the measurement records the
    packet quotes were invisible to the coverage check that exists to notice missing work.
    """
    named = {rel for rel, _why in SEND} | set(EXCLUDED)
    seen = []
    for pat in ("*.py", "*.md", "*.json", "*.ots"):
        seen += [p.relative_to(here).as_posix() for p in here.glob(pat)]
        seen += [p.relative_to(here).as_posix() for p in (here / "corpus").glob(pat)]
    # every run record referenced by a shipped measurement must itself be shipped or excused
    for run_json in sorted((here / "runs").glob("*/run.json")):
        rel = run_json.relative_to(here).as_posix()
        if rel not in named and _cited_by_a_measurement(here, run_json.parent.name):
            seen.append(rel)
    return sorted(set(seen) - named)


def _cited_by_a_measurement(here, run_name):
    """Does any shipped MEASUREMENT record name this run directory?"""
    for m in here.glob("MEASUREMENT-*.json"):
        try:
            if run_name in m.read_text(encoding="utf-8"):
                return True
        except OSError:
            continue
    return False


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    missing = [rel for rel, _ in SEND if not (HERE / rel).exists()]
    if missing:
        raise SystemExit(chr(0x26D4) + " the packet promises files that do not exist: %s" % missing)

    m1 = json.loads((HERE / "MEASUREMENT-1.json").read_text(encoding="utf-8"))
    m2 = json.loads((HERE / "MEASUREMENT-2.json").read_text(encoding="utf-8"))
    run = json.loads((HERE / "runs" / "det-1" / "run.json").read_text(encoding="utf-8"))
    man = json.loads((HERE / "corpus" / "MANIFEST.json").read_text(encoding="utf-8"))

    # the thread sweep, read from the runs rather than remembered
    sweep = {}
    for n in (1, 2, 4, 8, 16):
        p = HERE / "runs" / ("thr-%d" % n) / "run.json"
        if p.exists():
            sweep[n] = json.loads(p.read_text(encoding="utf-8"))["weights_sha256"]
    if len(sweep) != 5:
        raise SystemExit(chr(0x26D4) + " the thread sweep is incomplete: %s" % sorted(sweep))

    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(HERE),
                            capture_output=True, text=True).stdout.strip() or "unknown"
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(HERE),
                           capture_output=True, text=True).stdout.strip()

    OUT.mkdir(exist_ok=True)
    zp = OUT / "paper-b-review.zip"
    _dupes = sorted({r for r, _w in SEND if [x for x, _ in SEND].count(r) > 1})
    if _dupes:
        raise SystemExit(D + " SEND names the same file twice: %s. A duplicate zip entry is "
                         "written silently and a reader may extract either copy, so this is a "
                         "substitution vector, not a cosmetic slip." % _dupes)
    _missing = [rel for rel, _w in SEND if not (HERE / rel).exists()]
    if _missing:
        raise SystemExit(D + " SEND names %d file(s) that do not exist: %s" % (len(_missing),
                                                                              _missing))
    _fe = false_excuses(HERE)
    if _fe:
        raise SystemExit(D + " an excuse claims a file is absent and the file is on disk:" + NL
                         + NL.join("      " + x for x in _fe) + NL
                         + "  A coverage check that verifies a file is NAMED and not that the "
                         + "naming is TRUE is satisfied by a description of the thing it checks.")
    _un = unclassified(HERE)
    if _un:
        raise SystemExit(D + " file(s) in neither SEND nor EXCLUDED: " + NL
                         + NL.join("      " + u for u in _un) + NL
                         + "  Ship each or excuse it by name. A review packet that omits work the "
                         + "round did is a packet the reviewer cannot judge the round from.")

    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, _why in SEND:
            z.write(HERE / rel, rel)
        # ⛔ THE CORPUS TEXTS WERE MISSING FROM THIS ZIP. The packet told reviewers to run
        # `python reproduce_findings.py`, which calls train.py, which reads corpus/clean/*.txt --
        # and the zip shipped corpus/MANIFEST.json without the files it describes. The instruction
        # could not be followed. A reviewer had to copy them out of the embedded package by hand
        # before the advertised workflow would start.
        for f in sorted((HERE / "corpus" / "clean").glob("*.txt")):
            z.write(f, "corpus/clean/" + f.name)
        for p in sorted((HERE / "package").rglob("*")):
            if p.is_file():
                z.write(p, str(p.relative_to(HERE)).replace(chr(92), "/"))
        # the reference bundle, so a reviewer can audit the configuration-A numbers rather than
        # only re-derive their own
        for f in sorted((HERE / "reference").rglob("*")):
            if f.is_file():
                z.write(f, str(f.relative_to(HERE)).replace(chr(92), "/"))
    zsha = hashlib.sha256(zp.read_bytes()).hexdigest()

    L = []
    A = L.append
    # ⛔ EVERY CLAIM IN THIS PACKET IS NOW LIFTED FROM PHASE-2-FINDINGS.md, NOT RETYPED.
    # The round-1 packet was circulated carrying "+37%", "step 8", "83%" and "numerically
    # indistinguishable" -- all four withdrawn in the findings document it claimed to summarise --
    # because the covering note was a hardcoded string and a patch that was supposed to update it
    # silently matched nothing and reported success. Both reviewers read the contradiction.
    #
    # So the note is EXTRACTED, and a cross-check below refuses to write a packet whose numbers do
    # not appear in the findings.
    _find = (HERE / "PHASE-2-FINDINGS.md").read_text(encoding="utf-8")
    _round = json.loads((HERE / "REVIEW-ROUNDS.json").read_text(encoding="utf-8"))
    _last = max(_round["rounds"], key=lambda r: r["round"])
    A("# Paper B (`reproduction`) — internal review packet, round %d" % (_last["round"] + 1))
    A("")
    A("*Every figure below is read from the measurement files, and every claim is lifted from "
      "`PHASE-2-FINDINGS.md` rather than retyped. `build_review_packet.py` refuses to write if a "
      "figure it prints is absent from that document.*")
    A("")
    A("## ⇒ SEND THESE TWO")
    A("")
    A("```")
    # ⛔ THIS PRINTED len(SEND) + 1 -- 41 -- WHILE THE ZIP HELD 108 MEMBERS. The zip also
    # carries corpus/clean/, package/ and reference/ by projection, so a count taken from the
    # NAMED list was never the count of the artifact. A reader checking the packet against the
    # file it describes would have found it wrong on the first line of the first block.
    A("paper-b-review.zip     %d files" % len(zipfile.ZipFile(zp).namelist()))
    A("  sha256 %s" % zsha)
    A("this file")
    A("```")
    A("")
    A("Repository `provenance-laboratory/reproduction`, commit `%s`%s."
      % (commit, "  ⚠️ TREE DIRTY" if dirty else ""))
    A("")
    A("---")
    A("")
    A("## ★ THE COVERING NOTE — paste this verbatim")
    A("")
    A("> **This is round %d.** %s" % (_last["round"] + 1, _last["summary"]))
    A(">")
    for _line in _last["changed"]:
        A("> - %s" % _line)
    A(">")
    A("> ⚠️ **%s**" % _last["deadline"])
    A("")
    A("## ⭐ CHECK THE FINDINGS, NOT ONLY THE PACKAGING")
    A("")
    A("```")
    A("python reproduce_findings.py     five training runs, ~2 minutes, nothing timed")
    A("```")
    A("")
    A("It re-derives the thread partition and the divergence table **on YOUR stack**, from "
      "nothing but the corpus and `train.py`.")
    A("")
    A("⛔ **It does not adjudicate the findings, and an earlier version of this packet said "
      "it did.** The sentence read *if its numbers disagree with PHASE-2-FINDINGS.md, the "
      "findings are wrong* — which is false, because the script measures a DIFFERENT "
      "MACHINE. A reviewer whose stack produced one digest across all five thread counts got "
      "exactly that disagreement, and the script itself said correctly that this does not "
      "contradict configuration A while the packet said it did. Both could not be true.")
    A("")
    A("⇒ To audit the CONFIGURATION-A numbers rather than your own, use the reference "
      "bundle: `reference/` ships the arrays and `MEASUREMENT-5-7.json` the derived values, so "
      "the published figures can be recomputed from published bytes without training anything.")
    A("")
    A("```")
    A("python verify_package.py         the package run in a directory it has never seen")
    A("```")
    A("")
    A("## What is measured, and by what")
    A("")
    A("```")
    A("m1  cost of pinning     ratio %.3f  95%% CI [%.3f, %.3f]  sign-test p=%.1e  %d pairs"
      % (m1["ratio_of_medians"], m1["bootstrap_95_ratio"][0], m1["bootstrap_95_ratio"][1],
         m1["sign_test_p"], m1["reps"]))
    A("      threads=1  median %.2f s      threads=%s median %.2f s"
      % (m1["median_a"], m1["threads_b"], m1["median_b"]))
    A("      BLOCKED alternation, paired, execution order kept; both arms PINNED.")
    A("      order effect: AB %.4f vs BA %.4f -- the design's own control, printed"
      % (m1["order_effect"]["AB_median_ratio"], m1["order_effect"]["BA_median_ratio"]))
    A("      ⚠ the p is a SIGN TEST, not the randomisation distribution of a")
    A("      balanced design, whose space is C(n, n/2) rather than 2^n")
    A("      -> report as: roughly +%d%%, CI [+%d%%, +%d%%]. NOT as a decimal percentage"
      % (round((m1["ratio_of_medians"] - 1) * 100),
         round((m1["bootstrap_95_ratio"][0] - 1) * 100),
         round((m1["bootstrap_95_ratio"][1] - 1) * 100)))
    A("m2  apparatus           %d bytes on %d of artifact (%.3f%%); %d if train.py and"
      % (m2["apparatus_bytes"], m2["artifact_bytes"], m2["percent_of_artifact"],
         m2["apparatus_excluding_arguable_bytes"]))
    A("      build_corpus.py are called artifact instead -- the boundary is arguable and")
    A("      measure_storage.py reports it both ways. Timestamp proofs: %d bytes"
      % m2["timestamp_proof_bytes"])
    A("      " + chr(0x26a0) + " the PERCENTAGE does not transfer: the apparatus is near-")
    A("      constant and this artifact is deliberately tiny")
    _n_dig = len(m1["distinct_digests"][m1["threads_a"]])
    A("m3  REPEATABILITY, same hw %s"
      % ("one digest across %d runs at threads=%s" % (m1["reps"], m1["threads_a"])
         if _n_dig == 1
         else chr(0x26D4) + " %d DISTINCT DIGESTS: not even repeatable" % _n_dig))
    A("      " + chr(0x26D4) + " NOT REPORTED AS BIT-IDENTITY. Section 6 makes that an")
    A("      invalidating condition without an independent re-run. The previous revision of")
    A("      the findings said measurement 3 -HOLDS-; that was a violation and is withdrawn.")
    # ⛔ THIS SAID "NOT MEASURED" IN A PACKET SHIPPING THE FINDINGS THAT SAY IT WAS.
    # Three typed statements about measurement 4's status survived the measurement being taken --
    # the dead-noun defect in the file whose first line promises every figure is measured at build
    # time. The status is read from MEASUREMENT-4.json now, so it cannot be stale here and current
    # one file away.
    _m4p = HERE / "MEASUREMENT-4.json"
    if _m4p.exists():
        _m4 = json.loads(_m4p.read_text(encoding="utf-8"))
        A("m4  bit-identity, diff hw  %s -- %s, bit-identical %s"
          % (_m4["verdict"], _m4["arms"]["B"]["cpu"][:34], _m4["bit_identical"]))
    else:
        A("m4  bit-identity, diff hw  NOT MEASURED -- needs a second machine")
    _md = json.loads((HERE / "MEASUREMENT-5-7.json").read_text(encoding="utf-8"))
    _m5 = _md["m5_threads_1_vs_16"]
    A("m5  divergence            step 0 in EVERY array (trace records step -1 as the initial")
    A("                           state, and it is identical). relative L2 %.4e, %.2f%% of %d"
      % (_m5["relative_l2"], _m5["percent_differing"], _m5["params_total"]))
    A("                           parameters differ between threads 1 and 16")
    A("m6  engineering hours     NOT MEASURABLE under this design, and reported as such.")
    A("                           The estimand never existed: nothing was made deterministic")
    A("m7  monotonicity         %s: %s per cent differing"
      % ("monotone" if _md["m7_monotone_in_thread_count"] else "NOT monotone",
         ", ".join("%.1f" % v for v in _md["m7_percent_differing_by_thread_count"].values())))
    A("      " + chr(0x26D4) + " AND NOT SEPARABLE FROM THE SEED. Varying only the seed moves the")
    A("      differing fraction by %.1f percentage points and the relative L2 by %.1fx, against a"
      % (_md["seed_spread_percent_points"], _md["seed_relative_l2_ratio"]))
    A("      thread-count spread of %.1f points. m7's SHAPE is a claim about one trajectory."
      % (max(_md["m7_percent_differing_by_thread_count"].values())
         - min(_md["m7_percent_differing_by_thread_count"].values())))
    A("```")
    A("")
    A("## The thread sweep, read from the runs")
    A("")
    A("```")
    for n in sorted(sweep):
        A("threads=%-3d  %s" % (n, sweep[n][:48]))
    A("```")
    A("")
    A("⭐ **`--unconstrained` produces the threads=16 digest byte for byte**, so 'unconstrained' is "
      "not a separate condition on this machine — it is 16 threads. An identification, not an "
      "inference.")
    A("")
    A("## The artifact under test")
    A("")
    A("```")
    A("corpus        %d clean bytes, %d texts, merkle %s"
      % (man["total_clean_bytes"], man["text_count"], man["merkle_root"][:32]))
    A("model         %d-byte context, d_emb %d, d_hid %d, %d steps, batch %d, %s"
      % (run["spec"]["context"], run["spec"]["d_emb"], run["spec"]["d_hid"],
         run["spec"]["steps"], run["spec"]["batch"], run["spec"]["dtype"]))
    A("weights       sha256 %s" % run["weights_sha256"])
    A("published as  package/ -- %d files; OUR WEIGHTS ARE NOT IN IT, only the digest"
      % len(list((HERE / "package").rglob("*"))))
    A("```")
    A("")
    A("## ⚠️ Known-weak, and a reviewer should push here")
    A("")
    A("- **n = 2 machines.** Intel and AMD, matched on OS, Python, numpy and the OpenBLAS "
      "build -- and BOTH SELECTED THE SAME OpenBLAS MICROKERNEL (Haswell, X86_V3). So "
      "measurement 4 shows two vendors running the SAME REDUCTION SHAPE agree, which is not "
      "vendor-independence. A machine selecting a different kernel is a different experiment "
      "and has not been run.")
    A("- **Measurement 1 was +37%% in the previous revision and is +%d%% now.** The "
      "design was at fault, not the machine: fixed order, an \"unconstrained\" arm "
      "that was not a condition, and arrays sorted separately before storage. Ask "
      "whether the repaired design has its own faults."
      % round((m1["ratio_of_medians"] - 1) * 100))
    A("- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS "
      "reduction order and capability is explicitly out of scope — but a reviewer may reasonably "
      "argue the finding does not transfer to attention kernels or to CUDA, where atomics add a "
      "second source of the same phenomenon.")
    A("- **Measurement 6 is reported NOT MEASURABLE.** Everything else is a digest or a "
      "timing a stranger can "
      "re-run. That page cannot be checked and says so.")
    A("- **The independent reproduction does not exist**, and by section 2b we may not produce "
      "one. If nobody answers the call, section 2c pre-registered that silence as a result — a "
      "reviewer should decide whether that is a finding or a rationalisation, because it was "
      "written before the window opened precisely so that question could be asked.")
    A("")
    A("## ⛔ What the reviewer should NOT accept without pushing")
    A("")
    A("- that a package running on the machine that built it is evidence of anything beyond "
      "completeness;")
    A("- that the unconstrained runs agreeing three times means unconstrained training is "
      "reproducible — they agreed because nothing was contending;")
    A("- that about +%d%% is *the* cost of determinism. It is the cost of pinning to one "
      "thread rather than requesting %s, on one configuration, at one size -- and which "
      "constraint actually buys identity is a question measurement 4 addresses only for the "
      "reduction shape both arms shared; see PHASE-2-FINDINGS section 10."
      % (round((m1["ratio_of_medians"] - 1) * 100), m1["threads_b"]))
    A("")

    # ⛔ THE CROSS-CHECK WAS DEAD TWICE OVER, AND IT IS WHY THE STALE PACKET SHIPPED.
    #
    #   1. its pattern contained literal BACKSPACE bytes (0x08) where word boundaries were
    #      intended -- a `\b` written into a non-raw string and then saved. It matched nothing,
    #      so the "absent figures" set was always empty and the guard never fired.
    #   2. the name `D` in its refusal was never assigned in this file, so even had it fired it
    #      would have raised NameError instead of reporting -- the same defect fixed in
    #      reproduce_findings.py one round earlier and reintroduced here.
    #
    # A reviewer ran the guard as written over the shipped packet and got the empty set, then ran
    # an ordinary pattern and got {'step 0', 'step 8', '8.0e-06', '4.9e-04'}. The guard's job was
    # to prevent exactly the shipment it permitted.
    #
    # ⚠ A REGEX OVER PROSE IS A PROXY, so this does two things instead of one: it checks the
    # figures, AND it proves at build time that it is capable of failing.
    import re as _re
    _txt = NL.join(L)

    def _figures(s):
        """Numbers that read as measurements: exponentials, percentages, and step counts."""
        pats = (r"(?<![\w.])\d+\.\d+e[-+]\d+(?![\w.])",
                r"(?<![\w.])\d{1,3}\.\d\s?%",
                r"(?<![\w])step -?\d+(?![\w])")
        out = set()
        for p in pats:
            out |= {m.group(0).strip() for m in _re.finditer(p, s)}
        return out

    # ⛔ THE NEGATIVE TEST. A guard nobody has watched fail is indistinguishable from a comment,
    # and this project has now shipped four of those. Inject a figure the findings cannot contain
    # and require the check to notice; if it does not, the guard is broken and the build stops
    # before it can bless anything.
    _canary = "step 99999"
    if _canary in _find or not (_figures(_txt + " " + _canary) - _figures(_txt)):
        raise SystemExit(D + " the packet's cross-check cannot detect an injected figure, so it "
                         "cannot detect a stale one either. Fix the check before building.")

    _absent = sorted(f for f in _figures(_txt)
                     if f not in _find and f.replace(" ", "") not in _find.replace(" ", ""))
    if _absent:
        raise SystemExit(
            D + " this packet prints figure(s) that do not appear in PHASE-2-FINDINGS.md: %s."
            % _absent + NL
            + "  That is how the round-1 and round-2 packets shipped withdrawn claims -- +37%, "
            + "step 8, 83% and 8.0e-06 -- while asserting every figure was measured." + NL
            + "  Either the findings are stale or the packet is. Do not resolve it here.")

    (OUT / "PAPER-B-REVIEW-PACKET.md").write_text(NL.join(L) + NL, encoding="utf-8", newline=NL)
    print("  wrote review/PAPER-B-REVIEW-PACKET.md")
    print("  wrote review/paper-b-review.zip  (%.2f MB, sha256 %s)"
          % (zp.stat().st_size / 1e6, zsha[:16]))
    if dirty:
        print("  " + chr(0x26A0) + " the tree is DIRTY, so the commit named in the packet does "
              "not describe what is in the zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
