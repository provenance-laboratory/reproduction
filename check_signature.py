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


_REQUIRED_CACHE = {}


def required_fingerprints():
    """The fingerprints of the key(s) in `PUBKEY.asc` -- the only signer this protocol has.

    ⛔⛔ `verify()` ANSWERED *does some key gpg knows make a valid signature* AND WAS READ AS
    *does the protocol's key stand behind this*. `--require` compared the fingerprint, in
    `main()` only; `prepare_anchor.signature_state()` called `verify()` directly and never saw a
    fingerprint at all. A round-13 reviewer generated a second key, imported it and `PUBKEY.asc`
    into one keyring, signed v22 with the second key, and got:

        check_signature.verify(v22)          -> ('ok', 'signed by D59E526AA9CF2A90')
        prepare_anchor.signature_state(v22)  -> ok
        check_signature.py --require B128... -> rejected

    Two answers from one tree about one file, and the gate held the weaker one -- which is the
    shape the empty-`.asc` finding had a round earlier, one level up: not *is there a signature*
    but *whose*.

    ⇒ `ok` MEANS SIGNED BY THE PROTOCOL'S KEY, in `verify()` itself, so every caller gets the
    same answer. The required set is READ FROM `PUBKEY.asc` -- the file v21 pins -- rather than
    typed here, so it cannot drift from the key that ships; `--require` remains as a cross-check
    against a fingerprint obtained from somewhere that is not us. Returns None when gpg cannot
    read the key file, and `verify()` then fails closed: a signature that cannot be attributed
    to the protocol's key is not `ok`.
    """
    pub = HERE / "PUBKEY.asc"
    try:
        _k = (pub.stat().st_mtime_ns, pub.stat().st_size)
    except OSError:
        return None
    if _k in _REQUIRED_CACHE:
        return _REQUIRED_CACHE[_k]
    try:
        r = subprocess.run(["gpg", "--batch", "--with-colons", "--import-options", "show-only",
                            "--import", pub.name], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", cwd=str(HERE))
    except FileNotFoundError:
        return None
    out = set()
    for line in (r.stdout or "").splitlines():
        parts = line.split(":")
        # ⛔ ROUND 14: THIS STOPPED AT THE PRIMARY, so a signature by a SIGNING SUBKEY of the
        # protocol's own key -- the normal GnuPG hygiene once a key is rotated to subkeys -- read as
        # WRONG KEY: gpg's VALIDSIG names the subkey first and the primary last, and this compared
        # the first against a set holding only the primary. A reviewer made such a key and got
        # "WRONG KEY: a valid signature by <subkey>, and the protocol's key is <primary>" for a
        # signature that IS the protocol's key. ⇒ Every fingerprint in the key block is required:
        # the primary and each subkey it certifies. A second primary appended to the file is
        # still refused where it matters -- see `verify`, which also accepts the primary that
        # VALIDSIG reports for a subkey signature, so the two routes agree.
        if parts and parts[0] == "fpr" and len(parts) > 9 and parts[9]:
            out.add(parts[9].upper())
    _REQUIRED_CACHE[_k] = out or None
    return _REQUIRED_CACHE[_k]


def verify(doc):
    """(state, detail, fingerprint) for one document. States: ok / UNSIGNED / BAD.

    `ok` means: gpg reports GOODSIG and VALIDSIG, AND the signing key's fingerprint is the
    primary fingerprint of `PUBKEY.asc`. A valid signature by any other key is BAD (WRONG KEY):
    valid for the mathematics, not for this protocol -- see `required_fingerprints`.
    """
    sig = doc.with_suffix(doc.suffix + ".asc")
    if not sig.exists():
        return "UNSIGNED", "no detached signature alongside it", ""
    try:
        r = subprocess.run(["gpg", "--status-fd", "1", "--verify", str(sig), str(doc)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return "BAD", "gpg is not available, so the signature cannot be checked", ""
    # ⛔ THIS PASSED ON THE AUTHOR'S MACHINE AND COULD NOT PASS ANYWHERE ELSE. The key lived in
    # the author's keyring and no public key shipped, so every reproducer got NO_PUBKEY on every
    # document -- a check that returns the same answer for a good signature and a forged one,
    # for everyone but the one person who does not need it. Both round-6 reviewers reported it.
    # PUBKEY.asc ships now, and verification falls back to a THROWAWAY KEYRING containing only it.
    #
    # ⚠ THIS MAKES THE MATHEMATICS CHECKABLE, NOT THE IDENTITY. A signature verified against a
    # key we also shipped says these bytes were signed by whoever holds that key -- it cannot say
    # who that is. The fingerprint still has to be confirmed through a channel that is not us.
    if "[GNUPG:] NO_PUBKEY" in (r.stdout or ""):
        pub = HERE / "PUBKEY.asc"
        if pub.exists():
            import os as _os
            import shutil as _sh
            import tempfile as _tf
            # ⚠ A RELATIVE HOMEDIR, RUN FROM HERE. The gpg on this platform is an MSYS
            # build that resolves a Windows absolute path against its own POSIX cwd, so an
            # absolute --homedir produced "keyblock resource ...\\C:...: No such file" and
            # the fallback silently did nothing. The bug was in the fallback, not in the key.
            home = _tf.mkdtemp(prefix=".sigchk-", dir=str(HERE))
            rel = _os.path.basename(home)
            try:
                subprocess.run(["gpg", "--homedir", rel, "--batch", "--quiet", "--import",
                                pub.name], capture_output=True, text=True, cwd=str(HERE))
                # ⚠ RELATIVE TO HERE, WHICH IS WHERE THE HOMEDIR IS -- and `sig.name` was
                # relative to HERE too, so a document in a SANDBOX was verified against the
                # file of the same name in the real tree. A control that mutates a copy and
                # asks this function about it would have been answered about the original.
                def _relp(p):
                    try:
                        return _os.path.relpath(str(p), str(HERE))
                    except ValueError:                                   # another drive
                        return str(p)
                r = subprocess.run(["gpg", "--homedir", rel, "--batch", "--status-fd", "1",
                                    "--verify", _relp(sig), _relp(doc)],
                                   capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", cwd=str(HERE))
            finally:
                _sh.rmtree(home, ignore_errors=True)
    out = (r.stdout or "") + (r.stderr or "")
    fpr, primary = "", ""
    for line in (r.stdout or "").splitlines():
        if line.startswith("[GNUPG:] VALIDSIG"):
            parts = line.split()
            if len(parts) > 2:
                fpr = parts[2]
            # VALIDSIG's last field is the PRIMARY fingerprint of whatever key signed -- for a
            # subkey signature, the key the subkey belongs to. gpg reports it on the same line.
            if len(parts) > 11:
                primary = parts[11]
    # ⛔ THE STATUS LINE, NOT THE PROSE. `gpg`'s human output says "Good signature" for a signature
    # by an untrusted key too, and its exit code is 0 for an expired one. The machine-readable
    # status protocol is the only part of gpg's output meant to be parsed.
    if "[GNUPG:] GOODSIG" not in (r.stdout or ""):
        why = "no GOODSIG in gpg's status output"
        for k in ("BADSIG", "EXPKEYSIG", "REVKEYSIG", "ERRSIG", "NO_PUBKEY"):
            if "[GNUPG:] " + k in (r.stdout or ""):
                why = k
        return "BAD", why + " -- " + out.strip().splitlines()[0][:60] if out.strip() else why, fpr
    _req = required_fingerprints()
    if not _req:
        return "BAD", ("GOODSIG by %s, but PUBKEY.asc could not be read here, so the signature "
                       "cannot be attributed to the protocol's key" % (fpr[-16:] or "?")), fpr
    if fpr.upper() not in _req and primary.upper() not in _req:
        return "BAD", ("WRONG KEY: a valid signature by %s, and the protocol's key is %s. Valid "
                       "for the mathematics, not for this protocol"
                       % (fpr[-16:] or "?", ", ".join(k[-16:] for k in sorted(_req)))), fpr
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
    unsigned_names = []
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
            unsigned_names.append(doc.name)
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
        # ⛔ THIS HARD-CODED "They are anchored", AND IT WAS FALSE OF THE ONLY DOCUMENT IT
        # COVERED. The one unsigned document here is v18, which has no proof either -- so neither
        # WHO nor WHEN was established, and the sentence offered a reassurance about the single
        # case a reviewer is being asked to judge. Everything else in this tool is careful: it
        # prints a fingerprint and then says a fingerprint is not an identity. This is the one
        # place it asserted instead of checking.
        _anchored = [n for n in unsigned_names if (HERE / (n + ".ots")).is_file()]
        _neither = [n for n in unsigned_names if n not in _anchored]
        print("  " + W + " %d document(s) carry no signature: WHO wrote them is not established."
              % unsigned)
        if _anchored:
            print("      %d of those ARE anchored, so WHEN they existed is: %s"
                  % (len(_anchored), ", ".join(_anchored[:3])))
        if _neither:
            print("      " + D + " %d carry NEITHER a signature NOR a proof, so neither WHO nor "
                  "WHEN is established: %s" % (len(_neither), ", ".join(_neither[:3])))
        print("  That is a publication-gate failure and deliberately not a review-build failure.")
        return 2
    print("  ok  every protocol document is signed, and by the required key.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
