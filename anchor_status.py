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

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])

# ⛔ EXPLICIT, because "whatever is on disk" is how a missing governing document passed.
# Adding a protocol version means adding it here; that is the point.
REQUIRED = [
    ("PRE-REGISTRATION-v4-CONFIRMATORY.md",
     "measurement 4's admissibility, committed before any second-machine run exists"),
    ("PRE-REGISTRATION-v3-CONFIRMATORY.md", "the protocol the study runs under"),
    ("corpus/MANIFEST.json", "the corpus the model is trained on"),
    ("PRE-REGISTRATION.md", "version 1, retained as the pilot protocol"),
    ("PRE-REGISTRATION-v2-CONFIRMATORY.md", "version 2, retained as part of the record"),
]
# Proofs that are deliberately historical: they bind bytes that have been superseded, and their
# failure to bind anything current is the fact they exist to record.
SUPERSEDED_SUFFIXES = (".superseded-814acd24", ".superseded-metadata-only")


def check(rel):
    doc = HERE / rel
    proof = HERE / (rel + ".ots")
    if not doc.exists():
        return "DOCUMENT MISSING", 0
    if not proof.exists():
        return "NO PROOF", 0
    blob = proof.read_bytes()
    if len(blob) < 32:
        return "PROOF TOO SHORT TO BE ONE", len(blob)
    digest = hashlib.sha256(doc.read_bytes()).digest()
    if digest not in blob:
        return "PROOF DOES NOT BIND THIS DOCUMENT", len(blob)
    if BITCOIN_TAG not in blob:
        return "pending (calendar only)", len(blob)
    return "ANCHORED", len(blob)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("=" * 78)
    print("  OPENTIMESTAMPS — presence, binding, and attestation, over a REQUIRED list")
    print("=" * 78)
    print()

    bad = []
    for rel, why in REQUIRED:
        st, n = check(rel)
        ok = st == "ANCHORED"
        print("  %-34s %6d B  %-46s %s" % (st, n, rel, why))
        if not ok:
            bad.append((rel, st))

    extras = sorted(p for p in HERE.rglob("*.ots")
                    if "package" not in p.parts and "review" not in p.parts
                    and str(p.relative_to(HERE)).replace(chr(92), "/")
                    not in {r + ".ots" for r, _ in REQUIRED}
                    and not any(str(p).endswith(s) for s in SUPERSEDED_SUFFIXES))
    print()
    for p in sorted(HERE.rglob("*.ots*")):
        if any(str(p).endswith(s) for s in SUPERSEDED_SUFFIXES):
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
