"""The newest protocol version that is not yet in force, and whether it is ready to be.

⛔ WHY THIS IS NOT A README. Signing and anchoring are the operator's, not this tree's: the key is
theirs and an OpenTimestamps stamp is an outward act. So the last step is handed over rather than
performed -- and a hand-written instruction file is exactly the thing that goes stale, which is
the defect this whole project keeps paying for. This CHECKS the preconditions and then prints the
commands; if a precondition fails it refuses and says which, so the printed commands are never
advice about a state that no longer holds.

⚠️ ORDER MATTERS AND IT IS THE EASY THING TO GET WRONG. A protocol version pins the digests of the
tools the study runs, so it must be signed AFTER the tooling is final. Signing it earlier freezes
a digest of a file that is about to change, and every later run then reports a tampered tree --
which is the correct report, arrived at by a mistake in sequencing rather than in intent.
"""
import hashlib
import io
import pathlib
import re
import sys

# ⚠️ NOT AT IMPORT TIME. This module rebound `sys.stdout` as soon as it was imported, which
# detaches the stream of whatever imported it -- `control_identity.py` did exactly this in the
# census tree this round and made its importer raise *I/O operation on closed file* on the next
# print. A module that reconfigures a global on behalf of its importer is a module that breaks one.
# ⇒ It happens in `main()` now, so `pinned_digests()` can be READ by another tool instead of
# being copied into it -- which is how the packet builder learns what this document pins.
D, W, OK, AR = chr(0x26D4), chr(0x26A0), "ok  ", chr(0x21D2)
NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent
PATTERN = re.compile(r"^PRE-REGISTRATION-v(\d+)-CONFIRMATORY\.md$")


def versions():
    out = {}
    for p in HERE.glob("PRE-REGISTRATION-v*-CONFIRMATORY.md"):
        m = PATTERN.match(p.name)
        if m:
            out[int(m.group(1))] = p
    return out


_SIG_CACHE = {}
_SIG_DETAIL = {}       # {str(doc): the detail check_signature gave} -- for `_why`, never a verdict


def signature_state(doc):
    """"ok" / "absent" / "bad" / "unverifiable" for this document's detached signature.

    ⛔⛔ THIS WAS `is_file()`, AND A ZERO-BYTE FILE MOVED A DOCUMENT'S CLASSIFICATION. The
    docstring here used to argue that existence was enough, *because the question it asks is
    whether an edit could invalidate a signature, not whether one verifies*. That argument is
    sound for the WRITE GATE and it is not sound for the EXEMPTION, and both were reading this
    one function. A round-12 reviewer created an empty `.asc` beside v21, edited a tool, updated
    v21's pin, and got:

        build_review_packet.py ... re-pinned at these exact bytes by SIGNED v21
        READY

    -- turning THE UNSIGNED DRAFT IN HAND into SIGNED v21, WHICH IS WAITING FOR ITS PROOF, on a
    file with nothing in it. `check_signature.py`, sitting in the same directory, rejects that
    same file correctly. **Two definitions of "signed" in one tree, and the gate held the weaker
    one.**

    ⇒ THE STATE IS THE VERIFIED STATE, AND IT IS THREE-VALUED BECAUSE THE TWO CALLERS FAIL IN
    OPPOSITE DIRECTIONS. A boolean cannot serve both: the exemption must treat "cannot tell" as
    NOT signed (or an absent `gpg` grants the exemption), and the write gate must treat "cannot
    tell" as signed (or an absent `gpg` opens the write path over somebody's signature). Those
    are contradictory readings of one False, which is why a bare predicate was the wrong shape
    and not merely the wrong test. Every caller now names the state it requires.

    ⚠️ VERIFICATION IS DELEGATED TO `check_signature.verify`, which is the tree's one
    implementation of what a good signature is -- throwaway keyring, `PUBKEY.asc`, the GNUPG
    status protocol rather than the human prose. A second copy here would be a second definition,
    which is the defect this is repairing.
    """
    _sig = doc.parent / (doc.name + ".asc")
    if not _sig.is_file():
        return "absent"
    # ⚠ MEMOISED ON THE BYTES, NOT ON THE PATH. `gpg` is a process, `in_force()` is evaluated
    # across every version several times per run, and an unkeyed cache would answer for a file
    # that changed under it -- which is the whole class of defect this tool reports. The key is
    # what a change would move.
    # ⛔ AND "THE BYTES" WAS mtime AND size, WHICH A BYTE-FLIP THAT PRESERVES BOTH DOES NOT
    # MOVE. A round-13 reviewer cached `ok`, swapped in a BAD signature of equal length with
    # the mtime forged, and read `ok` back from the same process. Narrow -- a same-process
    # caller, after the state was cached -- and exactly the gap the sentence above claims not
    # to have. The key is the content digest now, which is what "the bytes" means.
    try:
        _k = (str(doc), hashlib.sha256(doc.read_bytes()).hexdigest(),
              hashlib.sha256(_sig.read_bytes()).hexdigest())
    except OSError:                                                       # pragma: no cover
        _k = None
    if _k is not None and _k in _SIG_CACHE:
        return _SIG_CACHE[_k]
    try:
        import check_signature as _CS
        _st, _why, _f = _CS.verify(doc)
    except Exception:                                                     # noqa: BLE001
        return "unverifiable"
    _SIG_DETAIL[str(doc)] = _why or ""
    if _st == "ok":
        _out = "ok"
    elif _st == "UNSIGNED":
        _out = "absent"
    else:
        # `gpg` missing is NOT a bad signature; it is no evidence either way, and the difference
        # decides which way each caller fails.
        _out = "unverifiable" if "gpg is not available" in (_why or "") else "bad"
    if _k is not None:
        _SIG_CACHE[_k] = _out
    return _out


def signed(doc):
    """Does a detached signature beside this document VERIFY? Fails closed -- see
    `signature_state`. An unreadable, forged or uncheckable signature is not a signature here."""
    return signature_state(doc) == "ok"


def stamped(doc):
    """Has ANY proof in this folder committed to these exact bytes? Commitment, not anchoring.

    ⛔⛔ THIS WAS `<doc>.ots` EXISTS, WHICH IS A STATEMENT ABOUT ONE FILENAME. A round-13
    reviewer took v20 -- real signature, real proof -- deleted the `.asc`, renamed the proof to
    `v20.md.ots.superseded-attack`, edited a tool and ran `--repin`:

        signature_state = absent   stamped = False   anchored = False   writable = True

    The proof was not destroyed. It was left in the directory under the exact historical-proof
    convention this study uses for retired proofs, and `writable()` -- whose own docstring says
    *nothing has ever committed these bytes* -- read the filename and not the folder. Round 12
    closed *delete the signature*; this is *rename the proof*, and both are the same claim: a
    timestamp cannot be un-taken by a filesystem operation.

    ⇒ PROJECTED OVER EVERY PROOF-SHAPED FILE BESIDE THE DOCUMENT, whatever it is called. A file
    whose OpenTimestamps header commits to sha256(doc) is a commitment to these bytes, current
    or superseded, and the document is history. The header parse is `ots_verify.commits`, the
    one place this tree reads a proof; nothing here re-implements it.
    """
    try:
        import ots_verify as _OTS
    except Exception:                                                     # noqa: BLE001
        # a folder whose proof reader cannot load is a folder this cannot clear for writing
        return True
    # ⛔ ROUND 14: "EVERY PROOF-SHAPED FILE, WHATEVER IT IS CALLED" WAS `".ots" in name`, a filename
    # test one convention over from the one round 13 closed. A reviewer renamed a real proof to
    # `...md.timestamp-retired-20260904` and `stamped()` said False with the commitment still in the
    # directory. ⇒ EVERY SIBLING FILE IS READ: the first bytes decide whether it is a proof (the
    # OpenTimestamps magic), and the header parse decides whether it commits to these bytes. A
    # name decides nothing.
    _bytes = doc.read_bytes()
    for _p in sorted(doc.parent.iterdir()):
        if not _p.is_file():
            continue
        try:
            with open(_p, "rb") as _fh:
                if _fh.read(len(_OTS.MAGIC)) != _OTS.MAGIC:
                    continue
            if _OTS.commits(_p.read_bytes(), _bytes):
                return True
        except OSError:                                                   # pragma: no cover
            return True
    return False


def anchored(doc):
    """Does that proof carry a BITCOIN ATTESTATION, or is it only a calendar receipt?

    ⛔⛔ `in_force` WAS `signed() and stamped()` -- TWO `is_file()` CALLS -- SO THIS TOOL SAID
    **ANCHORED** ON THE STRENGTH OF A FILE EXISTING. In the same tree, in the same minute,
    `anchor_status.py` reported all four proofs `pending (calendar only)` under its own printed
    rule that no document may say ANCHORED until that list is empty, and `check_commitments.py`
    reported `NOT AUTHORITY [PENDING]: carries no Bitcoin attestation`. **The START HERE command
    printed the strong word on the weak evidence**, and the letter that shipped with it drew the
    distinction correctly one paragraph away.

    ⇒ A PROOF IS PARSED, NOT COUNTED. An OpenTimestamps file that names no Bitcoin block is a
    receipt saying a calendar saw the digest; it becomes an anchor when a block carries it. The
    parse is deliberately shallow and conservative -- it looks for the attestation marker the
    format writes for Bitcoin -- and anything it cannot read is NOT anchored, because the failure
    it exists to prevent is the strong word on weak evidence.
    """
    p = doc.parent / (doc.name + ".ots")
    if not p.is_file():
        return False
    try:
        import ots_verify as _OTS          # the parser anchor_status.py already uses
        ok, _why, _found = _OTS.verify(p.read_bytes(), doc.read_bytes())
        return bool(ok)
    except Exception:                                                     # noqa: BLE001
        # ⚠ A PROOF THIS CANNOT PARSE IS NOT AN ANCHOR. Failing closed here is the whole point:
        # the defect being repaired is a tool saying ANCHORED on evidence it never read.
        return False


def _proof_state(doc):
    """('anchored'|'pending'|'tampered'|'absent', why) for `<doc>.ots`, by parsing it."""
    p = doc.parent / (doc.name + ".ots")
    if not p.is_file():
        return "absent", "no proof beside it"
    try:
        import ots_verify as _OTS
        ok, why, found = _OTS.verify(p.read_bytes(), doc.read_bytes())
    except Exception as e:                                                # noqa: BLE001
        return "tampered", "unreadable: %s" % e
    if ok:
        return "anchored", why
    if found and all(k != "bitcoin" for k, _v, _r in found) and any(k == "pending" for k, _v, _r in found):
        return "pending", why
    return "tampered", why


def attested_blocks(doc):
    """[(height, merkle root)] this document's proof attests, or [] if it attests none."""
    p = doc.parent / (doc.name + ".ots")
    if not p.is_file():
        return []
    try:
        import ots_verify as _OTS
        ok, _why, found = _OTS.verify(p.read_bytes(), doc.read_bytes())
    except Exception:                                                     # noqa: BLE001
        return []
    if not ok:
        return []
    return [(int(x[1]), str(x[2]).lower()) for x in (found or []) if x and x[0] == "bitcoin"]


CONFLICTING_FACTS = {}          # {height: {root: [version, ...]}} -- see `_committed_heights`


def _version_of(doc):
    """The version number of this document, or None if it is not one of the versioned series."""
    for _v, _d in versions().items():
        try:
            if _d.resolve() == pathlib.Path(doc).resolve():
                return _v
        except OSError:                                                   # pragma: no cover
            continue
    return None


def _committed_heights(after=None):
    """{height: root} committed as FACTS by signed+anchored versions STRICTLY NEWER than `after`.

    A height here was written into a document that is signed and whose own proof fixes when that
    text existed, so it cannot be introduced by anyone editing this tree afterwards.

    ⛔⛔ AND `setdefault` LET THE FIRST VERSION TO NAME A HEIGHT WIN IT FOREVER. If two
    anchored versions ever supply DIFFERENT roots for one height, that is two documents
    contradicting each other about what Bitcoin contains -- the single loudest thing this tree
    could discover -- and the map answered with whichever was read first and said nothing.
    `check_commitments.py` detects the contradiction separately, which made this defence in depth
    on paper and a silent wrong answer in this function.

    ⇒ A CONTRADICTED HEIGHT COMMITS NOTHING. It is dropped from the map, so it confirms no
    document, and it is recorded in `CONFLICTING_FACTS` for `main()` to refuse over. Fail closed
    where the evidence disagrees with itself, and do not wait for another tool to notice.
    """
    out, src = {}, {}
    CONFLICTING_FACTS.clear()
    try:
        import check_commitments as _CC
    except Exception:                                                     # noqa: BLE001
        return out
    # ⚠️ ONLY DOCUMENTS `governing()` ACCEPTS MAY SUPPLY FACTS. This filtered on signed and
    # anchored and applied none of the acceptance checks the authority rule applies -- a
    # RELABELLED, UNVERSIONED or NO-TABLE document with a genuine signature and a genuine proof
    # would have committed heights here that `check_commitments.py` refuses to let govern. The
    # signature requirement is what stood between that and a forgery, and a lock that is only
    # as good as one keyring is one lock. Two round-13 reviewers named it; sharing the verdict
    # makes this defence in depth rather than single-point. A tree `governing()` refuses outright
    # commits nothing: fail closed where the authority rule already has.
    try:
        _accepted = {_n for _v_, _n, _p in _CC.governing(HERE, _raise_on_blocking=False)[0]}
    except SystemExit:
        return out
    except Exception:                                                     # noqa: BLE001
        return out
    for _v, _d in sorted(versions().items()):
        if after is not None and _v <= after:
            continue
        if _d.name not in _accepted:
            continue
        if not (signed(_d) and anchored(_d)):
            continue
        try:
            _facts = _CC.anchor_facts(_d.read_text(encoding="utf-8")).items()
        except Exception:                                                 # noqa: BLE001
            continue
        for _h, _r in _facts:
            _h, _r = int(_h), str(_r).lower()
            src.setdefault(_h, {}).setdefault(_r, []).append(_v)
            out[_h] = _r
    for _h, _roots in src.items():
        if len(_roots) > 1:
            CONFLICTING_FACTS[_h] = {_r: sorted(_vs) for _r, _vs in _roots.items()}
            out.pop(_h, None)
    return out


def confirmed(doc):
    """Is this document's anchor CONFIRMED by a committed fact, or only PROVISIONAL?

    ⛔⛔ `anchored()` PROVED A PROOF IS SELF-CONSISTENT WITH `ANCHORS.json`, AND NOTHING PROVES
    `ANCHORS.json`. Two round-11 reviewers took the same ground from opposite sides. One flipped a
    byte in a valid proof, recomputed the root, wrote that root into `ANCHORS.json` at the same
    height, and got `verify -> True, anchored() -> True`. The other forged a 97-byte proof naming
    a block that was not pinned at all and APPENDED one row:

        BEFORE  STRUCTURAL only: block(s) [966666] ... NOT PINNED.        anchored(): False
        AFTER   ANCHORED in Bitcoin block(s) [966666] ...                 anchored(): True
                authority PRE-REGISTRATION-v20...md, composed over 17 anchored version(s)

    **The monotonic rule makes that permitted by design** -- additions are growth and growth is
    not a violation -- and `check_commitments.py` itself reports `ANCHORS.json` as RETIRED by v10
    and committed by nothing. An uncommitted file was the root of trust for the whole tree.

    ⇒ SPLIT THE WORD, WHICH IS WHAT THE EVIDENCE ALREADY SUPPORTS. A block named in the §2d
    anchor-fact table of a version that is itself signed and anchored is CONFIRMED: it was written
    down before anyone could choose it, and the monotonic rule cannot add to it. A block known
    only to `ANCHORS.json` is PROVISIONAL: real, probably, and asserted by a file this tree does
    not commit.

    ⚠️ A NEW VERSION IS NECESSARILY PROVISIONAL AT FIRST -- its block is newer than any
    committed table -- and that is not a defect but the cost of the property. It becomes confirmed
    when a later version commits its height, which is why the tables exist. Authority therefore
    lags anchoring by one committed table, and `in_force` is where that must bite, because that is
    the predicate deciding which commitments govern.

    ⛔⛔ AND THE ORDERING WAS IN THE PROSE AND NOT IN THE CODE. Every sentence above says a
    LATER version confirms an EARLIER one -- *it becomes confirmed when a later version commits
    its height* -- and the implementation walked ALL signed+anchored versions, `doc` among them.
    A document whose own §2d table names the block its own proof attests therefore confirmed
    itself, and `in_force()` -- the predicate that decides which commitments govern this tree --
    would have followed. No such document exists here: v2-v17 are confirmed by later facts and
    v18-v20 are provisional, so this is a missing invariant rather than a demonstrated forgery.
    An invariant that holds because nobody has written the document that breaks it is not an
    invariant; it is a coincidence with a deadline.

    ⇒ THE CONFIRMING FACT MUST COME FROM A VERSION STRICTLY NEWER THAN THIS ONE. That is the
    whole content of "written down before anyone could choose it": a table inside `doc` was
    written by whoever wrote `doc`, at the same moment, with the same freedom. Only a later
    document, separately signed and separately anchored, adds anything.

    ⚠️ `committed` IS NO LONGER AN ARGUMENT. It was a precomputed whole-tree map, and a
    whole-tree map is exactly what this may not use -- passing one in would reinstate the defect
    from the outside, silently, at any call site. The map is derived here from `doc`.
    """
    blocks = attested_blocks(doc)
    if not blocks:
        return False
    known = _committed_heights(after=_version_of(doc))
    return any(known.get(h) == r for h, r in blocks)


def in_force(doc):
    """A version is in force when it is signed AND its proof carries a Bitcoin attestation.

    ⚠️ AND BEING IN FORCE MUST NOT SKIP THE PIN CHECK. `main()` returned 0 the moment this was
    true, so on the shipped tree every repair round 9 made -- the imported grammar, `_NEAR_PIN`,
    `_inside()`, the declared table -- was dead code that never executed. **A document in force
    whose pins are broken is exactly the tampered tree this gate exists to report**, and it was
    the one state the gate declined to look at.

    ⛔⛔ AND `anchored()` RESTS ON A FILE NOTHING COMMITS. See `confirmed()`: two round-11
    reviewers moved authority by editing `ANCHORS.json`, which `check_commitments.py` reports in
    the same run as RETIRED by v10 and pinned by no version. One substituted a merkle root for an
    existing height; the other appended a row for a block that was never pinned. Both got
    `anchored() -> True` and `in_force() -> True`, and the second reached *authority ... composed
    over 17 anchored version(s)*.

    ⇒ THIS PREDICATE MOVES AUTHORITY AND DECIDES WHICH TABLE GOVERNS, so it takes the CONFIRMED
    anchor: a block a signed-and-anchored version wrote into its own fact table before anyone
    could choose it. `anchor_status.py` may print the provisional state -- that is reporting, not
    authority -- and this may not.

    ⚠️ THE COST, STATED: the newest anchored version is always provisional until a later
    version commits its height, so authority lags anchoring by one document. v18 and v19 are in
    exactly that position today: anchored in blocks 966979 and 966981, which no committed table
    names. That is not a regression introduced here -- it is the true state of the evidence, which
    the previous rule reported as authority. The repair is one document: the next version commits
    those two heights, and they become confirmed the moment its own proof anchors.
    """
    return signed(doc) and confirmed(doc)


def next_version(vs=None):
    """(n, doc) for the version this tool would prepare: the LOWEST not yet in force.

    ⚠️ EXPORTED BECAUSE THE SUITE HAD ITS OWN COPY. `test_controls.py` built every attack
    against `max(versions())` while this tool prepared the lowest waiting one, and the moment
    round 9 split v18 the two disagreed: the attacks edited v19 and the tool read v18, so three
    of them broke and two crashed. A control aimed at a document the tool is not reading is not
    a control, and the way to be sure is for both to call one function.
    """
    vs = versions() if vs is None else vs
    if not vs:
        return None, None
    # ⚠️ PREPARATION IS ABOUT SIGNATURE AND PROOF; AUTHORITY IS ABOUT CONFIRMATION. Since
    # `in_force` became `signed and confirmed`, the lowest version not in force is the oldest one
    # whose height no committed table names yet -- and there is nothing to PREPARE about it: it
    # is signed, it is stamped, and what it waits for is a successor. The version to prepare is
    # the lowest that still lacks a signature or a proof.
    waiting = sorted(v for v in vs if not (signed(vs[v]) and anchored(vs[v])))
    n = waiting[0] if waiting else max(vs)
    return n, vs[n]


def declaration_required(doc):
    """Must this document carry its count and membership declarations? Unless it is ANCHORED.

    ⛔⛔ THIS WAS `writable()`, WHICH IS `not signed()`, AND THE STATED REASON WAS ANCHORING.
    The justification written beside it is *an anchored document cannot be edited without breaking
    its proof, so the same question there is answered by a different control* -- and the predicate
    implements *not yet signed*. Those come apart in exactly the state this folder lives in: v20
    is SIGNED, UNANCHORED and editable, so deleting its count declaration produced
    `pinned_digests -> (3, 3)` and no refusal at all.
    """
    return not anchored(doc)


def writable(doc):
    """May `--repin` rewrite this document's bytes? Only while nothing has signed them.

    ⛔⛔ `--repin` WAS GATED ON `in_force()`, WHICH IMPLEMENTS *not yet stamped* AND NOT *not yet
    signed*. The printed sequence is gpg, then `_ots_stamp.py`, then `_ots_upgrade.py` -- so
    BETWEEN STEP 1 AND STEP 2 a document has a `.asc` and no `.ots`, `in_force()` is False, and
    the write path was open. A round-8 reviewer created a signature for v18, touched `train.py`,
    and ran it:

        ⚠ v18 is NOT in force: no proof
        ⛔ v18 pins 29 file digest(s); 28 hold against the files here
           ok   re-pinned train.py  ebd6153278... -> c389a0e785...
           ok   PRE-REGISTRATION-v18-CONFIRMATORY.md re-pinned. Run this again to confirm, THEN sign.

    It rewrote bytes a detached signature already covered, then told the operator to sign. The
    second run reported 29 hold / READY, with a signature on disk that no longer verifies.

    ⇒ The comment under the write branch said *the same edit to a signed version is forgery*. The
    gate did not implement that sentence; this function is that sentence. A signature is the point
    after which the bytes are somebody's word, whether or not a calendar has seen them yet.

    ⛔⛔ AND `not signed(doc)` MEANT *THERE IS NO .asc FILE NOW*, WHICH IS A STATEMENT ABOUT
    THE PRESENT AND NOT ABOUT THE HISTORY. A round-12 reviewer took v20 -- real signature, real
    OTS proof -- deleted ONLY the `.asc`, left the proof in place, edited a tool, and ran
    `--repin`. It returned 0 and rewrote v20's commitments:

        signed = False   stamped = True   anchored = False   writable = True

    The proof did not stop it. Afterwards the old `.ots` is a genuine timestamp over bytes that
    no longer exist, which is worse than no timestamp: it is evidence pointing at a document
    nobody can produce. **A signature can be deleted by whoever can edit this folder; a timestamp
    cannot be un-taken.**

    ⇒ WRITABLE MEANS NOTHING HAS EVER COMMITTED THESE BYTES, and the two committals are a
    verified signature and a timestamp proof. A stamped-but-unsigned document is history, not a
    draft. And the signature side reads "absent" rather than "not ok": a signature that is
    present but BAD or UNCHECKABLE blocks the write, because the one thing it certainly is not is
    absent, and an operator without `gpg` must not acquire a write path by not having it.
    """
    return signature_state(doc) == "absent" and not stamped(doc)


# The commitments live in fenced blocks under "## 3.". That is a STRUCTURE, and it is what this
# reads. Two shapes are commitments, and they are told apart by their KEY rather than by the
# heading above them:
#
#     a FILE PIN      a path-shaped name (it carries a dot or a slash) and a 64-hex digest
#     an ANCHOR FACT  a bare block height and a 64-hex merkle root
#
# Anything else carrying a 64-hex inside a commitment block is a third shape nobody declared, and
# this refuses rather than guessing which of the two it was meant to be.
#
# ⚠️ WHAT A ROW IS, IS NOT DECIDED HERE. It is decided by `check_commitments.py` and imported.
# ⛔⛔ THERE WERE TWO DIGEST GRAMMARS IN THIS TREE AND THIS WAS THE SOFTER ONE. Both halves
# of the pair above were `[0-9a-f]` -- lower case only -- while `check_commitments.py`, which is
# the authority on what these documents commit, has matched `[0-9a-fA-F]` since the round that
# found a whole table parsing as zero commitments because it was written in upper case.
#
# The two defects COMPOSED, and that is what made it a signing blocker rather than an annoyance:
#
#     the row parser missed an upper-case pin   -> the file is not checked
#     the completeness scan missed it TOO       -> and nothing calls the digest unconsumed
#
# So an upper-cased digest did not become a stray, a malformed row, or a refusal. It became
# *nothing*: `*28 pins; 28 hold ... READY` on a table of 29, with the pinned file free to change.
# That is `PUBKEY.asc` again -- the same silent-drop shape as the extension allowlist recorded
# below -- reproduced inside the fix that closed it, by a character class.
#
# ⚠️ AND A SECOND SHAPE THE LOCAL PAIR COULD NOT SEE. `_ANY_DIGEST` had no boundary guards, so
# it found a digest inside a longer hex run; `_DIGEST_TOKEN` has them, which is stricter and would
# have HIDDEN a height fused to its root. `check_commitments.py` already carries the answer --
# `_FUSED` splits the pair before the scan -- so the scan is run over the split probe here too.
#
# ⇒ ONE GRAMMAR, IMPORTED, NOT A SECOND ONE MAINTAINED IN PARALLEL. Where this tool and the
# gate disagree about what a commitment row is, the gate is right by construction: it is the thing
# a reviewer runs. A row this cannot read is now a row the gate cannot read either.
from check_commitments import DIGEST_LINE, _DIGEST_TOKEN, _FUSED           # noqa: E402
from check_commitments import commitments as _cc_commitments               # noqa: E402  (round 16: ONE parser)
from check_commitments import retires as _cc_retires                       # noqa: E402  (round 16: and one retirement rule)

# ⚠️ THE NEAR-MISS RULE IS SCOPED, DELIBERATELY, AND NOT IMPORTED. `check_commitments._NEARLY`
# recognises an almost-digest by the BLOCK HEIGHT beside it; a file pin has no height, so importing
# it would give a rule with a branch no row here can take. The local shape is: a path-shaped name,
# then one hex-shaped token of the wrong length, then END OF LINE. The end-of-line is what keeps it
# honest -- section 3's round-9 table writes `build_package.py  <16 hex> -> <16 hex>` on purpose,
# and an abbreviation with something after it is prose, not a truncated commitment.
_NEAR_PIN = re.compile(r"^\s*([A-Za-z0-9_./-]*[./][A-Za-z0-9_./-]*)\s+"
                       r"([0-9a-fA-F]{16,63}|[0-9a-fA-F]{65,})\s*(?:#.*)?$")


def _inside(name):
    """The file `name` points at, or None if it is not inside this folder.

    ⛔ NOTHING CHECKED THIS. `HERE / name` follows `../` out of the study without complaint, so a
    commitment row could pin a file the study does not contain, count it among the digests that
    HOLD, and report READY on a table whose subject is elsewhere -- and section 5's repair derives
    the review packet's ship list from this same function, so an escaping name would have been
    asked for by the builder as well. A pre-registration commits the bytes of THIS tree; a name
    that leaves it is not a commitment this document is able to make.
    """
    if name.startswith(("/", chr(92))) or (len(name) > 1 and name[1] == ":"):
        return None
    try:
        f = (HERE / name).resolve()
    except (OSError, ValueError):                                         # pragma: no cover
        return None
    return f if HERE in f.parents else None


# ⛔⛔ A ROW THAT STOPS MATCHING LEAVES SILENTLY, AND THE COUNT LEAVES WITH IT. Every repair
# above is a repair to the GRAMMAR, and a grammar cannot notice its own blind spot: whatever shape
# it fails to read is a shape it also fails to count. A round-9 reviewer put one non-hex character
# into a digest --
#
#     train.py  ebd615...  ->  train.py  gbd615...
#
# -- and got `28 pins; 28 hold ... READY`, the round-8 output quoted verbatim in the docstring
# below as the defect being repaired. The row left the table, the total went with it, and the
# printed sentence was true about a document that now commits one file fewer.
#
# ⇒ THE TOTAL MUST COME FROM SOMEWHERE OTHER THAN THE PATTERN THAT PRODUCES IT. Section 3
# declares, in prose a human writes and no parser maintains, how many file pins it contains. A
# reader can count them; this compares. The two sources are independent by construction, which is
# the one property no amount of fixing the regex can give.
#
# ⚠️ AND IT FAILS CLOSED. A document with no declaration is refused rather than parsed, because
# "the grammar found N" is exactly the statement that was not trustworthy.
# ⛔⛔ A COUNT FIXES CARDINALITY AND SUBSTITUTION IS FREE. Round 10 swapped the `PUBKEY.asc`
# row for `./train.py` with train.py's real digest: total still 28, declared still 28, every rule
# satisfied -- and **the key every detached signature in this tree verifies against is no longer
# committed by the document.** The alias made it free; plain substitution needs no alias at all,
# since any dotted filename with a correct digest holds the total while the row that mattered
# leaves.
#
# ⚠️ AND THE SEARCH TOOK THE FIRST MATCH IN §3's PROSE. These documents quote their own history
# constantly, so a sentence QUOTING an older "commits exactly N file pins" wins over the live one.
# It fails closed when the numbers differ and agrees silently when they do not, which is the worst
# of both.
#
# ⇒ DECLARE THE MEMBERSHIP. A hand-written digest over the sorted pinned NAMES, one line, is
# independent of the grammar in the way the integer only half was: it moves when any row is
# added, removed OR renamed, and a reader can recompute it from the table with `sha256sum`. The
# count stays because it is the thing a human can check by eye, and the two now fail for
# different reasons.
_DECLARED = re.compile(r"commits exactly ([0-9]+) file pin")
# ⛔⛔ AND THIS ONE WAS UNSCOPED, CASE-SENSITIVE, AND FAILED OPEN -- three of the defects its
# sibling three lines up had already been repaired for. `_declared_total` reads section 3 only,
# prose only, outside the fences, last match. `_DECLARED_SET.finditer(text)` ran over the WHOLE
# document, fences included. A round-11 reviewer substituted a row and put one line anywhere
# below §3:
#
#     §3 still reads  ...hash to 0c49fe43fe340e24   (the old set)
#     §5 now reads    ...hash to f9fffdddbd7829ff   (the new set)     total=3 held=3   PASSES
#
# ⛔ And `[0-9a-f]{64}` is lower case only -- the round-9 defect, in the newest reader in the
# file -- so an upper-case membership line was not a declaration at all, and the ABSENT branch
# only warns. The warning then prints the membership digest of the substituted set, which is
# exactly the line an attacker needs to paste in.
#
# ⇒ SAME SCOPE, SAME CASE CLASS, AND IT FAILS CLOSED ON A DRAFT, all three read off the sibling
# rather than re-derived. A draft that declares no membership is refused for the same reason a
# draft that declares no count is; an anchored document is exempt for the same reason, because
# its bytes cannot be edited without breaking its proof.
_DECLARED_SET = re.compile(r"the sorted pinned names hash to ([0-9a-fA-F]{64})")


def _membership_digest(names):
    """SHA-256 over the sorted pinned names, newline-joined, with a trailing newline."""
    return hashlib.sha256((NL.join(sorted(names)) + NL).encode("utf-8")).hexdigest()


def _section3_prose(text):
    """Section 3's prose: that section only, outside the fenced blocks. "" if there is no §3.

    ⇒ ONE READER FOR THE SCOPE, so the count declaration and the membership declaration cannot
    drift apart again. They are two claims about the same table and must be read out of the same
    place; writing the scope twice is what let one of them be read out of the whole document.
    """
    start = text.find("## 3.")
    if start < 0:
        return ""
    tail = text[start:]
    nxt = re.search(r"^## (?!3\.)", tail[5:], re.M)
    if nxt:
        tail = tail[:nxt.start() + 5]
    # a declaration inside a commitment block would be part of the table it describes
    return chr(10).join(tail.split(chr(96) * 3)[::2])


def _declared_total(text):
    """How many file pins section 3 SAYS it has, read outside the fenced blocks. None if absent."""
    prose = _section3_prose(text)
    if not prose:
        return None
    # ⇒ the LAST match: a document quoting its own history states old counts before the live one
    _all = list(_DECLARED.finditer(prose))
    m = _all[-1] if _all else None
    return int(m.group(1)) if m else None


def _commitment_blocks(text):
    """Every fenced block in the commitments section, as raw text."""
    start = text.find("## 3.")
    if start < 0:
        return []
    tail = text[start:]
    nxt = re.search(r"^## (?!3\.)", tail[5:], re.M)
    if nxt:
        tail = tail[:nxt.start() + 5]
    parts = tail.split(chr(96) * 3)
    return [parts[i] for i in range(1, len(parts), 2)]          # odd indices are inside fences


def _pairs_of(doc):
    """(name, digest) for every file pin in this document, parsed directly.

    None means this document carries no commitment table this parser can read -- which is a fact
    about the DOCUMENT and not about the files, so a caller must not read it as a pin that failed.
    """
    try:
        text = doc.read_text(encoding="utf-8")
    except OSError:                                                       # pragma: no cover
        return None
    # round 16: the one parser reads the whole document, so a version whose table sits under
    # another heading (v6, v8, v11 ...) is read here as check_commitments reads it
    # ⛔⛔ AND THIS IS THE SOFT READER, WHICH IS THE ONE THAT BUILDS THE COMPOSED TABLE.
    # `pinned_digests` refuses a row whose path escapes the tree, refuses two spellings of one
    # path, checks the declared count and checks the declared membership. `_pairs_of` silently
    # CONTINUED past a row `_inside()` rejects and had none of the other three -- and it is what
    # `current_commitments()` reads to decide what governs. A round-11 reviewer put it exactly:
    # *same table, same file, and the soft one is the authority for the composed set.*
    #
    # ⇒ A ROW THIS READER CANNOT ACCOUNT FOR MAKES THE WHOLE DOCUMENT UNREADABLE, which is the
    # answer this function already has for a document with no table at all: `None` is *a fact
    # about the document, not about the files*, and a caller must not read it as a pin that
    # failed. Silently dropping one row is the one thing it must not do, because the composed
    # table is then missing a commitment nobody can see is missing.
    # ⛔ ROUND 16: TWO PARSERS, TWO COMPOSED HISTORIES. This read only the fences under `## 3.`
    # and printed that v4, v6, v8, v9, v11–v14, v16 and v17 "carry no commitment table this parser
    # reads; they pin nothing" -- while `check_commitments.commitments()` read 16 to 28 rows from
    # several of them. Same files, two answers to *what does this version pin*: the §2i class, one
    # tool over. ⇒ The pairs come from the one reader `check_commitments` uses; the tree-scope
    # and duplicate-spelling refusals below are this tool's and stay.
    out, dropped = [], []
    _rows = _cc_commitments(text)
    if not _rows:
        return None
    for name, dg in _rows:
        if re.fullmatch(r"[0-9]{6,9}", name):
            continue                         # an anchor fact: a height, not a path
        if _inside(name) is None:
            dropped.append(name)
            continue
        out.append((name, dg))
    if dropped:
        print("  %s %s carries %d pin row(s) naming a path outside this tree (%s); the document's "
              "commitment table cannot be read as a whole and it contributes NOTHING to the "
              "composed set. That is a fact about the document, not about the files."
              % (D, doc.name, len(dropped), ", ".join(sorted(dropped)[:3])))
        return None
    # ⇒ AND TWO SPELLINGS OF ONE PATH IS A REFUSAL HERE TOO. `pinned_digests` has had this rule
    # since round 9; the composed reader did not, so `./x` and `x` could both stand and whichever
    # sorted last would win a comparison nobody made.
    _seen = {}
    for name, dg in out:
        _r = _inside(name)
        _seen.setdefault(_r.resolve() if _r else name, set()).add(name)
    _dupe = {k: v for k, v in _seen.items() if len(v) > 1}
    if _dupe:
        print("  %s %s pins one file under %d different spellings (%s); the composed set cannot "
              "say which row governs, so this document contributes nothing to it"
              % (D, doc.name, len(_dupe),
                 "; ".join(", ".join(sorted(v)) for v in list(_dupe.values())[:2])))
        return None
    return out


def pinned_digests(doc):
    """Every `<file> <sha256>` pair the document commits, and whether it still holds.

    ⛔⛔ THIS MATCHED AN EXTENSION ALLOWLIST -- a dot and one of py, json, md -- SO IT READ 28 OF 29 PINS.
    The row it skipped was `PUBKEY.asc`: the key against which every detached signature in this
    tree is verified, committed by the document and enforced by nothing. A round-8 reviewer
    appended one newline to it and the START HERE command still printed *28 pins; 28 hold ...
    READY*. `check_commitments.py` does catch it -- and in the state this tree ships in, that gate
    is in refusal, so the hardened parser sits idle and the soft one is what runs.

    An extension allowlist standing in for a projection, in the round whose own section 2.2 names
    that substitution as this project's recurring defect. And downstream: section 5's repair
    derives the review packet's ship list from this function, so `PUBKEY.asc` travelled only
    because it was ALSO hand-written into SEND -- the exact guarantee that repair replaced.

    ⇒ THE COMMITMENTS ARE A STRUCTURE, NOT A PATTERN. Every 64-hex inside a commitment block must
    belong to a file pin or an anchor fact, and a name may be pinned only once -- because `seen`
    de-duplicated by name and let the FIRST occurrence win, so a contradictory second pin was
    invisible here and caught only by the gate that is not running.
    """
    text = doc.read_text(encoding="utf-8")
    blocks = _commitment_blocks(text)
    if not blocks:
        raise SystemExit("%s %s has no fenced commitment blocks under section 3; this parser "
                         "cannot tell an empty commitment table from a moved one." % (D, doc.name))
    pairs, stray = [], []
    for blk in blocks:
        consumed = []
        for raw in blk.split(NL):
            # ⇒ SPLIT A FUSED HEIGHT FIRST, exactly as the gate's `_anchor_shaped_lines` does:
            # `964534aaaa...` is one unbroken hex run, and a bounded digest token cannot see a
            # pair inside it. The split is applied to the PROBE only; `raw` stays the document's.
            probe = _FUSED.sub(lambda m: m.group(1) + " " + m.group(2), raw)
            m = DIGEST_LINE.match(probe)
            if not m:
                near = _NEAR_PIN.match(probe)
                if near:
                    # ⚠️ A DIGEST ONE CHARACTER SHORT IS NOT A ROW AND WAS NOT A COMPLAINT
                    # EITHER -- it simply vanished, which is this whole failure class.
                    stray.append("%r is pinned to a %d-character hash, not a sha256"
                                 % (near.group(1)[:40], len(near.group(2))))
                continue
            name, dg = m.group(1), m.group(2).lower()
            consumed.append(dg)
            if re.fullmatch(r"[0-9]{6,9}", name):
                continue                        # an ANCHOR FACT: height -> merkle root
            if "." not in name and "/" not in name:
                stray.append("%r is neither a path nor a block height" % name[:40])
                continue
            _res = _inside(name)
            if _res is None:
                stray.append("%r resolves outside this folder" % name[:60])
                continue
            # ⛔⛔ CONTAINMENT WAS CHECKED AND IDENTITY WAS NOT. `_inside` resolved the name and
            # the result was discarded: `pairs` kept the RAW STRING and the duplicate rule counted
            # raw strings, so `train.py`, `./train.py`, `corpus/../train.py` and a symlink to it
            # are four pins of ONE file and no duplicate. Round 10 used that to substitute
            # `PUBKEY.asc` -- the key every signature in this tree verifies against -- out of the
            # table while the count stayed at 28. **Third time PUBKEY.asc has left through a
            # control built to stop the previous time.**
            #
            # ⇒ THE RESOLVED PATH IS THE IDENTITY. It is carried alongside the name, and the
            # duplicate rule below is over resolutions, so an alias is a repeat whatever it is
            # spelled like.
            pairs.append((name, dg, _res))
        # ⚠️ COMPLETENESS. A digest inside a commitment block that no row consumed is a commitment
        # nothing checks -- which is how a pin stops being enforced without disappearing, and is
        # the same invariant the sibling paper had to add to its own digest block this round.
        _probe = _FUSED.sub(lambda m: m.group(1) + " " + m.group(2), blk)
        for d in _DIGEST_TOKEN.findall(_probe):
            if d.lower() not in consumed:
                stray.append("unconsumed digest %s..." % d[:16])
    if stray:
        raise SystemExit(
            "%s %s: %d item(s) inside the commitment blocks are neither a file pin nor an anchor "
            "fact: %s. A commitment table whose grammar is not closed cannot say what it commits."
            % (D, doc.name, len(stray), stray[:3]))
    # ⇒ OVER THE RESOLVED PATH, so two spellings of one file are one pin and a repeat.
    _res = [r for _n, _d, r in pairs]
    _dupes = sorted({str(r) for r in _res if _res.count(r) > 1})
    if _dupes:
        _spell = {}
        for _n, _d, _r in pairs:
            _spell.setdefault(str(_r), []).append(_n)
        raise SystemExit(
            "%s %s pins the same FILE more than once, under %s. A repeat within a block is a lie "
            "-- whichever digest loses is a commitment the document makes and nothing enforces -- "
            "and two spellings of one path is how a row that mattered leaves while the count "
            "holds." % (D, doc.name,
                        "; ".join("%s as %s" % (pathlib.Path(k).name, v)
                                  for k, v in sorted(_spell.items()) if len(v) > 1)))

    # ⇒ THE SECOND WITNESS, CHECKED LAST, BECAUSE IT IS THE LEAST SPECIFIC THING THAT CAN BE
    # WRONG. Placed FIRST, it swallowed every rule beneath it: a duplicate pin adds a row, so the
    # count disagreed and the refusal named the count -- and the duplicate rule, which knows
    # exactly what is wrong, could never fire again. A general check in front of a specific one
    # does not add a finding, it replaces a better one with a worse one.
    _want = _declared_total(text)
    if _want is None and declaration_required(doc):
        raise SystemExit(
            "%s %s section 3 does not declare how many file pins it contains. Add a sentence "
            "saying it commits exactly N file pins, outside the fenced blocks. Without it the "
            "only answer to 'how many' comes from the pattern whose blind spots are the thing "
            "being guarded against, and a row that stops matching takes the total with it."
            % (D, doc.name))
    # ⚠️ REQUIRED UNLESS ANCHORED, and the asymmetry is not a concession. v2 through v17 are
    # signed and stamped; the sentence cannot be added to them
    # without breaking their proofs, so demanding it would make this function refuse to read the
    # seventeen documents whose bytes are the most fixed things in the tree -- and it did, the
    # first time it was written, which is how the scope was found.
    #
    # ⇒ The threat the declaration answers is a ROW EDITED OUT OF A TABLE THAT CAN STILL BE
    # EDITED. An anchored document cannot be edited without breaking its proof, so the same
    # question there is answered by a different control: `check_commitments.py` compares the rows
    # a document lays out in table shape against what its two parsers read, for every version.
    # Each guards the half it can reach.
    if _want is not None and _want != len(pairs):
        raise SystemExit(
            "%s %s section 3 declares %d file pin(s) and this parser reads %d. One of the two is "
            "wrong and neither can say which: a row that stopped matching, a row added without "
            "updating the sentence, or a digest edited into a shape the grammar cannot see."
            % (D, doc.name, _want, len(pairs)))

    seen, held, broken = set(), 0, []
    for name, dg, _res in pairs:
        seen.add(name)
        # ⇒ the RESOLVED path is what is hashed, so a pin cannot name one file and check another
        f = _res
        if not f.is_file():
            broken.append((name, dg, "absent"))
            continue
        now = hashlib.sha256(f.read_bytes()).hexdigest()
        if now == dg:
            held += 1
        else:
            broken.append((name, dg, now))
    # ⇒ MEMBERSHIP, checked against the hand-written line, so a substituted row is caught even
    # when the count is untouched.
    _decl = list(_DECLARED_SET.finditer(_section3_prose(text)))
    if _decl:
        _want_set = _decl[-1].group(1).lower()
        _got_set = _membership_digest(seen)
        if _want_set != _got_set:
            raise SystemExit(
                "%s %s declares that its sorted pinned names hash to %s and they hash to %s. A "
                "row has been added, removed or renamed. The count is a separate claim and can "
                "still agree -- substituting one name for another holds the total exactly."
                % (D, doc.name, _want_set[:16], _got_set[:16]))
    elif declaration_required(doc):
        # ⇒ FAIL CLOSED, LIKE THE COUNT. This printed a warning and carried on -- and printed the
        # membership digest of the set as it now stands, which is the line an attacker pastes in
        # to make the substitution declared. A draft without the declaration is refused; the
        # digest it would need is NOT printed, because computing it is the author's act.
        raise SystemExit(
            "%s %s section 3 declares no membership digest, so only the COUNT of its pins is "
            "checked and substituting one row for another holds the total exactly. Add a sentence "
            "to section 3, outside the fenced blocks, saying `the sorted pinned names hash to "
            "<sha256>`. Compute it yourself from the names you intend to commit -- this tool will "
            "not hand you the digest of whatever the table happens to say now."
            % (D, doc.name))
    else:
        print("  %s %s is anchored and declares no membership digest; its bytes cannot be edited "
              "without breaking its proof, so the count and check_commitments.py are what guard "
              "it. A newer version is where a membership declaration goes." % (W, doc.name))
    return len(seen), held, broken, sorted(seen)


def governing_pins():
    """({name: (version, digest)}, [versions in force], [unreadable]) -- what governs THIS tree.

    ⛔⛔ `max(versions())` IS "HIGHEST PRESENT", AND WHAT GOVERNS IS "IN FORCE". The two are the
    same only while nothing is waiting, which is never during a drafting period. A round-11
    reviewer found the selector in two more places -- `build_review_packet.py` checking that the
    archive ships every pin of v20 (three files) while v18 and v19 compose thirty, and
    `anchor_status.py` building its required-proof set from the same three -- so the packet could
    satisfy *all pins of the newest document are shipped* while failing *all files the governing
    protocol commits are shipped*.
    #
    ⇒ ONE FUNCTION ANSWERS "WHICH PINS GOVERN", AND EVERY CALLER ASKS IT. That was already the
    rule inside this file after round 10; the two callers outside it kept their own answer, which
    is this project's sibling corollary -- a fix is not finished until the other call sites are
    grepped for.
    """
    vs = versions()
    if not vs:
        return {}, [], []
    forced = sorted(v for v in vs if in_force(vs[v]))
    current, unreadable = current_commitments(vs, forced)
    return current, forced, unreadable


def current_commitments(vs, forced):
    """({name: (version, digest)}, [versions with no readable table]) over the versions IN FORCE.

    ⚠️ THE CURRENT COMMITMENT FOR A FILE IS THE HIGHEST IN-FORCE VERSION THAT PINS IT. The
    first cut checked every in-force version's whole table and reported SIXTEEN tampered versions
    -- because each version pins the tooling AS IT WAS THEN, and a later version re-pinning the
    same file supersedes the earlier row. An amendment chain in which every historical pin must
    still hold is a chain that can never be amended.

    ⚠️ And a version with no commitment table pins NOTHING. v16 and v17 predate the fenced
    §3 table, the parser refuses to read them -- correctly -- and refusing to read a table is not
    evidence about the files.
    """
    current, unreadable = {}, []
    for _v in sorted(forced):
        _pp = _pairs_of(vs[_v])
        if _pp is None:
            unreadable.append(_v)
            continue
        for _name, _dg in _pp:
            _prev = current.get(_name)
            if _prev is None or _v > _prev[0]:
                current[_name] = (_v, _dg)
        # round 16: with one parser this tool now reads v9's table, which pins ANCHORS.json, and v10
        # RETIRES that path by declaration. A retirement is as load-bearing as a pin and is read by
        # the same rule check_commitments applies: a path leaves the table only by a version saying so.
        try:
            _ret = _cc_retires(vs[_v].read_text(encoding="utf-8")) or []
        except SystemExit:
            _ret = []
        for _name in _ret:
            if _name in current and current[_name][0] <= _v:
                current.pop(_name)
    return current, unreadable


def broken_commitments(current, declared=None, drafted=None):
    """([undeclared], [by a signature], [by the draft]) -- (version, name, pinned, now, by).

    ⚠️ A BROKEN PIN A SIGNED SUCCESSOR ALREADY RE-PINS IS A DIFFERENT FINDING. Running the
    composed check on every path made this folder's normal drafting state fatal: v18 pins
    `build_review_packet.py` as it was then, the file has since been edited, and v20 -- signed,
    waiting only for its Bitcoin attestation -- re-pins it at exactly the current bytes. That is
    the sequencing mistake v20 §1 exists to record, not a tampered tree, and a tool that cannot
    tell them apart is one an operator learns to run with `|| true`.

    ⛔⛔ AND A THIRD CATEGORY BREAKS A LOOP THE SECOND ONE CREATED. `--repin` was carved out so
    a draft could be WRITTEN while the composed check refuses -- but the confirm run the tool
    itself prints (*run this again to confirm, THEN sign*) still refused, so there was no path to
    READY. **To sign you needed READY; to get READY you needed the signature.**

    ⇒ THREE CATEGORIES.
      * Nothing re-pins it                      -> FATAL. `PUBKEY.asc` stays exactly this loud.
      * A SIGNED successor re-pins these bytes  -> reported. The key holder has stood behind them.
      * THE DRAFT IN HAND re-pins these bytes   -> reported as *what you are about to sign*.

    ⚠️ The third buys nothing silently. The document must be named on the command line or be
    the lowest one waiting; every file is printed with UNSIGNED beside it; and the signature is
    the act that moves it into the second category. Anyone who can edit this tree can write a
    draft -- and would then have to get a person to read and sign it, which is the only place this
    design has ever put that decision.
    """
    declared, drafted = declared or {}, drafted or {}
    bad, by_sig, by_draft = [], [], []
    for _name, (_v, _dg) in sorted(current.items()):
        _f = _inside(_name)
        if _f is None or not _f.is_file():
            bad.append((_v, _name, _dg, "absent", None))
            continue
        _now = hashlib.sha256(_f.read_bytes()).hexdigest()
        if _now == _dg:
            continue
        _s, _d = declared.get(_name), drafted.get(_name)
        if _s and _s[1] == _now:
            by_sig.append((_v, _name, _dg, _now, _s[0]))
        elif _d and _d[1] == _now:
            by_draft.append((_v, _name, _dg, _now, _d[0]))
        else:
            bad.append((_v, _name, _dg, _now, None))
    return bad, by_sig, by_draft


def signed_successor_pins(vs, forced):
    """{name: (version, digest)} from SIGNED versions not yet in force -- the highest wins."""
    out = {}
    for _v in sorted(v for v in vs if v not in forced and signed(vs[v])):
        _pp = _pairs_of(vs[_v])
        if _pp is None:
            continue
        for _name, _dg in _pp:
            out[_name] = (_v, _dg)
    return out


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    argv = sys.argv[1:]
    vs = versions()
    if not vs:
        raise SystemExit("%s no pre-registration documents here." % D)
    # ⛔ THE NEWEST VERSION IS NOT THE NEXT ONE WHEN TWO ARE UNSIGNED. This took `max(vs)`, which
    # is right only while at most one version is waiting. Round 9 split v18 -- the withdrawal and
    # the re-pins in one version, the two new tools and the write path they carry in the next --
    # because v18's own §1d forbids bundling a governance change with the decision a reviewer is
    # weighing. The moment that split existed, `max` selected v19 and there was no way to prepare
    # v18, which v19 amends and which must be in force first.
    #
    # ⇒ PREPARE THE LOWEST VERSION NOT YET IN FORCE, and say what is queued behind it. Versions
    # are put in force in order because each amends the one below; a tool that offers the top of
    # the stack is offering the one step that cannot be taken.
    _waiting = sorted(v for v in vs if not in_force(vs[v]))
    newest = next_version(vs)[0]
    # ⇒ AND A DRAFT FURTHER UP THE STACK CAN STILL BE WORKED ON. Every unsigned version is a
    # draft, and `--repin` is how a draft's pins are made to describe the tree; refusing to reach
    # v19 until v18 is anchored would mean its pins could only be maintained by hand, which is the
    # thing this tool exists to stop. Naming a version is explicit and is refused for one that is
    # already signed, by the same `writable()` gate as everything else.
    if '--version' in argv:
        try:
            newest = int(argv[argv.index('--version') + 1])
        except (IndexError, ValueError):
            raise SystemExit('%s --version takes a version number.' % D)
        if newest not in vs:
            raise SystemExit('%s there is no v%d here. Present: %s'
                             % (D, newest, ', '.join('v%d' % v for v in sorted(vs))))
    doc = vs[newest]
    print("=" * 78)
    print("  THE NEXT PROTOCOL VERSION, AND WHETHER IT IS READY TO BE PUT IN FORCE")
    print("=" * 78)

    forced = sorted(v for v in vs if in_force(vs[v]))
    print("  in force: %s" % (", ".join("v%d" % v for v in forced) or "none"))

    # ⇒ TWO DOCUMENTS CONTRADICTING EACH OTHER ABOUT BITCOIN IS THE LOUDEST THING THIS TREE
    # CAN FIND, and `_committed_heights` used to answer with whichever it read first. It now
    # drops the height and records the contradiction here. Nothing downstream is meaningful
    # while one stands: the fact tables are what confirmation rests on.
    if CONFLICTING_FACTS:
        for _h, _rs in sorted(CONFLICTING_FACTS.items()):
            print("  %s   block %d is given %d different merkle roots by signed, anchored "
                  "versions:" % (D, _h, len(_rs)))
            for _r, _who in sorted(_rs.items()):
                print("       %s  by %s" % (_r, ", ".join("v%d" % _v for _v in _who)))
        raise SystemExit("%s the anchor-fact tables contradict each other. Two signed documents "
                         "cannot both be right about what a Bitcoin block contains, and this tool "
                         "will not choose between them. Establish which root that block actually "
                         "carries and correct the document that is wrong -- by superseding it, "
                         "not by editing signed bytes." % D)

    # ⛔⛔ AND THE COMPOSED CHECK RAN ONLY IN THE BRANCH THIS PROJECT IS NEVER IN. It lived
    # inside `if in_force(doc)`, so it fired only when NO version was waiting -- and a version is
    # always waiting while anyone is drafting one, which is exactly when the edits happen. A
    # round-11 reviewer mutated `PUBKEY.asc`, which v18 pins and v20 does not, and got:
    #
    #     ok   v20 pins 3 file digest(s); 3 hold against the files here        READY   rc=0
    #
    # Move v20 aside and the same tree reports four broken pins, including the key every detached
    # signature here verifies against. **v20 §2's claim -- every version in force has its pins
    # verified -- held only in the state this folder is never in**, and the control suite's
    # `PUBKEY.asc` attack has been passing for four rounds because of it.
    #
    # ⇒ THE COMPOSED COMMITMENT IS CHECKED BEFORE ANY PER-DOCUMENT BRANCH, on every path,
    # whatever is being prepared. What governs this tree is the union of the in-force versions'
    # current pins; which document is next is a separate question and must not gate the first one.
    # That is round 10's finding -- *a repair to the predicate that never reached the caller* --
    # in the caller it did reach, one branch over.
    _current, _unreadable = current_commitments(vs, forced)
    if in_force(doc):
        # ⛔⛔ AND THIS RETURNED 0 WITHOUT READING A PIN. Round 10 found the whole of section C
        # -- the imported grammar, `_NEAR_PIN`, `_inside()`, the declared table -- was DEAD CODE in
        # the shipped state, because `main()` stopped here the moment two files existed beside the
        # document. **A document in force whose pins are broken is exactly the tampered tree this
        # gate exists to report, and it was the one state the gate declined to look at.**
        #
        # ⚠️ I fixed `in_force` and left this, which is the same defect one line down: a repair
        # to the PREDICATE that never reached the CALLER. Caught only by re-reading the finding
        # against the code rather than against my own summary of it.
        #
        # ⇒ EVERY VERSION IN FORCE HAS ITS PINS CHECKED, not merely the newest, because a
        # commitment does not stop being one when a later version supersedes it. Nothing is
        # prepared here -- there is nothing to prepare -- but a broken pin is reported and refused.
        print("  %s v%d is already signed and anchored; nothing to prepare." % (OK, newest))
        # \u26a0\ufe0f THE CURRENT COMMITMENT FOR A FILE IS THE HIGHEST IN-FORCE VERSION THAT PINS IT.
        # The first cut of this checked every in-force version's whole table and reported SIXTEEN
        # tampered versions -- because each version pins the tooling AS IT WAS THEN, and a later
        # version re-pinning the same file supersedes the earlier row. An amendment chain in which
        # every historical pin must still hold is a chain that can never be amended.
        #
        # \u26a0\ufe0f And a version with no commitment table pins NOTHING. v16 and v17 predate the
        # fenced \u00a73 table, the parser refuses to read them -- correctly -- and refusing to read a
        # table is not evidence about the files.
        # ⇒ ALREADY DONE ABOVE, ON EVERY PATH. This used to be the only place the composed
        # commitment was checked, which is the finding this round.
        return 0
    if len(_waiting) > 1:
        print("  %s queued behind it, in order: %s. Each amends the one below, so they are put in "
              "force one at a time and this prepares only the first."
              % (W, ", ".join("v%d" % v for v in _waiting[1:])))
    # ⚠ NAME WHAT IS MISSING. When `in_force` became signed-AND-ANCHORED this printed an empty
    # reason for the commonest state there is -- signed, stamped, waiting on a block -- which is
    # the state a reader most needs told apart from "nothing has happened yet".
    # ⇒ THE THREE SIGNATURE STATES READ DIFFERENTLY TO AN OPERATOR, and telling someone "no
    # signature" when a file is sitting right there sends them to sign a second one over it.
    _why = ({"absent": "no signature",
             "bad": "there IS a signature beside it and it DOES NOT VERIFY (%s). Do not sign "
                    "over it -- find out where that file came from"
                    % _SIG_DETAIL.get(str(doc), "no detail"),
             "unverifiable": "there is a signature beside it and `gpg` did not run here, so it "
                             "could not be checked. Install gpg and run `check_signature.py`; "
                             "until then this tree cannot tell you what it is looking at"}
            .get(signature_state(doc))
            if not signed(doc)
            else "no proof" if not stamped(doc)
            # ⛔ THE FOURTH STATE. `confirmed()` split ANCHORED into confirmed and provisional
            # and this branch never learned it: for v21 -- two Bitcoin attestations, both
            # pinned -- it printed *carries no Bitcoin attestation yet* and prescribed
            # `_ots_upgrade.py`, which does nothing to an already-anchored proof. A false
            # cause with a useless remedy, one line above the line that stated the true one.
            else ("anchored, and PROVISIONAL: its proof carries a Bitcoin attestation and no "
                  "committed anchor-fact table names that block yet. Nothing to run here -- "
                  "only a LATER version's §2d table confirms it; see `confirmed()`.")
            if anchored(doc)
            else ("its proof carries no Bitcoin attestation yet -- a calendar has receipted it "
                  "and no block has carried it, so WHEN is not established. Run "
                  "`python ../../_ots_upgrade.py` once a block has.")
            if _proof_state(doc)[0] == "pending"
            # ⛔ ROUND 16: a truncated proof and a substituted root both printed the sentence
            # above and prescribed an upgrade that does nothing to a file that is not a proof
            else ("the file beside it named as its proof does not parse as a proof of these "
                  "bytes (%s). Not pending: not a proof of this document." % _proof_state(doc)[1]))
    print("  %s v%d is NOT in force: %s" % (W, newest, _why))

    total, held, broken, _names = pinned_digests(doc)
    print("  %s v%d pins %d file digest(s); %d hold against the files here"
          % (OK if not broken else D, newest, total, held))
    for name, was, now in broken:
        print("      %s %-28s pinned %s... now %s" % (D, name, was[:14], str(now)[:14]))
    if "--repin" in argv and not writable(doc):
        # ⇒ NAME WHICH COMMITTAL BLOCKS THE WRITE. The old message said "already carries a
        # detached signature" whatever the reason, which was wrong out loud in the two cases
        # that matter: a signature that does not verify, and a document whose signature was
        # deleted but whose timestamp proof is still on disk.
        _ss = signature_state(doc)
        _blocker = {
            "ok": "already carries a detached signature that verifies, so its bytes are "
                  "somebody's word",
            "bad": "carries a detached signature that DOES NOT VERIFY. That is not a draft and "
                   "it is not a signed document either -- it is a tree somebody should look at, "
                   "and overwriting the bytes underneath it would destroy the evidence",
            "unverifiable": "carries a detached signature this machine cannot check, because "
                            "`gpg` did not run. Not being able to check a signature is not the "
                            "same as there being none, and the write path may not be opened by "
                            "the absence of a tool",
        }.get(_ss, "carries no signature now, but it HAS BEEN TIMESTAMPED. A signature can be "
                   "deleted by anyone who can edit this folder; a timestamp cannot be un-taken. "
                   "Rewriting these bytes would leave a real proof standing over a document that "
                   "no longer exists, which is worse than no proof: it is evidence pointing at "
                   "nothing. A stamped document is history, not a draft")
        raise SystemExit(
            "%s v%d %s, and `--repin` is refused. Re-pinning a draft is editing a draft; the "
            "same edit to a committed document is forgery, and it stays forgery whether or not a "
            "calendar has seen it yet. If the pins are genuinely wrong, the honest route is a "
            "new version that states the change and its reason -- which is this protocol's own "
            "rule for amending an anchored text." % (D, newest, _blocker))
    if broken and "--repin" in argv:
        # ⛔ RE-PINNING IS SAFE EXACTLY WHILE NOTHING HAS SIGNED THE BYTES, and refused otherwise.
        # An unsigned version is a draft: correcting a digest in it is editing a draft. The guard
        # is `writable()` above -- NOT `in_force()`, which meant *not yet stamped* and left the
        # write path open across the whole gap between signing and stamping. A round-6 reviewer
        # found two pins that no longer described the files, both from deliberate repairs made
        # after the document was written; the sequencing, not the repairs, was the mistake.
        text = doc.read_text(encoding="utf-8")
        # ⛔⛔ AND THIS WAS KEYED ON THE DIGEST, NOT ON THE ROW. `text.replace(was, now)` rewrites
        # EVERY row carrying that digest, so repairing one row silently rewrote its neighbours --
        # found while writing v21, whose five rows were drafted with the same placeholder: the
        # first replacement gave all five the first file's digest, and the second assertion then
        # failed with a name it could not find. Two rows legitimately share a digest whenever two
        # pinned files have identical bytes, so this was not only a drafting artefact.
        #
        # ⇒ THE UNIT IS THE ROW: `<name><whitespace><digest>`, which is what the table commits and
        # what every other reader here parses. Exactly one row must match, or nothing is written.
        for name, was, now in broken:
            if now == "absent":
                raise SystemExit("%s %s is pinned and absent; re-pinning cannot invent it."
                                 % (D, name))
            _rx = re.compile(r"^(" + re.escape(name) + r")([ \t]+)" + re.escape(was)
                             + r"[ \t]*$", re.M)
            _hits = _rx.findall(text)
            if len(_hits) != 1:
                raise SystemExit(
                    "%s %s: %d row(s) in %s read `%s  %s...`, and re-pinning needs exactly one. "
                    "Nothing was written." % (D, name, len(_hits), doc.name, name, was[:16]))
            text = _rx.sub(lambda m: m.group(1) + m.group(2) + now, text, count=1)
            print("      %s re-pinned %-28s %s... -> %s..." % (OK, name, was[:14], now[:14]))
        doc.write_text(text, encoding="utf-8", newline=NL)
        print("  %s %s re-pinned. Run this again to confirm, THEN sign." % (OK, doc.name))
        return 0
    if broken:
        raise SystemExit(
            "%s %d pinned digest(s) do not describe the files in this folder. Signing now would "
            "freeze a commitment to bytes that have already changed, and every run afterwards "
            "would report a tampered tree -- correctly, from a sequencing mistake. Either restore "
            "the files, or re-pin with `--repin` (permitted only while nothing has signed it, "
            "force), then run this again." % (D, len(broken)))

    # ⛔⛔ AND RUNNING IT FIRST MADE IT ANSWER FOR EVERY OTHER RULE. Hoisting the composed
    # check onto every path was right; putting it in FRONT of the prepared document's own parser
    # was not. A duplicate row, an upper-cased digest, a short hex, a name that escapes the
    # folder -- each of those changes what the table says a file hashes to, so the composed check
    # saw a mismatch and refused with *no longer match the pin the highest version in force gives
    # them* before the rule that actually understands the defect could speak. Six of this suite's
    # attacks reported `WRONG`: they refused, for a sentence that was true and useless.
    #
    # ⇒ THE SPECIFIC RULE GOES FIRST AND THE GENERAL ONE LAST, which is this file's own stated
    # discipline three hundred lines up: *a general check in front of a specific one does not add
    # a finding, it replaces a better one with a worse one.* `pinned_digests` has already parsed,
    # counted and verified the prepared document by the time this runs, so what reaches here is a
    # commitment NO document's own table accounts for -- `PUBKEY.asc` being the case it was added
    # for, which no version in force re-pins and which therefore nothing else can see.
    _draft_pins = {}
    if writable(doc):
        for _n, _d in (_pairs_of(doc) or []):
            _draft_pins.setdefault(_n, (newest, _d))
    _tampered, _declared, _drafted = broken_commitments(
        _current, signed_successor_pins(vs, forced), _draft_pins)
    if _unreadable:
        print("  %s %d in-force version(s) carry no commitment table this parser reads (%s); "
              "they pin nothing and are not evidence either way"
              % (W, len(_unreadable), ", ".join("v%d" % _x for _x in _unreadable)))
    print("  %s %d file(s) carry a current commitment from the versions in force"
          % (OK if not _tampered else W, len(_current)))
    for _v, _name, _was, _now, _by in _declared:
        print("  %s %-28s pinned by v%d as %s, now %s -- re-pinned at these exact bytes by "
              "SIGNED v%d, whose proof no later version's §2d table has confirmed yet"
              % (W, _name, _v, _was[:16], _now[:16], _by))
    # ⛔ ROUND 16: THIS SAID READY FOR A FORGED RESTATEMENT. A cold reader appended a line to
    # `train.py`, wrote its new digest into v22's row, and this tool printed *re-pinned at these
    # exact bytes by v22, THE UNSIGNED DRAFT IN HAND ... READY*: it treated a §2q restatement like
    # a §2e–§2o repair. A repair is a row the draft NAMES in its repair sections; a restatement is
    # every other row, and §2q's own invariant is that it changes what is enforced not at all --
    # so a restated digest must equal the digest the versions in force already give the path.
    _repair_text = ""
    _t = doc.read_text(encoding="utf-8")
    _i, _k = _t.find("## 2."), _t.find("## 3.")
    if _i >= 0:
        _repair_text = _t[_i:_k if _k > _i else None]
        _q, _r = _repair_text.find("### 2q"), _repair_text.find("### 2r")
        if _q >= 0:                                   # §2q RESTATES; it names no repair
            _repair_text = _repair_text[:_q] + (_repair_text[_r:] if _r > _q else "")
    # the §2c note, which names the rows re-pinned at repaired bytes, is part of the repair statement
    _c = _t.find("### 2c")
    if _c >= 0:
        _f = _t.find(chr(96) * 3, _c)
        _repair_text += _t[_c:_f if _f > _c else None]
    _repairs = set(re.findall(r"`([A-Za-z0-9_./-]+)`", _repair_text))
    _forged = []
    for _v, _name, _was, _now, _by in _drafted:
        if _name in _repairs:
            print("  %s %-28s pinned by v%d as %s, now %s -- re-pinned at these exact bytes by v%d, "
                  "THE UNSIGNED DRAFT IN HAND, which names it as a repair. Signing it is what commits this."
                  % (W, _name, _v, _was[:16], _now[:16], _by))
        else:
            _forged.append((_v, _name, _was, _now, _by))
            print("  %s %-28s pinned by v%d as %s, now %s -- the draft RESTATES this path and does "
                  "not name it as a repair, so its row must carry the pin the versions in force give it"
                  % (D, _name, _v, _was[:16], _now[:16]))
    if _forged:
        _fmsg = ("%s %d restated row(s) do not restate: the draft pins a path at bytes the versions in "
                 "force do not give it, and names no repair for it (%s). A restatement that differs is a "
                 "forged pin or an unstated repair; either way this draft is not READY."
                 % (D, len(_forged), ", ".join(_n for _v, _n, *_ in _forged)))
        if "--repin" in argv and writable(doc):
            print(_fmsg)
            print("  %s continuing because this run is WRITING the draft; the next plain run refuses "
                  "until the row restates or a repair section names the path." % W)
        else:
            raise SystemExit(_fmsg)
    for _v, _name, _was, _now, _by in _tampered:
        print("  %s %-28s pinned by v%d as %s, now %s"
              % (D, _name, _v, _was[:16], str(_now)[:16]))
    if _tampered:
        _msg = ("%s %d file(s) no longer match the pin the highest version in force gives them. "
                "That is a tampered tree or a sequencing mistake, and either way it is the "
                "finding this tool exists to report -- being signed and anchored is what makes it "
                "serious, not what excuses it. A signed document cannot be re-pinned; the repair "
                "is a new version that pins the current bytes." % (D, len(_tampered)))
        # ⚠️ AND THE REFUSAL MUST NOT BLOCK THE ONE COMMAND THAT REPAIRS IT. Hoisting this
        # check onto every path made `--repin` unreachable in exactly the state it exists for: a
        # draft is written precisely BECAUSE the in-force pins no longer describe the tree, and a
        # gate that refuses to let the repair be written is a gate that has to be worked around.
        #
        # ⇒ REPORTED AND NOT FATAL WHILE WRITING AN UNSIGNED DRAFT -- which `writable()` already
        # limits to a document nobody has signed, so nothing here can launder a signed table. On
        # every other path, including the plain run an operator does next, it refuses.
        if "--repin" in argv and writable(doc):
            print(_msg)
            print("  %s continuing because this run is WRITING the draft that re-pins them; the "
                  "next plain run will refuse until that draft is signed." % W)
        else:
            raise SystemExit(_msg)


    prev = max((v for v in forced if v < newest), default=None)
    # ⛔⛔ AND THIS ASKED ABOUT AUTHORITY WHEN ORDERING IS ABOUT SIGNATURE AND PROOF. Once
    # `in_force` became `signed and confirmed`, v18 and v19 -- signed, stamped, anchored, and
    # waiting only for a later table to name their blocks -- counted as gaps, so **v21 could not
    # be prepared until v18 and v19 were confirmed, and confirming them is exactly what v21's
    # §2d does.** A deadlock between two rules that are each correct.
    #
    # ⇒ THE CONSTRAINT IS THAT EACH DOCUMENT BELOW HAS BEEN SIGNED AND STAMPED, which is what
    # *amends the one below it* actually requires: you cannot anchor an amendment to a document
    # nobody has signed. Confirmation is a later and automatic consequence of the chain
    # continuing, not a precondition for continuing it -- and `next_version` already draws the
    # line in this place.
    _gap = sorted(v for v in vs if v < newest and not (signed(vs[v]) and anchored(vs[v])))
    if _gap:                                                             # pragma: no cover
        raise SystemExit(
            "%s v%d cannot be prepared while %s below it %s not signed and stamped. A version "
            "amends the one below it, so putting this one in force first would anchor an "
            "amendment to a document nobody has signed."
            % (D, newest, ", ".join("v%d" % v for v in _gap),
               "is" if len(_gap) == 1 else "are"))
    if prev is not None:
        print("  %s v%d amends v%d, which is in force" % (OK, newest, prev))

    print()
    print("  READY. These are the operator's to run; nothing here does them.")
    print("  %s TWO OF THE THREE ARE OPERATOR TOOLING AND ARE NOT IN THIS TREE." % W)
    print("     `gpg` is a system tool. `_ots_stamp.py` and `_ots_upgrade.py` live two")
    print("     directories up, in the workspace, NOT in this study folder and NOT in the")
    print("     review archive -- so from an extracted archive they will not be found, and")
    print("     that is the separation rather than a missing file. A round-6 reviewer was")
    print("     right that saying \"these are the commands that exist\" without saying WHERE")
    print("     is a claim this tree cannot support.")
    print()
    print()
    # ⚠️ THESE ARE THE COMMANDS THAT EXIST. The first draft of this printed
    # `_ots_upgrade.py --stamp`, which is not a thing: that script COMPLETES a pending proof and
    # cannot create one, and the flag would simply have been ignored. Printing a command that
    # silently does nothing is worse than printing none, because the operator would have read
    # "Nothing to upgrade" as success. `_ots_stamp.py` is the one that creates a proof, and the
    # `ots` CLI on this machine is broken and must not be used.
    # ⛔⛔ AND THIS PRINTED ALL THREE WHATEVER THE DOCUMENT ALREADY HAD. v20 has its `.asc` and
    # its `.ots`; the READY branch told the operator to `gpg --armor --detach-sign` it -- which
    # would overwrite a signature somebody made -- and to stamp it again, with the one command it
    # actually needs printed third under a comment saying to run it later. **This module's own
    # docstring promises that the printed commands are never advice about a state that no longer
    # holds**, and round 10's repair to `in_force()` moved that defect out of the early return and
    # into here. The step that is DONE is stated as done; only the remaining ones are offered.
    _has_sig = signed(doc)
    _has_ots = (doc.parent / (doc.name + ".ots")).is_file()
    _ss = signature_state(doc)
    if _has_sig:
        print("      %s signed already -- %s.asc verifies; do NOT sign again, it would replace "
              "somebody's signature" % (OK, doc.name))
    elif _ss != "absent":
        # ⚠ NOT "sign it": there is a file there. Telling the operator to sign would overwrite
        # whatever it is, which is the one action that destroys the thing worth looking at.
        print("      %s %s.asc is present and is %s. Do NOT sign over it -- run "
              "`python check_signature.py` and establish what that file is first."
              % (D, doc.name, "not a valid signature" if _ss == "bad"
                 else "uncheckable here (`gpg` did not run)"))
    else:
        print("      gpg --armor --detach-sign %s" % doc.name)
    if _has_ots:
        print("      %s stamped already -- %s.ots exists; do NOT stamp again"
              % (OK, doc.name))
    else:
        print("      python ../../_ots_stamp.py %s %s.asc" % (doc.name, doc.name))
    if _has_ots and not anchored(doc):
        print("      python ../../_ots_upgrade.py          <-- THE ONE STEP LEFT: the proof is a "
              "calendar receipt and has no Bitcoin attestation yet")
    elif not _has_ots:
        print("      python ../../_ots_upgrade.py          # hours later, once a calendar "
              "anchors it")
    elif not confirmed(doc):
        print("      %s anchored, and PROVISIONAL: no committed anchor-fact table names its "
              "block yet, so it is not in force. The next version's \u00a72d table is what confirms "
              "it -- see `confirmed()`." % W)
    print()
    print("  %s The stamp is an OUTWARD act: it submits a digest of the document to public"
          % W)
    print("     calendar servers. The digest discloses nothing about the contents, and it is")
    print("     not reversible. Anchoring a cutoff is deliberate here; anchoring a draft is not.")
    print()
    print("  Then: python check_commitments.py   (it will select v%d as the authority)" % newest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
