"""Detached signatures over the protocol documents. An anchor answers WHEN; this answers WHO.

⛔ WHY THIS EXISTS. Every protocol document in this project is timestamped, and until now that was
the whole of its authenticity story. A round-5 reviewer stated the gap exactly: **stamping is free,
public and unilateral.** Anyone who can write to this directory can compose their own successor
document, stamp it, wait two hours for a calendar to anchor it, and hold a proof indistinguishable
from ours. What an OpenTimestamps proof establishes is that these bytes existed by a certain block.
It says nothing whatever about who wrote them.

⇒ So the anchor and the signature answer different questions and neither substitutes for the other:

    the anchor      these bytes existed no later than Bitcoin block N          WHEN
    the signature   this key asserts these bytes                               WHO
    together        this key asserted these bytes before block N               WHEN + WHO

⚠️ AND THE SIGNATURE ALONE WOULD BE WEAKER THAN THE PAIR, which is why this does not replace
`ots_verify.py`. A signature can be made at any time and backdated freely -- signing is as
unilateral as stamping. It is the anchor that fixes the signature in time. A reader who checks only
one of the two learns half of what the pair establishes.

⚠️ WHAT A PASS HERE DOES NOT MEAN. It means a key made this signature over these bytes. Whether
that key belongs to whom you think is a question about key distribution, not about this file, and
this tool cannot answer it -- it prints the fingerprint so a reader can check it against a channel
that does not come from us. `--require` names the fingerprint a build must see, so that a valid
signature by SOME OTHER key is a failure rather than a pass.

    python check_signature.py                     report on every protocol document
    python check_signature.py --require <fpr>     fail unless that key signed them
"""
import io
import pathlib
import subprocess
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent


def _documents():
    """Every protocol document PRESENT, derived from the tree -- never a list kept by hand.

    ⛔ THE ENUMERATION DEFECT IS THE ONE THIS PROJECT KEEPS MAKING, twelve times and counting, and
    a hand-kept list here would go stale at exactly the moment a new version was written -- which
    is the moment the signature check matters. So this globs, and an unsigned document is a
    reported failure rather than a silent omission.
    """
    return sorted(HERE.glob("PRE-REGISTRATION*.md"))


def verify(doc):
    """(state, detail, fingerprint) for one document. States: ok / UNSIGNED / BAD."""
    sig = doc.with_suffix(doc.suffix + ".asc")
    if not sig.exists():
        return "UNSIGNED", "no detached signature alongside it", ""
    try:
        r = subprocess.run(["gpg", "--status-fd", "1", "--verify", str(sig), str(doc)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return "BAD", "gpg is not available, so the signature cannot be checked", ""
    out = (r.stdout or "") + (r.stderr or "")
    fpr = ""
    for line in (r.stdout or "").splitlines():
        if line.startswith("[GNUPG:] VALIDSIG"):
            parts = line.split()
            if len(parts) > 2:
                fpr = parts[2]
    # ⛔ THE STATUS LINE, NOT THE PROSE. `gpg`'s human output says "Good signature" for a signature
    # by an untrusted key too, and its exit code is 0 for an expired one. The machine-readable
    # status protocol is the only part of gpg's output meant to be parsed.
    if "[GNUPG:] GOODSIG" not in (r.stdout or ""):
        why = "no GOODSIG in gpg's status output"
        for k in ("BADSIG", "EXPKEYSIG", "REVKEYSIG", "ERRSIG", "NO_PUBKEY"):
            if "[GNUPG:] " + k in (r.stdout or ""):
                why = k
        return "BAD", why + " -- " + out.strip().splitlines()[0][:60] if out.strip() else why, fpr
    return "ok", "signed by %s" % (fpr[-16:] or "?"), fpr


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    require = ""
    if "--require" in sys.argv:
        require = sys.argv[sys.argv.index("--require") + 1].replace(" ", "").upper()

    print("=" * 78)
    print("  SIGNATURES — an anchor says WHEN, a signature says WHO")
    print("=" * 78)
    print()

    docs = _documents()
    if not docs:
        print("  " + D + " no protocol documents found at all. Nothing to check is not a pass.")
        return 1

    bad = unsigned = 0
    seen = set()
    for doc in docs:
        state, detail, fpr = verify(doc)
        if fpr:
            seen.add(fpr.upper())
        mark = {"ok": "ok ", "UNSIGNED": W, "BAD": D}[state]
        print("  %s  %-44s %s" % (mark, doc.name, detail))
        if state == "BAD":
            bad += 1
        elif state == "UNSIGNED":
            unsigned += 1
        if require and state == "ok" and fpr.upper() != require:
            print("      " + D + " signed, but by %s -- NOT the required key. A valid signature by"
                  % fpr[-16:])
            print("      the wrong key is a failure, not a pass.")
            bad += 1

    print()
    if seen:
        print("  key(s) seen: %s" % ", ".join(sorted(seen)))
        print("  " + W + " a fingerprint printed by this tool is not an identity. Check it against")
        print("  a channel that does not come from us before it means anything.")
    print()
    if bad:
        print("  " + D + " %d document(s) FAILED signature verification." % bad)
        return 1
    if unsigned:
        print("  " + W + " %d document(s) carry no signature. They are anchored, so WHEN they"
              % unsigned)
        print("  existed is established; WHO wrote them is not. That is a publication-gate")
        print("  failure and deliberately not a review-build failure.")
        return 2
    print("  ok  every protocol document is signed, and by the required key.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
