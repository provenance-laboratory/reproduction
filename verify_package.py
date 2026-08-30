"""Run the published package the way a stranger would, in a directory it has never seen.

⛔ WHY THIS IS A SCRIPT AND NOT A THING I DID ONCE. Section 2b makes every omission from the
package a CONFOUND rather than an inconvenience: a reproducer who fails for want of a file we left
behind in the working tree has measured our packaging, and the paper has to report it as a fact
about reproducibility. The check that the package is complete therefore has to be repeatable and
has to run before every publication, not once on the day it was assembled.

⚠️ WHAT A PASS HERE DOES NOT MEAN. This runs on the machine that produced the expected digest. It
establishes that the package is COMPLETE -- nothing needed was left outside it. It establishes
nothing whatever about reproducibility on any other machine, and calling a pass here a successful
reproduction would be precisely the error this paper is about.

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
        exp = json.loads((work / "EXPECTED.json").read_text(encoding="utf-8"))
        ok = got["weights_sha256"] == exp["weights_sha256"]
        print("  training run  %s" % ("completed" if r.returncode == 0 else "FAILED"))
        print("  expected      %s" % exp["weights_sha256"])
        print("  obtained      %s" % got["weights_sha256"])
        print("  %s" % ("MATCH" if ok else chr(0x26D4) + " DIFFERENT"))
        print()
        print("  " + chr(0x26A0) + " This ran on the machine that produced the expected digest, so")
        print("  it shows the package is COMPLETE and shows nothing about other hardware.")
        print("=" * 78)
        return 0 if ok else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
