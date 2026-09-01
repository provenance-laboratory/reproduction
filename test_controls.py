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


def a_forge_proof(root):
    """⛔ THE FORGERY BOTH ROUND-5 REVIEWERS BUILT INDEPENDENTLY, in forty bytes.

    `anchored()` decided a proof was a proof by searching it for two byte strings: the document's
    SHA-256, and the eight-byte Bitcoin attestation tag. So concatenating them is accepted -- and
    it moved authority, and let a substituted pipeline through with exit 0. `ots info` on the same
    file says *is not a timestamp file*.

    ⚠ ROUND 4'S VERSION OF THIS ATTACK SURVIVED ITS OWN REPAIR. A reviewer passed 35 bytes of
    junk containing the tag; the fix added BINDING (require the digest to appear) and never added
    PARSING. The next reviewer supplied 40 bytes containing both strings. Two rounds, one defect,
    because the repair addressed the instance rather than the class.
    """
    gov = root / _governing(root)
    (root / (_governing(root) + ".ots")).write_bytes(
        hashlib.sha256(gov.read_bytes()).digest()
        + bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01]))


def a_foreign_proof(root):
    """A REAL, VALID, Bitcoin-anchored proof -- over a DIFFERENT document. Binding, not shape."""
    gov = _governing(root)
    for other in sorted(root.glob("*.ots")):
        if other.name != gov + ".ots":
            (root / (gov + ".ots")).write_bytes(other.read_bytes())
            return
    raise SystemExit(D + " no second proof in the tree to borrow; this attack needs one")


def a_truncate_proof(root):
    """Half a real proof. The structure must be walked to the end, not sampled."""
    p = root / (_governing(root) + ".ots")
    p.write_bytes(p.read_bytes()[:len(p.read_bytes()) // 2])


def a_trailing_bytes(root):
    """A real proof with bytes appended. A parser that stops early never sees them."""
    p = root / (_governing(root) + ".ots")
    p.write_bytes(p.read_bytes() + b"smuggled")


def a_add_anchor_block(root):
    """Add a block nobody's proof names. Every existing verification still succeeds.

    ⛔ ZERO OF THIRTY CASES TOUCHED THE FILE THAT DECIDES WHAT ANCHORED MEANS. A round-7
    reviewer added a fabricated block to it and nothing noticed: the file was protected against
    DAMAGE -- rewriting a real root breaks a real proof and everything goes red -- and unprotected
    against EXTENSION, which is the direction an attack uses because every existing check passes.
    """
    import json as _j
    f = root / "ANCHORS.json"
    d = _j.loads(f.read_text(encoding="utf-8"))
    d["blocks"]["7654321"] = {"hash": "0" * 64, "merkle_root": "a" * 64, "timestamp": 0}
    f.write_text(_j.dumps(d, indent=1) + chr(10), encoding="utf-8")


COMMIT_ATTACKS = [
    ("add a fabricated block to the anchor file", a_add_anchor_block),
    ("edit train.py AND its digest inside the governing document", a_edit_both),
    ("mint an unanchored synthetic v7", a_fake_v6),
    ("delete the governing document's proof", a_strip_proof),
    ("forge the governing proof: digest || Bitcoin tag, 40 bytes", a_forge_proof),
    ("substitute a REAL proof over a DIFFERENT document", a_foreign_proof),
    ("truncate the governing document's real proof", a_truncate_proof),
    ("append trailing bytes to the governing proof", a_trailing_bytes),
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
            if k in ("is_confirmatory_spec", "spec", "corpus_merkle_root"):
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

        # ⛔ ROUND 5, AND THE POINT IS *WHERE* THESE LANDED. Round 4's absences were caught one
        # at a time inside `conditions()`. These four delete fields read by the SAME-INPUT GATE
        # ABOVE it -- the gate deciding whether the comparison is a comparison -- where `a.get(k)
        # != b.get(k)` is FALSE when neither arm states k. Deleting the field that says the two
        # runs asked the same question made the pair MORE comparable and returned the strongest
        # verdict the tool can issue. Repairing instance N where it appears is how N+1 is made.
        ("BOTH arms' spec ABSENT", m(A, spec=None), m(B, spec=None), (True, True)),
        ("BOTH arms' corpus_merkle_root ABSENT",
         m(A, corpus_merkle_root=None), m(B, corpus_merkle_root=None), (True, True)),
        ("BOTH arms' threads_requested ABSENT",
         m(A, threads_requested=None), m(B, threads_requested=None), (True, True)),
        ("BOTH arms' spec the EMPTY STRING", m(A, spec=""), m(B, spec=""), (True, True)),
        ("BOTH arms' CPU identity ABSENT", m(A, cpu=None), m(B, cpu=None), (True, True)),
        ("arm B's CPU identity ABSENT", copy.deepcopy(A), m(B, cpu=None), (True, True)),
        ("BOTH arms' Python ABSENT", m(A, python=None), m(B, python=None), (True, True)),
        # ⚠ str(None).split(".") is ["None"] -- two absences that compared EQUAL AND TRUTHY
        ("BOTH arms' Python the STRING 'None'",
         m(A, python="None"), m(B, python="None"), (True, True)),
        ("BOTH arms' numpy ABSENT", m(A, numpy=None), m(B, numpy=None), (True, True)),
        ("BOTH arms' platform ABSENT", m(A, platform=None), m(B, platform=None), (True, True)),
    ]


class _SkipSection(Exception):
    """This section is out of scope for this distribution, by protocol §2c."""


def _subset_source():
    """(text, subset) from the governing document, or the highest one that declares a subset.

    ⛔ THE FIRST VERSION OF THIS CONTROL TESTED NOTHING. It read the subset from the GOVERNING
    document, and section 2c is declared in v8, which is stamped and pending -- so every case
    printed a warning and skipped, on the day the rule was written. **A control whose branch no
    input has taken is undefined, not settled**, and this project's other paper is largely about
    controls that never execute.

    ⚠ SO IT FALLS BACK, AND SAYS SO. The rule is a property of the declaration, not of which
    document happens to be in force, so it can be exercised against the highest declaration
    present. What it does NOT do is treat a pending document as authority for anything else.
    """
    import check_commitments as _CC
    import re as _re
    gov = _governing(HERE)
    text = (HERE / gov).read_text(encoding="utf-8")
    subset = _CC.distribution_subset(text)
    if subset:
        return text, subset
    best = None
    for f in sorted(HERE.glob("PRE-REGISTRATION*.md")):
        m = _re.search(r"-v(\d+)-", f.name)
        v = int(m.group(1)) if m else 1
        txt = f.read_text(encoding="utf-8")
        if _CC.distribution_subset(txt) and (best is None or v > best[0]):
            best = (v, f.name, txt)
    if best:
        if not _subset_source._said:
            print("    %s %s declares the subset and is NOT authority; the RULE is exercised"
                  % (chr(0x26A0), best[1]))
            print("      against it anyway, because the rule is a property of the declaration.")
            _subset_source._said = True
        return best[2], _CC.distribution_subset(best[2])
    return text, set()


_subset_source._said = False


def subset_rule_cases():
    """§2c's rule: a distribution's absent files must be EXACTLY the complement of the subset.

    ⛔ THE PACKAGE SHIPPED A CONTROL THAT COULD NOT PASS INSIDE THE PACKAGE, for two protocol
    versions, because every gate ran the checker against the SOURCE tree and never once where a
    reproducer runs it.

    ⚠ THE OBVIOUS REPAIR -- skip pinned files that are not present -- WOULD BE THE ABSENCE DEFECT
    AGAIN, and would make deleting a file the way to avoid its digest being checked. So the rule is
    an equality, and these cases exist because a rule with a branch no test has taken is undefined
    rather than settled. The `hide` case is the one that matters: it is the attack the naive repair
    would have allowed.
    """
    import check_commitments as _CC
    text, subset = _subset_source()
    pinned = [n for n, _d in _CC.commitments(text)]
    if not subset:
        return [("NO document in this tree declares a distribution subset", None, None)]
    comp = {n for n in pinned if n not in subset}
    return [
        ("a genuine distribution: absent == the complement", set(comp), True),
        ("a subset file ALSO deleted -- hiding a pinned file", set(comp) | {"train.py"}, False),
        ("a partial distribution: one complement file present", set(list(comp)[1:]), False),
        ("the source tree: nothing absent", set(), False),
        ("everything absent", set(pinned), False),
    ]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace",
                                  line_buffering=True)
    print("=" * 78)
    print("  CONTROL TESTS -- every attack rounds 4 and 5 used, all of which must be refused")
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
    # {D} THIS CRASHED INSIDE THE PACKAGE, with a FileNotFoundError traceback, on the file the
    # reproduction call tells a stranger to run. `measure_hardware.py` and the `runs/` fixtures are
    # OURS and are deliberately not distributed, so the suite it ships with died at the section
    # that needs them. The build had just gained a check that every shipped module IMPORTS -- and
    # importing a script is not running it, so it passed.
    #
    # {W} THE SCOPE IS TAKEN FROM §2c, NOT FROM WHETHER THE FILES HAPPEN TO BE THERE. "Skip when
    # absent" is the absence defect; "absent because the protocol says this distribution does not
    # contain it" is a rule. If `measure_hardware.py` IS in scope and its fixtures are gone, that
    # is still a failure.
    _text, _sub = _subset_source()
    _mh_in_scope = (not _sub) or ("measure_hardware.py" in _sub)
    _fixtures = [HERE / "runs" / n / "run.json" for n in ("tpc-thr-1", "amd-thr-1")]
    if not all(f.exists() for f in _fixtures):
        if _mh_in_scope:
            print("    " + D + " the hardware fixtures are MISSING and measure_hardware.py is in")
            print("    scope here. That is a broken tree, not a distribution.")
            missed += 1
        else:
            print("    -- not in this distribution (protocol section 2c): measure_hardware.py and")
            print("    its run fixtures are not shipped, so these cases are out of scope here.")
            print("    They are exercised in the source tree, where the instrument lives.")
        A = B = None
    else:
        A = json.loads(_fixtures[0].read_text(encoding="utf-8"))
        B = json.loads(_fixtures[1].read_text(encoding="utf-8"))
    work = pathlib.Path(tempfile.mkdtemp(prefix="mh-"))
    try:
        if A is None:
            raise _SkipSection
        for label, ra, rb, w in hardware_attacks(A, B):
            da, db = _arms(work, ra, rb, w)
            rc, out = run(HERE, "measure_hardware.py", "--a", str(da), "--b", str(db),
                          "--out", str(work / "o.json"))
            ok = "ok  MATCHED-STACK" not in out
            print("    %s %-52s" % ("refused " if ok else D + " PASSED", label))
            caught += ok
            missed += not ok
    except _SkipSection:
        pass
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print()
    print("  check_commitments.py -- the distribution-subset rule (protocol section 2c)")
    import check_commitments as _CCX
    _text, _subset = _subset_source()
    for _label, _absent, _want in subset_rule_cases():
        if _want is None:
            print("    " + chr(0x26A0) + " %s" % _label)
            continue
        _got = bool(_subset) and bool(_absent) and _absent == {
            n for n, _d in _CCX.commitments(_text) if n not in _subset}
        _ok = _got == _want
        print("    %s %-52s" % ("ok      " if _ok else D + " WRONG ", _label))
        caught += _ok
        missed += not _ok

    # ⛔ AND THE POSITIVE CASE, without which the whole file passes against a tool that refuses
    # everything. The real pair must still be admissible.
    print()
    if A is None:
        real_ok = True
        print("  --      the REAL pair is not in this distribution, so it is not asserted here")
    else:
        rc, out = run(HERE, "measure_hardware.py", "--a", "runs/tpc-thr-1",
                      "--b", "runs/amd-thr-1",
                      "--out", str(pathlib.Path(tempfile.gettempdir()) / "m4-selftest.json"))
        real_ok = "ok  MATCHED-STACK" in out
    if A is not None:
        print("  %s the REAL pair is still admissible"
              % ("ok      " if real_ok else D + " BROKEN"))
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
