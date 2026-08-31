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


def anchored(doc):
    """Does this document's OWN proof bind its current bytes and claim a Bitcoin attestation?

    ⛔ THIS CHECK DID NOT EXIST, AND WITHOUT IT THE WHOLE FILE WAS THEATRE. Two round-4 reviewers
    broke it independently, by different routes:

        append a line to train.py, then sed its digest inside v5 section 3   -> exit 0
        drop in an UNANCHORED synthetic v6 carrying the mutated digests      -> exit 0

    Both work because the table was read out of a MUTABLE FILE IN THE SAME DIRECTORY. Reading the
    protocol rather than restating it removed one hazard and introduced a worse one: whoever can
    change train.py can also change the document that says what train.py should be.

    ⇒ A digest table is authority only if the document carrying it is ANCHORED: the proof exists,
    binds these exact bytes, and carries a Bitcoin attestation. The same three conditions
    anchor_status.py applies -- applied here to the document this file takes its orders from.
    """
    proof = doc.parent / (doc.name + ".ots")
    if not proof.exists():
        return False, "no proof beside it"
    blob = proof.read_bytes()
    if len(blob) < 32:
        return False, "proof too short to be one"
    if hashlib.sha256(doc.read_bytes()).digest() not in blob:
        return False, "its proof does not bind these bytes -- edited after stamping"
    if BITCOIN_TAG not in blob:
        return False, "pending: calendar receipt only, no Bitcoin attestation"
    return True, "anchored"


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
        ok, why = anchored(f)
        if not ok:
            rejected.append((version, f.name, why))
            continue
        found.append((version, f.name, pinned))
    return found, rejected


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    found, rejected = governing(HERE)
    for _v, _name, _why in sorted(rejected, reverse=True):
        print("  " + W + " %-46s NOT AUTHORITY: %s" % (_name, _why))
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
    if _present and version < max(_present):
        raise SystemExit(
            D + " the highest ANCHORED protocol is v%d, but a v%d document is present and is not "
            "authority. Either it is unanchored work in progress -- do not build or publish "
            "against it -- or something is being substituted. This is the exact route a round-4 "
            "reviewer used to make a changed train.py pass." % (version, max(_present)))
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

    bad = []
    for rel, want in pinned:
        f = HERE / rel
        if not f.exists():
            print("  " + D + " %-26s MISSING" % rel)
            bad.append((rel, "missing", want, None))
            continue
        got = hashlib.sha256(f.read_bytes()).hexdigest()
        if got == want:
            print("  ok   %-26s %s" % (rel, got[:16]))
        else:
            print("  " + D + " %-26s %s  committed %s" % (rel, got[:16], want[:16]))
            bad.append((rel, "changed", want, got))

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

    print("  all %d committed file(s) hash to the digests the anchored protocol pins" % len(pinned))
    print()
    print("  " + W + " This says the FILES are unchanged AND that the document pinning them is")
    print("  anchored -- its proof binds its current bytes and carries a Bitcoin attestation.")
    print("  It does NOT say a run obeyed the protocol: nothing here records which pipeline")
    print("  produced any existing run, or when. That is round 4's open finding.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
