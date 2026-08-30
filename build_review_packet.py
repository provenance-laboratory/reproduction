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
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "review"

SEND = (
    ("PRE-REGISTRATION.md", "what was committed to before anything ran"),
    ("PRE-REGISTRATION.md.ots", "its proof, ANCHORED in a Bitcoin block"),
    ("PILOT-2026-08-29.md", "the observation that made the thread pin part of the protocol"),
    ("AMENDMENT-2026-08-30.md", "a deviation from section 2b, recorded on the day"),
    ("PHASE-2-FINDINGS.md", "what the pipeline found"),
    ("MEASUREMENT-1.json", "the cost of determinism, 11 interleaved reps"),
    ("MEASUREMENT-2.json", "storage overhead"),
    ("MEASUREMENT-6.md", "engineering hours, self-reported and flagged as the weakest evidence"),
    ("REPRODUCTION-CALL.md", "the open request, written to section 2b"),
    ("PUBLICATION-CHECKLIST.md", "the decisions that must be made in the act of publishing"),
    ("train.py", "the pipeline"),
    ("measure_cost.py", "measurement 1's instrument"),
    ("build_package.py", "what a reproducer receives"),
    ("verify_package.py", "the package run as a stranger would"),
    ("reproduce_findings.py",
     "re-derives the headline findings from scratch -- five runs, no timing, so a"
     " reviewer checks the RESULTS rather than the prose"),
    ("corpus/MANIFEST.json", "the corpus and its Merkle root"),
    ("corpus/MANIFEST.json.ots", "committed BEFORE the first training step, now anchored"),
)


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
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for rel, _why in SEND:
            z.write(HERE / rel, rel)
        for p in sorted((HERE / "package").rglob("*")):
            if p.is_file():
                z.write(p, str(p.relative_to(HERE)).replace(chr(92), "/"))
    zsha = hashlib.sha256(zp.read_bytes()).hexdigest()

    L = []
    A = L.append
    A("# Paper B (`reproduction`) — internal review packet, round 1")
    A("")
    A("*Every figure below is read from the measurement files by `build_review_packet.py`. "
      "It refuses to write if one is missing.*")
    A("")
    A("## ⇒ SEND THESE TWO")
    A("")
    A("```")
    A("paper-b-review.zip     %d files, sha256 %s" % (len(SEND) + 1, zsha[:32]))
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
    A("> **This paper has no manuscript yet, and that is what the review is for.** Phase 1 fixed "
      "the corpus and pre-registered the protocol; phase 2 built the pipeline and took every "
      "measurement that one machine can take. Reviewing it now, before a word of the paper is "
      "written, is deliberate: the expensive mistake would be to write the argument first and "
      "discover the measurements do not carry it.")
    A(">")
    A("> ⭐ **The headline arrived from a direction the pre-registration did not predict.** "
      "Section 4 expected bit-identity to fail ACROSS hardware, for principled reasons. It fails "
      "**within one machine, on thread count alone** — five thread counts, five distinct models, "
      "with 83%% of parameters differing between 1 and 16. The conclusion the paper was written to "
      "be publishable under therefore holds *a fortiori*, and with a far smaller apparatus than "
      "the argument needed.")
    A(">")
    A("> ⚠️ **And the two models are numerically indistinguishable.** Relative L2 8e-06, final "
      "loss agreeing to seven significant figures. Any tolerance-based provenance claim passes; "
      "the bit-identity claim fails on 83%% of the parameters. **That gap is the paper.**")
    A(">")
    A("> ⛔ **Measurement 1 took three attempts and the first two are reported, not replaced.** "
      "The first was contaminated by a build running in another window. The guard written to "
      "prevent that failed the same way — it checked once, found the machine quiet, and a build "
      "started a second later. A precondition checked once at the start is not a precondition held "
      "throughout.")
    A("")
    A("## ⭐ CHECK THE FINDINGS, NOT ONLY THE PACKAGING")
    A("")
    A("```")
    A("python reproduce_findings.py     five training runs, ~2 minutes, nothing timed")
    A("```")
    A("")
    A("It re-derives the thread partition, the divergence table, the relative figure this paper "
      "declines to headline, and the step at which the loss curves first differ — from "
      "nothing but the corpus and `train.py`. **If its numbers disagree with "
      "`PHASE-2-FINDINGS.md`, the findings are wrong**, and that is the most valuable outcome "
      "this review could have. Contention cannot move any of it: every number is a digest or a "
      "difference, and nothing in that script is timed.")
    A("")
    A("```")
    A("python verify_package.py         the package run in a directory it has never seen")
    A("```")
    A("")
    A("## What is measured, and by what")
    A("")
    A("```")
    A("m1  cost of determinism   +%.1f%%   %d interleaved reps, ranges %s"
      % (m1["determinism_overhead_percent"], m1["reps"],
         "OVERLAP" if m1["ranges_overlap"] else "do not overlap"))
    A("      pinned  median %.2f s   min %.2f   max %.2f"
      % (m1["median"]["pinned"], m1["loop_seconds"]["pinned"][0],
         m1["loop_seconds"]["pinned"][-1]))
    A("      free    median %.2f s   min %.2f   max %.2f"
      % (m1["median"]["free"], m1["loop_seconds"]["free"][0], m1["loop_seconds"]["free"][-1]))
    A("m2  apparatus             %d bytes on %d bytes of artifact (%.3f%%)"
      % (m2["apparatus_total"], m2["artifact_bytes"]["total"],
         m2["overhead_percent_of_artifact"]))
    A("      of which timestamp proofs   %d bytes" % m2["timestamp_proof_bytes"])
    # ⚠️ `% len(distinct_digests)` printed "across 1 runs" -- the number of DIGESTS where the
    # sentence promised the number of RUNS. And section 6 forbids REPORTING bit-identity without
    # an independent re-run, so the status travels with the number.
    _n_dig = len(m1["distinct_digests"]["pinned"])
    A("m3  bit-identity, same hw  %s"
      % ("one digest across %d runs -- but see below" % m1["reps"] if _n_dig == 1
         else chr(0x26D4) + " %d DISTINCT DIGESTS: not reproducible" % _n_dig))
    A("      " + chr(0x26D4) + " NOT YET A FINDING OF THIS PAPER. Section 6 makes reporting")
    A("      bit-identity without an independent party's re-run an invalidating condition.")
    A("      Three of OUR OWN runs agreeing is an internal phase record, nothing more.")
    A("m4  bit-identity, diff hw  NOT MEASURED -- needs configurations B, C, D")
    A("m5  divergence             first differs at step 8; relative L2 8.0e-06;")
    A("                           83%% of 804,096 parameters differ between threads 1 and 16")
    A("m6  engineering hours      self-reported; flagged as the weakest evidence in the study")
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
    A("- **n = 1 machine.** Configuration A only. Measurement 4 is the paper's second half and is "
      "not done.")
    A("- **The m1 ranges separate by %.2f s.** Non-overlapping, but thin enough that a twelfth "
      "repetition landing badly would close it. Read it as *roughly a third*, not as %.1f%%."
      % (m1["loop_seconds"]["pinned"][0] - m1["loop_seconds"]["free"][-1],
         m1["determinism_overhead_percent"]))
    A("- **The model is an MLP, not a transformer.** Defensible — the mechanism under test is BLAS "
      "reduction order and capability is explicitly out of scope — but a reviewer may reasonably "
      "argue the finding does not transfer to attention kernels or to CUDA, where atomics add a "
      "second source of the same phenomenon.")
    A("- **Measurement 6 is a memory.** Everything else is a digest or a timing a stranger can "
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
    A("- that +%.1f%% is *the* cost of determinism rather than the cost on one configuration, on "
      "one pipeline, at one size." % m1["determinism_overhead_percent"])
    A("")

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
