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
import ast
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
    ("check_commitments.py",
     "the control that enforces them -- v3 §2 was prose and was broken the next day"),
    ("test_controls.py",
     "every attack rounds 4 and 5 used against these controls, as a suite -- run it"),
    ("check_signature.py",
     "who asserted the protocol documents. Nothing IMPORTS it, so the dependency closure "
     "below would never have pulled it in -- and an anchor answers WHEN, never WHO"),
    ("corpus/verify_shipped.py",
     "check the shipped corpus against the manifest, using only what the package contains"),
    ("ENVIRONMENT-LOCK.json",
     "the interpreter and library recorded -- NOT a lock; see the file"),
    ("PILOT-2026-08-29.md", "the observation that made the thread pin part of the protocol"),
    ("AMENDMENT-2026-08-30.md",
     "a deviation from the protocol, disclosed to the reproducer rather than to a reader later"),
    ("corpus/MANIFEST.json", "the corpus, its digests and its Merkle root"),
    ("corpus/MANIFEST.json.ots", "the proof the corpus was fixed BEFORE the first training step"),
    ("corpus/sources.json", "where each text came from, so the corpus can be rebuilt from source"),
    ("corpus/build_corpus.py", "how raw became clean. The cleaning is part of the specification"),
)


# ⛔ INSTANCE THIRTEEN, AND V7 PAID FOR IT THE WRONG WAY. Every protocol document and its proof
# were listed here BY NAME, so shipping a new version meant editing this file -- and v7 recorded
# that edit as a cost of v6's rule rather than as the enumeration defect it was. A package that
# silently omits the version governing it is the exact failure `build_package` already refuses one
# line below, so the list was one forgotten edit away from producing it.
#
# ⚠ THE PROOF IS NOT OPTIONAL. A document shipped without its `.ots` is a rule a reader cannot
# check, so a missing proof raises rather than being skipped -- the projection fails closed.
def _local_imports(py):
    """Module names this file imports that are OUR files, resolved by reading the source.

    ⛔ `check_commitments.py` GAINED `import ots_verify` AND THE PACKAGE LIST DID NOT. The build
    reported exit 0 and shipped a package in which `check_commitments.py` and `test_controls.py`
    both died with ModuleNotFoundError -- the two scripts a reproducer is asked to run to check
    that anything here is what it claims. **The exit code was the envelope; the package was the
    letter, and nobody opened it.**

    ⚠ AND ADDING THE TWO NAMES TO THE LIST WOULD BE THE DEFECT, NOT THE FIX. A hand-kept list of
    what to ship goes stale the next time a script gains an import, which is the same shape as the
    protocol-document lists removed a section earlier. So the dependency is DERIVED: what a shipped
    script imports, the package contains, transitively.
    """
    try:
        tree = ast.parse(py.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return {n for n in names if (HERE / (n + ".py")).exists()}


def _with_dependencies(contents):
    """Close the shipped set over local imports, and over the signatures beside each document."""
    have = {rel for rel, _why in contents}
    out = list(contents)
    queue = [rel for rel in have if rel.endswith(".py")]
    while queue:
        rel = queue.pop()
        for mod in _local_imports(HERE / rel):
            dep = mod + ".py"
            if dep not in have:
                have.add(dep)
                out.append((dep, "imported by %s -- without it that script does not run" % rel))
                queue.append(dep)
    # ⛔ THE SIGNATURES DID NOT SHIP. This version's own section 4 says an anchor answers WHEN and
    # a signature answers WHO -- and the package carried every proof and not one signature, so the
    # question it introduced could not be asked by the person it was introduced for.
    for rel in sorted(have):
        if rel.endswith(".md") and (HERE / (rel + ".asc")).exists() and rel + ".asc" not in have:
            out.append((rel + ".asc", "its detached signature -- the anchor says WHEN, this WHO"))
    return tuple(out)


def _protocol_contents():
    out = []
    for doc in sorted(HERE.glob("PRE-REGISTRATION*.md")):
        why = ("THE PROTOCOL THIS STUDY RUNS UNDER"
               if doc.name == "PRE-REGISTRATION-v3-CONFIRMATORY.md"
               else "a protocol document, retained as part of the record")
        out.append((doc.name, why))
        if not (doc.parent / (doc.name + ".ots")).exists():
            raise SystemExit(
                D + " %s has no .ots proof. Shipping a protocol document a reader cannot check "
                "the provenance of is worse than not shipping it." % doc.name)
        out.append((doc.name + ".ots", "its OpenTimestamps proof"))
    return tuple(out)


CONTENTS = _with_dependencies(CONTENTS + _protocol_contents())


def publication_preconditions(expected_included):
    """v6 section 7's last two conditions, in code instead of in prose.

    ⛔ A REVIEWER DEMONSTRATED BOTH. `--with-target --publishing` wrote `EXPECTED.json` with no
    public commitment to the digest it contains, and `--publishing` succeeded with no reporting
    address and no close date. v6 listed them as known gaps so they would be commitments rather
    than discoveries -- which was the honest move, and is not the same as closing them.

    ⚠ A DECLARED GAP IS STILL A GAP. Writing "not yet enforced in code" converts a defect into a
    disclosure, and a reader who trusts the disclosure still gets a build that publishes a target
    nobody committed to. This is the enforcement; the disclosure stays in the paper as history.
    """
    import datetime
    fail = []

    # ⛔ A TARGET NOBODY COMMITTED TO IS NOT A PREDICTION. If the expected digest is published
    # without a prior public commitment, nothing stops it being chosen AFTER seeing a result. The
    # commitment is the anchored protocol document pinning the pipeline that produces it.
    if expected_included:
        import check_commitments as _CC
        found, _rej = _CC.governing(HERE)
        if not found:
            fail.append("EXPECTED.json is being published and NO anchored protocol document "
                        "governs. The target would be a number with no prior commitment behind "
                        "it, which is the thing this design exists to rule out.")

    # ⛔ A WINDOW WITH NO CLOSE DATE NEVER CLOSES, and a report with nowhere to arrive is not a
    # report. v3 section 7 makes both load-bearing: everything filed by the close date is reported,
    # including nothing.
    reg = HERE / "REGISTRATION.json"
    if not reg.exists():
        fail.append("REGISTRATION.json is absent: no reporting address and no close date. v3 "
                    "section 7 promises that everything filed by the close date is reported, "
                    "which is unfalsifiable without a date and unreachable without an address.")
    else:
        try:
            r = json.loads(reg.read_text(encoding="utf-8"))
        except Exception as e:                                                  # noqa: BLE001
            r = {}
            fail.append("REGISTRATION.json does not parse (%s)." % e)
        # ⛔ THE FIRST VERSION OF THIS CHECK ACCEPTED THE TEMPLATE'S OWN PLACEHOLDER. It refused
        # only "", "None", "TBD" and "?", so `report_to` reading "FILL IN: the URL a reproducer
        # files at..." passed -- an unfilled field satisfying the gate written to require it. Only
        # the date was caught, and only because a date must PARSE. Testing the shape of a value is
        # not testing the claim it makes.
        for key, why in (("report_to", "nowhere for a reproducer to file"),
                         ("window_closes_utc", "a window with no close date never closes")):
            v = str(r.get(key) or "").strip()
            if not v or v in ("None", "TBD", "?", "-"):
                fail.append("REGISTRATION.json states no %s -- %s." % (key, why))
                continue
            if any(m in v.upper() for m in ("FILL IN", "TODO", "TBD", "XXX", "EXAMPLE.COM",
                                            "<", ">")):
                fail.append("REGISTRATION.json's %s is still a placeholder (%r) -- %s."
                            % (key, v[:40], why))
        addr = str(r.get("report_to") or "").strip()
        if addr and not addr.lower().startswith(("http://", "https://", "mailto:")):
            fail.append("report_to %r is not an address a reproducer can open. The reproduction "
                        "call promises 'the address published with these artifacts'; prose is "
                        "not an address." % addr[:40])
        w = str(r.get("window_closes_utc") or "").strip()
        if w:
            try:
                when = datetime.datetime.strptime(w[:10], "%Y-%m-%d").replace(
                    tzinfo=datetime.timezone.utc)
                if when <= datetime.datetime.now(datetime.timezone.utc):
                    fail.append("the reproduction window closed on %s. Publishing an invitation "
                                "to a window that has shut is not an invitation." % w[:10])
            except ValueError:
                fail.append("window_closes_utc %r is not a YYYY-MM-DD date." % w)
    return fail


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
    # ⛔ v3 WAS WRITTEN, STAMPED, ANNOUNCED AS GOVERNING -- AND NEVER ADDED HERE, so the
    # package shipped v1 and a v2 whose own text says it is superseded. v4 is added to CONTENTS in
    # the same commit that creates it, and both are named below, because "the governing document"
    # is now two files and a refusal that checks only one of them is the same defect again.
    # ⛔ AND IT WAS STILL HARDCODED TO v3, NEVER NAMING v5 -- in the file whose comment three
    # lines up calls that "the same defect again". A round-4 reviewer found it. The governing set
    # is DERIVED from the anchored documents, by the same function check_commitments uses, so the
    # package and the commitment check cannot disagree about which protocol governs.
    import check_commitments as _CC
    _anchored, _rejected = _CC.governing(HERE)
    if not _anchored:
        raise SystemExit(D + " no ANCHORED protocol document carries a digest table. A package "
                         "built against an unanchored draft has no protocol.")
    GOVERNING = sorted(_anchored)[-1][1]
    GOVERNING_M4 = "PRE-REGISTRATION-v4-CONFIRMATORY.md"
    for _v, _n, _why, _state in _rejected:
        print("  " + chr(0x26A0) + " %s is present and is NOT authority [%s]: %s"
              % (_n, _state, _why))
    # ⛔ v3 §2 SAID A CHANGED DIGEST VOIDS THE PRE-REGISTRATION, AND NOTHING CHECKED IT. train.py
    # was edited the next day and every tool here reported success for a day, SHA256SUMS included
    # -- a checksum regenerated from the bytes it polices cannot notice a substitution. The
    # commitment is verified before a package is built, not described in a document.
    # ⛔ `--publishing` DID NOT TRAVEL. This build ran `check_commitments.py` with no arguments
    # even on a publishing run, so the checker's publishing path -- the one refusing to publish
    # while a newer protocol version is stamped and not yet anchored -- was never taken. The strict
    # mode existed, was tested, and was unreachable from the only tool that calls it.
    _pub = ["--publishing"] if "--publishing" in sys.argv else []
    _cc = subprocess.run([sys.executable, "-X", "utf8", "check_commitments.py"] + _pub,
                         cwd=str(HERE),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    _tc = subprocess.run([sys.executable, "-X", "utf8", "test_controls.py"], cwd=str(HERE),
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    if _tc.returncode != 0:
        print((_tc.stdout or "") + (_tc.stderr or ""))
        raise SystemExit(D + " a control this package depends on accepts an input it must refuse. "
                         "Round 4's reviewers broke both new controls because their positive "
                         "controls were PROSE; the suite runs in the gate now.")
    if _cc.returncode != 0:
        print((_cc.stdout or "") + (_cc.stderr or ""))
        raise SystemExit(D + " a file the protocol commits by digest has changed. The "
                         "pre-registration is void until it is restored, or until a new version "
                         "re-commits it with the change justified. Not a build problem to route "
                         "around.")
    if not (HERE / GOVERNING_M4).exists():
        raise SystemExit(D + " %s is missing. It carries measurement 4's admissibility "
                         "conditions, committed before any second-machine run exists. A package "
                         "without it invites a comparison the protocol has not defined."
                         % GOVERNING_M4)
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

    # ⛔ THE ONLY REASON THIS EXISTS IS THAT A GREEN BUILD SHIPPED A BROKEN PACKAGE. Every check
    # above reads the SOURCE tree; none of them ever ran anything inside `package/`. So the build
    # now imports each shipped module with the package as the working directory, which is the
    # cheapest possible test that the artifact is what the exit code claimed.
    _mods = [r[:-3].replace("/", ".") for r, _w in CONTENTS
             if r.endswith(".py") and "/" not in r]
    _broken = []
    for _m in _mods:
        _r = subprocess.run([sys.executable, "-X", "utf8", "-c", "import " + _m],
                            cwd=str(OUT), capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
        if _r.returncode != 0:
            _broken.append((_m, ((_r.stderr or "").strip().splitlines() or [""])[-1][:80]))
    if _broken:
        print()
        for _m, _e in _broken:
            print("  " + D + " package/%s.py does not import: %s" % (_m, _e))
        raise SystemExit(D + " the package was written and it does not run. A build that reports "
                         "success while shipping scripts that die on import is the exit code "
                         "standing in for the artifact.")
    print("  ok  %d shipped module(s) import cleanly INSIDE the package" % len(_mods))

    # {D} IMPORTING IS NOT RUNNING, and the import check passed while `test_controls.py` died in
    # the package with a FileNotFoundError -- the exact file the reproduction call tells a stranger
    # to run. The envelope again: the module loaded, so the artifact was assumed to work.
    #
    # {W} `check_commitments.py` CANNOT PASS IN THE PACKAGE UNTIL v8 ANCHORS, because section 2c is
    # declared there and v6 is still in force. That is reported by name rather than excused, and
    # `--publishing` refuses on it -- publishing a package whose own control refuses is exactly the
    # failure this block exists to prevent.
    _run_in_pkg = [r for r, _w in CONTENTS
                   if r in ("test_controls.py", "check_signature.py", "corpus/verify_shipped.py",
                            "check_commitments.py")]
    _fail = []
    for _rel in _run_in_pkg:
        _r = subprocess.run([sys.executable, "-X", "utf8", _rel], cwd=str(OUT),
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        _tail = ((_r.stdout or "") + (_r.stderr or "")).strip().splitlines()
        print("  %s  package/%-24s exit %d" % ("ok " if _r.returncode == 0 else D, _rel,
                                               _r.returncode))
        if _r.returncode != 0:
            _fail.append((_rel, _tail[-1][:90] if _tail else ""))
    if _fail:
        print()
        for _rel, _why in _fail:
            print("      " + D + " %s: %s" % (_rel, _why))
        if "--publishing" in sys.argv:
            raise SystemExit(D + " a shipped control fails INSIDE the package. Publishing a "
                             "package whose own controls refuse is worse than shipping none.")
        print("  " + W + " REVIEW BUILD: continuing. check_commitments.py cannot pass here until")
        print("  v8 anchors and section 2c takes effect. --publishing makes this fatal.")

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
    if "--publishing" in sys.argv:
        _fail = publication_preconditions("--with-target" in sys.argv)
        if _fail:
            print()
            print("  " + D + " PUBLICATION PRECONDITIONS NOT MET (v6 section 7):")
            for _f in _fail:
                print("      - " + _f)
            raise SystemExit("  Stopping. These are publishing conditions; a REVIEW build (no "
                             "--publishing) is unaffected.")
        print("  ok  publication preconditions met (commitment, address, open window)")

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

    # ⛔ SHA256SUMS WAS WRITTEN FROM `shipped` -- THE LIST -- AND A REPRODUCER VERIFIES THE
    # TREE. Running the shipped controls during the build made CPython write __pycache__/*.pyc
    # into the package after the list was fixed, so verify_package.py reported unlisted files and
    # the package failed its own verifier. Both round-6 reviewers hit it. The list is the
    # intention; the directory is the artifact, and only one of them is what gets extracted.
    for _pyc in list(OUT.rglob("__pycache__")):
        if _pyc.is_dir():
            shutil.rmtree(_pyc, ignore_errors=True)
    lines = []
    for f in sorted(OUT.rglob("*")):
        if not f.is_file() or f.name == "SHA256SUMS":
            continue
        rel = str(f.relative_to(OUT)).replace(chr(92), "/")
        lines.append("%s  %s" % (hashlib.sha256(f.read_bytes()).hexdigest(), rel))
    (OUT / "SHA256SUMS").write_text(NL.join(lines) + NL, encoding="utf-8", newline=NL)
    _unlisted = sorted({str(f.relative_to(OUT)).replace(chr(92), "/")
                        for f in OUT.rglob("*") if f.is_file()}
                       - {L.split("  ", 1)[1] for L in lines} - {"SHA256SUMS"})
    if _unlisted:
        raise SystemExit(D + " %d file(s) in the package are still unlisted after writing "
                         "SHA256SUMS from the tree: %s" % (len(_unlisted), _unlisted[:4]))

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
