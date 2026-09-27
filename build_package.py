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
    # ⛔ THE KEY THAT MAKES check_signature.py CAPABLE OF PASSING, and my edit adding it put the
    # filename INSIDE the tuple above, making it three elements where every consumer unpacks two.
    # build_package.py then crashed on an untouched tree, and I did not notice because the REVIEW
    # PACKET built fine -- a different tool passing is not this tool passing, which is the same
    # envelope-for-letter mistake this project keeps naming.
    ("PUBKEY.asc",
     "the public key. Without it check_signature.py returns NO_PUBKEY for every document, so the "
     "check gives the same answer for a good signature and a forged one"),
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
    # ⛔ THE PACKAGE SHIPPED A VERIFIER WITH NO DATA. `ots_verify.py` reads ANCHORS.json to learn
    # which Bitcoin block roots a proof may be checked against; without it EVERY proof degrades to
    # "STRUCTURAL only -- naming a block is not being in it", so `check_commitments.py` found no
    # anchored protocol document and refused, and `test_controls.py` died trying to mutate a file
    # that was not there. Both failures, one absent file. Found on the first attempt to actually
    # PUBLISH, because review builds had an escape hatch that absorbed it.
    ("ANCHORS.json",
     "the Bitcoin block roots each proof is checked against. WITHOUT IT ots_verify.py can only "
     "say a proof NAMES a block, never that it is IN one"),
    ("HOW-TO-RECHECK-THE-ANCHORS.md",
     "how to re-fetch those roots from a source that is not us. Shipping our own pins without "
     "this would hand over a tool that looks like verification and is not"),
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


# ⛔ ADDING ANCHORS.json TO `CONTENTS` IS NOT THE FIX -- it is instance N, and listing it would be
# how instance N+1 gets made. `_with_dependencies` closes the shipped set over PYTHON IMPORTS, and a
# data file opened at runtime is not an import, so that closure could never have reached ANCHORS.json
# however correct it was. THE RELATION WAS WRONG, NOT THE LIST.
#
# ⚠ So the other relation is projected too: a filename a shipped script uses AS A VALUE, which names
# a file that really exists here, must either ship or be classified as deliberately absent WITH A
# REASON. Anything unclassified fails closed.
#
# ⚠ Two refinements, both found by running it rather than by reasoning about it:
#   - a string that is a STATEMENT is prose, not a filename -- docstrings name files constantly.
#   - a name that does not resolve to a real file here is a fragment ("S.json" from concatenation),
#     not a dependency. Requiring the file to EXIST makes the rule self-limiting.
DATA_DEP_ABSENT = {
    "CONTROL-SUITE-VERDICT.json":
        "an OUTPUT of test_controls.py (it write_text()s it), never an input",
    "measure_hardware.py":
        "deliberately not in this distribution under protocol section 2c; test_controls.py "
        "detects its absence and says so, rather than failing on it",
}


def _string_values(tree):
    """String constants used as VALUES. A string standing alone as a statement is documentation."""
    prose = {id(n.value) for n in ast.walk(tree)
             if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
             and isinstance(n.value.value, str)}
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in prose:
            yield n.value


def _data_dependencies(shipped):
    """{filename: {scripts naming it}} for real local files the import closure cannot see."""
    out = {}
    for rel in sorted(shipped):
        if not rel.endswith(".py"):
            continue
        p = HERE / rel
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        for v in _string_values(tree):
            v = v.strip()
            if v and "/" not in v and "\\" not in v and "\n" not in v and (HERE / v).is_file():
                out.setdefault(v, set()).add(rel)
    return out


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


# ⛔⛔ THE TARGET WAS MUTABLE, AND THIS FILE HELD TWO DIFFERENT DEFINITIONS OF IT. The digest a
# reproducer is asked to arrive at is the one number the whole design exists to commit in advance,
# and it was not among v18's commitments at all. Worse, `_target_digest()` read
# `runs/tpc-thr-1/run.json` while `main()` read `runs/det-1/run.json` and populated EXPECTED.json
# from the latter -- so **the target-free check was checking for a different target from the one
# eventually shipped.** A reviewer built a two-run fixture where they differ and executed it: the
# withheld document was the one containing A, while the document containing B went out.
#
# ★ IT IS INERT TODAY BY COINCIDENCE. Both runs currently carry the same weights digest, which is
# exactly why four rounds of review never saw it. A defect that is dormant because two numbers
# happen to agree is not a defect that has been avoided.
#
# ⛔ AND NOTHING PINNED THE REFERENCE. An author could, after the public commitment, edit
# `runs/det-1/run.json`, regenerate EXPECTED.json, and present a different target while every
# v18 file commitment still verified. That is the freedom a pre-registration exists to remove.
#
# ⇒ ONE FUNCTION DERIVES THE TARGET, and it derives it from a run whose bytes the governing
# document commits. `reference_run()` reads it, checks its digest against the protocol's own
# commitment table, and REFUSES rather than returning a number nobody promised.
REFERENCE_RUN = "runs/det-1/run.json"


def reference_run(strict=True):
    """The reference run, verified against the governing document's commitment. One definition.

    ⚠️ `strict=False` is for the REVIEW build only. Publishing a target nobody committed to is
    the thing this refuses; circulating a package internally before the protocol version that pins
    the run has been signed is ordinary, and the difference is stated rather than assumed.
    """
    f = HERE / REFERENCE_RUN
    if not f.is_file():
        raise SystemExit(D + " no reference run at %s. Train before packaging." % REFERENCE_RUN)
    raw = f.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    import check_commitments as _CC
    try:
        found, _rej = _CC.governing(HERE)
    except SystemExit:
        found = None
    pinned = None
    if found:
        pinned = dict(_CC.commitments(found.read_text(encoding="utf-8"))).get(REFERENCE_RUN)
    if pinned is None:
        msg = ("%s %s is not committed by %s. The reproduction TARGET is derived from this file, "
               "so an uncommitted reference means the number a reproducer is asked to match was "
               "never promised in advance -- and could be changed after seeing who is watching."
               % (D, REFERENCE_RUN, found.name if found else "any governing document"))
        if strict:
            raise SystemExit(msg)
        print("  " + msg)
    elif pinned != got:
        raise SystemExit(
            "%s %s hashes to %s and %s commits %s. The reference run has been edited since the "
            "protocol committed it, so the target is no longer the one that was promised."
            % (D, REFERENCE_RUN, got[:16], found.name, pinned[:16]))
    return json.loads(raw.decode("utf-8"))


def _target_digest(strict=True):
    """The weights digest a reproducer is supposed to arrive at. ONE source, verified."""
    try:
        return reference_run(strict=strict)["weights_sha256"]
    except (OSError, ValueError, KeyError):
        return ""


WITHHELD = []


def _protocol_contents():
    """Every protocol document and its proof -- EXCEPT any that quotes the target.

    ⛔ THREE OF THEM DO. v5 quotes the reference weights digest to show a pipeline edit was
    numerically inert; v8 and v9 quote it to show a provenance change altered no result. All three
    are correct, signed and anchored, and all three were added to the package AFTER v3 made it
    target-free. A reproducer receiving them holds the answer before starting, and the run stops
    being blind whether or not they meant it to.

    ⇒ They are WITHHELD FROM THE PACKAGE and named in NO-TARGET.md, with where to read them. The
      audit trail is not lost -- the public repository carries every version -- but a reproducer is
      no longer handed the number.

    ⚠️ THIS DOES NOT MAKE THE ORDERING TRUE AGAIN. Those documents are public, so the digest has
      been readable since v5 was published and no packaging choice can unpublish it. Withholding
      changes "handed the answer" to "could go and look", which is a materially better test and
      is not the same as a blind one. The paper reports that distinction rather than papering it.
    """
    # ⚠️ NON-STRICT HERE, DELIBERATELY. This runs at import time to decide which protocol
    # documents carry the target and must be withheld, and it runs on every build including a
    # review one. Refusing at import would make the package unbuildable until the version that
    # pins the reference run is signed -- so the strict check lives where the decision is taken,
    # in `publication_preconditions`, and this reports rather than raising.
    #
    # ⇒ The withheld set is still computed from the SAME one function, so it cannot diverge from
    # the target that ships. That divergence was the defect.
    target = _target_digest(strict=False)
    out = []
    for doc in sorted(HERE.glob("PRE-REGISTRATION*.md")):
        if target and target.encode() in doc.read_bytes():
            WITHHELD.append(doc.name)
            continue
        why = ("THE PROTOCOL THIS STUDY RUNS UNDER"
               if doc.name == "PRE-REGISTRATION-v3-CONFIRMATORY.md"
               else "a protocol document, retained as part of the record")
        out.append((doc.name, why))
        if not (doc.parent / (doc.name + ".ots")).exists():
            # ⛔ AND SAY WHAT THIS MEANS FOR THE PACKAGE, NOT JUST FOR THE FILE. A round-6
            # reviewer found `package/` carrying v2 through v14 and not v15 through v18 -- so the
            # WITHDRAWAL was not in the artifact at all -- and concluded the newer versions were
            # being withheld as target-bearing. They are not: none of them contains the target.
            # The package on disk was simply built before v18 existed, and every build since has
            # stopped here, because the newest protocol document is not in force.
            raise SystemExit(
                D + " %s has no .ots proof. Shipping a protocol document a reader cannot check "
                "the provenance of is worse than not shipping it -- and until the newest version "
                "is in force NO package can be built, so any `package/` on disk predates it and "
                "does not contain the current protocol. Run `python prepare_anchor.py`."
                % doc.name)
        out.append((doc.name + ".ots", "its OpenTimestamps proof"))
    if not target:
        raise SystemExit(
            D + " cannot read the reference weights digest, so 'is this package target-free' "
            "cannot be answered. Refusing to build a package whose central property is unchecked.")
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
    # ⛔ ONE LOOKUP, AND ITS REFUSAL IS A COMPLAINT RATHER THAN AN EXIT. `governing()` raises on a
    # TAMPERED tree -- a higher version present with no proof beside it -- and this function's
    # contract is to RETURN the conditions that are unmet. Letting the exception through skipped
    # every condition after it and killed the build with a message about proofs, so a run missing
    # its reporting address AND its baseline would report neither. A caller that asks "what is
    # wrong" must be told everything that is wrong.
    import check_commitments as _CC
    try:
        found, _rej = _CC.governing(HERE)
    except SystemExit as _e:
        found = None
        fail.append("no protocol document governs: %s" % str(_e)[:200])

    # ⛔ THE PROGRAM PRINTED THAT IT HAD CHECKED A COMMITMENT IT NEVER LOOKED FOR. The condition
    # asked only whether an anchored protocol document exists -- which is not a reproducer
    # commitment -- and the caller then printed "publication preconditions met (commitment,
    # address, open window)". A reviewer ran it against a synthetic tree with an anchored protocol,
    # a reporting address, a future date and **no public commitment**, and got `[]` back.
    #
    # ★ A FALSE GREEN IS BAD; A FALSE GREEN THAT NAMES THE THING IT DID NOT CHECK IS WORSE,
    # because it is the sentence an author would quote to show the rule was enforced.
    #
    # ⛔⛔ AND THE ARGUMENT ABOVE WAS WRONG, WHICH A ROUND-6 REVIEWER FOUND BY READING THE CODE
    # AGAINST THE DOCUMENT IT CLAIMS TO IMPLEMENT. This block used to require an exposure capture
    # to exist AND to record at least one commitment-labelled issue before `EXPECTED.json` could be
    # published, under a comment asserting that "the rule itself survives the withdrawal".
    #
    # v18 §1c says, in bold: **Nothing here obliges any of them to be run.** It drops the exposure
    # floor, drops `INSUFFICIENT EXPOSURE`, and drops "announcement is an obligation, not an
    # option". A gate that will not publish until somebody else has filed an issue is the exposure
    # dependency wearing a different name -- and it is worse than the floor was, because the floor
    # was at least in a document a reader could find. **The withdrawal reached the prose and
    # stopped there**, which is this project's most reliable defect: a fix is not finished until
    # the other call sites have been read.
    #
    # ⚠️ THE PROPERTY IT WAS PROTECTING IS REAL AND IS NOT LOST. If the target is published before
    # anything commits to it, it could have been chosen after seeing a result. But the commitment
    # that rules that out is the ANCHORED PROTOCOL DOCUMENT pinning the reference run -- v18 §2a
    # pins `runs/det-1/run.json` by digest -- and that is inside the laboratory. It does not
    # require a stranger to act. Requiring one made publication depend on a party under nobody's
    # control, which is the dependency route 2 was chosen to refuse.
    #
    # ⇒ So what is checked is the commitment that actually does the work, and nothing else.
    if expected_included:
        if not found:
            fail.append("EXPECTED.json is being published and NO anchored protocol document "
                        "governs. The target would be a number with no prior commitment behind "
                        "it, which is the thing this design exists to rule out.")
        else:
            # ⚠️ NOT "a document exists" -- that was the false green a reviewer found two rounds
            # ago. The governing document must pin THIS target, by digest, and `reference_run`
            # verifies the run file against that pin or refuses.
            try:
                reference_run(strict=True)
            except SystemExit as _e:
                fail.append("EXPECTED.json is being published and the governing document does not "
                            "commit to the reference run it is derived from: %s" % str(_e)[:200])

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
        # ⛔ THE GATE ACCEPTED ANY FUTURE DATE, AND v18 FIXES ONE. A reviewer put 2099-12-31 in a
        # synthetic registration and it passed. The cutoff is carried by v15, v16 and v17, all
        # signed and Bitcoin-anchored, and §1d keeps it precisely because an open-ended stopping
        # point would let the study run until a reproduction arrives. **A gate that accepts any
        # future date restores exactly the freedom the anchored date removes.**
        #
        # ⇒ The required date is read OUT of the governing document rather than repeated here,
        # so this file cannot disagree with the protocol -- the rule `check_commitments.py` opens
        # with, applied to a date instead of a digest.
        if found and w:
            import re as _re
            # ⚠ v17 writes "close date of **7 December 2026**" and v18 writes "**the close date
            # of 7 December 2026**". A pattern that matched one and not the other would have
            # reported the date unreadable on half the versions it must read.
            _m = _re.search(r"close date[^.]{0,60}?"
                            r"(?:\*\*)?(\d{1,2} \w+ \d{4})(?:\*\*)?|"
                            r"close date[^.]{0,60}?(\d{4}-\d{2}-\d{2})",
                            found.read_text(encoding="utf-8"))
            _want = None
            if _m:
                _raw = _m.group(1) or _m.group(2)
                try:
                    _want = (datetime.datetime.strptime(_raw, "%d %B %Y")
                             if _m.group(1) else
                             datetime.datetime.strptime(_raw, "%Y-%m-%d")).strftime("%Y-%m-%d")
                except ValueError:
                    _want = None
            if _want is None:
                fail.append("%s states no close date this file can read, so the registration's "
                            "window cannot be checked against the protocol. The date is a "
                            "pre-committed parameter; an unreadable one is an uncommitted one."
                            % found.name)
            elif w[:10] != _want:
                fail.append("REGISTRATION.json closes the window on %s and %s fixes %s. A cutoff "
                            "the builder does not bind is a stopping point that can be moved after "
                            "the fact." % (w[:10], found.name, _want))

    # ⛔ v18 ROUND 4 MADE THESE PUBLISHING CONDITIONS, AND v18 §1 REMOVED THE CLAIM THEY SERVED.
    # They required `DISTRIBUTION-PLAN.md` and `capture_exposure.py` to be pinned by the governing
    # document, a stamped exposure baseline to exist, and that baseline to predate the first
    # recorded attempt. Every one of them was the right rule for a protocol that INFERRED SOMETHING
    # FROM SILENCE: if the paper is going to say "nobody reproduced it" and mean something by it,
    # then who was watching has to be measured, and measured before the announcement.
    #
    # ⇒ THE CLAIM IS WITHDRAWN, SO THE CONDITIONS GO WITH IT. A gate whose purpose has been
    # removed does not become harmless by being left in place -- it becomes a rule nobody can
    # explain, which is the thing that gets routed around the first time it is inconvenient. The
    # baseline capture still exists and is still stamped; nothing now requires it to.
    #
    # ⚠ WHAT IS KEPT: if the distribution record EXISTS, it must not be self-contradictory. That
    # is not an obligation to distribute -- an empty log passes -- it is the ordinary refusal to
    # publish alongside an artifact that fails its own integrity check.
    try:
        import attempts as _AT
        for _b in _AT.check(_AT.read_log(), verbose=False):
            fail.append("the distribution record does not check out: %s" % _b)
    except SystemExit as _e:
        fail.append("the distribution record cannot be read: %s" % str(_e)[:160])
    return fail


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    # ⇒ THE SAME ONE FUNCTION `_target_digest` USES. Two readers of the target was the defect;
    # a second reader here would reintroduce it however carefully it was written.
    run = reference_run(strict="--publishing" in sys.argv)

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
    # ⛔ THIS UNPACKED FOUR FIELDS FROM A FIVE-FIELD REJECTION and died with "too many values to
    # unpack" the first time a legitimate PENDING successor existed -- so the next ordinary
    # protocol round would have broken the shipping build path, and nothing would have said so
    # until it did. A reviewer minted a synthetic v10 with a calendar-only proof and found it.
    # Reading by NAME survives the next widening; the fixture below makes sure of it.
    for _r in _rejected:
        print("  " + chr(0x26A0) + " %s is present and is NOT authority [%s]: %s"
              % (_r.name, _r.state, _r.why))
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
    # ⇒ ISSUE A NONCE AND CLEAR ANY EXISTING VERDICT BEFORE THE SUITE RUNS. A file that cannot
    # survive this deletion cannot afterwards be mistaken for this run's output, and a verdict
    # without this nonce was produced by something else.
    import os as _os2
    import secrets as _sec
    _NONCE = _sec.token_hex(8)
    _stale_verdict = HERE / "CONTROL-SUITE-VERDICT.json"
    if _stale_verdict.exists():
        _stale_verdict.unlink()
    _tc = subprocess.run([sys.executable, "-X", "utf8", "test_controls.py"], cwd=str(HERE),
                         capture_output=True, text=True, encoding="utf-8", errors="replace",
                         env=dict(_os2.environ, CONTROL_SUITE_NONCE=_NONCE))
    # ⛔ EVERY PROTECTION BUILT LAST ROUND WAS INSIDE `if _tc.returncode != 0`. On the GREEN
    # path -- the one a shipping build takes -- the gate never opened the verdict file, never
    # checked the nonce, and never looked at the tree digest. The structured verdict was consulted
    # to explain a failure and never to justify a pass. A reviewer put it exactly right: the
    # round-11 repair was dead code on the path that matters, and it goes live the moment the
    # circularity resolves, which is why it must be fixed in the bytes the next version pins.
    #
    # ⇒ The verdict is read and validated BEFORE the branch, on every path. A pass that cannot
    # produce a verdict from this run over this tree is not a pass.
    import json as _json0
    _vp0 = HERE / "CONTROL-SUITE-VERDICT.json"
    try:
        _v0 = _json0.loads(_vp0.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise SystemExit(D + " the control suite produced no machine-readable verdict at %s. A "
                         "run that leaves no verdict cannot justify a pass." % _vp0.name)
    if _v0.get("nonce") != _NONCE:
        raise SystemExit(
            D + " the verdict does not carry this run's nonce (%r vs %r), so it was not produced "
            "by the suite this gate just ran." % (_v0.get("nonce"), _NONCE))
    import importlib.util as _ilu0
    _spec0 = _ilu0.spec_from_file_location("_tc_mod", str(HERE / "test_controls.py"))
    _tcm = _ilu0.module_from_spec(_spec0)
    _spec0.loader.exec_module(_tcm)
    _now_digest = _tcm.tree_digest()
    if _v0.get("tree_digest") != _now_digest:
        raise SystemExit(
            D + " the verdict describes a tree digesting to %r and this tree digests to %r. The "
            "verdict is about different bytes than the ones being packaged."
            % (_v0.get("tree_digest"), _now_digest))
    if _tc.returncode == 0 and not _v0.get("security_ok"):
        raise SystemExit(
            D + " the suite exited 0 and its verdict says an attack passed that should not have. "
            "The exit code and the verdict disagree, and the verdict is the one that carries the "
            "security claim.")

    if _tc.returncode != 0:
        print((_tc.stdout or "") + (_tc.stderr or ""))
        # ⛔ THIS SAID "A CONTROL ACCEPTS AN INPUT IT MUST REFUSE" WHENEVER THE SUITE EXITED
        # NON-ZERO, and the suite exits non-zero for two unrelated reasons: an attack passing,
        # which is a security failure, and the positive control failing, which while v9 pends is
        # a true statement about a red tree. So the build refused on an honest tree citing an
        # attack that did not happen. A reviewer flagged the counter conflation three rounds
        # running and it became consequential only when the suite reached the build gate.
        _out = (_tc.stdout or "") + (_tc.stderr or "")
        # ⛔ THIS CLASSIFIED BY SUBSTRING AND EXITED BEFORE REPORTING WHAT WAS ACTUALLY WRONG.
        # A round-10 reviewer changed `train.py` in a copied tree: check_commitments.py correctly
        # named it as a ninth changed committed file, and this gate exited with the routine
        # liveness message and never surfaced the substitution. Tampering and an honest pending
        # window ARE distinguishable -- check_commitments.py distinguishes them -- and the gate
        # discarded the distinction. The same reviewer then forged the substring itself.
        #
        # ⚠ The verdict is read as DATA, and the concrete changed-file list is printed BEFORE
        # any exit, so a red tree always says which files moved rather than only that it is red.
        import json as _json
        _vp = HERE / "CONTROL-SUITE-VERDICT.json"
        try:
            _v = _json.loads(_vp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raise SystemExit(D + " the control suite left no machine-readable verdict at %s, so "
                             "this gate would have to classify its decision by reading English. "
                             "That is how a forged summary line got past it." % _vp.name)
        # ⛔ THIS READ WHATEVER FILE WAS ON DISK. A round-11 reviewer pre-wrote a green verdict,
        # made the suite crash before its own write, and this gate consumed the stale one. The
        # structured verdict correctly killed round 10's substring forgery and replaced it with a
        # fresher problem: a decision read from an artifact not bound to what produced it, which
        # is the same disease one layer down from the one just fixed.
        #
        # ⇒ The gate issues a nonce in the environment and the verdict must carry it back.
        if _v.get("nonce") != _NONCE:
            raise SystemExit(
                D + " the control suite's verdict does not carry this run's nonce (%r vs %r), so "
                "it was not produced by the suite this gate just ran. A stale verdict is how a "
                "crashed suite reports a clean tree." % (_v.get("nonce"), _NONCE))
        _cc = subprocess.run([sys.executable, "-X", "utf8", "check_commitments.py"],
                      cwd=str(HERE), capture_output=True, text=True)
        _changed = [l.strip() for l in (_cc.stdout or "").splitlines()
                    if l.strip().endswith("changed")]
        if _changed:
            print()
            print("  " + W + " %d committed file(s) differ from the governing table:" % len(_changed))
            for _c in _changed[:12]:
                print("      " + _c)
            print("  A pending window explains a table that does not yet govern. It does not")
            print("  explain a file whose bytes moved.")
        if _v.get("security_ok") and _v.get("positive_control_failed"):
            raise SystemExit(
                D + " the control suite's POSITIVE case failed and no attack passed (%d refused, "
                "%d passed that should not have). The real tree does not currently satisfy "
                "check_commitments.py -- a liveness statement about the tree, not a security "
                "statement about these controls -- so this package is not built. The changed "
                "files above, if any, are a SEPARATE matter and are not excused by the window."
                % (_v.get("attacks_refused", -1),
                   _v.get("attacks_passed_that_should_not_have", -1)))
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
    # ⛔ THE DATA DEPENDENCIES, projected. See _data_dependencies: the import closure is blind to a
    # file a script merely OPENS, and that blindness shipped a verifier with no pins.
    _ship = {r for r, _w in CONTENTS}
    _unclassified = {}
    for _dep, _by in sorted(_data_dependencies(_ship).items()):
        if _dep in _ship or _dep in WITHHELD or _dep in DATA_DEP_ABSENT:
            continue
        _unclassified[_dep] = _by
    if _unclassified:
        print()
        for _dep, _by in sorted(_unclassified.items()):
            print("  " + D + " %s is named by %s and does not ship"
                  % (_dep, ", ".join(sorted(_by))))
        raise SystemExit(D + " a shipped script opens a file the package does not contain. Add it "
                         "to CONTENTS if it is an input, or to DATA_DEP_ABSENT with the reason it "
                         "is not -- an unexplained absence is how the verifier lost its pins.")
    print("  ok  %d data dependenc(ies) resolved, %d classified absent"
          % (len(_data_dependencies(_ship)), len(DATA_DEP_ABSENT) + len(WITHHELD)))

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
        # ⚠️ THIS MESSAGE USED TO SAY "cannot pass here until v8 anchors and section 2c takes
        # effect". v8 anchored in August and the failure stayed, because its real cause was that
        # ANCHORS.json never shipped -- so the excuse outlived the condition it named and went on
        # absorbing a defect for six protocol versions. A tolerated failure needs a reason that
        # EXPIRES, or it becomes the reason nobody looks.
        print("  " + W + " REVIEW BUILD: continuing, and the failure above is NOT expected.")
        print("  Every shipped control is meant to pass here. --publishing makes this fatal.")

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
        # ⚠️ THIS NAMED "commitment" WHILE NOTHING CHECKED ONE. It now lists exactly the
        # conditions that ran, and the commitment clause only appears when the target is being
        # published -- which is the only time that rule applies.
        print("  ok  publication preconditions met: %s"
              % ("public commitment, reporting address, open window bound to the protocol"
                 if "--with-target" in sys.argv
                 else "reporting address, open window bound to the protocol"))

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
            + NL
            # ⇒ A READER LEARNS OF THE OMISSION FROM THE PACKAGE, NOT FROM US. A package that is
            #   quietly incomplete is worse than one that says what it left out and why: the
            #   second can be argued with.
            + (("" if not WITHHELD else
                NL + "## What this package deliberately does NOT contain" + NL + NL
                + "These protocol documents are **withheld from this package because each one "
                + "quotes the reference weights digest** — correctly, in the course of showing "
                + "that some change altered no result:" + NL + NL
                + NL.join("- `%s`" % w for w in WITHHELD) + NL + NL
                + "Withholding them keeps this package blind. It does **not** make the ordering "
                + "true again: they are public in the project's repository, so the digest has "
                + "been readable since the first of them was published. **If you want to audit "
                + "the full protocol chain, read them there — but do so after you have run the "
                + "training, or you lose the property this omission exists to protect.**" + NL))
            , encoding="utf-8", newline=NL)
        shipped.append("NO-TARGET.md")

    # ⛔ AND THE TARGET SHIPPED ANYWAY, THREE TIMES, WHILE NO-TARGET.md SAT BESIDE IT SAYING IT
    # HAD NOT. The rule above guards ONE FILE -- EXPECTED.json -- because that is where the target
    # was the day the rule was written. It never asked the question the rule is actually about:
    # *is the answer anywhere in what we are about to hand a reproducer?* It is. v5 quotes the
    # weights digest to show a pipeline edit was numerically inert; v8 and v9 quote it to show a
    # provenance change altered no result. All three are correct, signed, anchored documents, and
    # all three were added to the package after v3 made it target-free. Each was added by asking
    # "is this part of the protocol chain?" and never "does this contain the answer?"
    #
    # ⇒ PROJECT OVER THE PACKAGE, DO NOT ENUMERATE THE PLACES A TARGET HAS BEEN SEEN. This scans
    #   every byte of every shipped file and fails closed. A note in a file is not a control;
    #   NO-TARGET.md was a note, and it was wrong for as long as it existed.
    _target = run["weights_sha256"]
    _leaks = []
    for _p in sorted(OUT.rglob("*")):
        if not _p.is_file():
            continue
        if _p.name == "EXPECTED.json":
            continue      # its whole purpose is to carry the target, under --with-target
        try:
            _blob = _p.read_bytes()
        except OSError:
            _leaks.append((_p, "unreadable"))     # cannot clear it => do not clear it
            continue
        if _target.encode() in _blob or _target.encode().upper() in _blob:
            _leaks.append((_p.relative_to(OUT).as_posix(), "carries the reference digest"))
    if _leaks and "--with-target" not in sys.argv:
        print()
        print("  " + D + " THE PACKAGE IS NOT TARGET-FREE. %d shipped file(s) contain the "
              "reference" % len(_leaks))
        print("  weights digest %s..., which a reproducer is supposed to" % _target[:24])
        print("  arrive at without having seen:")
        for _rel, _why in _leaks:
            print("      %-46s %s" % (_rel, _why))
        print()
        print("  This is the ordering v3 section 3 exists to establish: the commitment comes")
        print("  first, the target after. A reproducer holding the digest can self-select, and")
        print("  the run stops being blind whether or not they meant it to.")
        print()
        print("  ⚠ These documents are SIGNED AND ANCHORED and cannot be edited to remove it.")
        print("  The disposition is an author decision, not a build flag: exclude them from the")
        print("  package (the public repository keeps the audit trail), or ship them and report")
        print("  in the paper that the target was public before the window opened.")
        raise SystemExit("  Stopping rather than handing out the answer.")

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
    # ⛔ THE COMPLETION MARKER IS WRITTEN AFTER THIS LINE IS FIXED, and it lands INSIDE the
    # package. So every package this build produced carried one file that SHA256SUMS does not
    # list, and `verify_package.py` -- the command a reproducer is told to run FIRST -- reported
    # `BUILD-COMPLETE.json IS NOT LISTED in SHA256SUMS`. The build's own copy of that check passed
    # because it ran BEFORE the marker existed: the build and the reproducer were verifying two
    # different directories, and only one of them is the artifact.
    #
    # Round 8 fixed "a half-built package is byte-identical to a finished one" by adding a marker
    # whose whole value is being LAST, and the manifest is written from the tree -- so the two
    # requirements were in direct contradiction and the contradiction shipped.
    #
    # ⇒ The marker is metadata ABOUT this package, exactly as SHA256SUMS is, and self-reference
    # is why neither can appear in the list. What makes the exclusion safe is that it does not fail
    # open: `verify_package.py` REQUIRES the marker and reads it. A missing marker is a finding
    # there, so this is a name the manifest does not cover and the verifier does.
    SELF = ("SHA256SUMS", "BUILD-COMPLETE.json")
    lines = []
    for f in sorted(OUT.rglob("*")):
        if not f.is_file() or (f.name in SELF and f.parent == OUT):
            continue
        rel = str(f.relative_to(OUT)).replace(chr(92), "/")
        lines.append("%s  %s" % (hashlib.sha256(f.read_bytes()).hexdigest(), rel))
    (OUT / "SHA256SUMS").write_text(NL.join(lines) + NL, encoding="utf-8", newline=NL)
    _unlisted = sorted({str(f.relative_to(OUT)).replace(chr(92), "/")
                        for f in OUT.rglob("*") if f.is_file()}
                       - {L.split("  ", 1)[1] for L in lines} - set(SELF))
    if _unlisted:
        raise SystemExit(D + " %d file(s) in the package are still unlisted after writing "
                         "SHA256SUMS from the tree: %s" % (len(_unlisted), _unlisted[:4]))

    # ⚠️ THE SELF-VERIFICATION USED TO RUN HERE and that is precisely why it passed while the
    # reproducer's run of the same command failed: at this point the completion marker does not
    # exist yet, so the build was verifying a directory that is not the one it ships. It runs in
    # `_transactional()` now, after the last write, on the artifact itself.

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
    # ⚠️ "deadline" IS THE WRONG WORD SINCE v18 SS1d. The close date is a REPORTING CUTOFF:
    # nothing is required to happen on or before it. Leaving the word in an operational message
    # is how a withdrawn framing survives the document that withdrew it.
    print("  decision with a reporting cutoff attached, not a build step.")
    return 0


def _marked(pkg):
    """(is this directory vouched for, why not). The marker is READ, not merely counted."""
    import json as _json
    m = pkg / "BUILD-COMPLETE.json"
    s = pkg / "SHA256SUMS"
    if not m.is_file():
        return False, "carries no completion marker"
    if not s.is_file():
        return False, "carries a completion marker and no SHA256SUMS for it to bind to"
    try:
        want = _json.loads(m.read_text(encoding="utf-8")).get("sha256sums_sha256")
    except (OSError, ValueError):
        return False, "carries an unreadable completion marker"
    if not want:
        return False, ("carries a marker from before markers bound to bytes, so it vouches for a "
                       "build rather than for these files")
    if want != hashlib.sha256(s.read_bytes()).hexdigest():
        return False, "carries a marker that binds to a DIFFERENT SHA256SUMS than the one present"
    return True, ""


def _transactional():
    """Build into place, or leave what was there. Never leave a partial package behind.

    ⛔ A HALF-BUILT PACKAGE IS BYTE-IDENTICAL TO A FINISHED ONE. `SHA256SUMS` and `EXPECTED.json`
    are written last, and this script refuses partway through whenever the governing document is
    not in force -- so what a round-6 reviewer found in `package/` was a tree with neither file,
    reached by running the documented command. Two of the three documented steps then failed and
    `verify_package.py` died with a pathlib traceback rather than a finding. **Nothing in the
    directory says whether the build that produced it finished.**

    ⇒ The build is a transaction. The previous package is moved aside, the new one is built in its
    place, and only a clean return keeps it: any refusal or exception restores what was there.

    ⛔⛔ AND THAT DID NOT ESTABLISH WHAT THIS DOCSTRING CLAIMED. Round 8 found three things, and
    the first two are worse than the defect they were meant to fix.

    1.  **RESTORING AN UNKNOWN OBJECT.** If the previous `package/` was ITSELF half-built, the
        transaction moved it aside and put it back byte-for-byte after the new build failed. The
        claim *a reader who has a `package/` has one some run completed* was false in exactly the
        case that already existed on disk. Restoring is not the same as completing.

    2.  **THE RECOVERY COPY WAS DELETED BY THE RECOVERY ATTEMPT.** `rmtree(prev)` was the FIRST
        statement. `except BaseException` does not catch `kill -9`, an OOM, or power loss, so a
        hard crash after the rename leaves `package.prev` holding the ONLY complete package --
        and the next invocation destroys it before it checks anything. The atomicity boundary
        survived Python exceptions and not the machine.

    3.  **THE EXCUSE NAMED A DIRECTORY NOTHING CREATES.** The review packet excused
        `package.incomplete` as "the half-built package the transaction renamed rather than
        deleted". This code has always written `package.prev`. `package.incomplete` is created by
        nothing in this tree; the rename that produced the one on disk was a manual act, and the
        excuse stood for a directory no code path makes. `false_excuses()` could not catch it
        because it iterates `EXCLUDED` and never `EXCLUDED_DIRS`.

    ⇒ So: refuse to START when a `.prev` already exists, because that is the fingerprint of a
    crash and the operator must look rather than have the evidence swept; delete `.prev` only
    after a clean return; and write a COMPLETION MARKER as the last act, so *this directory
    represents a finished build* is a fact in the directory rather than an inference from its
    presence. Restoring a `.prev` whose marker is absent restores it and says so.
    """
    import shutil as _sh
    prev = OUT.with_name(OUT.name + ".prev")
    marker = OUT / "BUILD-COMPLETE.json"

    # ⛔ A LEFTOVER `.prev` IS THE FINGERPRINT OF A CRASH, and it may hold the only complete
    # package. Destroying it as the first act of the next run is the recovery deleting the thing
    # it is recovering. This refuses instead, and says which directory to look at.
    if prev.exists():
        # ⚠️ THE ONE MOMENT THE MARKER EXISTS FOR IS THE MOMENT IT WAS NOT ASKED. This said
        # *that directory may hold the only complete package here* unconditionally -- and there is
        # a real window, between the marker's write and `rmtree(prev)`, in which `package/` is
        # complete AND marked and the sentence is simply false. A refusal that states a falsehood
        # about the disk teaches the operator to stop reading refusals.
        #
        # ⇒ Still refuse -- a leftover `.prev` means a run died and somebody should look -- but
        # say which of the two directories is vouched for, by reading the marker rather than
        # guessing from its presence.
        _ok, _why = _marked(OUT)
        print("  %s %s already exists: a previous run was interrupted between moving the old "
              "package aside and finishing the new one." % (chr(0x26D4), prev.name))
        if _ok:
            print("      %s IS complete and its marker binds to its own SHA256SUMS, so %s is a "
                  "leftover rather than the only copy. Remove it deliberately and re-run."
                  % (OUT.name, prev.name))
        else:
            print("      %s %s, so %s may hold the only complete package here. Inspect it before "
                  "removing anything; this build will not decide for you."
                  % (OUT.name, _why, prev.name))
        return 1

    had = OUT.exists()
    had_complete = had and marker.is_file()
    if had:
        OUT.rename(prev)

    def _restore(why):
        _sh.rmtree(OUT, ignore_errors=True)
        if had:
            prev.rename(OUT)
            # ⚠️ SAY WHAT WAS RESTORED. Restoring a package whose completion marker is absent
            # puts an object of unknown provenance back where a finished one is expected, and the
            # operator is the only one who can decide what to do about it.
            print("  %s %s; the previous package is back. It %s a completion marker."
                  % (chr(0x26D4), why,
                     "carries" if had_complete else "DOES NOT carry"))
            if not had_complete:
                print("      That package was not finished by any run this code can vouch for. "
                      "It is restored, not repaired.")
        else:
            print("  %s %s; there was no previous package and none is left. A partial package is "
                  "indistinguishable from a complete one." % (chr(0x26D4), why))

    try:
        rc = main()
    except BaseException:
        _restore("the build did not finish")
        raise
    if rc != 0:
        _restore("the build returned %d" % rc)
        return rc

    # ⚠️ THE MARKER IS THE LAST WRITE. Everything above it can fail; nothing after it can.
    #
    # ⛔ AND IT USED TO BIND TO NOTHING. A time and a sentence assert a property of an EVENT --
    # *a build finished at 14:02* -- and it was read as a property of a DIRECTORY: *these bytes are
    # the ones that build finished with*. Those are different claims, and nothing connected them,
    # so copying the marker into a half-built tree made the half-built tree "complete".
    #
    # ⇒ THE CONTENT IS THE DIGEST OF SHA256SUMS, which is the digest of everything else. Now
    # `finished` is checkable rather than asserted: `verify_package.py` recomputes it, and a marker
    # that came from a different build says so instead of vouching for bytes it never saw.
    import json as _json
    import datetime as _dt
    marker.write_text(
        _json.dumps({"_what": "written as the last act of a build that returned 0. Its ABSENCE "
                              "means this directory was not finished by a run -- it does not mean "
                              "the contents are wrong, only that nothing vouches for them. "
                              "sha256sums_sha256 binds this marker to the manifest of the very "
                              "bytes that build produced; verify_package.py recomputes it.",
                     "completed_utc": _dt.datetime.now(_dt.timezone.utc)
                                         .strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "sha256sums_sha256": hashlib.sha256(
                         (OUT / "SHA256SUMS").read_bytes()).hexdigest()}, indent=2) + NL,
        encoding="utf-8", newline=NL)

    # ⛔ THE BUILD NEVER VERIFIED WHAT IT SHIPS. Round 6 added RUNNING the shipped controls and
    # not a gate that the shipped TREE is clean; round 7 added the gate and put it where the tree
    # was still one file short of final. The verifier a reader is told to run first is run HERE,
    # on the complete directory, with the marker in it -- and a failure restores the previous
    # package rather than leaving a marked one that does not verify.
    _vp = OUT / "verify_package.py"
    if _vp.exists():
        _r = subprocess.run([sys.executable, "-X", "utf8", "verify_package.py"], cwd=str(OUT),
                            capture_output=True, text=True, encoding="utf-8", errors="replace")
        if _r.returncode != 0:
            print((_r.stdout or "")[-900:])
            _restore("the package this build wrote does not pass its own verifier")
            return 1
    _sh.rmtree(prev, ignore_errors=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(_transactional())
