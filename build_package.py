"""Assemble the publication package a reproducer receives — and nothing else.

⛔ THE PACKAGE IS THE EXPERIMENT. Section 2b of the pre-registration says the reproducer gets the
published package and no assistance. That makes every omission here a confound rather than an
inconvenience: if a reproduction fails because a file was missing, the paper has measured our
packaging and will report it as a fact about reproducibility. So this refuses to build a package
it cannot verify, rather than shipping one and finding out later.

⚠️ WHAT IS DELIBERATELY *NOT* IN IT. Our trained weights. A reproducer who has our `weights.npz`
can compare digests without training anything, and — more to the point — cannot be sure they did
not accidentally compare our file with itself. Only the DIGEST is published, in EXPECTED.json.
The artifact under test is the procedure, not the file.

    python build_package.py
"""
import hashlib
import io
import json
import pathlib
import shutil
import subprocess
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "package"

# Everything a stranger needs, and the reason each is needed. A file with no reason is a file
# nobody can be asked to check.
CONTENTS = (
    ("train.py", "the pipeline. One file, numpy only, no network"),
    ("REPRODUCTION-CALL.md", "what we are asking for and the two rules we bind ourselves with"),
    ("PRE-REGISTRATION-v3-CONFIRMATORY.md",
     "THE PROTOCOL THIS STUDY RUNS UNDER"),
    ("PRE-REGISTRATION-v3-CONFIRMATORY.md.ots", "its proof"),
    ("PRE-REGISTRATION-v2-CONFIRMATORY.md", "version 2, superseded, retained as record"),
    ("PRE-REGISTRATION-v2-CONFIRMATORY.md.ots", "its proof"),
    ("ENVIRONMENT-LOCK.json",
     "the interpreter and library recorded -- NOT a lock; see the file"),
    ("PRE-REGISTRATION.md", "version 1, retained: the pilot protocol"),
    ("PRE-REGISTRATION.md.ots", "its OpenTimestamps proof, anchored in a Bitcoin block"),
    ("PILOT-2026-08-29.md", "the observation that made the thread pin part of the protocol"),
    ("AMENDMENT-2026-08-30.md",
     "a deviation from the protocol, disclosed to the reproducer rather than to a reader later"),
    ("corpus/MANIFEST.json", "the corpus, its digests and its Merkle root"),
    ("corpus/MANIFEST.json.ots", "the proof the corpus was fixed BEFORE the first training step"),
    ("corpus/sources.json", "where each text came from, so the corpus can be rebuilt from source"),
    ("corpus/build_corpus.py", "how raw became clean. The cleaning is part of the specification"),
)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ref = HERE / "runs" / "det-1" / "run.json"
    if not ref.exists():
        raise SystemExit(chr(0x26D4) + " no reference run at runs/det-1. Train before packaging.")
    run = json.loads(ref.read_text(encoding="utf-8"))

    # ⛔ THE CORPUS IN THE PACKAGE MUST BE THE CORPUS THAT WAS TRAINED ON. Checked here rather
    # than trusted, because the manifest and the files are two things and this is the one place
    # they are copied apart from each other.
    man = json.loads((HERE / "corpus" / "MANIFEST.json").read_text(encoding="utf-8"))
    if man["merkle_root"] != run["corpus_merkle_root"]:
        raise SystemExit(chr(0x26D4) + " the manifest's Merkle root is not the one the reference "
                         "run trained on (%s vs %s)"
                         % (man["merkle_root"][:16], run["corpus_merkle_root"][:16]))
    for e in man["texts"]:
        p = HERE / "corpus" / e["file"]
        if not p.exists():
            raise SystemExit(chr(0x26D4) + " %s is in the manifest and not on disk" % e["file"])
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got != e["clean_sha256"]:
            raise SystemExit(chr(0x26D4) + " %s does not match the manifest" % e["file"])

    # ⛔ THE GOVERNING PROTOCOL WAS NOT IN THE PACKAGE. v3 was written, stamped and
    # announced as in force, and never added to CONTENTS -- so the published package shipped v1
    # and a v2 whose own text says "superseded by v3", and NO-TARGET.md cited a §3 no reproducer
    # could read. Both round-3 reviewers found it within minutes, from the file listing.
    #
    # A list of files to ship cannot notice the one file that makes the rest interpretable. So the
    # governing version is named ONCE, here, and its absence stops the build.
    GOVERNING = "PRE-REGISTRATION-v3-CONFIRMATORY.md"
    if not (HERE / GOVERNING).exists():
        raise SystemExit(D + " the governing protocol %s does not exist. A package without it is "
                         "a package whose rules cannot be read." % GOVERNING)
    if GOVERNING not in [c[0] for c in CONTENTS]:
        raise SystemExit(D + " %s exists and is NOT in CONTENTS. That is exactly the defect two "
                         "reviewers found: the protocol governs a package it is not inside."
                         % GOVERNING)
    _st = subprocess.run([sys.executable, "-X", "utf8", "anchor_status.py"], cwd=str(HERE),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    # ⚠ ANCHORING GATES PUBLICATION, NOT REVIEW. v3 §3 makes a Bitcoin attestation a
    # precondition of step 2 -- publishing -- and circulating a package for internal review is not
    # that. A guard that refuses to BUILD would stop the very reviews that catch the defects, so
    # it reports loudly and continues, and only `--publishing` makes it fatal.
    _anchor_ok = _st.returncode == 0
    if not _anchor_ok:
        print(D + " anchor_status.py FAILS. This package MUST NOT BE PUBLISHED:")
        for _ln in (_st.stdout or "").splitlines():
            if "FAIL" in _ln or "pending" in _ln or "DOES NOT BIND" in _ln:
                print("      " + _ln.strip()[:100])
        if "--publishing" in sys.argv:
            raise SystemExit("  --publishing given and the proofs do not check out. Stopping.")
        print("  Continuing because this is a REVIEW build. Pass --publishing to make it fatal.")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "corpus" / "clean").mkdir(parents=True, exist_ok=True)

    shipped = []
    for rel, _why in CONTENTS:
        src = HERE / rel
        if not src.exists():
            raise SystemExit(chr(0x26D4) + " %s is listed in the package and does not exist. "
                             "A package missing a file it promises is the confound this "
                             "experiment cannot afford." % rel)
        dst = OUT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        shipped.append(rel)
    for e in man["texts"]:
        shutil.copy2(HERE / "corpus" / e["file"], OUT / "corpus" / e["file"])
        shipped.append("corpus/" + e["file"])

    # the issue template, so the reporting address travels with the artifacts
    tpl = HERE / ".github" / "ISSUE_TEMPLATE" / "reproduction-report.yml"
    if tpl.exists():
        (OUT / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True, exist_ok=True)
        shutil.copy2(tpl, OUT / ".github" / "ISSUE_TEMPLATE" / "reproduction-report.yml")
        shipped.append(".github/ISSUE_TEMPLATE/reproduction-report.yml")

    # ⚠️ THE WEIGHTS ARE NOT SHIPPED, ONLY THEIR DIGEST. See the module docstring.
    expected = {
        "_what": ("The result configuration A obtained. Compare the weights_sha256 your run "
                  "writes into run.json against this. The weights themselves are deliberately "
                  "NOT in this package: with our file present you could compare it against "
                  "itself and never know."),
        "weights_sha256": run["weights_sha256"],
        "final_loss": run["final_loss"],
        "corpus_merkle_root": run["corpus_merkle_root"],
        "spec": run["spec"],
        # ⛔ THE ENVIRONMENT DIGEST, so a reproducer's tooling can TELL whether it is on
        # configuration A rather than being told it is by a hard-coded sentence.
        "configuration_A_environment_digest": run["environment"]["digest"],
        "configuration_A": {k: run["environment"][k] for k in
                            ("cpu", "logical_processors", "platform", "machine", "python",
                             "numpy", "blas_openblas_line", "blas_build_config_line",
                             "blas_runtime_arch", "blas_config_sha256", "simd_baseline",
                             "simd_found", "threads_requested", "threads_effective",
                             "threads_effective_note",
                             "admissible_for_causal_attribution")
                            if k in run["environment"]},
        "_known": ("Thread count alone changes the result: on configuration A, threads "
                   "1/2/4/8/16 produced five distinct models. If your digest differs, check "
                   "your thread environment first -- and note that a differing digest is a "
                   "REPORTABLE RESULT, not a mistake to be fixed before reporting."),
    }
    # ⛔ THE TARGET DOES NOT SHIP IN THE INPUT PACKAGE. v2 wrote EXPECTED.json here, so
    # the digest a reproducer is asked to match went out at step 3 -- before the public commitment
    # at step 4 that the whole ordering exists to obtain. Two reviewers found it from the file
    # timestamps. v3 publishes a TARGET-FREE package; the reference bundle and EXPECTED.json are a
    # separate, later, signed artifact.
    if "--with-target" in sys.argv:
        (OUT / "EXPECTED.json").write_text(json.dumps(expected, indent=2) + NL,
                                           encoding="utf-8", newline=NL)
        shipped.append("EXPECTED.json")
        print("  " + D + " EXPECTED.json INCLUDED (--with-target). This is the step-5 package,")
        print("  not the step-2 one. Publishing it before a commitment exists voids v3 §6.")
    else:
        (OUT / "NO-TARGET.md").write_text(
            "# There is deliberately no expected digest in this package" + NL + NL
            + "The protocol (`PRE-REGISTRATION-v3-CONFIRMATORY.md` §3) publishes the inputs first "
            + "and the target only after someone has publicly committed to attempting a "
            + "reproduction." + NL + NL
            + "A digest published before the commitment is a target reproducers self-select "
            + "against; a commitment made before the target exists cannot be. An earlier version "
            + "of this package shipped the digest anyway, which defeated the ordering the protocol "
            + "was rewritten to establish." + NL + NL
            + "**Train it, record your `run.json`, and file it.** The reference bundle will be "
            + "published separately, signed and timestamped, and you will be able to compare then."
            + NL, encoding="utf-8", newline=NL)
        shipped.append("NO-TARGET.md")
    (OUT / "ANCHOR-STATUS.txt").write_text(
        (_st.stdout or "") + NL
        + ("" if _anchor_ok else
           NL + D + " THIS PACKAGE IS NOT PUBLISHABLE IN THIS STATE. The protocol proofs above do"
           + NL + "not all carry a Bitcoin attestation over their current bytes. It is circulated"
           + NL + "for REVIEW only." + NL),
        encoding="utf-8", newline=NL)
    shipped.append("ANCHOR-STATUS.txt")

    # SHA256SUMS over everything shipped, written last so it covers the final bytes
    lines = []
    for rel in sorted(shipped):
        h = hashlib.sha256((OUT / rel).read_bytes()).hexdigest()
        lines.append("%s  %s" % (h, rel))
    (OUT / "SHA256SUMS").write_text(NL.join(lines) + NL, encoding="utf-8", newline=NL)

    # ⛔ WITHOUT THE REFERENCE ARRAYS, MEASUREMENT 5 IS IMPOSSIBLE FOR A REPRODUCER.
    # After a digest mismatch they can see THAT their model differs and can compute nothing about
    # HOW -- no parameter distance, no differing fraction, no per-layer divergence. Both reviewers
    # raised it. The weights still do not go in the package a reproducer trains from, because a
    # file present is a file that can be compared against itself; they go in a SEPARATE bundle,
    # to be opened after their own run exists.
    REF = HERE / "reference"
    if REF.exists():
        shutil.rmtree(REF)
    REF.mkdir(parents=True)
    src = HERE / "runs" / "det-1" if (HERE / "runs" / "det-1").exists() else HERE / "runs" / "thr-1"
    for name in ("weights.npz", "run.json", "loss.json", "loss-full.json", "trace.json"):
        f = src / name
        if f.exists():
            shutil.copy2(f, REF / name)
    for n in (2, 4, 8, 16):
        d = HERE / "runs" / ("thr-%d" % n)
        if (d / "run.json").exists():
            (REF / ("thr-%d" % n)).mkdir(exist_ok=True)
            # ⛔ THE 16-THREAD TRACE WAS NOT SHIPPED, so the headline m5 claim -- step 0,
            # every array -- could not be audited from the bundle at all: with only the 1-thread
            # trace there is nothing to compare against. A reviewer reported it as the reason they
            # could not check the claim. trace.json now ships for every arm.
            for name in ("weights.npz", "run.json", "loss.json", "trace.json"):
                if (d / name).exists():
                    shutil.copy2(d / name, REF / ("thr-%d" % n) / name)
    ref_files = sorted(f for f in REF.rglob("*") if f.is_file())
    (REF / "SHA256SUMS").write_text(
        NL.join("%s  %s" % (hashlib.sha256(f.read_bytes()).hexdigest(),
                            str(f.relative_to(REF)).replace(chr(92), "/"))
                for f in ref_files) + NL, encoding="utf-8", newline=NL)
    (REF / "README.md").write_text(
        "# Reference outputs from configuration A" + NL + NL
        + "⚠️ **Open this after your own run, not before.** These are the arrays and raw records "
        + "configuration A produced. They are published so that a reproducer whose digest differs "
        + "can measure HOW it differs -- parameter distances, differing fraction, and with "
        + "`trace.json` the first step and array at which divergence appears." + NL + NL
        + "⛔ **A comparison you make before training your own model measures nothing.** The "
        + "package deliberately excludes these files for that reason; they are a separate "
        + "download so the choice to open them is yours and is made at the right moment." + NL,
        encoding="utf-8", newline=NL)
    print("  reference/  %d file(s) -- the configuration-A arrays, shipped SEPARATELY"
          % (len(ref_files) + 1))

    total = sum((OUT / rel).stat().st_size for rel in shipped)
    print("  package/  %d file(s), %.2f MB" % (len(shipped) + 1, total / 1e6))
    print("  expected  weights sha256 %s" % run["weights_sha256"][:32])
    print("  corpus    merkle %s" % man["merkle_root"][:32])
    print()
    print("  " + chr(0x26A0) + " NOT PUBLISHED BY THIS SCRIPT. Publishing opens the reproduction")
    print("  window, and section 2c fixes the window's close date at that moment -- so it is a")
    print("  decision with a deadline attached, not a build step.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
