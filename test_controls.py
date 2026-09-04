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
import ast
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
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
IGNORE = shutil.ignore_patterns("runs", "package", "reference", ".git", "review", "__pycache__")


# ⇒ PORTED FROM census/stress_test.py, NOT REIMPLEMENTED. Two copies of this rule
# is exactly how the round-11 evasion survived here after the census copy was fixed.
def _module_bindings(tree):
    """Names module scope binds, split by whether the binding is UNCONDITIONAL.

    ⛔ A NAME BOUND ONLY INSIDE `if False:` IS ASSIGNED TO symtable AND ABSENT AT RUNTIME. A
    reviewer defeated an earlier version with exactly that, four lines long, and the suite said
    "ok". Reading the module body as a SEQUENCE separates a binding that always happens from one
    that might not -- which is the one thing symtable cannot tell us.

    ⛔ THIS FUNCTION WAS DEFINED TWICE IN THIS FILE, and Python kept the second. The dead copy
    carried the ten-line argument for the round-12 wildcard/`globals()` repair; the live copy
    carried the repair itself and none of the reasoning. Anyone deleting "the duplicate" had a
    coin-flip chance of deleting the mechanism, and a reviewer showed the live copy could be
    removed with the suite still reporting 47 passed, 0 failed. That is the round-24 duplicated-
    paragraph finding one level out -- a shingle control was built for PROSE paragraphs and the
    three-line AST equivalent was not built for SOURCE, inside the very file that hosts the
    undefined-name control. The two copies are one function now, and `_duplicate_defs()` below
    fails the suite if any module in the tree defines one name twice.

    ⚠ THE ROUND-12 REASONING, kept here because it belongs beside the code it explains: a round-12
    reviewer showed `from math import *; sqrt(4)` and `globals()["DYNAMIC_NAME"] = ...` both
    reported as "reads a name nothing in scope defines". A wildcard import means the module's
    names cannot be enumerated, so findings for that module are SUPPRESSED and the wildcard is
    reported instead -- the undecidability is named rather than converted into a false accusation.
    A literal `globals()["X"] = ...` key IS a binding and is collected.
    """
    always, maybe = set(), set()
    # name -> [(first line, last line)] of each CONDITIONAL body that binds it. An inline scope
    # written inside one of these ranges is evaluated while that body runs; one written outside
    # is deferred. This is what lets the check narrow on containment instead of on scope type.
    spans = {}

    def _targets(node):
        tgts = list(getattr(node, "targets", []) or [])
        if getattr(node, "target", None) is not None:
            tgts.append(node.target)
        for tgt in tgts:
            for n in ast.walk(tgt):
                if isinstance(n, ast.Name):
                    yield n.id

    # ⛔ `match` AND `except*` BIND NAMES AND WERE NOT WALKED, so a module binding a name only in a
    # match case or a TryStar handler was reported as reading an undefined name -- a false
    # positive on code that runs clean. A reviewer wrote both. They do not occur in this tree
    # today, which is exactly why they were missed: a branch no data has taken is UNDEFINED, not
    # settled.
    _COND = (ast.If, ast.While, ast.For, ast.Try, ast.With)
    for _extra in ("Match", "TryStar", "AsyncFor", "AsyncWith"):
        if hasattr(ast, _extra):
            _COND = _COND + (getattr(ast, _extra),)

    def _note(names, span):
        if span is None:
            return
        for _nm in names:
            spans.setdefault(_nm, []).append(span)

    def _walk(body, conditional, span=None):
        sink = maybe if conditional else always
        for st in body:
            if isinstance(st, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                _t = set(_targets(st))
                sink.update(_t)
                if conditional:
                    _note(_t, span)
            elif isinstance(st, (ast.Import, ast.ImportFrom)):
                if any(a.name == "*" for a in st.names):
                    sink.add("*")
                sink.update((a.asname or a.name).split(".")[0]
                            for a in st.names if a.name != "*")
            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                sink.add(st.name)
            elif isinstance(st, ast.Delete):
                # ⚠ `del X` at module scope UNBINDS. Treating the earlier assignment as still
                # standing made a real NameError invisible. A deleted name is demoted to `maybe`
                # rather than dropped, because reporting it as undefined would be a second guess
                # about control flow this pass cannot make.
                for t in st.targets:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name):
                            always.discard(n.id)
                            maybe.add(n.id)
            elif isinstance(st, _COND):
                _span = (st.lineno, getattr(st, "end_lineno", st.lineno) or st.lineno)
                for attr in ("body", "orelse", "finalbody"):
                    _walk(getattr(st, attr, []) or [], True, _span)
                for h in getattr(st, "handlers", []) or []:
                    _walk(h.body, True, _span)
                for c in getattr(st, "cases", []) or []:
                    # ⚠ AN IRREFUTABLE CASE ALWAYS RUNS IF IT IS REACHED: `case _:` or a bare
                    # capture, with no guard, cannot fail to match. Its bindings are therefore
                    # unconditional, and calling them conditional would cry wolf on the ordinary
                    # exhaustive-match idiom. A case with a PATTERN can fail, so its bindings stay
                    # conditional -- which is a true statement about the name, and is why the
                    # message says "binds only inside a conditional" rather than "nothing defines
                    # it": the earlier version could not see match bindings at all and gave the
                    # wrong diagnosis for the right sentence.
                    _pat = getattr(c, "pattern", None)
                    _irrefutable = (getattr(c, "guard", None) is None
                                    and isinstance(_pat, ast.MatchAs)
                                    and getattr(_pat, "pattern", None) is None)
                    _walk(c.body, not _irrefutable, _span)
                    # The capture names in the PATTERN bind the same way the case body does, so
                    # they follow the same irrefutability. Adding them to `maybe` unconditionally
                    # made `case N:` -- which cannot fail -- look conditional, and the check then
                    # fired on the ordinary exhaustive idiom.
                    _psink = always if _irrefutable else maybe
                    for n in ast.walk(_pat or ast.Pass()):
                        if isinstance(n, ast.MatchAs) and n.name:
                            _psink.add(n.name)
                        elif isinstance(n, ast.MatchStar) and getattr(n, "name", None):
                            _psink.add(n.name)
                        elif isinstance(n, ast.MatchMapping) and getattr(n, "rest", None):
                            _psink.add(n.rest)
                        if _psink is maybe:
                            _note([x for x in (getattr(n, "name", None),
                                               getattr(n, "rest", None)) if x], _span)
    _walk(tree.body, False)
    for n in ast.walk(tree):
        if (isinstance(n, ast.Subscript) and isinstance(n.value, ast.Call)
                and isinstance(n.value.func, ast.Name) and n.value.func.id == "globals"
                and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str)):
            always.add(n.slice.value)
        # An `except* E as e:` handler binds `e`; so does `except E as e:`.
        if isinstance(n, ast.ExceptHandler) and n.name:
            maybe.add(n.name)
    return always, maybe - always, spans


def _shadowed_reads(tree):
    """Functions that READ a name above the line they assign it, where an outer scope has it.

    ⚠ This is the one question symtable cannot answer: it knows a name is local to a function,
    not WHERE. `build_paper.py` read `D` at line 709 and assigned it at 1198 -- a defect -- while
    a function that assigns `out` and then reads it is not. Only the ordering separates them, so
    only the ordering is computed here, and everything else is left to symtable.
    """
    # ⛔ THIS EXAMINED FunctionDef AND AsyncFunctionDef ONLY, so a lambda could shadow a name and
    # read it before assigning: `D = 1; f = lambda: (D, (D := 2))` raises UnboundLocalError at
    # runtime and this said nothing. A reviewer wrote it in two lines. A lambda is a function
    # scope with the same local-shadowing rule; the only reason it was excluded is that the walk
    # enumerated node TYPES instead of asking what a scope is.
    out = []
    _SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
    for fn in ast.walk(tree):
        if not isinstance(fn, _SCOPES):
            continue
        first, reads, glob = {}, [], set()
        for n in ast.walk(fn):
            # ⚠ Do not descend into a NESTED scope: its locals are its own, and reading a name
            # there says nothing about the ordering in this one.
            if isinstance(n, _SCOPES) and n is not fn:
                continue
            if isinstance(n, (ast.Global, ast.Nonlocal)):
                glob.update(n.names)
            elif isinstance(n, ast.Name):
                # ⚠ ORDER IS (line, column), NOT LINE. A lambda fits the shadowing read and the
                # assignment on ONE line -- `lambda: (D, (D := 2))` -- so comparing line numbers
                # alone made the read look non-earlier and the check stayed silent on code that
                # raises UnboundLocalError. Within a line, position decides.
                _pos = (n.lineno, n.col_offset)
                if isinstance(n.ctx, (ast.Store, ast.Del)):
                    if n.id not in first or _pos < first[n.id]:
                        first[n.id] = _pos
                elif isinstance(n.ctx, ast.Load):
                    reads.append((n.id, _pos))
        for nm, ln in reads:
            if nm in glob or nm not in first:
                continue
            if ln < first[nm]:
                out.append((getattr(fn, "name", None) or "<lambda>", nm))
    return out


def undefined_module_reads(where=None):
    """Names a function cannot read when its line runs -- in each of the ways that happens.

    ⛔ NINE OF THESE SHIPPED ACROSS THE TWO PROJECTS, every one on an error path, so each raised
    instead of reporting and only once something had already gone wrong. Three shapes: UNDEFINED
    (nothing in scope binds it), SHADOWED (an outer scope binds it and this function assigns it
    later, so reads above that line raise UnboundLocalError), and CONDITIONAL (module scope binds
    it only inside `if`/`try`/`while`).

    ⛔ THIS FUNCTION WAS REWRITTEN ONTO RAW AST TO GET STATEMENT ORDER, AND IN DOING SO
    REIMPLEMENTED PYTHON'S SCOPE RULES BADLY -- eight iterations, and each one traded a fixed
    false negative for a new class of false positive: 141 findings when nested functions were
    dropped, 197 when comprehension targets were half-modelled, 258 when the module walk descended
    into functions, 25 when nested comprehensions were not scopes. A round-25 reviewer then showed
    the version that survived all that was blind to every lambda body -- 87 in this directory, 75
    in the paper toolchain, 69 of them `claim(sentence, predicate)` -- and read comprehensions
    with Python 2 scoping.

    ⇒ symtable IMPLEMENTS PYTHON'S SCOPE RULES AND WAS HERE ALL ALONG. It handles lambdas,
    comprehensions, closures and class bodies correctly and for free. It was abandoned because it
    cannot order a read against an assignment -- which is ONE of the three shapes. So symtable
    answers the two it can and a small AST pass answers the third, instead of a hand-rolled scope
    walker answering all three approximately.

    ⚠ KNOWN BLIND SPOT, DISCLOSED RATHER THAN FIXED: a binding created through
    `globals()[expr] = ...` with a non-literal key is not statically decidable and is not
    detected. A literal key IS collected.
    """
    import builtins as _b
    import symtable as _st
    out = []
    for f in sorted((where or HERE).glob("*.py")):
        try:
            src = f.read_text(encoding="utf-8")
            tree = ast.parse(src)
            top = _st.symtable(src, f.name, "exec")
        except (SyntaxError, UnicodeDecodeError, ValueError):
            continue
        always, maybe, _spans = _module_bindings(tree)
        if "*" in always:
            # ⚠ A wildcard import makes the module's names unenumerable. Reporting every
            # unresolved read would be a false accusation; the wildcard is the finding, once.
            out.append("%s: `from ... import *` makes this module's names unenumerable, so "
                       "undefined-name findings are SUPPRESSED here. Remove the wildcard to get "
                       "the check back." % f.name)
            continue
        known = always | set(dir(_b)) | {"__file__", "__name__", "__doc__", "__package__",
                                         "__spec__", "__loader__", "__builtins__", "__debug__",
                                         "__class__", "__qualname__", "__module__"}
        stack = [top]
        while stack:
            sc = stack.pop()
            stack.extend(sc.get_children())
            if sc is top:
                continue
            for s in sc.get_symbols():
                # a name symtable calls GLOBAL here is one no enclosing scope binds
                if not (s.is_global() and not s.is_assigned()):
                    continue
                n = s.get_name()
                if n in known:
                    continue
                if n in maybe:
                    # ⛔ A CONDITIONAL BINDING READ FROM AN INLINE SCOPE IS NOT A DEFECT. A
                    # comprehension or lambda written inside the same `for`/`if` body that binds
                    # the name is evaluated while that body runs, so the binding has happened.
                    # Reporting those gave two false positives on a clean tree -- `sc` in
                    # mp_metric.py and `_low` in this file -- and a checker that cries wolf gets
                    # switched off, which this project has now written down three times.
                    #
                    # ⚠ The reviewer's evasion was `if False: X = ...` read from a DEF, which is
                    # deferred: the function can be called at any later time, including a time at
                    # which the branch never ran. That case is kept. The narrowing is to scopes
                    # whose execution is deferred, not to scopes that happen to be convenient.
                    #
                    # ⛔ AND THE CODE DID NOT DO WHAT THE COMMENT ABOVE SAYS. It narrowed on the
                    # scope's TYPE, so every lambda and every comprehension was exempted -- which
                    # made lambdas blind to the conditional shape again, through the exact
                    # construct the previous round had been fixing, and restored the round-10
                    # reviewer's `if False: X = ...` evasion. `f = lambda: X` at module level is
                    # deferred in precisely the way a `def` is: it is CALLED later, possibly never
                    # having had the branch run. A reviewer wrote it in four lines and the
                    # detector said nothing while Python raised NameError.
                    #
                    # ⇒ Narrow on LEXICAL CONTAINMENT, which is what the comment always said: an
                    # inline scope written INSIDE the conditional body that binds the name is
                    # evaluated while that body runs, so the binding has happened. One written
                    # outside it is deferred and is reported. `_spans` carries the line range of
                    # each conditional body that binds each name.
                    _inline = (sc.get_type() != "function"
                               or sc.get_name() in ("lambda", "genexpr", "listcomp",
                                                    "setcomp", "dictcomp"))
                    if _inline:
                        _ln = sc.get_lineno()
                        if any(_a <= _ln <= _b for _a, _b in _spans.get(n, ())):
                            continue
                        what = ("which module scope binds only inside a conditional this "
                                "deferred scope is not written inside -- it may not exist when "
                                "this line runs")
                        out.append("%s:%s reads %r, %s" % (f.name, sc.get_name(), n, what))
                        continue
                    what = ("which module scope binds only inside a conditional -- it may not "
                            "exist when this line runs")
                else:
                    # ⛔ THE MESSAGE ASSERTED MORE THAN THE ANALYSIS KNEW. "nothing in scope
                    # defines it" is a claim about the program; what this pass knows is that no
                    # STATICALLY VISIBLE binding exists. A module that binds through
                    # `globals()[expr] = ...` with a computed key is not statically decidable --
                    # the docstring discloses exactly that -- and the finding still read as an
                    # accusation. A reviewer hit it with a dynamic-key probe: a liveness false
                    # positive stated as a defect.
                    #
                    # ⇒ The tolerated edge is NAMED in the finding, so a reader can tell an
                    # undecidable case from a real one without reading this source.
                    _dyn = any(isinstance(_x, ast.Subscript)
                               and isinstance(_x.value, ast.Call)
                               and isinstance(_x.value.func, ast.Name)
                               and _x.value.func.id == "globals"
                               and isinstance(_x.ctx, ast.Store)
                               for _x in ast.walk(tree))
                    what = ("which no statically visible binding defines -- and this module also "
                            "assigns through globals() with a computed key, which is UNDECIDABLE "
                            "here, so treat this as a dynamic-globals edge rather than a defect"
                            if _dyn else "which nothing in scope defines")
                out.append("%s:%s reads %r, %s" % (f.name, sc.get_name(), n, what))
        for fname, nm in _shadowed_reads(tree):
            if nm in known:
                out.append("%s:%s reads %r above the line it assigns it, while an outer scope "
                           "also defines it -- that read raises UnboundLocalError"
                           % (f.name, fname, nm))
    return sorted(set(out))


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
    # ⚠ ASKING, NOT DECIDING. The suite must be able to identify the governing document
    # even in a tree that check_commitments refuses -- otherwise anchoring a pre-registration,
    # which is what the protocol asks for, stops the controls from running at all.
    try:
        found, _rej = cc.governing(root, _raise_on_blocking=False)
    except TypeError:
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


def tree_digest(root=None):
    """A digest of the tree this suite examined. One implementation, imported by the gate.

    ⛔ THE PREVIOUS VERSION COVERED `glob("*.py")` ON THE TOP DIRECTORY -- 16 files of 320. The
    protocol documents, the .ots proofs, the signatures, ANCHORS.json, the corpus: none of it. A
    verdict could faithfully describe a run over TAMPERED PROTOCOL DOCUMENTS and its tree digest
    would be byte-identical. And it was written and never read: the field appeared once, where the
    suite wrote it, and `build_package.py` never recomputed or compared it. A field that looks
    like it binds the verdict to the tree and binds nothing -- the same shape as the anchor-file
    check a reviewer found inert in round 8, in the repair written to close round 11.

    ⇒ It covers every file the tree contains, excluding only caches and the verdict itself, and
    the GATE RECOMPUTES IT. It is defined once here and imported there, because two copies of one
    rule is how the undefined-name evasion survived a round.
    """
    import hashlib as _hl
    _root = pathlib.Path(root) if root else HERE
    _h = _hl.sha256()
    for _f in sorted(_root.rglob("*")):
        if not _f.is_file():
            continue
        _rel = _f.relative_to(_root).as_posix()
        # ⛔ THIS EXCLUDED BY SUBSTRING, NOT BY PATH COMPONENT. `"__pycache__" in _rel` skips any
        # path merely CONTAINING the string, so `evil__pycache__notacache/train.py` and a
        # top-level `notes__pycache__.md` were invisible to the digest -- a reviewer planted one
        # and the digest was byte-identical before and after. The binding is what that defeats:
        # the verdict certifies "this tree" while provably blind to a namable class of paths.
        #
        # ⚠ Bounded, and the bound is worth stating exactly rather than overstating the fix: the
        # package is built from an explicit include list, so a hidden file cannot ride into a
        # reproducer package, and no pinned or checked path legitimately carries that substring.
        # What was broken was the digest's claim about its own coverage, not the package.
        #
        # ⇒ A path component is a component. This is the substring-is-not-a-token defect, in the
        # function whose whole job is to say what the tree contains.
        _parts = _f.relative_to(_root).parts
        if "__pycache__" in _parts or ".git" in _parts:
            continue
        if _rel in ("CONTROL-SUITE-VERDICT.json",):
            continue
        _h.update(_rel.encode("utf-8"))
        _h.update(_hl.sha256(_f.read_bytes()).digest())
    return _h.hexdigest()[:16]


def _shape_fixtures():
    """(label, got, want) for each demonstrated defect in a pure shape rule.

    These are cheap because they call the rule directly rather than building a tree. They exist
    because the rules they cover were all defeated by a document or a path nobody had tried.
    """
    import check_commitments as _CC
    out = []
    _d, _u, _F = "e" * 64, "E" * 64, "```"
    _other = "f" * 64

    def _doc(*lines):
        return NL.join(lines) + NL

    def _facts_doc(*rows):
        return NL.join(["# t", "", "### 2d.", "", _F] + list(rows) + [_F, ""])

    def _refused(fn):
        """True if the rule REFUSES. A rule that cannot refuse has not been shown to work."""
        try:
            fn()
            return False
        except SystemExit:
            return True

    # ⛔ THE MECHANISM v10 EXISTS TO INTRODUCE HAD NO CONTROLS AT ALL. A round-14 reviewer found
    # that `anchor_facts`, `anchor_facts_hold`, `_retirement_is_permitted` and `retires` -- the
    # four functions implementing the monotonic fact pin -- were never called by this suite. They
    # worked when called; the suite that is supposed to demonstrate they work did not call them.
    # v10 §5 requires a positive control that makes each rule FAIL and a negative control one step
    # outside its trigger, and neither existed for any of them. The rule was violated by the
    # document that introduced it.
    out.append(("a repeated height is REFUSED (the monotonic lie)",
                _refused(lambda: _CC.anchor_facts(
                    _facts_doc("964534    " + _d, "964534    " + _other))), True))
    out.append(("two heights, one each, is accepted",
                len(_CC.anchor_facts(_facts_doc("964534    " + _d, "964535    " + _other))), 2))

    # anchor_facts_hold(): the `here=` parameter existed so a test could point it at a synthetic
    # tree, and no test ever passed it -- the THIRD instance of that shape, after
    # _retirement_is_permitted(text="") and undefined_module_reads(where=).
    _w = pathlib.Path(tempfile.mkdtemp(prefix="af-"))
    try:
        _facts = {964534: _d, 964535: _other}

        def _write(blocks):
            (_w / "ANCHORS.json").write_text(json.dumps({"blocks": blocks}), encoding="utf-8")

        _write({"964534": {"merkle_root": _d}, "964535": {"merkle_root": _other}})
        out.append(("intact facts hold", _CC.anchor_facts_hold(_facts, _w), []))
        _write({"964534": {"merkle_root": _d}, "964535": {"merkle_root": _other},
                "999999": {"merkle_root": "a" * 64}})
        out.append(("GROWTH is permitted (the whole point of a fact pin)",
                    _CC.anchor_facts_hold(_facts, _w), []))
        _write({"964534": {"merkle_root": "0" * 64}, "964535": {"merkle_root": _other}})
        out.append(("a SUBSTITUTED root is detected",
                    bool(_CC.anchor_facts_hold(_facts, _w)), True))
        _write({"964535": {"merkle_root": _other}})
        out.append(("a REMOVED height is detected",
                    bool(_CC.anchor_facts_hold(_facts, _w)), True))
    finally:
        shutil.rmtree(_w, ignore_errors=True)

    # _retirement_is_permitted(): the anchor file may move from a byte pin to a fact pin, and may
    # not simply be dropped. This is the parameter that was passed "" by its only caller.
    _with = _facts_doc("964534    " + _d) + NL + "### RETIRES" + NL + NL + _F + NL \
        + "ANCHORS.json" + NL + _F + NL
    out.append(("retiring the anchor file WITH facts is permitted",
                _CC._retirement_is_permitted("v10", "ANCHORS.json", _with), None))
    out.append(("retiring it with NO facts is refused",
                bool(_CC._retirement_is_permitted("v10", "ANCHORS.json", "# t" + NL)), True))
    out.append(("retiring an experimental input is always refused",
                bool(_CC._retirement_is_permitted("v10", "train.py", _with)), True))
    out.append(("retires() reads the declaration", sorted(_CC.retires(_with)), ["ANCHORS.json"]))

    # --- presents_table(): "is this a table" must not be inferred from a digest COUNT.
    # A real three-row table in pipe layout: 3 raw digests escaped the >= MIN_EXPECTED rule and
    # the document was SILENTLY SKIPPED, which is the hole the NO-TABLE rule exists to close.
    pipe = _doc("# Pre-registration v100 - t", "", "| file | digest |", "| --- | --- |",
                "| train.py | %s |" % _d, "| corpus/sources.json | %s |" % _d,
                "| corpus/build_corpus.py | %s |" % _d)
    out.append(("a 3-row pipe table is a table (was silently skipped)",
                bool(_CC.presents_table(pipe)), True))
    # Prose quoting four digests and pinning nothing was FATALLY rejected as a broken table --
    # the v2/v4 amendment shape, refused by the fix for refusing the v2/v4 amendment shape.
    prose = _doc("# Pre-registration v102 - t", "",
                 "The digest moved from %s to %s, and the record said %s not %s."
                 % (_d, _d, _d, _d))
    out.append(("prose quoting 4 digests is NOT a table (was fatal)",
                bool(_CC.presents_table(prose)), False))
    # Hex is case-insensitive; an uppercase table parsed as zero commitments.
    upper = _doc("# Pre-registration v103 - t", "", _F,
                 "train.py                %s" % _u, "corpus/sources.json     %s" % _u,
                 "corpus/build_corpus.py  %s" % _u, "corpus/MANIFEST.json    %s" % _u, _F)
    out.append(("an uppercase table parses (parsed as 0 pins)",
                len(_CC.commitments(upper)), 4))
    out.append(("uppercase pins are normalised to lower case",
                all(g == g.lower() for _p, g in _CC.commitments(upper)), True))

    # --- Rejection is a NAMED record, so widening it cannot break a caller by unpacking.
    out.append(("a Rejection carries 5 named fields",
                list(_CC.Rejection._fields),
                ["version", "name", "why", "state", "has_table"]))

    # --- tree_digest(): the cache exclusion must be a PATH COMPONENT, not a substring.
    work = pathlib.Path(tempfile.mkdtemp(prefix="td-"))
    try:
        (work / "train.py").write_text("print(1)" + NL, encoding="utf-8")
        _base = tree_digest(work)
        (work / "__pycache__").mkdir()
        (work / "__pycache__" / "x.pyc").write_bytes(b"c")
        out.append(("a real __pycache__ is still ignored", tree_digest(work) == _base, True))
        _decoy = work / "evil__pycache__notacache"
        _decoy.mkdir()
        (_decoy / "train.py").write_bytes(b"payload")
        out.append(("a path merely CONTAINING __pycache__ moves the digest",
                    tree_digest(work) != _base, True))
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return out


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace",
                                  line_buffering=True)
    print("=" * 78)
    print("  CONTROL TESTS -- every attack rounds 4 and 5 used, all of which must be refused")
    print("=" * 78)
    print()

    # ⚠ THREE CLAIMS, THREE COUNTERS. `missed` is a security claim (an attack was accepted),
    # `positive_failed` is a liveness claim (the real tree is red), and `hygiene_failed` is a
    # claim about this codebase's own error paths. Round 9 split the first two after a reviewer
    # flagged the conflation three times; round 10 added a control that folded the third back
    # into the first, and reported a crashing error path as an attack that had passed.
    caught = missed = 0
    hygiene_failed = False

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
    # ⛔ THIS FOLDED A POSITIVE-CONTROL FAILURE INTO THE ATTACK TALLY, and then printed the sum
    # as "N PASSED THAT SHOULD NOT HAVE" -- a sentence asserting that a control accepted an input
    # it must refuse, when no negative case had passed at all. A reviewer flagged the conflation
    # at rounds 6, 7 and 8 and I called it cosmetic each time.
    #
    # ⇒ IT STOPPED BEING COSMETIC WHEN TWO CORRECT REPAIRS MET. Wiring the suite into the build
    # gate was right; shipping `runs/det-1/run.json` so the builder reaches the suite was right;
    # together they mean the build now refuses on an honest tree, citing an attack that did not
    # happen. Two right repairs made a third defect consequential, which is this project's
    # recurring shape seen from the other side.
    #
    # ⚠ THE FIX IS NOT TO FORCE THE POSITIVE CASE GREEN. While v9 pends the tree is genuinely
    # red and the positive control genuinely cannot pass; pretending otherwise would be the
    # substitution this suite exists to catch. The two claims are SEPARATED instead: the negative
    # cases carry the security claim, the positive case carries a liveness claim, and a liveness
    # failure is reported as one.
    positive_failed = (not real_ok) or rc2 != 0
    if positive_failed:
        print()
        print("  " + W + " THE POSITIVE CONTROL FAILED, AND NO ATTACK PASSED. A suite that")
        print("  rejects everything proves nothing, so the negative cases below are reported")
        print("  separately from the positive case rather than summed with it.")


    # ⛔ A NAME USED ONLY ON AN ERROR PATH IS A NAME NOBODY EXECUTES UNTIL SOMETHING BREAKS. This
    # project has now shipped four of them -- `W` in a cleanup that reported a leak, `D` in a disk
    # pre-flight, `D` in an audit's own count-fell warning, `W` in the counter split beside this
    # comment. Each would have raised NameError instead of reporting the thing it exists to
    # report: a control that crashes on its own failure path, which is the defect a reviewer found
    # in anchor_status.py and which I then reproduced three more times by hand.
    #
    # ⚠ `symtable` answers the question directly -- which names does a function read from module
    # scope that module scope does not define -- so this is a property of the code rather than a
    # list of the symbols that have bitten so far.
    # ⛔ THIS FILE KEPT THE SINGLE-SHAPE VERSION AND BOTH ROUND-11 REVIEWERS DEFEATED IT with
    # four lines: `if False: REPORT_NAME = ...` binds the name for symtable and not at runtime, so
    # the suite printed "ok" over a function that raises NameError when called. The census copy of
    # this control was rewritten to catch three shapes -- undefined, shadowed-by-a-later-local, and
    # bound only inside a conditional -- and that rewrite was never ported here. A fix is not
    # finished until you grep for the other call sites, which is the sibling corollary this project
    # has now recorded five times and committed a sixth.
    #
    # ⇒ The implementation is LIFTED from the census one rather than reimplemented, because two
    # copies of a rule is how this happened. It is pointed at HERE.
    # ⛔ PORTING LEAVES TWO COPIES, AND A REVIEWER SAID SO: the durable fix is one shared
    # implementation, and two independently distributed packages cannot share a module. What they
    # CAN do is refuse to differ silently. The census copy is the origin; this one is a transcript
    # of it, and its digest is pinned here. If either moves without the other, this says so where
    # both exist -- and says nothing inside a distribution, where the origin is not present.
    _PORTED_FROM_CENSUS = "4b0f1af5082fa5f7"
    _origin = HERE.parent / "census" / "stress_test.py"
    if _origin.exists():
        import hashlib as _hl2
        _osrc = _origin.read_text(encoding="utf-8")
        try:
            _oi = _osrc.index("def _module_bindings(tree):")
            _oj = _osrc.index("    return sorted(set(out))", _oi) + len("    return sorted(set(out))")
            _od = _hl2.sha256(_osrc[_oi:_oj].encode("utf-8")).hexdigest()[:16]
        except ValueError:
            _od = "GONE"
        if _od != _PORTED_FROM_CENSUS:
            print()
            print("  " + D + " THE PORTED CONTROL HAS DRIFTED FROM ITS ORIGIN: census says %s, "
                  "this copy was taken at %s." % (_od, _PORTED_FROM_CENSUS))
            print("  One of the two was repaired and the other was not, which is exactly how the")
            print("  round-11 evasion survived here for a round after the census copy was fixed.")
            hygiene_failed = True

    _undef = undefined_module_reads(HERE)
    print()
    if _undef:
        print("  " + D + " %d name(s) read from module scope that do not exist:" % len(_undef))
        for _u in _undef[:6]:
            print("      " + _u)
        print("  Each raises NameError the first time its path runs -- and these paths run when")
        print("  something has already gone wrong, which is when a report matters most.")
        # ⛔ THIS INCREMENTED THE ATTACK COUNTER, so a crashing error path was reported
        # as "1 PASSED THAT SHOULD NOT HAVE" -- a sentence asserting a control accepted an input
        # it must refuse, when none had. That is the exact conflation round 9 split apart, two
        # sections further down the same file, reintroduced by the control added to catch a
        # different defect. It found a real one immediately -- `_sp` in build_package.py, written
        # an hour earlier -- and then mislabelled it.
        hygiene_failed = True
    else:
        print("  ok      no function reads a module-scope name that does not exist")

    # ⛔ THE FIXTURES THAT JUSTIFY A CONTROL MUST SHIP WITH IT. Round 13's reviewer could not
    # check the "8 fixtures / 0 findings" claim because the fixtures were not in the archive, and
    # was the first person ever to exercise `undefined_module_reads(where=)` -- a parameter with
    # one caller that never passes it. A fixture kept outside the tree is an assertion about work
    # nobody can repeat, which is the thing this paper is about.
    #
    # ⇒ Each entry below is a DEMONSTRATED defect, so each is a positive control: it must produce
    # the stated answer, and one step outside its trigger must produce the other one.
    print()
    print("  shape fixtures -- each of these was a live defect")
    _shape_bad = []
    for _label, _got, _want in _shape_fixtures():
        _ok = _got == _want
        if not _ok:
            _shape_bad.append(_label)
        print("    %s %-56s %s" % ("ok     " if _ok else D + " WRONG", _label,
                                   "" if _ok else "got %r want %r" % (_got, _want)))
    if _shape_bad:
        print("  " + D + " %d shape fixture(s) wrong: %s" % (len(_shape_bad), _shape_bad))
        hygiene_failed = True

    print()
    print("  %d attack(s) refused, %d PASSED THAT SHOULD NOT HAVE" % (caught, missed))
    if hygiene_failed:
        print("  " + D + " hygiene: an error path in this codebase cannot report -- see above.")
        print("  That is neither an attack passing nor a red tree; it is a control that would")
        print("  crash instead of speaking, and it is counted on its own line for that reason.")
    if positive_failed:
        print("  " + D + " positive control: FAILED -- the real tree does not currently pass")
        print("  check_commitments.py. That is a liveness statement about the tree, not a")
        print("  security statement about these controls.")
    else:
        print("  ok  positive control: the real tree still passes check_commitments.py")
    print("=" * 78)

    # ⛔ A CALLER READ THIS SUITE'S DECISION OUT OF ITS PROSE. build_package.py searched the
    # output for the substring "0 PASSED THAT SHOULD NOT HAVE", and a round-10 reviewer forged it
    # by printing that line alongside a genuine failure -- the gate reported "no attack passed"
    # while an attack had. That is the substring-for-a-token defect, in the gate that decides
    # whether a package ships.
    #
    # ⚠ The verdict is DATA now, written where a caller can consume it without parsing English,
    # and it carries the counts separately so a liveness failure can never be read as a security
    # one. The prose above stays for a human; it is no longer load-bearing for a machine.
    import json as _json
    # ⛔ THE VERDICT WAS NOT BOUND TO THE RUN THAT PRODUCED IT. A round-11 reviewer pre-wrote a
    # green verdict, made this suite crash before its own write, and build_package.py consumed the
    # stale file. The structured verdict correctly killed the round-10 substring forgery and
    # replaced it with a fresher one: a decision read from an artifact that is not tied to what
    # produced it, which is the same disease one layer down.
    #
    # ⇒ The gate issues a nonce in the environment and the verdict carries it back, together
    # with the digest of the tree examined. A verdict without this run's nonce is somebody else's.
    import os as _os
    _verdict = {"nonce": _os.environ.get("CONTROL_SUITE_NONCE", ""),
                "tree_digest": tree_digest(),
                "attacks_refused": caught,
                "hygiene_failed": bool(hygiene_failed),
                "attacks_passed_that_should_not_have": missed,
                "positive_control_failed": bool(positive_failed),
                "security_ok": missed == 0,
                "liveness_ok": not positive_failed}
    (HERE / "CONTROL-SUITE-VERDICT.json").write_text(
        _json.dumps(_verdict, indent=1) + NL, encoding="utf-8", newline=NL)
    print("  verdict written to CONTROL-SUITE-VERDICT.json (a caller must read that, not this)")
    return 1 if (missed or positive_failed or hygiene_failed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
