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


def governing(here):
    """The HIGHEST protocol version that carries a digest table, and its commitments.

    {D} AN EARLIER VERSION OF THIS FILE NAMED v3 IN A CONSTANT. That is the enumeration defect
    the whole project keeps re-committing: v5 replaces v3 §2, and a constant naming v3 would have
    gone on verifying a superseded table while reporting success. The version is DERIVED from
    what is on disk, and if two versions both carry a table the newer one wins -- which is what
    "replaces §2" means.
    """
    found = []
    for f in sorted(here.glob("PRE-REGISTRATION*.md")):
        m = re.search(r"-v(\d+)-", f.name)
        version = int(m.group(1)) if m else 1
        pinned = commitments(f.read_text(encoding="utf-8"))
        if len(pinned) >= MIN_EXPECTED:
            found.append((version, f.name, pinned))
    if not found:
        return None, None, []
    found.sort()
    return found[-1][0], found[-1][1], found[-1][2]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    version, PROTOCOL, pinned = governing(HERE)
    if PROTOCOL is None:
        raise SystemExit(D + " no protocol document on disk carries a digest table, so nothing "
                         "here is committed to anything.")
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
    print("  " + W + " This says the FILES are unchanged. It does not say the protocol is")
    print("  anchored -- that is anchor_status.py -- and it does not say a run obeyed the")
    print("  protocol, which is what the measurement tools are for.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
