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
ALWAYS = ("corpus/MANIFEST.json",)


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
    """
    out = [(p.name, WHY.get(p.name, "a protocol document -- undescribed here, still required"))
           for p in sorted(HERE.glob("PRE-REGISTRATION*.md"))]
    return out + [(f, WHY.get(f, "")) for f in ALWAYS]


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
    proof = HERE / (rel + ".ots")
    if not doc.exists():
        return "DOCUMENT MISSING", 0, False
    if not proof.exists():
        return "NO PROOF", 0, False
    blob = proof.read_bytes()
    if len(blob) < 32:
        return "PROOF TOO SHORT TO BE ONE", len(blob), False
    digest = hashlib.sha256(doc.read_bytes()).digest()
    # ⛔ THIS SEARCHED FOR THE DIGEST AND THE TAG AS SUBSTRINGS. Forty bytes containing both
    # passed as ANCHORED. It parses now, and the block heights it prints are read out of the
    # attestation records rather than assumed to exist.
    ok, why, found = _OTS.verify(blob, doc.read_bytes())
    if ok:
        return ("ANCHORED " + why.split(";")[0].replace("anchored in Bitcoin block(s) ", ""),
                len(blob), True)
    if "carries no Bitcoin attestation" in why:
        return "pending (calendar only)", len(blob), False
    return why[:46].upper() if "NOT A PROOF" in why else "PROOF DOES NOT BIND THIS DOCUMENT", len(blob)


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
