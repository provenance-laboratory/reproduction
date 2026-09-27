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
import os
import re as _re
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
# ⛔ THE SANDBOX MUST NOT OMIT A FILE THE GOVERNING DOCUMENT PINS. `runs` was excluded wholesale
# for bulk, and v18 section 2a newly commits `runs/det-1/run.json` -- the reference run, the one
# number this whole design exists to fix in advance. So every control that ran `prepare_anchor.py`
# inside the sandbox saw that pin as **absent** and the tool refused, for a reason that was an
# artefact of the copy rather than a fact about the tree.
#
# ⚠️ IT IS THE SAME SHAPE AS ROUND 7'S ARCHIVE FINDING, one level in: to a checker that only
# hashes, an unshipped file and a deleted one are the same thing. That one was found by running
# the documented commands from the extracted archive; this one by running them in the sandbox.
#
# ⇒ `_keep_pinned` reads what the document commits and keeps those paths, whatever the bulk rule
# says. The bulk rule stays a bulk rule; the exception is derived, not typed.
_BULK = ("runs", "package", "reference", ".git", "review", "__pycache__")


def _pinned_paths():
    """Every path the governing document commits, as a set of posix-relative strings."""
    # ⛔ `vs[max(vs)]` WAS ONE DOCUMENT'S ANSWER TO A QUESTION ABOUT THE WHOLE TREE. The moment
    # round 9 split v18, `max` was v19 -- which commits two files on purpose -- so the sandbox
    # stopped keeping `runs/det-1/run.json`, which v18 commits, and every attack ran against a
    # tree with a pinned file missing. The baseline caught it; had the baseline not existed, ten
    # refusals would have been scored against a sandbox that was already broken.
    #
    # ⇒ THE UNION OVER EVERY VERSION PRESENT. A path any document in this tree commits is a path
    # the sandbox must contain, whichever version is currently authority: they are all here, and
    # the cost of keeping one file too many is nothing beside the cost of a control measuring a
    # tree that is missing one.
    out = set()
    try:
        import prepare_anchor as _PA
        for _v, _doc in sorted(_PA.versions().items()):
            try:
                out |= set(_PA.pinned_digests(_doc)[3])
            except BaseException:
                continue        # a version this parser cannot read contributes nothing, not a veto
    except BaseException:
        # A sandbox that cannot read the pins keeps everything rather than guessing.
        return set()
    return out


def IGNORE(src, names):
    """Exclude the bulk directories, keeping only the chain down to each pinned path.

    Excluding `runs` wholesale drops a pinned file; keeping `runs` wholesale copies 120 of them
    into every sandbox. Neither is what is wanted: what is wanted is the bulk rule, minus exactly
    the paths the document commits.
    """
    try:
        base = pathlib.Path(src).resolve().relative_to(HERE).as_posix()
    except ValueError:
        return set()
    base = "" if base == "." else base + "/"
    out = set()
    for n in names:
        rel = base + n
        if rel.split("/", 1)[0] not in _BULK:
            continue
        # keep it if it IS a pinned path, or is a directory on the way to one
        if any(pin == rel or pin.startswith(rel + "/") for pin in _PINNED):
            continue
        out.add(n)
    return out


# ⛔ ROUND 14: `_pinned_paths()` RAN AT IMPORT, BEFORE main() MADE STDOUT UTF-8, and prepare_anchor prints a
# warning glyph while reading pins -- so under a redirected (cp1252) stdout every version's read raised
# UnicodeEncodeError, each was swallowed as 'a version this parser cannot read', _PINNED came back EMPTY,
# every sandbox lost runs/det-1/run.json, and the prepare_anchor baseline failed for a reason that had
# nothing to do with the tree. In a terminal it passed. The stream is made utf-8 before anything prints.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):                                      # pragma: no cover
    pass
_PINNED = _pinned_paths()


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

    ⛔ AND IT CAME BACK, 6 SEP 2026, THROUGH MODULE CACHING INSTEAD OF HARDCODING. This evicted
    only `check_commitments` from sys.modules. Its dependencies -- ots_verify, pin_anchors,
    anchor_status -- stayed cached, bound to the FIRST attack's temp tree, which had already been
    deleted. From the second attack onward every document failed verification, `found` came back
    empty, and the silent fallback below returned v3. Five attacks then vandalised a SUPERSEDED
    document's proof, check_commitments correctly ignored it, and the suite reported those correct
    passes as SECURITY FAILURES. The defences were sound the whole time; the harness was lying in
    both directions at once.

    ⇒ Two changes. Evict every locally-importable module, not one by name -- a dependency list
      written by hand is the same enumeration defect one layer down. And REFUSE rather than guess:
      a fallback that silently names a version is how a control stops testing without saying so.
    """
    import importlib
    import sys as _s
    root = pathlib.Path(root)
    # Drop stale copies of THIS tree's modules and any sys.path entry pointing at a tree that has
    # been removed; both make a later import resolve against a directory that no longer exists.
    # ⛔⛔ AND THE REPAIR ABOVE FIXED THE WAY IN AND NOT THE WAY OUT. This evicts stale modules
    # on ENTRY and then leaves the process rooted at `root` -- so after it returns, and after the
    # caller deletes that directory, `ots_verify.__file__` still points inside it:
    #
    #     ots_verify.__file__ before: <tree>/ots_verify.py
    #     ots_verify.__file__ after : C:/.../Temp/cc-7ouz5v84/r/ots_verify.py
    #
    # `_pinned()` then finds no `ANCHORS.json`, every proof degrades to STRUCTURAL-only, every
    # version looks unanchored, and any later IN-PROCESS question about authority is answered
    # from a tree that no longer exists. Round 11 met it as four attacks refusing against v5 and
    # one crashing -- the same symptom as 6 Sep, from the half of the same defect that was left.
    #
    # ⇒ THE PROCESS IS LEFT AS IT WAS FOUND. `sys.path` and every module this displaces are
    # saved and restored, so the sandbox is visible for exactly the call that needs it. A helper
    # that measures a tree must not re-root the process that is doing the measuring.
    _local = {p.stem for p in root.glob("*.py")}
    _saved_path = list(_s.path)
    _saved_mods = {m: _s.modules[m] for m in list(_s.modules) if m in _local}
    for m in _saved_mods:
        del _s.modules[m]
    _s.path[:] = [p for p in _s.path if p == str(root) or pathlib.Path(p).exists()]
    _s.path.insert(0, str(root))

    try:
        cc = importlib.import_module("check_commitments")
        # ⚠ ASKING, NOT DECIDING. The suite must be able to identify the governing document
        # even in a tree that check_commitments refuses -- otherwise anchoring a pre-registration,
        # which is what the protocol asks for, stops the controls from running at all.
        try:
            found, _rej = cc.governing(root, _raise_on_blocking=False)
        except TypeError:
            found, _rej = cc.governing(root)
    finally:
        for m in list(_s.modules):
            if m in _local:
                del _s.modules[m]
        _s.modules.update(_saved_mods)
        _s.path[:] = _saved_path
    if not found:
        raise SystemExit(
            D + " _governing() found NO anchored protocol document in %s. Every attack below "
            "would target a document chosen by guesswork, so the whole commit-attack section "
            "would report on nothing. Refusing to guess." % root)
    return sorted(found)[-1][1]


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


def a_signature_gone_proof_renamed(root):
    """ROUND 16: delete the governing document's signature and rename its proof under the retired-proof
    convention. The proof still commits to the bytes; a document somebody stood behind is not a draft
    because its signature went missing. MUST REFUSE."""
    gov = _governing(root)
    (root / (gov + ".asc")).unlink()
    (root / (gov + ".ots")).rename(root / (gov + ".ots.superseded-attack"))


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
    ("delete the governing signature and RENAME its proof .superseded-", a_signature_gone_proof_renamed),
    ("forge the governing proof: digest || Bitcoin tag, 40 bytes", a_forge_proof),
    ("substitute a REAL proof over a DIFFERENT document", a_foreign_proof),
    ("truncate the governing document's real proof", a_truncate_proof),
    ("append trailing bytes to the governing proof", a_trailing_bytes),
]


# ── attacks on measure_hardware: presence is not equality, absence is not agreement ──────────
# ── attacks on prepare_anchor: the gate that stands between a draft and a signature ──────────
#
# ⛔ THIS GROUP DID NOT EXIST, AND THAT IS THE FINDING. Round 7 added a WRITE PATH into a protocol
# document (`--repin`) and a generator (`withdrawn_claims.py`), and shipped both unattacked. This
# file's digest moved that round, so the suite WAS edited -- just not to cover what had been
# built. v18 section 2 records Finding 3 as *a control that exists for the last defect and not for
# this one*; that is what happened, in the version that records it.
#
# ⚠️ EACH ATTACK NAMES THE REFUSAL IT MUST PROVOKE. `rc != 0` is not enough and this project has
# paid for learning it twice: a gate that stops for an unrelated reason scores as a catch, and the
# suite reports a hole as covered. The phrase is asserted.

def _newest(root):
    """The document `prepare_anchor.py` would prepare in this tree -- ASKED, not re-derived.

    ⛔ THIS RETURNED THE HIGHEST VERSION while the tool prepares the LOWEST not yet in force, and
    for as long as exactly one version was waiting the two happened to agree. Round 9 split v18
    into v18 and v19 and they stopped agreeing instantly: every attack edited v19's table, the
    tool read v18's, and the suite reported two crashes and a wrong refusal rather than the
    thing it was built to measure. Two answers to *which document is under test* is the same
    defect as two answers to *what a commitment row is*, one level up.
    """
    import prepare_anchor as _pa
    vs = {}
    for f in root.glob("PRE-REGISTRATION-v*-CONFIRMATORY.md"):
        m = _pa.PATTERN.match(f.name)
        if m:
            vs[int(m.group(1))] = f
    _n, _doc = _pa.next_version(vs)
    assert _doc is not None, "no pre-registration documents in %s" % root
    return _doc


def _sign(root):
    """A detached signature beside the newest version. Its CONTENTS do not matter -- existence is
    the fact under test, because the write gate asks whether an edit could invalidate a
    signature, not whether one verifies."""
    gov = _newest(root)
    (gov.parent / (gov.name + ".asc")).write_text(
        "-----BEGIN PGP SIGNATURE-----" + chr(10) + "not a real signature" + chr(10)
        + "-----END PGP SIGNATURE-----" + chr(10), encoding="utf-8", newline=chr(10))


def p_forged_restatement(root):
    """ROUND 16 (a cold reader's Attack A): append a line to `train.py` and write its new digest into
    the draft's restatement row. `check_commitments.py` refused; `prepare_anchor.py` said READY. A
    restatement that does not restate is a forged pin. MUST REFUSE, saying so."""
    # ⛔ WAS `_newest(root)`, AND THAT IS WHY THIS CONTROL REPORTED WRONG ON A HEALTHY TREE.
    # The restatement rule it exercises only applies to a version whose DECLARATIONS are checked,
    # which means one that is not yet anchored. `_newest` returns whatever is newest, and once the
    # newest is signed and anchored, editing it trips the general pin-mismatch rule first: the tree
    # refuses, correctly, by a different rule than the one under test. The attack was recorded as
    # passing-when-it-should-not because the refusal came from the wrong place, not because
    # anything was bypassable.
    # `_declaration_target` is the question this control means to ask, and it already raises
    # `_Unmeasurable` when the tree is fully anchored -- which is the honest answer here, and the
    # same answer its eight siblings give.
    gov, _txt, _row = _declaration_target(root)
    tgt = root / "train.py"
    tgt.write_bytes(tgt.read_bytes() + b"# touched" + bytes([10]))
    new = hashlib.sha256(tgt.read_bytes()).hexdigest()
    t = gov.read_text(encoding="utf-8")
    t2 = _re.sub(r"(?m)^(train\.py\s+)[0-9a-f]{64}", lambda m: m.group(1) + new, t, count=1)
    assert t2 != t, "no train.py row in the draft"
    gov.write_text(t2, encoding="utf-8", newline=chr(10))


def p_pubkey_untouched(root):
    """Append a byte to PUBKEY.asc. It is pinned by the document; the gate must say so.

    The 29th pin. `pinned_digests()` matched an extension allowlist and read 28, so this exact
    edit produced `28 pins; 28 hold ... READY` -- the key every detached signature in the tree is
    verified against, committed by the document and enforced by nothing.
    """
    p = root / "PUBKEY.asc"
    p.write_bytes(p.read_bytes() + bytes([10]))


def p_repin_after_signing(root):
    """Sign the document, break a pin, then ask to re-pin. Editing signed bytes is forgery."""
    _sign(root)
    p = root / "train.py"
    p.write_bytes(p.read_bytes() + b"# touched" + bytes([10]))


def p_duplicate_pin(root):
    """A second, contradictory pin for a file already pinned. The first must not silently win.

    ⚠ THIS KEPT ITS OWN COPY OF THE ROW LOOKUP -- `_newest` plus a private regex -- so the
    round-10 repair to `_pin_row` did not reach it and it still crashed, taking five controls with
    it. A fix is not finished until every call site of the thing it fixed is found; that sentence
    is in this project's notes and this is its next instance.
    """
    gov, txt, m = _declaration_target(root)
    _row = m.group(0)
    _name = _row.split()[0]
    gov.write_text(txt.replace(_row, _row + chr(10) + _name + "  " + "0" * 64, 1),
                   encoding="utf-8", newline=chr(10))


# ⛔⛔ `_pin_row` STOOD HERE AND NOTHING CALLS IT ANY MORE. Its history is worth keeping even
# though its code is not, because it is three rounds of the same mistake:
#
#   round 7  no group at all
#   round 8  aimed at `_governing()`      -> 3 attacks PASSED
#   round 9  aimed at `next_version()`    -> 2 PASSED, one crashed and took 5 controls with it
#   round 10 aimed at "whichever version pins the file this attack mutates" -- correct, and the
#            rule it stated is the one that survives: *an attack that mutates `train.py` must edit
#            the table that COMMITS `train.py`.*
#   round 11 and that rule is right for an attack on a PIN and wrong for an attack on a PARSER.
#            A duplicate row, a short digest, a stray 64-hex and a name that escapes the folder
#            are questions about the GRAMMAR READING the table, and the table being read is the
#            one the tool is preparing. Six attacks edited an in-force document instead; the
#            composed commitment check saw the edit first and answered for them, and all six
#            reported `WRONG`.
#
# ⇒ The two kinds now go to two places and neither has a private copy: a pin attack changes a
# FILE and lets the composed check find it (`p_pubkey_untouched`), a parser attack edits the
# document `_declaration_target` names. Nothing is left that needs to ask "which version pins
# this path", so the function that answered it is gone rather than kept as scenery.


def p_upper_case_pin(root):
    """Change a pinned file AND write its pin in upper case. Hex is case-insensitive.

    \u26d4 THE SIGNING BLOCKER. `prepare_anchor.py` kept its own digest grammar, and both halves of
    it were `[0-9a-f]` while `check_commitments.py` -- the authority on what these documents
    commit -- has matched `[0-9a-fA-F]` since the round that found an entire table parsing as zero.
    The two defects composed: the ROW parser missed the pin, so the file went unchecked, and the
    COMPLETENESS scan missed the same digest, so nothing called it unconsumed. The pin did not
    become a stray or a refusal. It became nothing, and the tool printed READY over a changed file.
    """
    gov, txt, m = _declaration_target(root)
    # ⚠ THE ROW'S OWN NAME, NOT A SPELLED ONE. This rebuilt the row as `train.py` + the
    # upper-cased digest; once the target stopped being train.py's row that RENAMED it, and the
    # count rule answered instead of the digest rule. The file whose bytes then change is the one
    # the row names, for the same reason.
    gov.write_text(txt.replace(m.group(0), m.group(1) + m.group(2) + m.group(3).upper(), 1),
                   encoding="utf-8", newline=NL)
    p = root / m.group(1)
    p.write_bytes(p.read_bytes() + b"# moved after the pin was written" + bytes([10]))


def p_pin_escapes_the_folder(root):
    """A pin whose name resolves outside the study, against a file that really is there.

    \u26d4 NOTHING CHECKED CONTAINMENT. `HERE / name` follows `../` out without complaint, so the
    document could commit a file the study does not contain and count it among the digests that
    HOLD -- and section 5's repair derives the review packet's ship list from the same function,
    so the builder would have gone looking for it too. The file here EXISTS and its digest is
    CORRECT, which is the point: this passes every check except the one about what a
    pre-registration is able to commit.
    """
    out = root.parent / "outside.txt"
    out.write_bytes(b"a file this study does not contain" + bytes([10]))
    gov, txt, m = _declaration_target(root)
    dg = hashlib.sha256(out.read_bytes()).hexdigest()
    # ⚠ group(2) is the separator: _declaration_target captures the NAME as group(1), where
    # the retired _pin_row did not capture it at all. Two attacks still read it the old way.
    gov.write_text(txt.replace(m.group(0), "../outside.txt" + m.group(2) + dg + NL + m.group(0), 1),
                   encoding="utf-8", newline=NL)


def p_short_digest(root):
    """A pin one hex character short: not a row, and -- until this round -- not a complaint either.

    \u26a0\ufe0f THE RULE IS SCOPED ON PURPOSE. Section 3's round-9 table writes
    `build_package.py  <16 hex> -> <16 hex>` deliberately, so an abbreviation with something after
    it on the line is prose. A path-shaped name, one hash-shaped token of the wrong length, and
    then END OF LINE is a truncated commitment. Both branches are exercised by this suite: this
    attack takes the first, and the live document takes the second on every run.
    """
    gov, txt, m = _declaration_target(root)
    gov.write_text(txt.replace(m.group(0), m.group(1) + m.group(2) + m.group(3)[:63], 1),
                   encoding="utf-8", newline=NL)


def p_one_non_hex_character(root):
    """`g` in place of one hex digit. The row leaves the table and the COUNT leaves with it.

    \u26d4 THIS IS THE SHAPE NO GRAMMAR REPAIR CAN CATCH. Every fix to `_PIN` is a fix to what the
    parser can read, and whatever it still cannot read is also what it cannot count -- so the
    printed total re-derives itself around the hole and the sentence stays true of a document that
    has silently stopped committing a file. A round-9 reviewer got `28 pins; 28 hold ... READY`,
    which is the round-8 output quoted verbatim in `pinned_digests()`'s own docstring as the defect
    being repaired.

    \u21d2 What catches it is not a better pattern. It is section 3 declaring its own total in
    prose no tool maintains, so the answer to *how many* has a source independent of the machine
    that keeps failing to read one.
    """
    gov, txt, m = _declaration_target(root)
    gov.write_text(txt.replace(m.group(0), m.group(1) + m.group(2) + "g" + m.group(3)[1:], 1),
                   encoding="utf-8", newline=NL)


def _declaration_target(root):
    """(document, text, first pin row) for the version whose DECLARATIONS are checked.

    ⛔⛔ THE TWO DECLARATION ATTACKS EDITED A DOCUMENT THE GUARD EXEMPTS. They used `_pin_row`,
    which finds the version that pins `train.py` -- the right rule for an attack on a PIN, and the
    wrong one for an attack on a DECLARATION. Every version pinning `train.py` is anchored, and
    round 11 made the count and membership declarations required of everything that is NOT
    anchored, because an anchored document's bytes cannot be edited without breaking its proof.
    So deleting the total from v18 tested nothing: the reviewer saw the refusal come from the
    broken proof, named it *WRONG-CAUSE*, and was right.

    ⇒ AN ATTACK ON A DECLARATION GOES WHERE THE DECLARATION IS CHECKED: the lowest version this
    tool will read that `prepare_anchor.declaration_required` says must carry one. That is the
    draft, by construction, and it is the same function the gate asks -- not a second opinion about
    which document matters.
    """
    import prepare_anchor as _pa
    _vs = {}
    for _f in root.glob("PRE-REGISTRATION-v*-CONFIRMATORY.md"):
        _m = _pa.PATTERN.match(_f.name)
        if _m:
            _vs[int(_m.group(1))] = _f
    # ⚠ A VERSION WHOSE DECLARATIONS ARE CHECKED BUT WHICH CARRIES NO PIN TABLE IS SKIPPED,
    # NOT ASSERTED ON. The first cut raised on the lowest candidate, and a tree where an early
    # version momentarily looked unanchored crashed the whole suite from the third attack
    # onward -- round 9's exact failure, where one crash took five controls with it. The
    # candidates are tried in order and only an empty list is a broken control.
    _cands = [(_n, _d) for _n, _d in sorted(_vs.items()) if _pa.declaration_required(_d)]
    # ⛔ AND A BARE REGEX MATCHED AN ANCHOR FACT. `<height>  <root>` has the same shape as
    # `<path>  <digest>`, so the first "pin row" this found was 964534 -- a row in the §2d fact
    # table. An attack aimed there fires the anchor-fact rules and reports the pin rules as
    # broken. The document's OWN parser is what says which rows are pins, and it already refuses
    # a 6-9 digit name for exactly this reason.
    for _n, _doc in _cands:
        _txt = _doc.read_text(encoding="utf-8")
        for _name, _dg in (_pa._pairs_of(_doc) or []):
            _m = re.search(r"^(" + re.escape(_name) + r")(\s+)(" + re.escape(_dg) + r")\s*$",
                           _txt, re.M | re.I)
            if _m:
                return _doc, _txt, _m
    # ⛔ AND AN EMPTY LIST IS UNMEASURABLE, NOT A CRASH. This branch raised `AssertionError`,
    # which no caller catches, and it took the whole run with it -- round 9's exact failure,
    # which the comment above says this function must not reproduce. Once v22 anchored there was
    # no unanchored draft to plant a row in, so the healthy steady state of the tree became the
    # one state the suite could not measure: every control after this one was skipped and the
    # positive control was never reached. The case does test nothing here, and a control that
    # tests nothing says so instead of ending the run.
    raise _Unmeasurable(
        "no version whose declarations are checked carries a pin row (candidates: %s). Either "
        "every version is anchored, or the draft has no commitment table -- and this attack "
        "tests nothing either way." % ([_n for _n, _ in _cands] or "none"))


def p_undeclared_total(root):
    """Delete the declared total. An absent second witness must refuse, not fall back to the first.

    ⚠ It edits the document whose declarations are CHECKED, which is not the one that pins
    `train.py`. See `_declaration_target`.
    """
    gov, txt, _m0 = _declaration_target(root)
    _ms = list(re.finditer(r"[^" + NL + r"]*commits exactly [0-9]+ file pins[^" + NL + r"]*", txt))
    assert _ms, "no declared total to delete"
    m = _ms[-1]
    gov.write_text(txt.replace(m.group(0), "", 1), encoding="utf-8", newline=NL)


def p_miscounted_total(root):
    """Add a pin row and leave the sentence alone. The two sources must be compared, not averaged.

    ⚠ Same target as the deletion above, and for the same reason: an anchored document's count
    is not checked, so adding a row to one would be caught by its proof rather than by the count.
    """
    gov, txt, m = _declaration_target(root)
    # ⚠️ A PATH-SHAPED NAME THAT IS NOT ALREADY PINNED. `LICENSE` carries no dot and no slash,
    # so it is a stray rather than a pin and this fixture refused for the wrong reason; a name
    # already in the table is a duplicate and refuses for a different wrong reason. The attack is
    # about the COUNT, so the row it adds has to be an otherwise unremarkable one.
    gov.write_text(txt.replace(m.group(0),
                               m.group(0) + NL + "REPRODUCER-STATUS-NOTE.md" + m.group(2)
                               + "0" * 64, 1),
                   encoding="utf-8", newline=NL)


def p_orphan_digest(root):
    """A 64-hex inside a commitment block that no row consumes -- a commitment nothing checks."""
    # ⚠ the third private copy of the row lookup; see p_duplicate_pin
    gov, txt, m = _declaration_target(root)
    gov.write_text(txt.replace(m.group(0), m.group(0) + chr(10) + "  note: " + "a" * 64, 1),
                   encoding="utf-8", newline=chr(10))


def p_empty_signature_is_not_a_signature(root):
    """A ZERO-BYTE `.asc` beside the draft, and a pin rewritten under its authority.

    The exemption that lets a not-yet-anchored version account for an edited file was gated on
    `signed()`, and `signed()` was `(doc.name + ".asc").is_file()`. A round-12 reviewer wrote an
    empty file, edited a tool, updated the draft's pin to the new digest, and got:

        build_review_packet.py ... re-pinned at these exact bytes by SIGNED v21
        READY

    -- so a file with nothing in it moved the document from THE UNSIGNED DRAFT IN HAND to SIGNED
    v21, WHICH IS WAITING FOR ITS PROOF. `check_signature.py`, in the same directory, rejects that
    same file. Two definitions of "signed" in one tree, and the gate held the weaker one.

    MUST REFUSE: as a tampered tree. An empty file verifies against nothing, so it grants neither
    the signed-successor exemption nor the draft-in-hand one -- and it is not "absent" either, so
    it does not open the write path.
    """
    gov = _newest(root)
    (gov.parent / (gov.name + ".asc")).write_bytes(b"")
    tgt = root / "check_commitments.py"
    was = hashlib.sha256(tgt.read_bytes()).hexdigest()
    tgt.write_bytes(tgt.read_bytes() + b"# touched" + bytes([10]))
    now = hashlib.sha256(tgt.read_bytes()).hexdigest()
    gov.write_text(gov.read_text(encoding="utf-8").replace(was, now),
                   encoding="utf-8", newline=chr(10))


def p_repin_a_stamped_document(root):
    """Delete the signature, LEAVE the timestamp proof, and ask to re-pin.

    `writable()` was `not signed()`, which asks *is there a `.asc` on disk right now* -- a
    question about the present. A round-12 reviewer took v20, which had a real signature and a
    real OTS proof, deleted only the `.asc`, edited a tool and ran `--repin`. It returned 0 and
    rewrote v20's commitments:

        signed = False   stamped = True   anchored = False   writable = True

    A signature can be deleted by anyone who can edit this folder. A timestamp cannot be
    un-taken: afterwards the old proof is a genuine timestamp over bytes that no longer exist,
    which is worse than no proof because it is evidence pointing at nothing.

    MUST REFUSE: a stamped document is history, not a draft.
    """
    # ⛔ THIS TARGETED `_newest()`, WHICH IS THE DRAFT, AND FABRICATED A PROOF BESIDE IT --
    # a sibling's `.ots`, which commits to the SIBLING's bytes. Under `stamped()` as existence
    # that tested presence of a file; under `stamped()` as commitment it tests nothing, because
    # a proof of other bytes is not a commitment to these. A round-13 reviewer said it exactly:
    # it tested presence of a `.ots`, not the case that matters. The document this is about is
    # the highest one that really carries a signature AND a proof over its own bytes.
    gov = _stamped_and_signed(root)
    (gov.parent / (gov.name + ".asc")).unlink()
    p = root / "train.py"
    p.write_bytes(p.read_bytes() + b"# touched" + bytes([10]))


def _stamped_and_signed(root):
    """The highest version carrying a signature and a proof over its own bytes."""
    import ots_verify as _OV
    best = None
    for f in sorted(root.glob("PRE-REGISTRATION-v*-CONFIRMATORY.md")):
        m = _re.search(r"-v(\d+)-", f.name)
        sig, ots = f.parent / (f.name + ".asc"), f.parent / (f.name + ".ots")
        if not (m and sig.is_file() and ots.is_file()):
            continue
        if _OV.commits(ots.read_bytes(), f.read_bytes()) and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), f)
    if best is None:
        raise SystemExit(D + " no version carries both a signature and a proof over its own bytes, "
                         "so the stamped-document controls test nothing either way")
    return best[1]


def p_rename_the_proof_superseded(root):
    """Delete the signature and RENAME the proof under the study's own retired-proof convention.

    A round-13 reviewer took v20 -- real signature, real proof -- deleted the `.asc`, renamed
    `v20.md.ots` to `v20.md.ots.superseded-attack`, edited a tool and ran `--repin`:

        signature_state = absent   stamped = False   anchored = False   writable = True

    and it re-pinned all three rows and returned 0. The proof was not destroyed; it sat in the
    directory under the exact convention this study uses for retired proofs, and `writable()`
    read a filename where its docstring promised *nothing has ever committed these bytes*.

    MUST REFUSE: a proof that commits to these bytes is a commitment whatever it is called.
    """
    gov = _stamped_and_signed(root)
    (gov.parent / (gov.name + ".asc")).unlink()
    ots = gov.parent / (gov.name + ".ots")
    ots.rename(gov.parent / (gov.name + ".ots.superseded-attack"))
    p = root / "train.py"
    p.write_bytes(p.read_bytes() + b"# touched" + bytes([10]))


class _Unmeasurable(Exception):
    """A control that cannot be set up on this machine. Reported, never scored either way."""


def p_wrong_key_signature(root):
    """A VALID detached signature by a key that is not the protocol's, over the draft.

    A round-13 reviewer generated a second key, imported it and `PUBKEY.asc` into one keyring,
    signed v22 with the second key, and got `signature_state -> ok` from `prepare_anchor` while
    `check_signature.py --require <fpr>` rejected the same file. `signed()` asked whether SOME
    key gpg knows made a valid signature; the protocol's question is whether ITS key did.

    MUST REFUSE, naming the WRONG KEY: `ok` means signed by the key in `PUBKEY.asc`, in
    `verify()` itself, so every caller gets one answer. Set up in a throwaway keyring under
    the sandbox, selected through GNUPGHOME for the attacked run only.
    """
    # ⛔ `--yes` OR THIS CONTROL NEVER RUNS. The detached signature is written to `<gov>.asc`,
    # which is already in the sandbox beside the document it signs. Without it, `--batch` gpg
    # refuses to overwrite and exits `signing failed: File exists`; the setup raises
    # `_Unmeasurable`, and the case that catches a valid signature by a key that is NOT the
    # protocol's was reported unmeasured rather than run. The message names the key, so it reads
    # as an agent fault on the machine and points one call too early; the fault is the output
    # path. The subkey control below writes `-o <doc>.asc` the same way and carries the same
    # flag for the same reason.
    gov = _newest(root)
    home = ".altkeys"
    (root / home).mkdir()
    # ⚠ A PROBE FOR A "USABLE" gpg WAS ADDED HERE AND WITHDRAWN THE SAME DAY. The reasoning was
    # that this asks for `gpg` by bare name, and a machine can carry two GnuPG installations: on one
    # reviewer's shell the first on PATH was the shell's own, whose agent cannot start, so key
    # generation failed with "No agent running" whatever flags it was given. The probe picked a
    # binary that could generate a key.
    # ⛔ IT BROKE THE CONTROL, and the way it broke is the lesson. The probe chose a DIFFERENT gpg
    # for signing than `verify()` uses for verifying, so the signature landed in a keyring the
    # verifier could not read and the control failed with "no GOODSIG in gpg's status output" --
    # reporting a bypass where there was none. A control that signs with one tool and verifies with
    # another is not testing the protocol; it is testing two installations against each other.
    # ⇒ Bare `gpg` is correct: whatever the protocol verifies with is what the attack must sign
    # with. If an environment's `gpg` cannot generate a key, the control is unmeasurable THERE and
    # says so, which is the honest answer and already the behaviour. v23's `--yes` was the whole
    # repair this control needed.
    _g = ["gpg", "--yes", "--homedir", home, "--batch", "--pinentry-mode", "loopback", "--passphrase", ""]
    try:
        r = subprocess.run(_g + ["--quick-gen-key", "Alternate Test Signer <alt@example.invalid>",
                                 "default", "default", "never"],
                           cwd=str(root), capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    except FileNotFoundError:
        raise _Unmeasurable("gpg is not installed here, so a wrong-key signature cannot be made")
    if r.returncode != 0:
        raise _Unmeasurable("gpg could not generate a throwaway key: %s"
                            % (r.stderr or r.stdout).strip().splitlines()[-1:][0:1])
    subprocess.run(["gpg", "--homedir", home, "--batch", "--quiet", "--import", "PUBKEY.asc"],
                   cwd=str(root), capture_output=True)
    # the edit and the pin FIRST, then the signature over the edited document -- a signature
    # made before the edit is merely BAD, and BAD was refused a round ago; the case is VALID
    tgt = root / "check_commitments.py"
    was = hashlib.sha256(tgt.read_bytes()).hexdigest()
    tgt.write_bytes(tgt.read_bytes() + b"# touched" + bytes([10]))
    now = hashlib.sha256(tgt.read_bytes()).hexdigest()
    gov.write_text(gov.read_text(encoding="utf-8").replace(was, now),
                   encoding="utf-8", newline=chr(10))
    r = subprocess.run(_g + ["--local-user", "alt@example.invalid", "--armor", "--detach-sign",
                             "-o", gov.name + ".asc", gov.name],
                       cwd=str(root), capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    if r.returncode != 0 or not (gov.parent / (gov.name + ".asc")).is_file():
        raise _Unmeasurable("gpg could not sign with the throwaway key")
    # the attacked run alone sees this keyring, which holds BOTH keys -- the reviewer's setup
    os.environ["GNUPGHOME"] = home


# (label, mutate, argv, the phrase the refusal MUST carry)
PREPARE_ATTACKS = [
    ("a pinned PUBKEY.asc changed under the gate", p_pubkey_untouched, [], "PUBKEY.asc"),
    ("a restatement row forged to a tampered train.py", p_forged_restatement, [], "do not restate"),
    ("re-pin a document that is already signed", p_repin_after_signing, ["--repin"],
     "and `--repin` is refused"),
    ("an EMPTY .asc grants the signed-successor exemption",
     p_empty_signature_is_not_a_signature, [], "no longer match the pin"),
    ("re-pin after deleting the signature, proof left in place",
     p_repin_a_stamped_document, ["--repin"], "HAS BEEN TIMESTAMPED"),
    ("re-pin after deleting the signature and RENAMING the proof .superseded-",
     p_rename_the_proof_superseded, ["--repin"], "HAS BEEN TIMESTAMPED"),
    # the refusal is the pin mismatch -- the exemption was NOT granted -- and the in-process
    # check below this loop asserts that `verify()` names the WRONG KEY for the same fixture
    ("a VALID signature by a key that is not the protocol's grants the exemption",
     p_wrong_key_signature, [], "no longer match the pin"),
    ("a second, contradictory pin for one file", p_duplicate_pin, [], "more than once"),
    ("a digest in a commitment block that no row consumes", p_orphan_digest, [],
     "neither a file pin nor an anchor fact"),
    ("a pinned file changed and its pin upper-cased", p_upper_case_pin, [],
     "do not describe the files"),
    ("a pin whose name leaves the study folder", p_pin_escapes_the_folder, [],
     "resolves outside this folder"),
    ("a pin one hex character short", p_short_digest, [], "not a sha256"),
    ("one non-hex character, so the row AND the count leave", p_one_non_hex_character, [],
     "and this parser reads"),
    ("the declared total deleted", p_undeclared_total, [],
     "does not declare how many file pins"),
    ("a row added without updating the declared total", p_miscounted_total, [],
     "and this parser reads"),
]


# ⛔ v18 FINDING 3 LISTED FIVE TERMS AND THE REPAIR COVERED FOUR. `withdrawn` stood at zero
# occurrences in this suite: v18's own preamble named "a write path into a protocol document
# (--repin) and a generator (withdrawn_claims.py), and shipped both unattacked", then attacked the
# first only. What that uncovered generator let through was demonstrated in round 9 -- the anchored
# carrier this tool exists for, flipped to `clean` in the record, `--check` exiting 0, and the
# doctored tree passing the step the honest one fails.
def w_flip_the_carrier(root):
    """Rewrite the record so the anchored carrier reads clean. The published record then omits it.

    ⚠️ THE PER-ENTRY DIGEST DEFENDS THE WRONG THING. It binds a reading to the bytes of the
    document it was taken over, so it sees the DOCUMENT change. It never saw the RECORD OF THE
    READING change, and those are different threats. The chain is over the record.
    """
    p = root / "WITHDRAWN-DISPOSITIONS.jsonl"
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        e = json.loads(line)
        if e["doc"] == "PRE-REGISTRATION.md":
            e["disposition"] = "clean"
        out.append(json.dumps(e, sort_keys=True, separators=(",", ":")))
    p.write_text(NL.join(out) + NL, encoding="utf-8", newline=NL)


def w_delete_the_last_reading(root):
    """Drop the final entry. A chain that is still valid, one reading shorter."""
    p = root / "WITHDRAWN-DISPOSITIONS.jsonl"
    lines = p.read_text(encoding="utf-8").splitlines()
    p.write_text(NL.join(lines[:-1]) + NL, encoding="utf-8", newline=NL)


def w_respell_an_entry(root):
    """The same object, different bytes. The chain is over the bytes, so it must notice."""
    p = root / "WITHDRAWN-DISPOSITIONS.jsonl"
    lines = p.read_text(encoding="utf-8").splitlines()
    lines[0] = json.dumps(json.loads(lines[0]), sort_keys=True)       # a space after each comma
    p.write_text(NL.join(lines) + NL, encoding="utf-8", newline=NL)


def w_restate_in_a_new_file(root):
    """A text file that states the claim and is not a `.md`. The walk is over TEXT, not names.

    ⚠️ THE PHRASE IS TAKEN FROM THE TOOL, NOT WRITTEN HERE. A literal copy of it in this file
    makes THIS file a carrier -- which the baseline caught on the first run, correctly -- and a
    fixture that has to be excused is a fixture that has stopped testing. Deriving it also keeps
    the attack honest if the hint list ever changes.
    """
    import withdrawn_claims as _WC
    phrase = _WC.WITHDRAWN[0]["hints"][1]
    (root / "restated.txt").write_text(
        "Note to self: if nobody reproduces it, " + phrase + " about the ecosystem." + NL,
        encoding="utf-8", newline=NL)


WITHDRAWN_ATTACKS = [
    ("the anchored carrier flipped to clean in the record", w_flip_the_carrier,
     "has been rewritten"),
    ("the last reading deleted from the end of the log", w_delete_the_last_reading,
     "deleted from the end"),
    ("an entry respelled without changing the object", w_respell_an_entry,
     "not in canonical form"),
    ("the claim restated in a file that is not a .md", w_restate_in_a_new_file,
     "no reading bound to their current digest"),
]


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


def _subset_source(root=None):
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
    # ⛔⛔ AND IT DIVERGED FROM ITS OWN TOOL THREE WAYS AT ONCE. `HERE`, not the sandbox root --
    # so this control read the LIVE tree during a sandboxed run and no mutation could reach it. A
    # wider glob than the `-v*-CONFIRMATORY` form every other reader uses, which admits a file
    # called `PRE-REGISTRATION.md`. And `v = 1` when the name carries no version -- a silent
    # fallback that NAMES A VERSION, which `_governing`'s own docstring records as the round-6
    # defect: *a fallback that silently names a version is how a control stops testing without
    # saying so.*
    #
    # ⇒ The root is a parameter, the glob is the one the tool uses, and a name this cannot
    # version is skipped and reported rather than given a number.
    root = pathlib.Path(root or HERE)
    gov = _governing(root)
    text = (root / gov).read_text(encoding="utf-8")
    subset = _CC.distribution_subset(text)
    if subset:
        return text, subset
    best, _unversioned = None, []
    for f in sorted(root.glob("PRE-REGISTRATION-v*-CONFIRMATORY.md")):
        m = _re.search(r"-v(\d+)-", f.name)
        if not m:
            _unversioned.append(f.name)
            continue
        v = int(m.group(1))
        txt = f.read_text(encoding="utf-8")
        if _CC.distribution_subset(txt) and (best is None or v > best[0]):
            best = (v, f.name, txt)
    if _unversioned:
        print("    %s %d protocol document(s) carry no version in their name and were SKIPPED "
              "(%s); a control must not invent one" % (chr(0x26D4), len(_unversioned),
                                                       ", ".join(_unversioned[:3])))
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
    try:
        text, subset = _subset_source()
    except SystemExit as _e:
        # round 16: a document declaring two subset blocks made this raise and the suite die
        # with no verdict; the refusal is the right outcome and is RECORDED as one
        return [("the declaring document was refused (%s): no subset rule exercised" % str(_e)[:60], None, None)]
    pinned = [n for n, _d in _CC.commitments(text)]
    if not subset:
        return [("NO document in this tree declares a distribution subset", None, None)]
    comp = {n for n in pinned if n not in subset}
    # ⛔ ROUND 16: THE HIDDEN FILE WAS A NAME, NOT A MEMBER OF THE SUBSET. This case deleted
    # `train.py` -- which no version in force pinned, so its absence fell outside the pinned set
    # and the rule refused for THAT reason, while the label said "a subset file". The moment v22
    # pinned `train.py` it was in the complement, the absent set equalled the complement, and the
    # case that exists to catch the naive repair passed for the naive repair. The hidden file is
    # now drawn from the declared subset, which is what the label always claimed.
    hidden = sorted(subset)[0]
    return [
        ("a genuine distribution: absent == the complement", set(comp), True),
        ("a subset file ALSO deleted -- hiding a pinned file (%s)" % hidden,
         set(comp) | {hidden}, False),
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
    # ⛔⛔ ROUND 14: THE DIGEST WALKED THE WHOLE TREE AND THE ARCHIVE SHIPS A PROJECTION OF IT. The
    # verdict was bound to the digest of everything under HERE -- review/, runs/, scratch, and a
    # REVIEW-COMMANDS.json the builder writes into the zip after the verdict is sealed -- so the
    # shipped verdict said d361... and a reviewer's pristine extraction computed 2c26...; the
    # binding presented as this round's fix could not hold for any archive, and did not. Third
    # round of "the verdict disagrees with the shipped tree", inside the repair for it.
    # ⇒ THE DIGEST IS OVER THE SHIPPED PROJECTION, defined once in `build_review_packet.shipped_rels`,
    # minus the two files that are measurements ABOUT the tree (the verdict, and the builder's
    # exit-code record, which lives under review/ -- the directory every projection excludes by
    # the same declaration). The same function over the source tree and over a clean extraction
    # yields the same value, and the builder now extracts its own zip and requires that.
    import hashlib as _hl
    _root = pathlib.Path(root) if root else HERE
    _h = _hl.sha256()
    import build_review_packet as _BRP
    for _rel in sorted(_BRP.shipped_rels(_root)):
        if _rel in ("CONTROL-SUITE-VERDICT.json",) or _rel.startswith("review/"):
            continue
        _f = _root / _rel
        if not _f.is_file():
            _h.update(("MISSING " + _rel).encode("utf-8"))
            continue
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


def _import_from(root, name):
    """Import module `name` from `root` for one call, leaving sys.path and sys.modules as found."""
    import importlib
    import sys as _s
    _local = {p.stem for p in root.glob("*.py")}
    _saved_path = list(_s.path)
    _saved_mods = {m: _s.modules[m] for m in list(_s.modules) if m in _local}
    for m in _saved_mods:
        del _s.modules[m]
    _s.path.insert(0, str(root))
    try:
        return importlib.import_module(name), (_saved_path, _saved_mods, _local)
    except Exception:
        _restore_imports((_saved_path, _saved_mods, _local))
        raise


def _restore_imports(saved):
    import sys as _s
    _saved_path, _saved_mods, _local = saved
    for m in list(_s.modules):
        if m in _local:
            del _s.modules[m]
    _s.modules.update(_saved_mods)
    _s.path[:] = _saved_path


def _pending_only_proof(ots, document_bytes, calendar=b"https://example.invalid/calendar"):
    """A minimal, VALID OpenTimestamps proof over these bytes that names no Bitcoin block.

    Built from `ots_verify.MAGIC` and the format's own varint encoding, and accepted by the tree's
    own reader -- `commits()` true, `verify()` false with "carries no Bitcoin attestation". No
    network call and no calendar is contacted: the point of the fixture is a file that IS a proof
    and is only a receipt.
    """
    def _varuint(n):
        out = bytearray()
        while True:
            b = n & 0x7F
            n >>= 7
            out.append(b | (0x80 if n else 0))
            if not n:
                return bytes(out)

    def _varbytes(b):
        return _varuint(len(b)) + b

    pending_tag = bytes([0x83, 0xdf, 0xe3, 0x0d, 0x2e, 0xf9, 0x0c, 0x8e])
    return (ots.MAGIC + _varuint(1) + bytes([0x08])
            + hashlib.sha256(document_bytes).digest()
            + bytes([0x00]) + pending_tag + _varbytes(_varbytes(calendar)))


def _round17_fixtures():
    """(label, got, want) for the round-17 finding: THE STRONGEST COMMITMENT DECIDES.

    ⛔ `check_commitments.anchored()` PROJECTED OVER EVERY PROOF-SHAPED SIBLING AND THEN TOOK THE
    FIRST ONE AND BROKE. A reviewer planted a small, valid proof over the highest anchored
    version's exact bytes carrying only a calendar receipt, named so it SORTS FIRST, and the
    document read PENDING with its Bitcoin-attested proof unread one file along. PENDING did not
    block, so authority rolled back a version in silence and `prepare_anchor.py` still said READY.

    Two halves, because the repair has two halves:

    1. the planted receipt BESIDE the real proof must change nothing -- the document still reads
       ANCHORED and still governs;
    2. with ONLY the receipt present, the document reads PENDING and the tree must REFUSE, because
       a proof of its own signature still witnesses the Bitcoin block it has stopped naming.
    """
    out = []
    work = pathlib.Path(tempfile.mkdtemp(prefix="r17-"))
    root = work / "r"
    try:
        shutil.copytree(HERE, root, ignore=IGNORE)
        cc, saved = _import_from(root, "check_commitments")
        try:
            ots = cc._OTS
            top = sorted(cc.governing(root, _raise_on_blocking=False)[0])[-1]
            doc = root / top[1]
            shadow = root / (top[1] + ".0shadow")
            shadow.write_bytes(_pending_only_proof(ots, doc.read_bytes()))
            # the fixture is a proof, and it is only a receipt -- asserted with the tree's reader
            out.append(("the planted file IS a proof of these bytes, by this tree's own reader",
                        ots.commits(shadow.read_bytes(), doc.read_bytes()), True))
            out.append(("... and carries no Bitcoin attestation",
                        ots.verify(shadow.read_bytes(), doc.read_bytes())[0], False))
            # 1. beside the real proof it must change nothing
            out.append(("a pending-only proof planted beside the real one leaves it ANCHORED",
                        cc.anchored(doc)[2], "ANCHORED"))
            _found, _rej = cc.governing(root, _raise_on_blocking=False)
            out.append(("... and the same version still governs, not the one below it",
                        max(v for v, _n, _p in _found), top[0]))
            try:
                cc.governing(root)
                _raised = False
            except SystemExit:
                _raised = True
            out.append(("... and the tree is not refused for having it", _raised, False))
            # 2. with ONLY the receipt present the tree must refuse
            (root / (top[1] + ".ots")).unlink()
            out.append(("with ONLY the pending proof present the document reads PENDING",
                        cc.anchored(doc)[2], "PENDING"))
            out.append(("... and the projection names the file that answered",
                        shadow.name in cc.anchored(doc)[1], True))
            try:
                cc.governing(root)
                _raised, _why = False, ""
            except SystemExit as e:
                _raised, _why = True, str(e)
            out.append(("... and the tree REFUSES rather than falling back a version",
                        _raised, True))
            out.append(("... naming the state it found, not 'its proof is not a proof'",
                        "taken off it" in _why and "is not a proof (" not in _why, True))
        finally:
            _restore_imports(saved)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return out


def _round14_fixtures():
    """(label, got, want) for the three round-14 findings, each demonstrated by a reviewer.

    1. an anchored, UNSIGNED successor must not govern (governing() selected it);
    2. a signature by a signing SUBKEY of the protocol's key is the protocol's key (it read WRONG KEY);
    3. a proof committing to a document is a commitment whatever its file is called (a rename
       without ".ots" in it reopened the document).
    Each is set up in a sandbox copy of this tree and asked in-process of the sandbox's own modules.
    """
    out = []
    # --- 1. the unsigned anchored successor
    work = pathlib.Path(tempfile.mkdtemp(prefix="r14-"))
    root = work / "r"
    try:
        shutil.copytree(HERE, root, ignore=IGNORE)
        cc, saved = _import_from(root, "check_commitments")
        try:
            top = sorted(cc.governing(root, _raise_on_blocking=False)[0])[-1]
            src = root / top[1]
            n = top[0] + 50
            body = src.read_text(encoding="utf-8")
            i = body.index(NL)
            body = body[:i].replace("v%d" % top[0], "v%d" % n, 1) + body[i:]
            fake = root / ("PRE-REGISTRATION-v%d-CONFIRMATORY.md" % n)
            fake.write_text(body, encoding="utf-8", newline=NL)
            _real_anchored = cc.anchored
            cc.anchored = (lambda d: (True, "forced by the control", "ANCHORED") if d.name == fake.name
                           else _real_anchored(d))
            try:
                found, rej = cc.governing(root, _raise_on_blocking=False)
            finally:
                cc.anchored = _real_anchored
            out.append(("an anchored UNSIGNED successor is not selected as authority",
                        n in {v for v, _n, _p in found}, False))
            out.append(("... and is rejected by name as UNSIGNED",
                        [r.state for r in rej if r.version == n], ["UNSIGNED"]))
            cc.anchored = (lambda d: (True, "forced by the control", "ANCHORED") if d.name == fake.name
                           else _real_anchored(d))
            try:
                try:
                    cc.governing(root)
                    _raised = False
                except SystemExit:
                    _raised = True
            finally:
                cc.anchored = _real_anchored
            out.append(("... and above the authority it BLOCKS the tree, like a stripped signature",
                        _raised, True))
        finally:
            _restore_imports(saved)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    # --- 2. the signing subkey
    work = pathlib.Path(tempfile.mkdtemp(prefix="r14-"))
    root = work / "r"
    _env = dict(os.environ)
    try:
        shutil.copytree(HERE, root, ignore=IGNORE)
        home = ".subkeys"
        (root / home).mkdir()
        _g = ["gpg", "--yes", "--homedir", home, "--batch", "--pinentry-mode", "loopback", "--passphrase", ""]
        _run = lambda a: subprocess.run(_g + a, cwd=str(root), capture_output=True, text=True,
                                        encoding="utf-8", errors="replace")
        try:
            # a primary that can sign AND certify, as the protocol's key is (scSC); a cert-only primary
            # cannot make the "by the primary itself" signature the control also checks
            r = _run(["--quick-gen-key", "Subkey Test Signer <sub@example.invalid>", "default", "default",
                      "never"])
        except FileNotFoundError:
            r = None
        if r is None or r.returncode != 0:
            out.append(("(subkey control unmeasured: gpg could not make a key here)", True, True))
        else:
            cols = _run(["--with-colons", "--list-keys", "sub@example.invalid"]).stdout
            fprs = [ln.split(":")[9] for ln in cols.splitlines() if ln.startswith("fpr:")]
            primary = fprs[0]
            _run(["--quick-add-key", primary, "default", "sign", "never"])
            cols = _run(["--with-colons", "--list-keys", "sub@example.invalid"]).stdout
            fprs = [ln.split(":")[9] for ln in cols.splitlines() if ln.startswith("fpr:")]
            sub = [f for f in fprs if f != primary][-1]
            (root / "PUBKEY.asc").write_text(_run(["--armor", "--export", primary]).stdout,
                                             encoding="utf-8", newline=NL)
            doc = root / "PRE-REGISTRATION-v1.md"
            doc.write_text("# Pre-registration v1 - subkey control" + NL, encoding="utf-8", newline=NL)
            _rs = _run(["--local-user", sub + "!", "--armor", "--detach-sign", "-o", doc.name + ".asc", doc.name])
            if _rs.returncode != 0 or not (doc.parent / (doc.name + ".asc")).is_file():
                # a control that could not be set up says so, with gpg's own words, and scores nothing
                out.append(("(subkey control unmeasured: gpg would not sign with the subkey: %s)"
                            % (_rs.stderr or _rs.stdout or "").strip().splitlines()[-1:][0:1], True, True))
                shutil.rmtree(work, ignore_errors=True)
                work = None
            # no GNUPGHOME: the MSYS gpg on this platform cannot open a Windows absolute homedir, and
            # the route under test is the reproducer's -- NO_PUBKEY in the default keyring, then the
            # throwaway keyring that imports the sandbox's own PUBKEY.asc (relative to the module's HERE)
            cs, saved = _import_from(root, "check_signature")
            try:
                if work is None:
                    raise _Unmeasurable("subkey signature not made")
                state, detail, fpr = cs.verify(doc)
                out.append(("a signature by a signing SUBKEY of the protocol's key is ok", state, "ok"))
                out.append(("... made by the subkey, not the primary", fpr.upper() == sub.upper()
                            and sub.upper() != primary.upper(), True))
                (doc.parent / (doc.name + ".asc")).unlink()
                _run(["--local-user", primary + "!", "--armor", "--detach-sign", "-o", doc.name + ".asc",
                      doc.name])
                out.append(("... and by the primary itself is still ok", cs.verify(doc)[0], "ok"))
                (root / home / "alt").mkdir()
                _g2 = ["gpg", "--homedir", home + "/alt", "--batch", "--pinentry-mode", "loopback",
                       "--passphrase", ""]
                subprocess.run(_g2 + ["--quick-gen-key", "Other <other@example.invalid>", "default",
                                      "default", "never"], cwd=str(root), capture_output=True)
                (doc.parent / (doc.name + ".asc")).unlink()
                subprocess.run(_g2 + ["--local-user", "other@example.invalid", "--armor", "--detach-sign",
                                      "-o", doc.name + ".asc", doc.name], cwd=str(root), capture_output=True)
                out.append(("... and by another key is still BAD", cs.verify(doc)[0], "BAD"))
            except _Unmeasurable:
                pass
            finally:
                _restore_imports(saved)
    finally:
        os.environ.clear()
        os.environ.update(_env)
        shutil.rmtree(work, ignore_errors=True)
    # --- 3. a proof is a proof whatever it is called
    work = pathlib.Path(tempfile.mkdtemp(prefix="r14-"))
    root = work / "r"
    try:
        shutil.copytree(HERE, root, ignore=IGNORE)
        doc = _stamped_and_signed(root)
        proof = doc.parent / (doc.name + ".ots")
        pa, saved = _import_from(root, "prepare_anchor")
        try:
            out.append(("a stamped document is stamped", pa.stamped(doc), True))
            proof.rename(doc.parent / (doc.name + ".timestamp-retired-20260904"))
            out.append(("... and still stamped with its proof renamed with no .ots in the name",
                        pa.stamped(doc), True))
            for p in list(doc.parent.iterdir()):
                if p.is_file() and p.name.startswith(doc.name) and p.name != doc.name and \
                        not p.name.endswith(".asc"):
                    p.unlink()
            out.append(("... and NOT stamped once every proof over it is gone", pa.stamped(doc), False))
        finally:
            _restore_imports(saved)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return out


def _attempts_fixtures():
    """(label, got, want) for the distribution record -- an instrument that shipped with no rules.

    ⛔ THE PLAN MOVED THE ATTEMPTS OUT OF THE PINNED DOCUMENT AND PROTECTED THEM WITH NOTHING.
    `exposure/attempts.jsonl` was named in an anchored file, had no writer, no reader and no
    control, and did not exist. Every gate in this tree reported green over a record of the one
    thing v18 is about -- whether the call reached anyone -- that anybody could have edited.

    ⇒ Each attack below rewrites the record in a way that a "just append to a file" discipline
    would not notice, and demands a complaint. The negatives matter as much: growth is the normal
    case, and a control that refused new entries would be switched off within a week.
    """
    import attempts as _AT
    out = []
    w = pathlib.Path(tempfile.mkdtemp(prefix="att-"))
    _save = (_AT.HERE, _AT.PLAN, _AT.SERIES, _AT.LOG)
    try:
        (w / "exposure").mkdir()
        # The vocabulary comes from a PLAN, exactly as in production -- so these controls also
        # exercise the parser, which is the only thing standing between a typo in the plan and a
        # validator that accepts every string.
        (w / "DISTRIBUTION-PLAN.md").write_text(NL.join([
            "# plan", "", "The first token is the identifier.", "", "```",
            "alpha-venue         the first one", "beta-venue          the second one",
            "gamma-venue         the third, so that GROWTH can be tested at all", "```", "",
            'Each entry: `{"n": 1, "venue": "...", "outcome": "posted|removed|rejected"}`', "",
        ]), encoding="utf-8")
        _AT.HERE, _AT.PLAN = w, w / "DISTRIBUTION-PLAN.md"
        _AT.SERIES, _AT.LOG = w / "exposure", w / "exposure" / "attempts.jsonl"

        _v, _o = _AT.plan_vocabulary()
        out.append(("the venue list is READ OUT of the plan, not retyped", _v,
                    ["alpha-venue", "beta-venue", "gamma-venue"]))
        out.append(("...and so are the permitted outcomes", _o,
                    ["posted", "rejected", "removed"]))

        def _write(entries):
            _AT.LOG.write_bytes(b"".join(_AT.canonical(e) + b"\n" for e in entries))

        def _entries():
            """Two linked entries, built the way `record()` builds them."""
            e1 = {"n": 1, "outcome": "posted", "prev": _AT.GENESIS, "url": "https://a/1",
                  "utc": "2026-09-10T10:00:00Z", "venue": "alpha-venue"}
            e2 = {"n": 2, "outcome": "removed", "prev": hashlib.sha256(_AT.canonical(e1))
                  .hexdigest(), "url": "https://b/2", "utc": "2026-09-11T10:00:00Z",
                  "venue": "beta-venue"}
            return [e1, e2]

        def _complains(mutate=None, heads=None, capture=None):
            """True if the record is refused. Raise or complain both count -- a rule that dies is
            a rule that spoke; a rule that returns [] is one that did not."""
            for f in list(_AT.SERIES.glob("attempts-*.head")) + \
                    list(_AT.SERIES.glob("exposure-*.json")):
                f.unlink()
            es = _entries()
            _write(es)
            if heads:
                for k, h in heads.items():
                    (_AT.SERIES / ("attempts-%d.head" % k)).write_text(h + NL, encoding="utf-8")
            if capture is not None:
                (_AT.SERIES / "exposure-2026-09-11.json").write_text(
                    json.dumps({"captured_utc": "2026-09-11T12:00:00Z", "attempts": capture}),
                    encoding="utf-8")
            if mutate:
                mutate()
            try:
                return bool(_AT.check(verbose=False))
            except SystemExit:
                return True

        _h1 = hashlib.sha256(_AT.canonical(_entries()[0])).hexdigest()
        _h2 = hashlib.sha256(_AT.canonical(_entries()[1])).hexdigest()

        def _raw_sub(old, new):
            def go():
                _AT.LOG.write_bytes(_AT.LOG.read_bytes().replace(old, new))
            return go

        def _drop_line(i):
            def go():
                ls = [l for l in _AT.LOG.read_bytes().split(b"\n") if l.strip()]
                del ls[i]
                _AT.LOG.write_bytes(b"".join(l + b"\n" for l in ls))
            return go

        out.append(("NEGATIVE: an intact two-entry record checks out", _complains(), False))
        out.append(("NEGATIVE: heads and a capture that agree check out",
                    _complains(heads={1: _h1, 2: _h2},
                               capture={"count": 2, "head": _h2}), False))
        out.append(("NEGATIVE: an empty record is not a violation",
                    _complains(mutate=lambda: _AT.LOG.unlink()), False))
        out.append(("a CHANGED outcome breaks the chain",
                    _complains(_raw_sub(b'"outcome":"posted"', b'"outcome":"rejected"')), True))
        out.append(("a CHANGED url breaks the chain",
                    _complains(_raw_sub(b"https://a/1", b"https://x/9")), True))
        out.append(("a DELETED first entry is caught by the numbering",
                    _complains(_drop_line(0)), True))
        out.append(("a DELETED LAST entry is caught by its head file",
                    _complains(heads={1: _h1, 2: _h2}, mutate=_drop_line(1)), True))
        out.append(("...and by a capture that had already counted it",
                    _complains(capture={"count": 2, "head": _h2}, mutate=_drop_line(1)), True))
        out.append(("a head file that disagrees with the log is caught",
                    _complains(heads={2: "b" * 64}), True))
        out.append(("a capture whose head no longer matches is caught",
                    _complains(capture={"count": 2, "head": "c" * 64}), True))
        out.append(("NON-CANONICAL bytes are refused (the digest would cover other bytes)",
                    _complains(_raw_sub(b'{"n":1,', b'{"n": 1,')), True))
        out.append(("an UNKNOWN field is refused rather than ignored",
                    _complains(_raw_sub(b'"url"', b'"note":"x","url"')), True))
        # ⛔ THIS PASSED FOR A REASON UNRELATED TO ITS CLAIM. `_raw_sub` rewrites the log's bytes,
        # which breaks the hash chain -- so the case was refused as a chain break whether or not
        # any venue rule existed. Once the superseded plan stopped being a permission list, the
        # control kept reporting "ok" while testing nothing it named.
        # ⚠ Rebuilt properly: a correctly-chained entry at an unlisted venue must be ACCEPTED
        # (the plan is a historical record), and a malformed identifier must be REFUSED (the log
        # is read back by machine).
        def _unlisted():
            es = _entries()
            es[0]["venue"] = "delta-venue"
            es[1]["prev"] = hashlib.sha256(_AT.canonical(es[0])).hexdigest()
            _write(es)

        def _malformed():
            es = _entries()
            es[0]["venue"] = "Delta Venue!"
            es[1]["prev"] = hashlib.sha256(_AT.canonical(es[0])).hexdigest()
            _write(es)

        out.append(("NEGATIVE: a venue the superseded plan never named is ACCEPTED",
                    _complains(mutate=_unlisted), False))
        out.append(("a MALFORMED venue identifier is refused",
                    _complains(mutate=_malformed), True))
        out.append(("an outcome the plan does not permit is refused",
                    _complains(_raw_sub(b'"outcome":"removed"', b'"outcome":"ignored"')), True))
        # ⚠ ONE PER VENUE WAS A RULE AND IS NOT ONE NOW. It existed to stop a study posting
        # repeatedly until it cleared its own exposure floor; v18 withdrew the floor and the claim
        # behind it, so rationing posts rations nothing. The case is kept as a NEGATIVE control --
        # a repeat must be ACCEPTED -- because a rule that is removed and left untested is
        # indistinguishable from a rule that broke.
        def _repost():
            es = _entries()
            es[1]["venue"] = "alpha-venue"
            es[1]["prev"] = hashlib.sha256(_AT.canonical(es[0])).hexdigest()
            _write(es)
        out.append(("NEGATIVE: a SECOND attempt at one venue is now ACCEPTED",
                    _complains(mutate=_repost), False))

        def _backdate():
            es = _entries()
            es[1]["utc"] = "2026-09-09T10:00:00Z"
            es[1]["prev"] = hashlib.sha256(_AT.canonical(es[0])).hexdigest()
            _write(es)
        out.append(("dates running BACKWARDS are refused, chain intact",
                    _complains(mutate=_backdate), True))

        # ⚠ GROWTH IS THE NORMAL CASE. Without this the suite could not tell a control that
        # protects the record from one that has frozen it.
        def _grow():
            """Append a third entry, correctly linked, at the one venue not yet used."""
            es = _entries()
            e3 = {"n": 3, "outcome": "posted",
                  "prev": hashlib.sha256(_AT.canonical(es[1])).hexdigest(),
                  "url": "https://c/3", "utc": "2026-09-12T10:00:00Z", "venue": "gamma-venue"}
            _write(es + [e3])

        out.append(("NEGATIVE: APPENDING is permitted with an old head still pinned",
                    _complains(heads={1: _h1}, mutate=_grow), False))

        # ⛔ AND THE VOCABULARY READER MUST FAIL CLOSED. A plan whose venue block cannot be parsed
        # would otherwise yield an empty list, and an empty list accepts nothing -- or, if the
        # membership test had been written the other way, everything. Either way the rule stops
        # being about the plan.
        _AT.PLAN.write_text("# plan with no venue block" + NL, encoding="utf-8")
        try:
            _AT.plan_vocabulary()
            out.append(("an UNREADABLE plan fails closed", False, True))
        except SystemExit:
            out.append(("an UNREADABLE plan fails closed", True, True))
    finally:
        _AT.HERE, _AT.PLAN, _AT.SERIES, _AT.LOG = _save
        shutil.rmtree(w, ignore_errors=True)
    return out


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

    # ⛔⛔ AND IT HAPPENED AGAIN, TO THE FUNCTION WHOSE FAILURE COST THREE PROTOCOL VERSIONS.
    # `_without_anchor_facts` decides whether an anchor height is read as a FILE PATH. v15's
    # renumbered heading defeated it, 30 heights became committed paths, and v16 and v17 were spent
    # on the consequences -- and this suite never called it once. A reviewer pointed at the gap and
    # then walked through it: with `ANCHOR_FACT_LINE` forbidding a trailing comment while
    # `DIGEST_LINE` allowed one, a single `# comment` on any height line turned all 32 heights back
    # into committed paths, on a signed and anchored version.
    #
    # ⇒ Every attack below is that reviewer's, run against the rule directly. The negative controls
    # matter as much: a real commitment table must SURVIVE the strip, or the fix has simply broken
    # the thing it was protecting.
    _A, _B = "964534  " + "a" * 64, "964535  " + "b" * 64
    _head = _doc("# v", "", "### 2d. facts", "")

    def _n_comm(doc):
        return len(_CC.commitments(doc))

    def _n_facts(doc):
        return len(_CC.anchor_facts(doc))

    _bare = _head + _doc(_F, _A, _B, _F)
    _cmt = _head + _doc(_F, _A + "  # the block that anchored v16", _B, _F)
    _tag = _head + _doc(_F + "text", _A, _B, _F)
    _two = _head + _doc(_F, _A, _F, "", "text", "", _F, _B, _F)
    _renum = _doc("# v", "", "### 3d. facts", "") + _doc(_F, _A, _B, _F)
    _real = _doc("# v", "", "### 2b.", "", _F, "train.py  " + _d, "verify.py  " + _other, _F)

    out.append(("a bare fact block is stripped from commitments", _n_comm(_bare), 0))
    out.append(("...and IS read as facts", _n_facts(_bare), 2))
    out.append(("a TRAILING COMMENT does not turn heights into file paths", _n_comm(_cmt), 0))
    out.append(("...and the annotated block is still read as facts", _n_facts(_cmt), 2))
    out.append(("a TAGGED fence is still an anchor-fact block", _n_comm(_tag), 0))
    out.append(("a SECOND fact block is not silently dropped", _n_facts(_two), 2))
    out.append(("a RENUMBERED heading still yields its facts", _n_facts(_renum), 2))
    out.append(("...and its heights are still not commitments", _n_comm(_renum), 0))
    # negative controls: the strip must not eat a real commitment table
    out.append(("NEGATIVE: a commitment table survives the strip", _n_comm(_real), 2))
    out.append(("NEGATIVE: it is not read as anchor facts", _n_facts(_real), 0))
    out.append(("NEGATIVE: a commitment row may carry a trailing comment",
                _n_comm(_doc("# v", "", _F, "train.py  " + _d + "  # unchanged", _F)), 1))

    # ⛔ THE RULE THAT CATCHES EVERY OTHER SHAPE HAD NO CONTROLS OF ITS OWN, FOR THREE ROUNDS.
    # `_anchor_fact_blocks` ends in a projection -- every anchor-fact-shaped line in the document
    # must lie inside a block that was read -- and it is the ONLY thing standing behind all the
    # rules above: when a fence is defeated in some way nobody has thought of, this is what is
    # supposed to notice. It was rewritten twice and this suite's bytes did not change either
    # time, so both rewrites shipped having never been attacked. The second was defeated by a
    # numbered list; a reviewer found five more spellings in one sitting.
    #
    # ⇒ Each POSITIVE control below hides one anchor fact outside every block, in a decoration
    # that was invisible to some previous version of the rule, and demands a refusal. The point is
    # not the list -- a list is the defect -- it is that the rule now refuses on the two TOKENS,
    # so a decoration nobody has written down is covered by the same code path these exercise.
    _root = "a" * 64
    _valid = [_F, "964534  " + _root, _F]

    def _with_loose(line):
        """A document with one real fact block AND one anchor fact hidden outside every block."""
        return _head + _doc(*(_valid + ["", line, ""]))

    for _lab, _line in [
        ("a numbered list item", "1. 964601 " + _root),
        ("prose: 'Block N <root>'", "Block 964601 " + _root),
        ("prose: 'at height N the root is'", "at height 964601 the root is " + _root),
        ("a colon separator", "height 964601: " + _root),
        ("the columns reversed", _root + "  964601"),
        ("a blockquote", "> 964601  " + _root),
        ("a pipe-table row", "| 964601 | " + _root + " |"),
        ("a bullet", "- 964601  " + _root),
    ]:
        out.append(("a fact hidden by %s is REFUSED" % _lab,
                    _refused(lambda _t=_with_loose(_line): _CC.anchor_facts(_t)), True))

    # ⛔ AND THE THREE WAYS A BLOCK IS DISQUALIFIED RATHER THAN MISSED. The error message named
    # two of these as its most likely causes while nothing tested that either produced it.
    out.append(("an INDENTED fence (invisible to _FENCE) is REFUSED",
                _refused(lambda: _CC.anchor_facts(
                    _head + _doc("  " + _F, "  964534  " + _root, "  " + _F))), True))
    out.append(("a comment on its OWN LINE inside the fence is REFUSED",
                _refused(lambda: _CC.anchor_facts(
                    _head + _doc(_F, "# the block that anchored v17",
                                 "964534  " + _root, "964535  " + _other, _F))), True))
    # ⚠ A 65-hex digest is why the digest token reads {64,} and not {64}. With an exact-64 rule the
    # malformed row disqualifies its block AND is invisible to the projection, so a one-row block
    # corrupted this way commits nothing and says nothing.
    # ⛔ TWO BLIND SPOTS A ROUND-5 REVIEWER EXECUTED AGAINST THE REAL PARSER. A height is made of
    # hex characters, so a height written hard against its digest is one unbroken run and the
    # digest token swallowed the pair whole. And a digest one character short vanished silently --
    # not refused, dropped. The 16 controls here exercised neither.
    out.append(("a FUSED height+digest (no separator at all) is REFUSED",
                _refused(lambda: _CC.anchor_facts(
                    _head + _doc(_F, "964534" + "a" * 64, _F))), True))
    out.append(("a 63-char digest inside a fact block is REFUSED, not dropped",
                _refused(lambda: _CC.anchor_facts(
                    _head + _doc(_F, "964534  " + _root, "964535  " + "a" * 63, _F))), True))
    out.append(("a 65-char digest inside a fact block is REFUSED, not dropped",
                _refused(lambda: _CC.anchor_facts(
                    _head + _doc(_F, "964534  " + _root, "964535  " + "a" * 65, _F))), True))
    # ⚠ AND PROSE STAYS PROSE. Lowering the threshold globally would turn every abbreviated
    # digest quoted beside a height into a malformed fact; these documents do that deliberately.
    out.append(("NEGATIVE: an abbreviated digest beside a height, in PROSE, is still prose",
                _refused(lambda: _CC.anchor_facts(
                    _with_loose("965840 -> 8aac2039, the block that anchored v16"))), False))
    out.append(("a 65-hex digest disqualifies its block and is REFUSED",
                _refused(lambda: _CC.anchor_facts(
                    _head + _doc(_F, "964534  " + _root + "a", _F))), True))

    # NEGATIVE CONTROLS -- one step outside the trigger. Without these the rule could refuse
    # everything and every positive control above would still pass.
    out.append(("NEGATIVE: an ABBREVIATED digest beside a height is prose, not a fact",
                _refused(lambda: _CC.anchor_facts(
                    _with_loose("965840 -> 8aac2039, the block that anchored v16"))), False))
    out.append(("NEGATIVE: a digest with no height on the line is prose",
                _refused(lambda: _CC.anchor_facts(
                    _with_loose("the archive hashes to " + _other))), False))
    out.append(("NEGATIVE: a digest beside a SHORT number is not a height",
                _refused(lambda: _CC.anchor_facts(
                    _with_loose("run 4210 produced " + _other))), False))
    out.append(("NEGATIVE: a real commitment row is not an anchor fact",
                _refused(lambda: _CC.anchor_facts(
                    _with_loose("corpus/build_corpus.py  " + _other))), False))
    out.append(("NEGATIVE: an ISO date beside a digest is not a height",
                _refused(lambda: _CC.anchor_facts(
                    _with_loose("exposure/exposure-2026-09-07.json  " + _other))), False))

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

    # --- tree_digest(): the SHIPPED projection, and nothing outside it (round 14).
    work = pathlib.Path(tempfile.mkdtemp(prefix="td-"))
    try:
        (work / "corpus" / "clean").mkdir(parents=True)
        (work / "corpus" / "clean" / "a.txt").write_text("one" + NL, encoding="utf-8")
        _base = tree_digest(work)
        (work / "corpus" / "clean" / "a.txt").write_text("two" + NL, encoding="utf-8")
        out.append(("a byte change in a SHIPPED file moves the digest", tree_digest(work) != _base, True))
        (work / "corpus" / "clean" / "a.txt").write_text("one" + NL, encoding="utf-8")
        (work / "review").mkdir()
        (work / "review" / "REVIEW-COMMANDS.json").write_text("{}", encoding="utf-8")
        (work / "CONTROL-SUITE-VERDICT.json").write_text("{}", encoding="utf-8")
        out.append(("the two measurement files do not move it (they describe the tree)",
                    tree_digest(work) == _base, True))
        _decoy = work / "evil__pycache__notacache"
        _decoy.mkdir()
        (_decoy / "train.py").write_bytes(b"payload")
        out.append(("a file OUTSIDE the shipped set does not move it (the packet walk refuses it)",
                    tree_digest(work) == _base, True))
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
    print("  prepare_anchor.py -- the gate between a draft and a signature")
    # ⚠️ THE UNMUTATED TREE MUST PASS FIRST. If it does not, every "refused" below is a refusal
    # for an unrelated reason and the group measures nothing. This is the lesson the sibling
    # paper's allowlist harness paid for: a suite that scores a run it never really made.
    # ⚠ AND THE OLD VERDICT GOES FIRST. `build_package.py` unlinks it, issues a nonce and
    # validates both before it branches, so the packaged path was never at risk. But
    # OPERATOR-ACTIONS.md tells the operator to run this file directly, and on that path a run
    # that crashed left the PREVIOUS verdict in place with no timestamp and nothing saying which
    # tree it described. Absence should mean "no verdict" by hand as well.
    try:
        (HERE / "CONTROL-SUITE-VERDICT.json").unlink()
    except OSError:
        pass
    _w = pathlib.Path(tempfile.mkdtemp(prefix="pa-"))
    try:
        _r = _w / "r"
        shutil.copytree(HERE, _r, ignore=IGNORE)
        _rc, _out = run(_r, "prepare_anchor.py")
        _base_ok = (_rc == 0)
        print("    %s %-52s" % ("baseline" if _base_ok else D + " BASELINE",
                                "the unmutated tree prepares cleanly"))
        if not _base_ok:
            print("      %s the baseline does not pass, so nothing below is measured:" % D)
            print("      " + (_out.strip().splitlines() or ["(no output)"])[-1][:100])
            hygiene_failed = True
    finally:
        shutil.rmtree(_w, ignore_errors=True)

    for label, build, argv, phrase in PREPARE_ATTACKS:
        work = pathlib.Path(tempfile.mkdtemp(prefix="pa-"))
        root = work / "r"
        shutil.copytree(HERE, root, ignore=IGNORE)
        _env = dict(os.environ)
        try:
            build(root)
            rc, out = run(root, "prepare_anchor.py", *argv)
        except _Unmeasurable as _u:
            # ⚠ NEITHER CAUGHT NOR MISSED. A control that could not be set up says so and is
            # scored as nothing; a suite that counted it as refused would be measuring the
            # absence of gpg, and one that counted it as passed would be crying wolf.
            print("    %s %-52s unmeasured: %s" % (W, label, _u))
            continue
        finally:
            os.environ.clear()
            os.environ.update(_env)
            shutil.rmtree(work, ignore_errors=True)
        # ⛔ THE NAMED REFUSAL, NOT ANY REFUSAL.
        ok = rc != 0 and phrase in out
        why = ("refused " if ok else
               D + " WRONG   " if rc != 0 else
               D + " PASSED ")
        print("    %s %-52s %s" % (why, label, "" if ok else "(wanted %r)" % phrase))
        # ⚠ A `WRONG` VERDICT YOU CANNOT READ IS HALF A FINDING. It says the gate refused
        # for some other reason and not which, so diagnosing one meant re-running the attack
        # by hand -- which is how four of them were mis-read for three rounds. The refusal it
        # DID give is printed here, because that is the whole of what the verdict is about.
        if not ok:
            _tail = [l for l in out.strip().splitlines() if l.strip()]
            print("        got: %s" % (_tail[-1].strip()[:150] if _tail else "(no output)"))
        caught += ok
        missed += not ok

    print()
    print("  withdrawn_claims.py -- the generator, and the record of the readings")
    # ⚠️ THIS BASELINE RUNS IN THE REAL TREE, and every other one runs in a sandbox. The
    # difference is not laziness: the generated file states how many text files were SCANNED, and
    # `IGNORE` copies a deliberate subset, so a sandbox is a folder the shipped document correctly
    # does not describe. Asserting it there would measure the sandbox. `--check` writes nothing.
    # The four attacks below still need copies -- they mutate -- and each of their refusals fires
    # before the document is compared, so none of them depends on the count.
    _rc, _out = run(HERE, "withdrawn_claims.py", "--check")
    _base_ok = _rc == 0 and "describes this folder" in _out
    print("    %s %s" % ("baseline" if _base_ok else D + " BASELINE",
                         "the unmutated record verifies and the file describes this folder"))
    if not _base_ok:
        print("      %s the baseline does not pass, so nothing below is measured:" % D)
        print("      " + (_out.strip().splitlines() or ["(no output)"])[-1][:100])
        hygiene_failed = True

    for label, build, phrase in WITHDRAWN_ATTACKS:
        work = pathlib.Path(tempfile.mkdtemp(prefix="wc-"))
        root = work / "r"
        shutil.copytree(HERE, root, ignore=IGNORE)
        try:
            build(root)
            rc, out = run(root, "withdrawn_claims.py", "--check")
        finally:
            shutil.rmtree(work, ignore_errors=True)
        ok = rc != 0 and phrase in out
        why = ("refused " if ok else
               D + " WRONG   " if rc != 0 else
               D + " PASSED ")
        print("    %s %-52s %s" % (why, label, "" if ok else "(wanted %r)" % phrase))
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

    # ⛔ AND SHAPE ALONE COULD NOT SAY WHAT A BLOCK WAS FOR. The rule that replaced the heading
    # -- a fence whose rows are all bare paths the document pins -- read a coincidence, and a
    # round-12 reviewer appended an ordinary code example naming one pinned file and had it come
    # back as the declared distribution. The discriminator is now IN the block: a fence whose info
    # string is `distribution-subset`. These four exercise the grammar itself rather than the rule
    # it feeds.
    print()
    print("  check_commitments.py -- what MAKES a block a distribution subset")
    _F = chr(96) * 3
    # ⚠ THE BASE TEXT MUST DECLARE NOTHING, or every "declares" fixture below is a second
    # block and a refusal. v22 carries the sentinel form, so its own block is cut out here.
    _text = _re.sub("^ {0,3}(?:" + _F + "|~~~)[ \t]*distribution-subset[ \t]*\n.*?^ {0,3}(?:"
                    + _F + "|~~~)[ \t]*\n", "", _text, flags=_re.M | _re.S)
    _pin = sorted({n for n, _d in _CCX.commitments(_text)})[:1]
    if not _pin:
        print("    " + chr(0x26A0) + " the governing document pins nothing, so this is not asserted")
    else:
        _p = _pin[0]
        _grammar = [
            ("an ordinary example fence naming a pinned file is not a declaration",
             _text + NL + "Run it like this:" + NL + NL + _F + NL + _p + NL + _F + NL,
             lambda got: got != {_p}),
            ("a block that DECLARES itself is read as the subset",
             _text + NL + _F + "distribution-subset" + NL + _p + NL + _F + NL,
             lambda got: got == {_p}),
            ("a declared block naming a file the document does not pin is refused",
             _text + NL + _F + "distribution-subset" + NL + "not_pinned_anywhere.py" + NL
             + _F + NL, "refuse"),
            ("two declared blocks are a refusal, not a choice",
             _text + (NL + _F + "distribution-subset" + NL + _p + NL + _F + NL) * 2, "refuse"),
            # ⛔ ROUND 13: THE READER WAS A REGEX AND MARKDOWN IS NOT A REGULAR LANGUAGE. A
            # sentinel nested inside a four-backtick fence is LITERAL TEXT to a renderer and was
            # a declaration to the regex; an indented sentinel is a fence to a renderer and was
            # nothing to the regex, which then fell through to the shape rule. Both directions.
            ("a sentinel nested inside a 4-backtick fence is a REFUSAL, not a declaration",
             _text + NL + chr(96) * 4 + "text" + NL + _F + "distribution-subset" + NL + _p + NL
             + _F + NL + chr(96) * 4 + NL, "refuse"),
            ("a sentinel indented two spaces is a fence to CommonMark, so it declares",
             _text + NL + "  " + _F + "distribution-subset" + NL + "  " + _p + NL + "  " + _F + NL,
             lambda got: got == {_p}),
            ("a tilde fence with the sentinel declares",
             _text + NL + "~~~distribution-subset" + NL + _p + NL + "~~~" + NL,
             lambda got: got == {_p}),
            ("a sentinel inside a blockquote is a refusal",
             _text + NL + "> " + _F + "distribution-subset" + NL + "> " + _p + NL + "> " + _F + NL,
             "refuse"),
            ("a sentinel with trailing text in the info string is a refusal, not the shape rule",
             _text + NL + _F + "distribution-subset x" + NL + _p + NL + _F + NL, "refuse"),
            ("the pre-sentinel SHAPE form -- a bare fence of pinned paths -- declares NOTHING now",
             _text + NL + _F + NL + _p + NL + _F + NL, lambda got: got == set()),
        ]
        for _label, _txt, _want in _grammar:
            try:
                _got, _raised = _CCX.distribution_subset(_txt), False
            except SystemExit:
                _got, _raised = None, True
            _ok = _raised if _want == "refuse" else (not _raised and _want(_got))
            print("    %s %-62s" % ("ok      " if _ok else D + " WRONG ", _label))
            caught += _ok
            missed += not _ok

    # ⛔ ROUND 13: THE SIGNATURE CACHE WAS KEYED ON mtime AND size, WHICH A BYTE-FLIP THAT
    # PRESERVES BOTH DOES NOT MOVE. Cache `ok`, swap in a BAD signature of the same length with
    # the mtime put back, ask again in the same process: `ok`. Narrow -- one process, after the
    # state was cached -- and precisely the gap the cache's own comment claimed not to have.
    print()
    print("  prepare_anchor.py -- the signature cache under a same-size, same-mtime byte flip")
    _w = pathlib.Path(tempfile.mkdtemp(prefix="sc-"))
    try:
        _r = _w / "r"
        shutil.copytree(HERE, _r, ignore=IGNORE)
        import prepare_anchor as _PAX
        _doc = _stamped_and_signed(_r)
        _sig = _doc.parent / (_doc.name + ".asc")
        _st0 = _PAX.signature_state(_doc)
        _raw = bytearray(_sig.read_bytes())
        _lines = _sig.read_text(encoding="utf-8").splitlines()
        _body = [i for i, l in enumerate(_lines) if len(l) > 40 and not l.startswith(("-----", "="))]
        _pos = _sig.read_bytes().index(_lines[_body[len(_body) // 2]].encode("utf-8")) + 5
        _raw[_pos] = ord("A") if _raw[_pos] != ord("A") else ord("B")
        _mt = _sig.stat()
        _sig.write_bytes(bytes(_raw))
        os.utime(_sig, ns=(_mt.st_atime_ns, _mt.st_mtime_ns))
        _st1 = _PAX.signature_state(_doc)
        _ok = _st0 == "ok" and _st1 == "bad"
        print("    %s %-52s %s -> %s" % ("ok      " if _ok else D + " WRONG ",
                                         "a flipped byte under an unchanged size and mtime", _st0, _st1))
        caught += _ok
        missed += not _ok
    finally:
        shutil.rmtree(_w, ignore_errors=True)

    print()
    print("  check_signature.py -- a valid signature by a key that is not the protocol's")
    _w = pathlib.Path(tempfile.mkdtemp(prefix="wk-"))
    _env = dict(os.environ)
    try:
        _r = _w / "r"
        shutil.copytree(HERE, _r, ignore=IGNORE)
        try:
            p_wrong_key_signature(_r)
            import check_signature as _CSX
            # GNUPGHOME is relative (the MSYS gpg cannot take a Windows absolute homedir), so the
            # verifying process has to stand where the sandbox keyring is
            _cwd = os.getcwd()
            os.chdir(str(_r))
            try:
                _st, _why, _fpr = _CSX.verify(_newest(_r))
            finally:
                os.chdir(_cwd)
            _ok = _st == "BAD" and "WRONG KEY" in (_why or "")
            print("    %s %-52s %s: %s" % ("ok      " if _ok else D + " WRONG ",
                                            "verify() names the wrong key, not merely a bad one",
                                            _st, (_why or "")[:50]))
            caught += _ok
            missed += not _ok
        except _Unmeasurable as _u:
            print("    %s %-52s unmeasured: %s" % (W, "verify() names the wrong key", _u))
    finally:
        os.environ.clear()
        os.environ.update(_env)
        shutil.rmtree(_w, ignore_errors=True)

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
    print("  the distribution record -- an append-only log that nothing checked")
    for _label, _got, _want in _attempts_fixtures():
        _ok = _got == _want
        if not _ok:
            _shape_bad.append(_label)
            hygiene_failed = True
        print("    %s %-64s %s" % ("ok     " if _ok else D + " WRONG", _label,
                                   "" if _ok else "got %r want %r" % (_got, _want)))

    print()
    print("  round 17 -- the strongest commitment decides, not the first one found")
    for _label, _got, _want in _round17_fixtures():
        _ok = _got == _want
        print("    %s %-70s %s" % ("refused " if _ok else D + " PASSED ", _label,
                                   "" if _ok else "got %r want %r" % (_got, _want)))
        caught += _ok
        missed += not _ok

    print()
    print("  round 14 -- the three findings, in process")
    for _label, _got, _want in _round14_fixtures():
        _ok = _got == _want
        print("    %s %-70s %s" % ("refused " if _ok else D + " PASSED ", _label,
                                   "" if _ok else "got %r want %r" % (_got, _want)))
        caught += _ok
        missed += not _ok

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
