"""Do the files v3 §2 commits BY DIGEST still hash to those digests?

⛔ WHY THIS EXISTS. `PRE-REGISTRATION-v3-CONFIRMATORY.md` §2 lists four files with their SHA-256
digests and says:

    "Any change to a file above changes its digest and voids this pre-registration. That is the
     property v2 lacked: it named files, and a name is not a commitment."

That sentence was **unenforced prose**. On 2026-08-31, `corpus/build_corpus.py` was edited to add a
verification mode -- a change with no effect on how the corpus is derived -- and its digest moved
from `2d3ce23b` to `d9fd717e`. The pre-registration was void for as long as that edit stood, and
**not one tool in this project said anything**: the package rebuilt, `verify_package.py` passed,
and `SHA256SUMS` was regenerated over the new bytes, which is exactly how a substitution passes a
checksum that is derived from the thing it is meant to police.

⇒ A note inside a document is not a control. This is the control.

⚠️ IT PARSES THE PROTOCOL, IT DOES NOT RESTATE IT. A hand-copied list here would drift from §2 the
moment §2 changed, and the drift would be invisible because both would look authoritative. The
digests are read out of the anchored document itself, so this file cannot disagree with the
protocol -- it can only report that the world disagrees with both.

⛔ AND IT FAILS CLOSED ON AN EMPTY PARSE. If the table's format changes and the regex matches
nothing, that is a BROKEN CHECK, not a clean bill of health. Reporting "0 commitments verified,
all good" is how a control becomes a comment.

    python check_commitments.py
"""
import hashlib
import io
import pathlib
import re
import ots_verify as _OTS
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
MIN_EXPECTED = 4
DIGEST_LINE = re.compile(r"^([A-Za-z0-9_./-]+)\s+([0-9a-f]{64})\s*$", re.M)


def commitments(text):
    """(path, digest) for every file a protocol version pins. Read out, never retyped."""
    return [(m.group(1), m.group(2)) for m in DIGEST_LINE.finditer(text)]


BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])


DISTRIBUTION_HEADING = "### 2c."


def distribution_subset(text):
    """The files the protocol says a REPRODUCER PACKAGE contains. Empty if it declares none.

    ⛔ THE PACKAGE SHIPPED A CONTROL THAT COULD NOT PASS INSIDE THE PACKAGE. Since v6 pinned the
    instruments, `check_commitments.py` has pinned sixteen files while the reproducer's package
    deliberately contains nine -- so a stranger following the documented instruction saw nine
    `MISSING` lines and a refusal, on an untampered package. It was never noticed because every
    gate ran the checker against the SOURCE tree; nothing ever ran it where a reproducer runs it.

    ⚠ AND "SKIP FILES THAT ARE NOT THERE" WOULD BE THE ABSENCE DEFECT AGAIN, in the checker whose
    own protocol version was written about absences. Deleting a file would then be a way to avoid
    its digest being checked. So the subset is DECLARED IN THE ANCHORED DOCUMENT and the rule is an
    equality, not a skip: the absent set must be EXACTLY the pinned set minus the declared subset.
    One file missing from the subset, or one absence outside the complement, and this refuses.
    """
    if DISTRIBUTION_HEADING not in text:
        return set()
    tail = text.split(DISTRIBUTION_HEADING, 1)[1]
    block = re.search(r"```" + NL + r"(.*?)```", tail, re.S)
    if not block:
        return set()
    return {ln.strip() for ln in block.group(1).split(NL) if ln.strip()}


def anchored(doc):
    """Does this document's proof PARSE, commit to these bytes, and name a Bitcoin block?

    ⛔ THIS SEARCHED THE FILE FOR TWO BYTE STRINGS. Two round-5 reviewers independently built the
    same 40-byte forgery -- SHA256(document) followed by the Bitcoin tag -- and it passed here,
    moved authority, and let a substituted train.py through with exit 0. `ots info` on that file
    says it is not a timestamp file at all.

    ⇒ Round 4's 35-bytes-of-junk attack survived its own repair, because the repair added BINDING
    and never added PARSING. The class was "a proof is a structure and I am looking for bytes in
    it", and fixing the instance left the class alone. ots_verify.py reads the structure.
    """
    proof = doc.parent / (doc.name + ".ots")
    if not proof.exists():
        return False, "no proof beside it", "MISSING"
    ok, why, found = _OTS.verify(proof.read_bytes(), doc.read_bytes())
    if ok:
        return True, why, "ANCHORED"
    # ⚠ PENDING AND TAMPERED ARE NOT THE SAME REJECTION, and §11 now turns on the difference,
    # so it is a VALUE and not a phrase in `why`. A proof that parses, commits to these bytes and
    # carries a calendar attestation is a document waiting for Bitcoin -- the normal state for
    # hours after stamping. Anything else is a proof that is not a proof.
    state = "PENDING" if (found and all(k != "bitcoin" for k, _v, _r in found)
                          and any(k == "pending" for k, _v, _r in found)) else "TAMPERED"
    return False, why, state


def governing(here):
    """Every ANCHORED protocol version carrying a digest table, and every rejected candidate.

    ⛔ AN EARLIER VERSION NAMED v3 IN A CONSTANT -- the enumeration defect. Deriving the version
    from disk fixed that and opened the hole above: "highest version present" is not an authority
    rule, because anyone who can write a file can mint a higher version.

    ⚠ A REJECTED CANDIDATE IS REPORTED, NEVER SKIPPED. An unanchored document carrying a digest
    table means someone is mid-round or someone is substituting, and silently consulting an older
    table would hide both. The previous version also made its own fail-closed branch DEAD: it
    filtered to tables with at least MIN_EXPECTED entries before main could ever see an empty
    parse, so a broken table silently downgraded enforcement to a retired one. A reviewer read
    that from the source.
    """
    found, rejected = [], []
    for f in sorted(here.glob("PRE-REGISTRATION*.md")):
        m = re.search(r"-v(\d+)-", f.name)
        version = int(m.group(1)) if m else 1
        pinned = commitments(f.read_text(encoding="utf-8"))
        if not pinned:
            continue
        if len(pinned) < MIN_EXPECTED:
            rejected.append((version, f.name,
                             "parses only %d commitment(s); the table's format has changed and "
                             "this parser no longer reads it" % len(pinned)))
            continue
        ok, why, state = anchored(f)
        if not ok:
            rejected.append((version, f.name, why, state))
            continue
        found.append((version, f.name, pinned))

    # ⛔ DESTROYING A PROOF MADE THE CHECKER CHECK LESS, AND PASS. Forging v6's proof did not
    # promote anything -- `ots_verify` refused it correctly, and v6 simply dropped out of `found`.
    # Authority then fell back to v5, WHICH PINS FOUR FILES WHERE v6 PINS SIXTEEN, and every one of
    # the four still matched. Exit 0. The attack does not defeat the proof check; it defeats the
    # SELECTION RULE by removing the strongest candidate, and a weaker table is not a smaller
    # authority, it is a different one.
    #
    # ⚠ A PENDING VERSION MUST NOT TRIGGER THIS, or the project cannot function: for the hours
    # between stamping a successor and its anchor, a legitimately pending document sits above the
    # authority. That is why `anchored()` returns a STATE. Pending is a transition; TAMPERED or
    # MISSING above the selected authority is someone removing the table that would have governed.
    if found:
        top = max(v for v, _n, _p in found)
        blocking = [(v, n, w) for v, n, w, s in rejected
                    if v > top and s in ("TAMPERED", "MISSING")]
        if blocking:
            raise SystemExit(
                D + " %s is present, is a HIGHER version than the authority %s would select, and "
                "its proof is not a proof (%s). Falling back to an older document would enforce a "
                "SMALLER table -- v5 pins 4 files where v6 pins 16 -- so destroying a proof would "
                "make this check weaker and still pass. A protocol document whose proof has been "
                "destroyed is a tampered tree, not an older one."
                % (blocking[-1][1], "the next version down", blocking[-1][2][:60]))
    return found, rejected


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    found, rejected = governing(HERE)
    for _v, _name, _why, _state in sorted(rejected, reverse=True):
        print("  " + W + " %-46s NOT AUTHORITY [%s]: %s" % (_name, _state, _why))
    if rejected:
        print()
    if not found:
        raise SystemExit(D + " no ANCHORED protocol document carries a digest table, so nothing "
                         "here is committed to anything. An unanchored document is a draft.")
    _present = [int(re.search(r"-v(\d+)-", f.name).group(1))
                if re.search(r"-v(\d+)-", f.name) else 1
                for f in HERE.glob("PRE-REGISTRATION*.md")]
    found.sort()
    version, PROTOCOL, pinned = found[-1]
    # ⛔ A NEWER UNANCHORED VERSION MUST NEVER BECOME AUTHORITY -- that is the attack. But
    # REFUSING EVERY BUILD while a freshly stamped version waits hours for its Bitcoin attestation
    # is a rule people work around, and a control that gets worked around is worse than one that
    # is merely strict. So: the anchored version governs, the pending one is reported loudly, and
    # only PUBLISHING is fatal.
    _pending = max(_present) if _present else version
    if _pending > version:
        print()
        print("  " + W + " v%d IS PRESENT AND IS NOT AUTHORITY. v%d governs." % (_pending, version))
        print("  A newly stamped version is pending until a calendar anchors it, which takes")
        print("  hours. Building against v%d is fine and is what is happening. PUBLISHING while a"
              % version)
        print("  newer version is pending is not, and --publishing refuses it.")
        if "--publishing" in sys.argv:
            raise SystemExit(
                D + " v%d is pending and this is a PUBLISHING run. Publish under an anchored "
                "protocol or wait for the anchor." % _pending)
    print("=" * 78)
    print("  COMMITMENTS — the files %s pins by digest" % PROTOCOL)
    print("=" * 78)
    print()

    if len(pinned) < MIN_EXPECTED:
        print("  " + D + " parsed only %d commitment(s) from %s; expected at least %d."
              % (len(pinned), PROTOCOL, MIN_EXPECTED))
        print("  The table's format has changed and this parser no longer reads it. That is a")
        print("  BROKEN CHECK, not a pass: fix the parser before trusting anything below.")
        return 1

    # the subset a distribution is allowed to be, read from the ANCHORED document
    _subset = distribution_subset((HERE / PROTOCOL).read_text(encoding="utf-8"))
    _absent = {rel for rel, _w in pinned if not (HERE / rel).exists()}
    _complement = {rel for rel, _w in pinned if rel not in _subset}
    _is_distribution = bool(_subset) and _absent and _absent == _complement
    if _is_distribution:
        print("  " + W + " THIS IS THE REPRODUCER PACKAGE, not the source tree. %s declares a"
              % PROTOCOL)
        print("  subset of %d file(s); the %d pinned file(s) outside it are absent, which is"
              % (len(_subset), len(_absent)))
        print("  EXACTLY the complement -- not a file missing, and not a file hidden.")
        print()

    bad = []
    for rel, want in pinned:
        f = HERE / rel
        if not f.exists():
            if _is_distribution:
                print("  --   %-26s not in this distribution, by %s" % (rel, PROTOCOL))
                continue
            print("  " + D + " %-26s MISSING" % rel)
            bad.append((rel, "missing", want, None))
            continue
        got = hashlib.sha256(f.read_bytes()).hexdigest()
        if got == want:
            print("  ok   %-26s %s" % (rel, got[:16]))
        else:
            print("  " + D + " %-26s %s  committed %s" % (rel, got[:16], want[:16]))
            bad.append((rel, "changed", want, got))

    # ⛔ A FILE THAT MATCHES THE PENDING VERSION AND NOT THE ANCHORED ONE IS A TRANSITION, NOT A
    # SUBSTITUTION -- and the difference is exactly what an attacker cannot fake, because the
    # pending document is stamped and its proof binds these bytes even before a block confirms it.
    # Calling it a violation would make every round's first hours look like an attack, and a
    # control that cries wolf on its own workflow is one people learn to ignore.
    _transitional = []
    if bad and _pending > version:
        _pdoc = [f for f in HERE.glob("PRE-REGISTRATION*.md")
                 if re.search(r"-v%d-" % _pending, f.name)]
        _ptable = dict(commitments(_pdoc[0].read_text(encoding="utf-8"))) if _pdoc else {}
        _pproof = HERE / (_pdoc[0].name + ".ots") if _pdoc else None
        # ⛔ THE ALLOWANCE REIMPLEMENTED A WEAKER TWO-TEST VERSION INLINE and dropped the length
        # guard, so a 32-byte "proof" containing only the document's own digest satisfied it. A
        # reviewer found the duplicate. One parser, one place.
        #
        # ⚠ AND THE ALLOWANCE'S STATED ARGUMENT WAS WRONG. It said a pending stamp is "exactly
        # what an attacker cannot fake" -- but stamping is free, public and unilateral. The one
        # unforgeable property is the Bitcoin attestation, which the allowance is DEFINED by
        # waiving. It is a convenience for the hours before an anchor lands, and nothing more.
        _stamped = False
        if _pproof and _pproof.exists():
            _pok, _pwhy, _pf = _OTS.verify(_pproof.read_bytes(), _pdoc[0].read_bytes())
            # a pending proof is legitimately not anchored; it must still BE a proof
            _stamped = _pok or ("carries no Bitcoin attestation" in _pwhy)
        # ⛔ AND THE EXCUSE MUST NOT SURVIVE A MISSING PROOF. The transitional allowance was
        # added so a freshly stamped version does not make every build look like an attack -- and
        # it immediately swallowed one: DELETING the anchored document's proof dropped authority
        # to an older version, whereupon the pending version vouched for the changed file and the
        # check passed. An escape hatch that opens when the thing it trusts is REMOVED is the
        # absence-defect this round is about, committed inside the fix for it. Caught by the
        # control suite one minute after it was written.
        _all_proved = all((HERE / (f.name + ".ots")).exists()
                          and hashlib.sha256(f.read_bytes()).digest()
                          in (HERE / (f.name + ".ots")).read_bytes()
                          for f in HERE.glob("PRE-REGISTRATION*.md"))
        if not _all_proved:
            print("  " + D + " a protocol document is present with no proof binding it, so the")
            print("  transitional allowance does not apply. A missing proof is the alarm.")
            _stamped = False
        if _stamped:
            for rel, why, want, got in list(bad):
                if why == "changed" and _ptable.get(rel) == got:
                    _transitional.append(rel)
                    bad.remove((rel, why, want, got))

    print()
    if _transitional:
        print("  " + W + " %d file(s) match the PENDING v%d and not the anchored v%d: %s"
              % (len(_transitional), _pending, version, _transitional))
        print("  v%d is stamped and its proof binds its current bytes, so this is a"
              % _pending)
        print("  transition between versions rather than a substitution.")
        print("  It becomes a violation if v%d never anchors. --publishing already refuses"
              % _pending)
        print("  while anything is pending.")
        print()
    if bad:
        print("  " + D + " %d COMMITTED FILE(S) NO LONGER MATCH. By %s this pre-registration"
              % (len(bad), PROTOCOL))
        print("  IS VOID until they are restored or a new version re-commits them.")
        print()
        for rel, why, want, got in bad:
            print("      %-26s %s" % (rel, why))
            print("        committed %s" % want)
            if got:
                print("        now      %s" % got)
        print()
        print("  " + W + " RESTORE IS ALMOST ALWAYS THE RIGHT ANSWER. Re-committing new digests")
        print("  makes the pipeline a moving target, which is the property v2 had and v3 exists")
        print("  to remove. If a committed file genuinely must change, that is a new protocol")
        print("  version, stamped and anchored before any further run.")
        return 1

    if _transitional:
        print("  %d of %d committed file(s) hash to the anchored protocol's digests; %d match the"
              % (len(pinned) - len(_transitional), len(pinned), len(_transitional)))
        print("  stamped-but-pending v%d instead. Nothing here is unaccounted for." % _pending)
    else:
        print("  all %d committed file(s) hash to the digests the anchored protocol pins"
              % len(pinned))
    print()
    print("  " + W + " This says the FILES are unchanged AND that the document pinning them is")
    print("  anchored -- its proof binds its current bytes and carries a Bitcoin attestation.")
    print("  It does NOT say a run obeyed the protocol: nothing here records which pipeline")
    print("  produced any existing run, or when. That is round 4's open finding.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
