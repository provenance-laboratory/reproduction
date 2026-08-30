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
import sys

NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "package"

# Everything a stranger needs, and the reason each is needed. A file with no reason is a file
# nobody can be asked to check.
CONTENTS = (
    ("train.py", "the pipeline. One file, numpy only, no network"),
    ("REPRODUCTION-CALL.md", "what we are asking for and the two rules we bind ourselves with"),
    ("PRE-REGISTRATION.md", "what was committed to before any of this ran"),
    ("PRE-REGISTRATION.md.ots", "its OpenTimestamps proof, anchored in a Bitcoin block"),
    ("PILOT-2026-08-29.md", "the observation that made the thread pin part of the protocol"),
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
        "configuration_A": {k: run["environment"][k] for k in
                            ("cpu", "logical_processors", "platform", "python", "numpy",
                             "blas", "threads_env")},
        "_known": ("Thread count alone changes the result: on configuration A, threads "
                   "1/2/4/8/16 produced five distinct models. If your digest differs, check "
                   "your thread environment first -- and note that a differing digest is a "
                   "REPORTABLE RESULT, not a mistake to be fixed before reporting."),
    }
    (OUT / "EXPECTED.json").write_text(json.dumps(expected, indent=2) + NL,
                                       encoding="utf-8", newline=NL)
    shipped.append("EXPECTED.json")

    # SHA256SUMS over everything shipped, written last so it covers the final bytes
    lines = []
    for rel in sorted(shipped):
        h = hashlib.sha256((OUT / rel).read_bytes()).hexdigest()
        lines.append("%s  %s" % (h, rel))
    (OUT / "SHA256SUMS").write_text(NL.join(lines) + NL, encoding="utf-8", newline=NL)

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
