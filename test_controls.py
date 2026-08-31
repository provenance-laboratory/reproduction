"""Every attack two round-4 reviewers used, as a suite that must refuse all of them.

⛔ WHY THIS FILE EXISTS. Round 3 shipped two new controls and described their positive controls in
prose. Round 4's reviewers read that and broke both, nine ways between them:

    check_commitments.py   edit train.py AND its digest inside v5      -> exit 0
                           drop in an unanchored synthetic v6           -> exit 0, authority moved
    measure_hardware.py    the SAME run record as both arms            -> ISOLATING
                           runtime microkernel Haswell vs SkylakeX     -> ISOLATING
                           effective threads 1 vs 8                    -> ISOLATING
                           both BLAS build lines absent                -> ISOLATING
                           both arms non-confirmatory                  -> ISOLATING
                           identical CPU on both arms                  -> ISOLATING
                           weights.npz deleted                         -> BIT-IDENTICAL: YES

⇒ One reviewer put the generalisation exactly: *every one of these is a control that can be
satisfied by the ABSENCE, the NAME, or the DESCRIPTION of the thing it checks.* Four of the nine
are absences. The mechanical test they proposed is the one this file runs: **for every check,
construct the input where the thing it names is absent, and see whether it passes.**

⚠️ A control described in a commit message is a control nobody has watched fail. This file is in
the package and in the publication gate, so the descriptions cannot drift from the behaviour again.

    python test_controls.py
"""
import copy
import hashlib
import io
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

NL = chr(10)
D = chr(0x26D4)
HERE = pathlib.Path(__file__).resolve().parent
IGNORE = shutil.ignore_patterns("runs", "package", "reference", ".git", "review", "__pycache__")


def _governing(root):
    """The document that is ACTUALLY authority in this tree, not one named in this file.

    {D} THIS FILE HARDCODED v5. The moment v6 anchored and became authority, "delete the governing
    document's proof" deleted a SUPERSEDED document's proof and the check correctly passed -- so
    the control stopped testing anything and reported success. The enumeration defect, in the file
    written to catch enumeration defects, found by the suite one minute after v6 anchored.
    """
    import importlib
    import sys as _s
    _s.path.insert(0, str(root))
    for m in ("check_commitments",):
        if m in _s.modules:
            del _s.modules[m]
    cc = importlib.import_module("check_commitments")
    found, _rej = cc.governing(root)
    return sorted(found)[-1][1] if found else "PRE-REGISTRATION-v3-CONFIRMATORY.md"


def run(root, tool, *args):
    r = subprocess.run([sys.executable, "-X", "utf8", tool] + list(args), cwd=str(root),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# ── attacks on check_commitments: authority must not come from a mutable file ────────────────
def a_edit_both(root):
    """Change the pipeline AND the digest that pins it. The document's proof must catch it."""
    b = (root / "train.py").read_bytes() + b"# appended" + bytes([10])
    (root / "train.py").write_bytes(b)
    # the digest is edited in whichever document is AUTHORITY, not in a version this file names
    gov = root / _governing(root)
    txt = gov.read_text(encoding="utf-8")
    gov.write_text(re.sub(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])",
                          lambda m: hashlib.sha256(b).hexdigest()
                          if m.group(0) != hashlib.sha256(b).hexdigest() else m.group(0),
                          txt, count=1), encoding="utf-8")


def a_fake_v6(root):
    """Mint a higher version. 'Highest present' is not an authority rule; anchored is."""
    b = (root / "train.py").read_bytes() + b"# appended" + bytes([10])
    (root / "train.py").write_bytes(b)
    rows = ["train.py                   %s" % hashlib.sha256(b).hexdigest()]
    for f in ("corpus/MANIFEST.json", "corpus/build_corpus.py", "corpus/sources.json"):
        rows.append("%-26s %s" % (f, hashlib.sha256((root / f).read_bytes()).hexdigest()))
    (root / "PRE-REGISTRATION-v7-CONFIRMATORY.md").write_text(
        "# v7" + NL * 2 + "## 3. What is committed" + NL + "```" + NL
        + NL.join(rows) + NL + "```" + NL, encoding="utf-8")


def a_strip_proof(root):
    """Delete the ACTUAL governing document's proof. An unanchored protocol is a draft."""
    (root / (_governing(root) + ".ots")).unlink()


COMMIT_ATTACKS = [
    ("edit train.py AND its digest inside the governing document", a_edit_both),
    ("mint an unanchored synthetic v7", a_fake_v6),
    ("delete the governing document's proof", a_strip_proof),
]


# ── attacks on measure_hardware: presence is not equality, absence is not agreement ──────────
def _arms(work, ra, rb, weights=(True, True)):
    out = []
    for tag, rec, want, src in (("a", ra, weights[0], "tpc-thr-1"),
                                ("b", rb, weights[1], "amd-thr-1")):
        d = work / tag
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        (d / "run.json").write_text(json.dumps(rec), encoding="utf-8")
        src_w = HERE / "runs" / src / "weights.npz"
        if want and src_w.exists():
            shutil.copy2(src_w, d / "weights.npz")
        out.append(d)
    return out


def hardware_attacks(A, B):
    """(label, arm A record, arm B record, which weights to place)."""
    def m(rec, **env):
        r = copy.deepcopy(rec)
        for k, v in env.items():
            if k in ("is_confirmatory_spec",):
                r[k] = v
            else:
                r["environment"][k] = v
        return r
    tp = [{"num_threads": 1, "version": "0.3.33.112.0", "prefix": "libscipy_openblas"}]
    tp8 = [{"num_threads": 8, "version": "0.3.33.112.0", "prefix": "libscipy_openblas"}]
    return [
        ("the SAME record as both arms", copy.deepcopy(A), copy.deepcopy(A), (True, True)),
        ("identical CPU on both arms", copy.deepcopy(A),
         m(B, cpu=A["environment"]["cpu"]), (True, True)),
        ("runtime microkernel Haswell vs SkylakeX", m(A, blas_runtime_arch="Haswell"),
         m(B, blas_runtime_arch="SkylakeX"), (True, True)),
        ("effective threads 1 vs 8", m(A, threads_effective=tp),
         m(B, threads_effective=tp8), (True, True)),
        ("both BLAS build lines ABSENT", m(A, blas_build_config_line=None),
         m(B, blas_build_config_line=None), (True, True)),
        ("both arms NON-CONFIRMATORY", m(A, is_confirmatory_spec=False),
         m(B, is_confirmatory_spec=False), (True, True)),
        ("arm B's weights.npz deleted", copy.deepcopy(A), copy.deepcopy(B), (True, False)),
        ("arm B's run.json claims a digest its bytes do not have",
         copy.deepcopy(A), m(B) | {"weights_sha256": "0" * 64}, (True, True)),
    ]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace",
                                  line_buffering=True)
    print("=" * 78)
    print("  CONTROL TESTS -- every attack round 4 used, which must all be refused")
    print("=" * 78)
    print()

    caught = missed = 0

    print("  check_commitments.py")
    for label, build in COMMIT_ATTACKS:
        work = pathlib.Path(tempfile.mkdtemp(prefix="cc-"))
        root = work / "r"
        shutil.copytree(HERE, root, ignore=IGNORE)
        try:
            build(root)
            rc, _out = run(root, "check_commitments.py")
        finally:
            shutil.rmtree(work, ignore_errors=True)
        ok = rc != 0
        print("    %s %-52s" % ("refused " if ok else D + " PASSED", label))
        caught += ok
        missed += not ok

    print()
    print("  measure_hardware.py -- none of these may return MATCHED-STACK")
    A = json.loads((HERE / "runs" / "tpc-thr-1" / "run.json").read_text(encoding="utf-8"))
    B = json.loads((HERE / "runs" / "amd-thr-1" / "run.json").read_text(encoding="utf-8"))
    work = pathlib.Path(tempfile.mkdtemp(prefix="mh-"))
    try:
        for label, ra, rb, w in hardware_attacks(A, B):
            da, db = _arms(work, ra, rb, w)
            rc, out = run(HERE, "measure_hardware.py", "--a", str(da), "--b", str(db),
                          "--out", str(work / "o.json"))
            ok = "ok  MATCHED-STACK" not in out
            print("    %s %-52s" % ("refused " if ok else D + " PASSED", label))
            caught += ok
            missed += not ok
    finally:
        shutil.rmtree(work, ignore_errors=True)

    # ⛔ AND THE POSITIVE CASE, without which the whole file passes against a tool that refuses
    # everything. The real pair must still be admissible.
    print()
    rc, out = run(HERE, "measure_hardware.py", "--a", "runs/tpc-thr-1", "--b", "runs/amd-thr-1",
                  "--out", str(pathlib.Path(tempfile.gettempdir()) / "m4-selftest.json"))
    real_ok = "ok  MATCHED-STACK" in out
    print("  %s the REAL pair is still admissible" % ("ok      " if real_ok else D + " BROKEN"))
    rc2, _o2 = run(HERE, "check_commitments.py")
    print("  %s the REAL tree still passes check_commitments" % ("ok      " if rc2 == 0
                                                                 else D + " BROKEN"))
    if not real_ok or rc2 != 0:
        print()
        print("  " + D + " A SUITE THAT REJECTS EVERYTHING PROVES NOTHING. The negative cases")
        print("  above are only meaningful while the positive case still passes.")
        missed += 1

    print()
    print("  %d refused, %d PASSED THAT SHOULD NOT HAVE" % (caught, missed))
    print("=" * 78)
    return 1 if missed else 0


if __name__ == "__main__":
    raise SystemExit(main())
