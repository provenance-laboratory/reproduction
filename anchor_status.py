"""Does each REQUIRED proof exist, bind the document beside it, and carry a Bitcoin attestation?

⛔ THE PREVIOUS VERSION OF THIS FILE WAS A DEAD CONTROL, AND IT IS THE REASON EVERYTHING ELSE GOT
THROUGH. It globbed whatever `*.ots` files happened to exist and searched each for an eight-byte
tag. A round-3 reviewer demonstrated three ways to pass it:

    35 bytes of junk containing the tag        -> ANCHORED
    the last 16 bytes of a real proof          -> ANCHORED
    deleting every proof in the directory      -> "every active proof carries a Bitcoin
                                                  attestation", exit 0

⇒ **It reported success while the governing pre-registration had no proof, no presence in the
package, and no existence in the review archive.** A control that enumerates what it finds cannot
notice what is missing, and this one was written specifically to stop a claim about anchoring from
drifting from the facts. It drifted further than the prose it was policing.

⛔ AND THE SECOND FAILURE IT MISSED: A PROOF BINDS BYTES, NOT A FILENAME. v2 and v3 were both
stamped and then EDITED -- v3 to say "now anchored", which is the sentence whose truth the edit
destroyed. Their proofs still sat beside them, still contained the tag, and no longer committed to
the documents they were named for. Checking the tag says a calendar answered; checking the digest
says WHAT it answered about.

⇒ So this now:

    * takes an EXPLICIT REQUIRED LIST -- absence is a failure, not an empty success
    * recomputes each document's sha256 and requires the proof to contain it
    * requires the Bitcoin attestation tag
    * refuses on an empty set, a malformed proof, or an unlisted extra

⚠️ WHAT IT STILL DOES NOT DO, STATED SO NOBODY READS MORE INTO A PASS. It does not walk the
attestation path to a block header, and tag presence is not verification. Confirming that a proof
actually commits to a Bitcoin block requires an OpenTimestamps verifier against a node or a
calendar, which is a network operation and belongs in the publication checklist rather than here.
A pass means *this proof is over these bytes and claims a Bitcoin attestation* -- no more.

    python anchor_status.py
"""
import hashlib
import io
import pathlib
import sys

import ots_verify as _OTS

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])

# Reasons, where a document deserves one. ⚠ THIS IS AN ANNOTATION TABLE, NOT THE LIST OF WHAT
# MUST BE ANCHORED -- a document missing from here is still required, and merely goes undescribed.
WHY = {
    "PRE-REGISTRATION-v8-CONFIRMATORY.md":
        "proofs parsed rather than substring-matched, and signatures for WHO",
    "PRE-REGISTRATION-v7-CONFIRMATORY.md":
        "v6 section 2b re-committed after repairing a control, which v6 said would cost a version",
    "PRE-REGISTRATION-v6-CONFIRMATORY.md":
        "the instruments and gates, committed after round 4 showed only the inputs were",
    "PRE-REGISTRATION-v5-CONFIRMATORY.md":
        "the digest commitments, re-committed after v3 section 2 went unenforced for a day",
    "PRE-REGISTRATION-v4-CONFIRMATORY.md":
        "measurement 4's admissibility, committed before any second-machine run exists",
    "PRE-REGISTRATION-v3-CONFIRMATORY.md": "the protocol the study runs under",
    "PRE-REGISTRATION-v2-CONFIRMATORY.md": "version 2, retained as part of the record",
    "PRE-REGISTRATION.md": "version 1, retained as the pilot protocol",
    "corpus/MANIFEST.json": "the corpus the model is trained on",
}
# never annotated, always required
# ⛔ REMOVED IN ROUND 8. This was `("corpus/MANIFEST.json",)` -- see `required()`. The corpus
# manifest is still required, and it is required because the governing version PINS it, which is a
# fact this tool now reads rather than a line somebody has to remember to add.


PINNED_UNANCHORED = []


def required():
    """Every protocol document PRESENT, discovered -- plus the inputs that must always be anchored.

    ⛔ THIS WAS A HAND-KEPT LIST, AND IT IS INSTANCE THIRTEEN OF THE DEFECT THIS PROJECT KEEPS
    MAKING. Worse, v7 NOTICED THE COST AND PAID IT THE WRONG WAY: it recorded that this file "moved
    only because it must NAME this document", and the repair was to add a line to the list rather
    than to remove the list. Fixing instance N by enumerating is how instance N+1 gets made -- here
    inside a protocol version whose own subject was an enumeration defect.

    ⚠ THE OLD COMMENT HAD A REAL ARGUMENT AND IT IS PRESERVED. "Whatever is on disk" is how a
    missing governing document once passed unnoticed, and globbing alone would reintroduce exactly
    that. So the projection FAILS CLOSED: a document that exists without a proof is a FAILURE
    rather than an omission, and a version that is absent from the disk entirely is caught by
    `check_commitments.governing()`, which selects authority rather than trusting this list.

    ⛔⛔ AND `ALWAYS` SURVIVED THE FIX AS A ONE-ELEMENT LIST. `("corpus/MANIFEST.json",)` --
    four characters of residue beside the projection that replaced it, inside a docstring that
    calls the hand-kept list instance thirteen. v18 pinned and ANCHORED a new artifact,
    `exposure/exposure-2026-09-07.json`, whose entire claim is *captured before any announcement*
    and whose proof this round genuinely repaired from a 530-byte calendar receipt to Bitcoin
    block 965922 -- and this tool filed it under:

        ⚠ 7 proof(s) present but not in the required list ... An unlisted proof is not a
          failure, but it is not evidence for anything either.

    Nobody added a line, because adding a line is the maintenance step the fix was meant to
    abolish. That is instance fourteen, in the file that names instance thirteen.

    ⚠️ THE SIX `.asc.ots` FILES ARE THE SAME SHAPE ONE LEVEL OVER. This derived the required
    set as {document name + ".ots"}, so a proof over a SIGNATURE could never be in it -- and those
    six ship with the stated reason *proof over v12's signature*, while this reports them as
    evidence for nothing.

    ⇒ DERIVE THE WHOLE SET FROM WHAT MUST BE ANCHORED: every protocol document, every file the
    governing version PINS, and every detached signature sitting beside either. Nothing is
    appended by hand, so nothing has to be remembered.
    """
    out = [(p.name, WHY.get(p.name, "a protocol document -- undescribed here, still required"))
           for p in sorted(HERE.glob("PRE-REGISTRATION*.md"))]
    names = {n for n, _w in out}
    _pinned_unanchored = PINNED_UNANCHORED

    # Everything the governing version commits by digest. Read, not listed.
    try:
        import prepare_anchor as _PA
        _vs = _PA.versions()
        if _vs:
            # ⛔ `max(_vs)` AGAIN -- the sixth occurrence of the same selector. Highest present
            # is not governing while a successor waits; the required set is composed over the
            # versions IN FORCE. Less severe here only because the recursive `.ots` projection
            # below rediscovers most proof-bearing files anyway, which is luck and not a design.
            for _n in sorted(_PA.governing_pins()[0]):
                # ⚠️ A PINNED FILE IS ANCHORED THROUGH THE DOCUMENT THAT PINS IT. Its digest is
                # inside a text whose own proof fixes when that text existed, so demanding a
                # separate proof for `train.py` would be a requirement this design never made --
                # and would put every pinned tool into NO PROOF, blocking publication over
                # versions in force for weeks.
                #
                # ⇒ It enters the REQUIRED set when it carries a proof of its own, which is
                # what `corpus/MANIFEST.json` and `exposure/exposure-2026-09-07.json` do. That is
                # the misfiling this replaces: the exposure capture's genuinely repaired proof --
                # Bitcoin block 965922, on the one artifact whose claim is *captured before any
                # announcement* -- was being reported as "not evidence for anything".
                if _n not in names and (HERE / _n).is_file() and (HERE / (_n + ".ots")).is_file():
                    out.append((_n, "pinned by the governing version AND independently anchored"))
                    names.add(_n)
                elif _n not in names and (HERE / _n).is_file():
                    _pinned_unanchored.append(_n)
    except BaseException as _e:                                       # pragma: no cover
        out.append(("<pins unreadable>", "could not read what the governing version pins: %s"
                    % type(_e).__name__))

    # ⚠️ A SIGNATURE IS ACCOUNTED FOR, NOT REQUIRED TO BE ANCHORED. The complaint this answers
    # was that the six existing `.asc.ots` proofs -- shipped with the stated reason *proof over
    # v12's signature* -- were reported as "present but not in the required list", i.e. as
    # evidence for nothing. So a signature enters the required set exactly when its proof EXISTS,
    # which stops that misfiling.
    #
    # ⛔ AND NOT FURTHER. Requiring a proof for every `.asc` would put eight historical
    # signatures into NO PROOF and block publication over versions that have been in force for
    # weeks -- a retroactive demand this project did not make when they were signed. Those are
    # listed below as a stated gap instead: WHO is established for them, WHEN is not.
    for _n in sorted(names):
        _asc = _n + ".asc"
        if (HERE / _asc).is_file() and _asc not in names and (HERE / (_asc + ".ots")).is_file():
            out.append((_asc, "a detached signature whose own proof exists -- it says WHO, and "
                              "its proof says by when it said it"))
    return out


def signatures_without_proofs():
    """Signatures beside a required file that carry no proof of their own. A gap, stated."""
    have = {n for n, _w in REQUIRED}
    out = []
    for n in sorted(have):
        asc = n + ".asc"
        if (HERE / asc).is_file() and not (HERE / (asc + ".ots")).is_file():
            out.append(asc)
    return out


REQUIRED = required()
# Proofs that are deliberately historical: they bind bytes that have been superseded, and their
# failure to bind anything current is the fact they exist to record.
#
# ⛔ THIS WAS A LIST OF THE TWO SUFFIXES THAT HAPPENED TO EXIST, and it was found by trying to
# USE the convention it encodes: retiring a proof under a new `.superseded-<digest>` name would
# have made that proof an unrecognised extra, reported as clutter rather than as the record it is.
# A convention with a documented naming rule, enforced by a list of the names used so far, is
# instance fourteen of the defect this project keeps making.
#
# ⚠ IT STAYS ANCHORED TO A PATTERN, NOT OPENED UP. `.superseded-` followed by something is
# recognised; a bare `.superseded` is not, because a retired proof must say WHAT it binds.
def _is_superseded(path):
    name = str(path)
    i = name.find(".superseded-")
    return i != -1 and len(name) > i + len(".superseded-")


def check(rel):
    doc = HERE / rel
    if not doc.exists():
        return "DOCUMENT MISSING", 0, False
    # ⛔ ROUND 17: THIS FOUND THE PROOF BY FILENAME, `rel + ".ots"`, AND WAS THE THIRD TOOL IN
    # THIS TREE TO ANSWER *is there a proof of these bytes*. §2n repaired `stamped()` and §2r
    # repaired `check_commitments.anchored()`; a reporting tool left deciding by name reports NO
    # PROOF for a commitment that is sitting in the folder under another name. It failed closed,
    # which is why it was a report and not a bypass, and a report that is wrong about the tree is
    # still wrong. ⇒ The same projection the other two use, from the one place it now lives.
    _proofs = _OTS.proofs_over(doc)
    if not _proofs:
        _named = HERE / (rel + ".ots")
        if _named.is_file():
            return "NOT A PROOF OF THESE BYTES", _named.stat().st_size, False
        return "NO PROOF", 0, False
    proof, blob, _ok = None, None, False
    for _p in _proofs:
        _b = _p.read_bytes()
        if proof is None:
            proof, blob = _p, _b
        if len(_b) < 32:
            continue
        if _OTS.verify(_b, doc.read_bytes())[0]:
            proof, blob = _p, _b
            break
    if len(blob) < 32:
        return "PROOF TOO SHORT TO BE ONE", len(blob), False
    digest = hashlib.sha256(doc.read_bytes()).digest()
    # ⛔ THIS SEARCHED FOR THE DIGEST AND THE TAG AS SUBSTRINGS. Forty bytes containing both
    # passed as ANCHORED. It parses now, and the block heights it prints are read out of the
    # attestation records rather than assumed to exist.
    ok, why, found = _OTS.verify(blob, doc.read_bytes())
    if ok:
        # ⛔⛔ AND `ANCHORED` IS TWO DIFFERENT CLAIMS. `ots_verify` proves a proof is structurally
        # valid and self-consistent WITH `ANCHORS.json`; it cannot prove `ANCHORS.json` carries
        # the chain's real merkle root, and this tree's own `check_commitments.py` reports that
        # file as RETIRED by v10 and committed by no version. Round-11 reviewers substituted a
        # root at an existing height, and appended a row for a block that was never pinned, and
        # both reached `ANCHORED`. A full node would have rejected each.
        #
        # ⇒ THE WORD IS QUALIFIED BY WHAT SUPPORTS IT. A block a signed-and-anchored version
        # names in its own §2d fact table is CONFIRMED -- written down before anyone could choose
        # it. A block known only to `ANCHORS.json` is PROVISIONAL. This tool REPORTS both, which
        # is its job; `prepare_anchor.in_force()` requires the confirmed one, which is its job.
        _w = why.split(";")[0].strip()
        _blocks = _w[_w.find("["):] if "[" in _w else _w
        try:
            import prepare_anchor as _PA
            _conf = _PA.confirmed(doc)
        except Exception:                                                # noqa: BLE001
            _conf = None
        if _conf is True:
            return ("ANCHORED (confirmed) " + _blocks, len(blob), True)
        if _conf is False:
            return ("ANCHORED against the pinned anchor set, PROVISIONAL " + _blocks,
                    len(blob), True)
        return ("ANCHORED against the pinned anchor set " + _blocks, len(blob), True)
    if "carries no Bitcoin attestation" in why:
        return "pending (calendar only)", len(blob), False
    # ⛔ THIS RETURNED TWO VALUES WHERE THE CALLER UNPACKS THREE, so the tool CRASHED on the
    # tampering path -- the one failure it exists to report. The comment above separated display
    # from verdict and updated five of six return paths; the sixth is this one. A round-7 reviewer
    # reached it by making the corpus proof structural, and got a traceback instead of a verdict.
    #
    # ⚠ And "PROOF DOES NOT BIND THIS DOCUMENT" was FALSE for that input: the corpus proof binds
    # its document perfectly well and was refused for naming an unpinned block. A catch-all label
    # that asserts a specific cause is worse than one that admits it does not know.
    if "NOT A PROOF" in why:
        return why[:46].upper(), len(blob), False
    if "STRUCTURAL" in why:
        return "STRUCTURAL, BLOCK NOT PINNED", len(blob), False
    if "REFUSED" in why:
        return "ROOT IS NOT THAT BLOCK'S", len(blob), False
    return "PROOF DOES NOT BIND THIS DOCUMENT", len(blob), False


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=" * 78)
    print("  OPENTIMESTAMPS — presence, binding, and attestation, over a REQUIRED list")
    print("=" * 78)
    print()

    bad = []
    for rel, why in REQUIRED:
        # ⛔ THIS READ `ok = st == "ANCHORED"` WHILE `check()` HAD BEEN CHANGED TO RETURN
        # `"ANCHORED [964761, 964762]"`. Making the status more informative silently broke every
        # comparison against the bare literal, and the tool reported nine anchored documents as
        # failures. It failed CLOSED, which is the only reason it was noticed within a minute --
        # `"ANCHORED" in st` would have failed OPEN and matched "NOT ANCHORED" too.
        #
        # ⚠ A DISPLAY STRING IS NOT A VERDICT. The two are separate values now, so a change to
        # what is printed cannot move what is decided.
        st, n, ok = check(rel)
        print("  %-34s %6d B  %-46s %s" % (st, n, rel, why))
        if not ok:
            bad.append((rel, st))

    extras = sorted(p for p in HERE.rglob("*.ots")
                    if "package" not in p.parts and "review" not in p.parts
                    and str(p.relative_to(HERE)).replace(chr(92), "/")
                    not in {r + ".ots" for r, _ in REQUIRED}
                    and not _is_superseded(p))
    print()
    for p in sorted(HERE.rglob("*.ots*")):
        if "package" in p.parts or "review" in p.parts:      # round 16: the shipped projection, not scratch
            continue
        if _is_superseded(p):
            print("  (superseded, binds historical bytes)  %s" % p.relative_to(HERE))
    if extras:
        print()
        print("  " + W + " %d proof(s) present but not in the required list:" % len(extras))
        for p in extras:
            print("      %s" % p.relative_to(HERE))
        print("  An unlisted proof is not a failure, but it is not evidence for anything either.")

    print()
    if bad:
        print("  " + D + " %d REQUIRED proof(s) do not pass:" % len(bad))
        for rel, st in bad:
            print("      %-46s %s" % (rel, st))
        print()
        print("  Nothing may be published, and no document may say ANCHORED, until this is empty.")
        print("  %s AND `ANCHORED` HERE MEANS *against the pinned anchor set*. ANCHORS.json is an"
              % chr(0x26A0))
        print("     explorer-sourced assertion this tree does not commit; a block a signed and")
        print("     anchored version names in its own fact table is CONFIRMED, and a block known")
        print("     only to that file is PROVISIONAL. Only the confirmed one moves authority.")
        print("  " + W + " 'PROOF DOES NOT BIND THIS DOCUMENT' usually means the document was")
        print("  EDITED AFTER STAMPING. Stamp last. If the text must change, retire the old proof")
        print("  under a name that says what it binds and create a new one.")
        return 1

    print("  every required document exists, its proof binds its current bytes, and each proof")
    print("  carries a Bitcoin attestation tag")
    print()
    print("  " + W + " Tag presence is NOT full verification. Confirming the attestation path to a")
    print("  block requires an OpenTimestamps verifier against a node or calendar -- a network")
    print("  step, listed in PUBLICATION-CHECKLIST.md and deliberately not done here.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
