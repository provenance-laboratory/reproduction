"""Run the published package the way a stranger would, in a directory it has never seen.

⛔ WHY THIS IS A SCRIPT AND NOT A THING I DID ONCE. Section 2b makes every omission from the
package a CONFOUND rather than an inconvenience: a reproducer who fails for want of a file we left
behind in the working tree has measured our packaging, and the paper has to report it as a fact
about reproducibility. The check that the package is complete therefore has to be repeatable and
has to run before every publication, not once on the day it was assembled.

⚠️ WHAT A PASS MEANS DEPENDS ON WHOSE MACHINE IT IS, and this script no longer guesses. On the
machine that produced the expected digest, a match shows the package is COMPLETE and shows nothing
about other hardware. On anyone else's, a match or a mismatch is evidence about cross-machine
reproducibility -- which is measurement 4, the open half of this study.

⛔ AND A DIGEST MISMATCH IS NOT AN ERROR HERE. The first version exited non-zero when the digests
differed, so a reviewer on different hardware saw a red failure for producing exactly the result
the experiment is asking about. Exit status now reports whether the PACKAGE is sound -- files
present, checksums good, code runs, no absolute paths. Whether the weights match is printed as a
finding, because that is what it is.

    python verify_package.py
"""
import hashlib
import io
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE / "package"


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if not PKG.exists():
        raise SystemExit(chr(0x26D4) + " no package/. Run build_package.py first.")

    print("=" * 78)
    print("  THE PACKAGE, RUN AS A STRANGER WOULD")
    print("=" * 78)
    print()

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="stranger-"))
    try:
        shutil.copytree(PKG, tmp / "pkg")
        work = tmp / "pkg"

        # 1. the manifest covers the bytes that are there
        sums = (work / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
        bad = []
        for line in sums:
            want, rel = line.split("  ", 1)
            f = work / rel
            if not f.exists():
                bad.append("%s MISSING" % rel)
            elif hashlib.sha256(f.read_bytes()).hexdigest() != want:
                bad.append("%s DIGEST MISMATCH" % rel)
        # ⛔ AN UNLISTED FILE PASSED. A reviewer dropped a forged EXPECTED.json into the
        # extraction: every listed checksum still matched, so this reported 0 problems, and then
        # READ THE FORGERY as authoritative. SHA256SUMS says what the listed files are; it says
        # nothing about what else is present, and a checksum manifest that only looks at its own
        # list cannot see an addition. This is not only a tampering story -- an overlaid extraction
        # or a stale directory produces it by accident.
        _listed = {ln.split("  ", 1)[1] for ln in sums if "  " in ln}
        _present = {str(f.relative_to(work)).replace(chr(92), "/")
                    for f in work.rglob("*") if f.is_file()}
        _extra = sorted(_present - _listed - {"SHA256SUMS"}
                        - {f for f in _present if f.startswith("my-run/")})
        if _extra:
            bad += ["%s IS NOT LISTED in SHA256SUMS" % e for e in _extra[:5]]
        # ⛔ AND EXACTLY ONE STAGE. The input package carries NO-TARGET.md and no
        # EXPECTED.json; the target package carries EXPECTED.json and no NO-TARGET.md. Both, or
        # neither, means the package does not know which stage of the protocol it is.
        _has_target = "EXPECTED.json" in _present
        _has_notarget = "NO-TARGET.md" in _present
        if _has_target == _has_notarget:
            bad.append("the package declares %s stage: EXPECTED.json=%s NO-TARGET.md=%s"
                       % ("BOTH" if _has_target else "NEITHER", _has_target, _has_notarget))
        print("  SHA256SUMS   %d entries, %d problem(s)" % (len(sums), len(bad)))
        for b in bad[:5]:
            print("      " + chr(0x26D4) + " " + b)
        if bad:
            return 1

        # 2. nothing in the package refers to a path outside it
        # ⛔ A package that reaches into the working tree passes on the machine that built it and
        # fails everywhere else -- the failure mode this check exists for, and it cannot be seen
        # by running the package on the machine that has those paths.
        strays = []
        for f in work.rglob("*.py"):
            src = f.read_text(encoding="utf-8", errors="replace")
            for needle in ("C:/Users", "C:\\\\Users", "/home/", "vscode_workspace"):
                if needle in src:
                    strays.append("%s mentions %s" % (f.name, needle))
        print("  absolute paths in shipped code: %d" % len(strays))
        for s in strays[:4]:
            print("      " + chr(0x26D4) + " " + s)
        if strays:
            return 1

        # 3. it runs, and it produces the published digest
        r = subprocess.run([sys.executable, "-X", "utf8", "train.py", "--out", "my-run"],
                           cwd=str(work), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0:
            print("  " + chr(0x26D4) + " the package does not run:")
            print((r.stderr or "")[-600:])
            return 1
        got = json.loads((work / "my-run" / "run.json").read_text(encoding="utf-8"))
        # ⛔ THE INPUT PACKAGE HAS NO TARGET, BY DESIGN, and this script assumed one --
        # crashing on the package it exists to verify. v3 publishes the inputs first and the
        # reference digest only after a public commitment, so "no EXPECTED.json" is the CORRECT
        # state of a step-2 package and must be reported as such rather than raised.
        _exp = work / "EXPECTED.json"
        if not _exp.exists():
            print("  training run  completed")
            print("  obtained      %s" % got["weights_sha256"])
            print("  expected      -- this is the TARGET-FREE input package (see NO-TARGET.md)")
            print()
            print("  " + chr(0x26A0) + " Nothing to compare against yet, and that is the protocol")
            print("  working: the reference digest is published only after someone has publicly")
            print("  committed to attempting a reproduction. The package is COMPLETE -- it ran to")
            print("  completion in a directory it had never seen, with no absolute paths.")
            print("=" * 78)
            return 0
        exp = json.loads(_exp.read_text(encoding="utf-8"))
        ok = got["weights_sha256"] == exp["weights_sha256"]
        print("  training run  %s" % ("completed" if r.returncode == 0 else "FAILED"))
        print("  expected      %s" % exp["weights_sha256"])
        print("  obtained      %s" % got["weights_sha256"])
        print("  %s" % ("MATCH" if ok else
                        chr(0x26A0) + " DIFFERENT -- a RESULT, not a failure. Please report it."))
        print()
        # ⛔ THIS SENTENCE WAS PRINTED UNCONDITIONALLY AND WAS FALSE FOR EVERY REVIEWER.
        # It claimed the run had happened on the machine that produced the expected digest, which
        # is true when WE run it and false whenever anyone else does -- and the people it misleads
        # are exactly the people it was written for. The record knows the difference: compare the
        # environment digest.
        here = got.get("environment", {}).get("digest")
        there = exp.get("configuration_A_environment_digest")
        same_machine = bool(here and there and here == there)
        print("  " + chr(0x26A0) + " SCOPE OF THIS RESULT")
        if same_machine:
            print("  This ran on the machine that produced the expected digest, so it shows the")
            print("  package is COMPLETE and shows nothing about other hardware.")
        else:
            print("  This is NOT the machine that produced the expected digest -- the environment")
            print("  records differ. A match here would be evidence about cross-machine")
            print("  reproducibility; a mismatch is a REPORTABLE RESULT and not a failure of the")
            print("  package. Either way, please file it.")
        print("=" * 78)
        # The package is sound; whether the digest matches is the measurement.
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
