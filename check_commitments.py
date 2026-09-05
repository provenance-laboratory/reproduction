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
import json
import pathlib
import re
import ots_verify as _OTS
import sys
import typing

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
MIN_EXPECTED = 4
# ⚠ How long a stamped-but-unanchored successor may sit before it is a violation rather than a
# wait. Calendars aggregate on their own schedule and a few days is ordinary; a week during which
# OTHER proofs in this tree reached blocks is not.
STALE_PENDING_DAYS = 7
# ⚠ HEX IS CASE-INSENSITIVE. This matched `[0-9a-f]{64}` only, so a table written with uppercase
# digests parsed as zero commitments and the document was filed as "present and not authority"
# rather than as a table the parser cannot read. The digest is lower-cased on the way out, because
# everything it is compared against comes from `hexdigest()`.
DIGEST_LINE = re.compile(r"^([A-Za-z0-9_./-]+)\s+([0-9a-fA-F]{64})\s*(?:#.*)?$", re.M)

# ⛔ "IS THIS A TABLE?" WAS INFERRED FROM A DIGEST COUNT, AND ONE INTEGER CANNOT CARRY TWO
# QUESTIONS. MIN_EXPECTED meant both "how many pins make a table" and "how many loose digests make
# an empty parse suspicious", and it was wrong from both sides. A reviewer demonstrated both:
#
#   * a REAL three-entry table in an unreadable layout carries fewer than MIN_EXPECTED raw
#     digests, so it escaped the NO-TABLE rule and fell into the silent skip the rule exists to
#     close -- the hole was only ever closed for tables of four or more; and
#   * a document quoting four digests IN PROSE and pinning nothing was fatally rejected as a
#     broken table. That is the v2/v4 defect reappearing inside the fix for the v2/v4 defect: the
#     comment congratulated the threshold for handling v2's single prose digest while the same
#     mechanism fatally rejected a v2-shaped amendment that happened to cite four.
#
# ⇒ Detect the table STRUCTURALLY. A commitment row is a path beside a digest inside a fenced
# block or a pipe-table row -- something with table shape. Prose is not table shape however many
# digests it quotes, and a three-row table is a table.
_FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S)
# ⛔ THE TWO PATTERNS DISAGREED ABOUT THE LINE'S TAIL, AND THE DISAGREEMENT WAS FATAL. `_ROW`
# ended at a word boundary and `DIGEST_LINE` at end-of-line, so a fenced block whose rows carry
# trailing annotations -- `train.py  <64hex>  # unchanged` -- is SEEN as four commitment rows and
# PARSED as zero, which lands in NO-TABLE and exits. A legitimate document that annotates its own
# examples was refused outright. A round-14 reviewer built it and confirmed the exit.
#
# ⇒ Both ends agree now: a commitment row may carry a trailing comment, and both the detector and
# the parser accept exactly the same shape. Where they must differ they differ deliberately, not
# by one having a stricter tail than the other.
#
# ⚠ The detector also accepts the layouts a human reads as a table but the parser cannot: pipe
# cells with backticks, a colon separator, and a digest-first column. Those are STILL not parsed
# as commitments -- deliberately, one syntax is enough -- but they are now recognised as a table
# the parser cannot read, which is a loud NO-TABLE rather than a silent skip. That was the whole
# point of detecting tables structurally, and it only covered one spelling.
_ROW = re.compile(
    r"^\s*\|?\s*[`\"']?([A-Za-z0-9_./-]+)[`\"']?\s*[|:]?\s+[`\"']?([0-9a-fA-F]{64})[`\"']?"
    r"\s*(?:\|)?\s*(?:#.*)?$"
    r"|^\s*\|?\s*[`\"']?([0-9a-fA-F]{64})[`\"']?\s*[|:]?\s+[`\"']?([A-Za-z0-9_./-]+)[`\"']?"
    r"\s*(?:\|)?\s*(?:#.*)?$", re.M)


def presents_table(text):
    """Does this document lay out commitment rows, whether or not this parser can read them?

    Counts rows with TABLE SHAPE: inside a fenced block, or written as a pipe-table row. The
    question is deliberately independent of how many rows there are and of whether DIGEST_LINE
    matches any of them -- those are the two things the old digest-count conflated.
    """
    n = 0
    for block in _FENCE.findall(text):
        n += len(_ROW.findall(block))
    for line in text.split(NL):
        if line.lstrip().startswith("|") and _ROW.match(line):
            n += 1
    return n


def _without_anchor_facts(text):
    """The document with its §2d anchor-fact block removed.

    ⛔ AN ANCHOR FACT LOOKS EXACTLY LIKE A COMMITMENT. `964534  <64 hex>` matches the path+digest
    pattern, because a block height is a legal path. Introducing §2d therefore silently doubled
    the parsed commitment table -- 21 real pins plus 21 heights read as files -- and the first
    generated v10 reported 42. Caught by parsing the document back immediately after writing it,
    which is the only reason it did not ship.
    """
    if ANCHOR_FACTS_HEADING not in text:
        return text
    head, tail = text.split(ANCHOR_FACTS_HEADING, 1)
    block = re.search(r"```" + NL + r".*?```", tail, re.S)
    return head + (tail[:block.start()] + tail[block.end():] if block else tail)


def commitments(text):
    """(path, digest) for every file a protocol version pins. Read out, never retyped."""
    return [(m.group(1), m.group(2).lower())
            for m in DIGEST_LINE.finditer(_without_anchor_facts(text))]


BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])

ANCHOR_FACTS_HEADING = "### 2d."
ANCHOR_FACT_LINE = re.compile(r"^\s*(\d{6,9})\s+([0-9a-fA-F]{64})\s*$", re.M)


def anchor_facts(text):
    """(height -> merkle root) a version commits to, as FACTS rather than as file bytes.

    ⛔ WHY THIS SHAPE. ANCHORS.json was pinned by digest, and anchoring a new version rewrites it
    -- so every version was void the instant it became authoritative. The commitment being wrong
    was not carelessness; a byte pin cannot express "this file may grow but never lie".

    ⇒ A fact pin is MONOTONIC: each listed height must still carry the listed merkle root, and new
    heights are permitted. Later anchoring adds; it never contradicts. Anyone can re-derive every
    line from the chain, which is the property a digest of the file never had.
    """
    if ANCHOR_FACTS_HEADING not in text:
        return {}
    tail = text.split(ANCHOR_FACTS_HEADING, 1)[1]
    block = re.search(r"```" + NL + r"(.*?)```", tail, re.S)
    if not block:
        return {}
    # ⛔ THE DICT COLLAPSE WAS THE LIE. A fact pin promises "every committed height keeps its
    # merkle root", and a comprehension keyed on height silently kept the LAST line for a
    # repeated height. So a document could commit 964534 twice -- once truthfully, once with a
    # fabricated root -- and the fabricated one would be the only fact ever checked. The older
    # commitment stops being checked without ever being contradicted: monotonic in shape, a lie
    # in substance. A round-14 reviewer built it and watched the real fact's failure vanish.
    #
    # ⇒ A repeated height is refused before any collapse, whatever the roots say. Two lines for
    # one height is never a legitimate document: the block is a set of commitments, and a set
    # cannot name the same thing twice.
    _pairs = [(int(m.group(1)), m.group(2).lower())
              for m in ANCHOR_FACT_LINE.finditer(block.group(1))]
    _seen = {}
    for _h, _r in _pairs:
        if _h in _seen:
            raise SystemExit(
                D + " an anchor-fact block commits height %d TWICE (%s then %s). A repeated "
                "height silently replaces the earlier commitment when the block is read as a "
                "mapping, which is how a fact pin lies while still looking monotonic."
                % (_h, _seen[_h][:16], _r[:16]))
        _seen[_h] = _r
    return _seen


def anchor_facts_hold(facts, here=None):
    """Every committed (height, root) still present and identical. Returns a list of failures."""
    here = here or HERE
    try:
        blocks = json.loads((here / ANCHOR_FILE).read_text(encoding="utf-8"))["blocks"]
    except (OSError, ValueError, KeyError) as e:
        return ["%s cannot be read (%s), so no anchor fact can be checked" % (ANCHOR_FILE, e)]
    out = []
    for h, root in sorted(facts.items()):
        got = (blocks.get(str(h)) or {}).get("merkle_root", "")
        if not got:
            out.append("height %d is committed and is ABSENT from %s -- a fact pin may grow, "
                       "never shrink" % (h, ANCHOR_FILE))
        elif got.lower() != root:
            out.append("height %d committed root %s and %s now says %s"
                       % (h, root[:16], ANCHOR_FILE, got[:16]))
    return out


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


NEVER_RETIRE = ("train.py", "corpus/MANIFEST.json", "corpus/build_corpus.py",
                "corpus/sources.json")

ANCHOR_FILE = "ANCHORS.json"


def _retirement_is_permitted(name, path, text):
    """May THIS version retire THIS path?

    ⛔ THE GUARD CHECKED THAT A RETIREMENT WAS WELL-FORMED, NOT THAT IT WAS WARRANTED. A round-7
    reviewer chained it: add a fabricated block to ANCHORS.json, mint a version with a short proof
    naming that block, and have it RETIRE train.py. The retirement is well-formed -- five lower
    versions pin train.py -- so it was allowed, and the experiment left the commitment table with
    the checker reporting success.

    ⇒ Two things can never be legitimate, and they are refused by name rather than by judgement:
    retiring an EXPERIMENTAL INPUT, and a version retiring the ANCHOR FILE THAT AUTHENTICATED IT.
    The second is the self-authenticating hole both reviewers found: the local file that decides a
    version is anchored must not be removable by the version it just blessed.

    ⚠ This does not close the circularity, and saying it does would be the overclaim. Offline,
    ANCHORED is a statement about a file we wrote. What is closed is the chained escalation.
    """
    if path in NEVER_RETIRE:
        return ("%s retires %r, which is an EXPERIMENTAL INPUT. 'This file stopped being checked' "
                "can never be legitimate for the pipeline or the corpus: retiring one is how a "
                "substitution stops being visible." % (name, path))
    if path == ANCHOR_FILE:
        # ⛔ THE CIRCULARITY, AND WHY BYTE-PINNING CANNOT RESOLVE IT. Anchoring a new protocol
        # version stamps it, which produces new Bitcoin attestations, which `pin_anchors.py` must
        # record in ANCHORS.json -- so the act of anchoring version N rewrites the very file
        # version N pins, and N is void the moment it becomes authoritative. No amount of care
        # fixes that; the commitment is the wrong SHAPE for the thing being committed.
        #
        # ⇒ A version may move the anchor file from a BYTE pin to a FACT pin: section 2d lists
        # (height, merkle root) pairs that must remain present and unchanged, while the file is
        # free to GROW. That is monotonic, so a later anchoring cannot invalidate an earlier
        # commitment, and it is strictly stronger than the byte pin in the way that matters --
        # reformatting the file cannot launder a changed root, and adding a fabricated block
        # cannot remove a real one.
        #
        # ⚠ The round-7 guard stands otherwise: retiring the anchor file while declaring NOTHING
        # in its place is still a version removing the root that authenticated it, and is refused.
        if anchor_facts(text):
            return None
        return ("%s retires %r -- the file whose contents decided that %s is anchored -- without "
                "declaring anchor facts in their place. A document may not remove the root that "
                "authenticated it; it may only replace a byte pin with a monotonic fact pin."
                % (name, path, name))
    return None


RETIRES_HEADING = "### RETIRES"


def retires(text):
    """Paths a version explicitly RETIRES from the commitment table.

    ⛔ v9 WAS INERT AND BOTH ROUND-7 REVIEWERS PROVED IT. `compose()` is a monotone union --
    every path any anchored version pins stays pinned, and a newer version wins only where it
    supplies a digest for the SAME path. v9's entire content was the ABSENCE of ANCHORS.json, and
    absence is not a statement. One reviewer forged v9's anchoring to put the tree in the state I
    was waiting for and asked the tool: ANCHORS.json, pinned by v8, still mismatched, exit 1, with
    v9 governing. The round-6 repair forbade the round-7 one.

    ⇒ Retirement is a DECLARATION, not an omission, and it is checked the way v8 section 2c checks
    the distribution subset: named explicitly, so a path can only leave the table by a document
    saying so under its own anchor.

    ⚠ A retirement is as load-bearing as a pin -- it is how a file stops being checked -- so it
    is refused unless some lower anchored version actually pinned that path. Retiring something
    nothing pinned is a no-op that reads like an action.
    """
    if RETIRES_HEADING not in text:
        return []
    body = text.split(RETIRES_HEADING, 1)[1].split(NL + "## ", 1)[0]
    out = []
    for line in body.splitlines():
        s = line.strip().lstrip("-*").strip()
        s = s.strip("`")
        if s and re.match(r"^[A-Za-z0-9_./-]+$", s) and "." in s:
            out.append(s)
    return out


def attested_heights(found):
    """Every height any ANCHORED version commits in its own §2d anchor-fact block.

    ⇒ v12. This is the set that makes the monotonic rule and the pin rule compatible. A height
      here was committed as a FACT by a document that is signed and anchored, so it cannot be
      introduced by anyone editing the tree -- which is the whole property the pin rule defends.
    """
    out = set()
    for _v, _name, _pins in found or ():
        try:
            out |= set(anchor_facts((HERE / _name).read_text(encoding="utf-8")))
        except (OSError, SystemExit):
            continue
    return out


def anchor_file_is_exact(attested=None):
    """Does ANCHORS.json pin EXACTLY the blocks our proofs name? (ok, why)

    ⛔ v12 — THE RULE WAS SET EQUALITY AND IT MADE THE TREE UNSATISFIABLE. §2d commits anchor
    facts MONOTONICALLY: "Every line must remain present and unchanged." This function required
    the pinned set to EQUAL the set the proofs currently name. The moment a proof was superseded,
    the heights it used to name stayed pinned -- because §2d forbids removing them -- and were
    reported as roots somebody added. On 5 September the tree failed on exactly that, with
    964878 and 964881, and NO edit to the anchor file could satisfy both rules: removing the
    lines violates an anchored document, keeping them failed here.

    Each rule was right when it was written. Neither was written knowing the other would outlive a
    superseded proof.

    ⇒ CONTAINMENT, NOT EQUALITY -- against what an ANCHORED VERSION COMMITTED, not against a list
      anyone can extend. A pinned height with no current proof is permitted only when some
      anchored version's §2d block commits it as a fact. That keeps the property this check
      exists for: the round-7 reviewer's fabricated block still fails, because getting a height
      into an anchored document's fact table needs the signing key and a Bitcoin block, not a text
      editor. And it stops punishing the tree for obeying §2d.

    ⚠ `attested` defaults to EMPTY, which is the strict old behaviour. A caller that forgets to
      pass it gets a check that is too harsh, never one that is too lenient -- the failure
      direction is the safe one.

    ⛔ A PIN NOBODY NEEDS IS A ROOT SOMEBODY ADDED. The file was checked block-by-block against
    the proofs, which never looks at a block no proof names -- so a round-7 reviewer added a
    fabricated block with a chosen root and every check still passed. Protected against DAMAGE,
    unprotected against EXTENSION, and extension is the direction an attack uses because every
    existing verification continues to succeed.

    ⚠ This is the OFFLINE half: set equality, no network. `pin_anchors.py --verify` does the
    other half by re-fetching each block. Neither closes the circularity -- the file still decides
    what ANCHORED means -- but an addition is no longer silent.
    """
    f = HERE / ("ANCHOR" + "S.json")
    if not f.exists():
        return True, "no anchor file"
    try:
        pinned = {int(k) for k in json.loads(f.read_text(encoding="utf-8"))["blocks"]}
    except Exception as e:                                                   # noqa: BLE001
        return False, "the anchor file does not parse: %s" % str(e)[:60]
    sys.path.insert(0, str(HERE))
    import pin_anchors as _PA
    named = set(_PA.heights())
    attested = set(attested or ())
    extra = sorted(pinned - named - attested)
    if extra:
        return False, ("%d block(s) are pinned that NO PROOF NAMES and NO ANCHORED VERSION "
                       "COMMITS: %s. A pin nobody needs is a root somebody added."
                       % (len(extra), extra[:4]))
    missing = sorted(named - pinned)
    if missing:
        return False, ("%d block(s) our proofs name are NOT pinned: %s, so those proofs are "
                       "STRUCTURAL only." % (len(missing), missing[:4]))
    carried = sorted((pinned - named) & attested)
    if carried:
        return True, ("%d pinned block(s): %d named by a current proof, %d carried as anchor "
                      "facts by an anchored version after their proof was superseded (%s)"
                      % (len(pinned), len(pinned & named), len(carried), carried[:4]))
    return True, "%d pinned block(s), exactly the set our proofs name" % len(pinned)


def anchor_file_is_self_invalidating(protocol, bad):
    """Is the ONLY mismatch the anchor file, differing by the authority's own blocks?

    ⛔ THE PACKET CLAIMED THE TREE GOES GREEN THE MOMENT v9 ANCHORS, AND IT DOES NOT. A round-9
    reviewer simulated the anchor and showed the shape: to promote a version its blocks must be in
    ANCHORS.json, and adding them changes the file that version pins -- so the version can be
    STRUCTURAL (blocks absent) or GOVERNING-AND-RED (blocks present), and never green. That is the
    circularity this project has been circling since round 7, arriving as a LIVENESS failure
    rather than an escalation: not a hole an attacker walks through, a state the honest path
    cannot leave.

    ⇒ Naming it is not fixing it. What is fixed here is that the checker stops calling it a
    substitution: a file that changed because the thing it records happened is a different
    situation from a file somebody swapped, and reporting them identically is how a permanently
    red line stops carrying information -- which a reviewer warned about two rounds ago.

    ⚠ STILL NON-ZERO. The state is unresolved and the exit code says so. The fix is v10's
    adopted design: report height and computed root as DATA, verdict unverified-here, and let a
    live re-fetch settle authority -- because no version can authenticate itself offline from a
    file its own anchoring rewrites.
    """
    if [rel for rel, _w, _a, _b in bad] != [ANCHOR_FILE]:
        return None
    try:
        import ots_verify as _OV
        doc = HERE / protocol
        _ok, _why, found = _OV.verify((HERE / (protocol + ".ots")).read_bytes(),
                                      doc.read_bytes())
        mine = sorted({int(h) for k, h, _r in (found or []) if k == "bitcoin"})
    except Exception:                                                        # noqa: BLE001
        return None
    if not mine:
        return None
    try:
        have = {int(k) for k in json.loads(
            (HERE / ANCHOR_FILE).read_text(encoding="utf-8"))["blocks"]}
    except Exception:                                                        # noqa: BLE001
        return None
    if not set(mine) <= have:
        return None
    return mine


def compose(found):
    """The cumulative commitment table: every path any anchored version pins, highest version wins.

    ⛔ v7 PINS TWELVE FILES AND NONE OF THEM IS THE EXPERIMENT. v3 pinned train.py,
    corpus/MANIFEST.json, corpus/build_corpus.py and corpus/sources.json; v6 pinned sixteen; v7
    pinned twelve and silently dropped all four. Both round-6 reviewers substituted train.py and
    corrupted the corpus manifest under v7 authority and both gates exited 0. **The selection
    attack the blocking rule above was written to stop was achieved by legitimate succession** --
    no forgery needed, just a successor that pins less. The rule guarded the direction the attack
    came from, not the property it was defending.

    ⇒ So authority is not "the highest anchored table" but the UNION of every anchored table, with
    the highest version's digest winning for any path two of them both pin. This is v8 section 2c's
    own equality-not-skip reasoning -- absence must be accounted for, never assumed benign --
    applied to succession instead of to the package.

    ⚠ A COMPOSED TABLE CAN REPORT A FILE AS CHANGED THAT NO CURRENT DOCUMENT PINS. That is not a
    bug in the composition; it is the situation being reported honestly. train.py's digest moved
    when two recording defects were repaired, and no ANCHORED document pins the new one, so the
    experiment is currently unpinned and this will say so.
    """
    table, whence, retired = {}, {}, {}
    for version, name, pinned in sorted(found, key=lambda x: x[0]):
        for path, digest in pinned:
            table[path] = digest
            whence[path] = (version, name)
            retired.pop(path, None)
        # ⛔ THIS PASSED "" AS THE DOCUMENT TEXT. `_retirement_is_permitted` took a `text`
        # parameter that its only caller had never supplied -- harmless while nothing read it,
        # and a false refusal the moment something did: the anchor-file rule asks whether the
        # retiring version declares anchor facts IN PLACE of the byte pin, and against an empty
        # string the answer is always no. v10 declares 21 facts and was refused for declaring
        # none. Exactly the shape a reviewer found in `undefined_module_reads(where=)` -- a
        # parameter with one caller that never passes it is untested by construction.
        _doc_text = (HERE / name).read_text(encoding="utf-8")
        for path in retires(_doc_text):
            if path not in table:
                raise SystemExit(
                    D + " %s RETIRES %r, which no lower anchored version pins. A retirement that "
                    "removes nothing reads like an action and is not one." % (name, path))
            _why = _retirement_is_permitted(name, path, _doc_text)
            if _why:
                raise SystemExit(D + " " + _why)
            del table[path]
            whence.pop(path, None)
            retired[path] = (version, name)
    return table, whence, retired


def declared_version(text):
    """The version the document's own SIGNED, ANCHORED BYTES claim.

    ⛔ THE VERSION THAT DECIDES PRECEDENCE WAS READ FROM THE FILENAME, WHICH NOTHING
    AUTHENTICATES. `re.search(r"-v(\\d+)-", f.name)` -- and `compose()` resolves every
    per-path digest conflict by "highest version wins". Every instrument in this pipeline is
    pinned at two to four distinct digests across the anchored history, because each version
    froze the then-current bytes, so which digest governs turned entirely on an unauthenticated
    string. A round-10 reviewer demonstrated it in two commands:

        cp PRE-REGISTRATION-v5-CONFIRMATORY.md      PRE-REGISTRATION-v101-CONFIRMATORY.md
        cp PRE-REGISTRATION-v5-CONFIRMATORY.md.ots  PRE-REGISTRATION-v101-CONFIRMATORY.md.ots

    v5 is genuinely anchored -- its proof parses, commits to its own bytes and names a real
    Bitcoin block -- so `anchored()` accepts the copy, and as the highest version its oldest
    `train.py` pin governs. The signed content still said "Pre-registration v5" while the
    filename said v101, and the composition trusted the filename over the bytes the signature
    covers.

    ⚠ BOUNDED, AND WORTH STATING PRECISELY: this is a DOWNGRADE, not a substitution. The
    winning digest must be one some real anchored document committed, and the attacker cannot
    invent one -- that needs a forged proof, which `ots_verify` still refuses. The harm is that
    anyone holding a historically-anchored (document, instrument) pair can relabel it highest,
    put that round's bytes on disk, and the tree goes green over a superseded pipeline the
    current protocol does not intend, with every control passing.

    ⇒ Reading the version from the H1 title closes it completely. To make `declared_version`
    return 101 an attacker must edit the document body, and the proof commits to those bytes,
    so `anchored()` refuses. The ordering key is now covered by the same anchor as the table.
    """
    # ⛔ THIS KNEW ONE TITLE FORM AND THE CORPUS HAS TWO. v2 and v3 are headed "Confirmatory
    # pre-registration, version N", not "Pre-registration vN", so this returned None for both --
    # and since round 10 made an unversioned candidate a REJECTION, two legitimate historical
    # documents silently stopped contributing to the composed table. Nobody noticed because they
    # are superseded and their pins are subsets of later ones. A repair that recognises one
    # spelling of a thing is the substring-for-a-token defect wearing a title.
    #
    # ⚠ Both forms are read out of the H1, which is inside the bytes the proof commits to. The
    # rule is "a version stated in the title", not "stated the way v4 onward states it".
    # ⚠ A UTF-8 BOM MADE A VERSIONED DOCUMENT READ AS UNVERSIONED. The first line
    # begins \ufeff# and does not start with a hash, so the title was never found and a real
    # protocol document would be refused for having no version. Windows tools write BOMs by
    # default; the parser strips it rather than blaming the author.
    _h1 = next((ln for ln in text.splitlines() if ln.lstrip(chr(65279)).strip().startswith("#")), "")
    m = re.search(r"\bv(\d+)\b", _h1) or re.search(r"\bversion\s+(\d+)\b", _h1, re.I)
    if m:
        return int(m.group(1))
    if re.search(r"pre-registration", _h1, re.I):
        return 1
    return None


class Rejection(typing.NamedTuple):
    """One rejected protocol candidate, as a NAMED record rather than a bare tuple.

    ⛔ WHY THIS IS NOT A TUPLE. The rejection grew a fifth field (`has_table`) when the NO-TABLE
    state was added. `check_commitments.py` was updated; `build_package.py` line 258 still wrote
    `for _v, _n, _why, _state in _rejected:` and died with

        ValueError: too many values to unpack (expected 4)

    the first time a legitimate PENDING successor existed -- i.e. the shipping build path was
    broken by the next ordinary protocol round, and nothing failed until then. A reviewer found it
    by minting a synthetic v10.

    ⇒ Widening a positional tuple silently breaks every call site that unpacks it, and the breakage
    is invisible until the new shape actually occurs. A NamedTuple is still a tuple, so existing
    index and iteration code keeps working, but callers that read `.state` and `.has_table` by name
    keep working across the NEXT widening too. This is the sibling of the rule this project already
    states about hand-kept lists: a fix is not finished until you have grepped for the other call
    sites -- and better than grepping is a shape that does not need it.
    """
    version: object
    name: str
    why: str
    state: str
    has_table: bool


def governing(here, _raise_on_blocking=True):
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
        _body = f.read_text(encoding="utf-8")
        # ⇒ THE TABLE IS PARSED FIRST so a version rejection can say whether the document it
        # refuses carries commitments. A relabelled file with no table is litter; a relabelled
        # file WITH a table is someone presenting an authority, and the two must not exit alike.
        _pinned_probe = commitments(_body)
        m = re.search(r"-v(\d+)-", f.name)
        _named = int(m.group(1)) if m else 1
        version = declared_version(_body)
        if version is None:
            rejected.append(Rejection(_named, f.name,
                             "no version in the document's own title line, so its precedence "
                             "would have to come from the filename, which no proof or signature "
                             "covers", "UNVERSIONED",
                             bool(_pinned_probe)))
            continue
        if version != _named:
            rejected.append(Rejection(_named, f.name,
                             "the FILENAME says v%d and the signed, anchored CONTENT says v%d. "
                             "Precedence is decided by the content. A relabelled copy of a real "
                             "anchored document is how an old table is promoted over a new one."
                             % (_named, version), "RELABELLED",
                             bool(_pinned_probe)))
            continue
        pinned = commitments(_body)
        if not pinned:
            # ⛔ A SILENT `continue` WAS THE WHOLE HOLE. `DIGEST_LINE` matches only
            # `path<whitespace>64hex` on its own line, so a document whose table is written as a
            # markdown pipe-table, or `path: hash`, or digest-first, parses as ZERO commitments
            # and fell out here -- not in `found`, not in `rejected`, no output whatsoever. Both
            # round-12 reviewers built a "Pre-registration v101/v50" with a pipe-table and
            # `governing()` never mentioned it. The fatal-rejection scope added last round fires
            # on 1 <= pinned < MIN_EXPECTED; zero pins escaped it entirely, because the scope test
            # was `bool(pinned)` and `pinned` is the output of the parser under test.
            #
            # ⇒ THIS IS THE v2/v3 DEFECT ONE LEVEL OVER -- title-form then, table-form now, and
            # the same consequence: a legitimate higher version silently stops governing and
            # nobody notices, because silence is what it produces. A document that CARRIES
            # digests the parser could not read is a broken check, not litter, and says so.
            # ⚠ ANY 64-hex WAS TOO BROAD AND REFUSED A LEGITIMATE DOCUMENT. v2 mentions one
            # digest in prose and pins nothing -- it names files, which is the whole reason v3
            # exists -- and v4 amends a measurement with no table at all. Both were refused by the
            # first version of this rule, which is the v2/v3 title defect repeating inside the fix
            # for the v2/v3 title defect. MIN_EXPECTED is already this project threshold for
            # what counts as a table, so it is what distinguishes a table the parser cannot read
            # from a document that legitimately has none.
            _rows = presents_table(_body)
            if _rows:
                rejected.append(
                    Rejection(_named, f.name,
                     "lays out %d commitment row(s) -- a path beside a digest, in table shape -- " % _rows +
                     "and this parser reads NONE of them, so the table is in a layout "
                     "`DIGEST_LINE` does not match. An empty parse of a document that plainly "
                     "has a table is a broken check, not an absent one.",
                     "NO-TABLE", True))
            continue
        if len(pinned) < MIN_EXPECTED:
            # ⛔ A THREE-TUPLE WHERE THE CONSUMER UNPACKS FOUR. This rejection path
            # raised ValueError instead of reporting, which is the same class as the eight
            # crashing error paths the sibling project found this round: a control that fires
            # and then destroys its own message. Found by adding a second rejection beside it.
            rejected.append(Rejection(version, f.name,
                             "parses only %d commitment(s); the table's format has changed and "
                             "this parser no longer reads it" % len(pinned), "UNPARSEABLE",
                             True))
            continue
        ok, why, state = anchored(f)
        if not ok:
            rejected.append(Rejection(version, f.name, why, state, bool(pinned)))
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
    # ⛔ THIS RAISE LIVED INSIDE `governing()`, WHICH IS A QUESTION, NOT A VERDICT. Any caller
    # asking "which document is authority here" was killed by it -- and one such caller is
    # `test_controls.py:_governing`, so the whole control suite died after its first attack the
    # moment v9 anchored. While v9 was PENDING the raise was suppressed and the suite ran; the
    # act of anchoring, which is the thing the protocol wants, made the suite unrunnable.
    #
    # ⚠ The classification is unchanged and nothing is now permitted that was not permitted
    # before: `governing()` REPORTS the blocking condition and `main()` still refuses on it. A
    # library function that exits the process cannot be asked a question by a control.
    # ⛔ A REFUSAL THAT EXITS 0 IS A WARNING. Round 10 closed the version spoof -- a relabelled
    # v5 no longer GOVERNS -- and a round-11 reviewer showed the checker printed
    # "NOT AUTHORITY [RELABELLED]" and then exited 0, so a relabelled higher protocol can sit in a
    # green tree indefinitely. Not letting it govern is not the same as refusing it, and a tree
    # containing a document that presents itself as a higher authority is not a clean tree.
    #
    # ⚠ Scoped to candidates that CARRY A COMMITMENT TABLE. A stray file with a version-shaped
    # name and no table is litter and must not fail a build.
    # ⛔ THE NAMED RECORD PROTECTED EVERY CALLER EXCEPT ITS OWN MODULE. `build_package.py` and
    # `main()` were converted to named fields last round and the claim was made that widening a
    # Rejection can no longer break a caller -- while these two comprehensions inside
    # `governing()` still unpacked five positionally. BOTH round-14 reviewers found it by adding
    # a sixth field and watching `ValueError: too many values to unpack` fire on the governing
    # path itself. The repair's claim was false where it mattered most.
    _presenting = [r for r in rejected
                   if r.has_table
                   and r.state in ("RELABELLED", "UNVERSIONED", "UNPARSEABLE", "NO-TABLE")]
    if _presenting:
        raise SystemExit(
            D + " %d document(s) present a commitment table under a version this tree cannot "
            "accept: %s. Not letting them govern is not the same as refusing them; a tree that "
            "contains an unacceptable authority is not clean."
            % (len(_presenting), [(r.name, r.state) for r in _presenting[:3]]))

    if found:
        top = max(v for v, _n, _p in found)
        blocking = [r for r in rejected
                    if r.version > top and r.state in ("TAMPERED", "MISSING")]
        if blocking and _raise_on_blocking:
            raise SystemExit(
                D + " %s is present, is a HIGHER version than the authority %s would select, and "
                "its proof is not a proof (%s). Falling back to an older document would enforce a "
                "SMALLER table -- v5 pins 4 files where v6 pins 16 -- so destroying a proof would "
                "make this check weaker and still pass. A protocol document whose proof has been "
                "destroyed is a tampered tree, not an older one."
                % (blocking[-1].name, "the next version down", blocking[-1].why[:60]))
    return found, rejected


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    found, rejected = governing(HERE)
    # ⛔ SECOND ARITY CRASH ON A REJECTION PATH IN THREE ROUNDS. Round 10's rejection appended a
    # 3-tuple where the consumer unpacked 4; round 12 added the table flag and this reporter still
    # unpacked 4 of 5. Both were found only because a case was added beside them -- the shape a
    # round-11 reviewer asked us to confirm the tooling covers, and it does not. Named fields
    # would end the class; until then this unpacks by length so a reporter cannot be the thing
    # that crashes while reporting.
    # ⚠ Reading by NAME now that a rejection is a `Rejection` record. Unpacking by length was the
    # right defensive move while it was a bare tuple; a named field ends the class, which is what
    # the comment above asked for.
    for _rej in sorted(rejected, reverse=True):
        print("  " + W + " %-46s NOT AUTHORITY [%s]: %s" % (_rej.name, _rej.state, _rej.why))
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
        # ⛔ "IT BECOMES A VIOLATION IF v11 NEVER ANCHORS" WAS PRINTED AND NEVER DETERMINED. PENDING
        # is not in the blocking set, so a proof that parses, commits to the right bytes and
        # carries a calendar attestation but never receives a Bitcoin block stays PENDING FOREVER:
        # a round-14 reviewer observed that one hour, one month and one year produced identical
        # output and an identical exit code. An abandoned successor would then block publishing
        # indefinitely without ever being a violation -- absorbed rather than reported.
        #
        # ⇒ THE CHAIN IS THE CLOCK. If this tree holds proofs anchored in blocks mined well after
        # the pending document was written, that document has had ample opportunity to anchor and
        # has not. No new trust root: the block timestamps are already pinned in ANCHORS.json and
        # already agreed by independent operators.
        #
        # ⚠ The comparison uses the pending file's mtime, which is the weakest part and is stated
        # as such: mtime is not evidence, and a tree copied without timestamps will read as young
        # rather than old. It fails SAFE in that direction -- it can only under-report staleness.
        try:
            _newest = max(int(b.get("timestamp") or 0) for b in json.loads(
                (HERE / ANCHOR_FILE).read_text(encoding="utf-8"))["blocks"].values())
        except Exception:                                                    # noqa: BLE001
            _newest = 0
        _pend_doc = next((f for f in HERE.glob("PRE-REGISTRATION*.md")
                          if declared_version(f.read_text(encoding="utf-8")) == _pending), None)
        if _newest and _pend_doc:
            _age_days = (_newest - _pend_doc.stat().st_mtime) / 86400.0
            if _age_days > STALE_PENDING_DAYS:
                print()
                raise SystemExit(
                    D + " v%d has been PENDING while this tree anchored proofs in blocks mined "
                    "%.1f days after it was written, and %d days is the bound. A proof that "
                    "cannot get into a block that others are getting into is not waiting; it is "
                    "not going to anchor. Re-stamp it or withdraw it -- an abandoned successor "
                    "blocks publishing forever without ever being a violation."
                    % (_pending, _age_days, STALE_PENDING_DAYS))
            print("  v%d has been pending for at most %.1f day(s) against a bound of %d."
                  % (_pending, max(0.0, _age_days), STALE_PENDING_DAYS))
        if "--publishing" in sys.argv:
            raise SystemExit(
                D + " v%d is pending and this is a PUBLISHING run. Publish under an anchored "
                "protocol or wait for the anchor." % _pending)
    # ⛔ THE AUTHORITY'S OWN TABLE IS NOT THE COMMITMENT. Every anchored version's pins are
    # composed, highest wins, because v7 dropped the four files v3 pinned -- train.py and the
    # corpus -- and under v7 alone the experiment was checked by nothing.
    _composed, _whence, _retired = compose(found)
    _inherited = sorted(k for k, (v, _n) in _whence.items() if v != version)
    pinned = sorted(_composed.items())

    _aok, _awhy = anchor_file_is_exact(attested_heights(found))
    if not _aok:
        raise SystemExit(D + " the anchor file is not exactly what the proofs require: " + _awhy)

    print("=" * 78)
    print("  COMMITMENTS — every file any ANCHORED version pins, highest version wins")
    print("=" * 78)
    print()
    print("  authority %s (v%d), composed over %d anchored version(s): %d path(s)"
          % (PROTOCOL, version, len(found), len(pinned)))
    if _retired:
        print("  " + W + " %d path(s) are RETIRED by an anchored version and are no longer"
              % len(_retired))
        print("  checked. A retirement is a declaration, not an omission:")
        for _k, (_v, _n) in sorted(_retired.items()):
            print("      %-28s retired by v%d" % (_k, _v))
        print()
    if _inherited:
        print("  " + W + " %d path(s) are INHERITED from an older version because v%d does not"
              % (len(_inherited), version))
        print("  pin them. Under the authority's own table alone these were checked by nothing:")
        for k in _inherited[:6]:
            print("      %-28s pinned by v%d" % (k, _whence[k][0]))
    print()

    if len(pinned) < MIN_EXPECTED:
        print("  " + D + " parsed only %d commitment(s) from %s; expected at least %d."
              % (len(pinned), PROTOCOL, MIN_EXPECTED))
        print("  The table's format has changed and this parser no longer reads it. That is a")
        print("  BROKEN CHECK, not a pass: fix the parser before trusting anything below.")
        return 1

    # the subset a distribution is allowed to be, read from the ANCHORED document
    # ⛔ A FACT PIN THAT NOTHING CHECKS IS A NOTE. Section 2d is the mechanism that resolves the
    # anchor-file circularity, so it is verified on every run, over every ANCHORED version's
    # facts rather than only the newest -- an older version's committed root does not stop being
    # committed because a newer document exists. Monotonic: absent or changed is a failure,
    # additional heights are not.
    # ⛔ AND `dict.update()` LET A NEWER VERSION OVERWRITE AN OLDER VERSION'S COMMITTED ROOT --
    # the same lie one level up. The comment above says an older version's committed root does not
    # stop being committed because a newer document exists, and `update` did exactly that
    # silently. A contradiction between two anchored versions about the same height is not a
    # precedence question: both are signed, both are anchored, and the chain has one answer, so
    # the tree is broken and says so.
    _facts, _whence = {}, {}
    for _v, _name, _p in found:
        for _h, _r in anchor_facts((HERE / _name).read_text(encoding="utf-8")).items():
            if _h in _facts and _facts[_h] != _r:
                raise SystemExit(
                    D + " %s and %s COMMIT DIFFERENT ROOTS for height %d (%s vs %s). Two anchored "
                    "versions cannot disagree about a settled block; one of them is not describing "
                    "the chain." % (_whence[_h], _name, _h, _facts[_h][:16], _r[:16]))
            _facts[_h] = _r
            _whence.setdefault(_h, _name)
    if _facts:
        _bad_facts = anchor_facts_hold(_facts)
        if _bad_facts:
            print()
            print("  " + D + " %d ANCHOR FACT(S) NO LONGER HOLD:" % len(_bad_facts))
            for _b in _bad_facts[:6]:
                print("      " + _b)
            raise SystemExit(D + " a committed anchor fact changed or vanished. The chain does "
                             "not move; this file did.")
        print("  ok  %d anchor fact(s) still hold in %s (monotonic: growth is permitted)"
              % (len(_facts), ANCHOR_FILE))

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
            # ⛔ THIS REMOVED THE FILE FROM `bad`, so a changed committed file became exit 0 on
            # the strength of a document that "governs nothing". A round-6 reviewer wrote a
            # synthetic pending v9 containing the digest of a train.py they had just modified and
            # the check went green. A pending document has no authority BY DEFINITION -- that is
            # what pending means -- so it cannot excuse a mismatch, only explain one.
            #
            # ⚠ The build may continue past a non-zero commitment result; that is build_package's
            # decision to make and it says so loudly. What must not happen is the COMMITMENT CHECK
            # reporting green. Reported, not excused.
            for rel, why, want, got in list(bad):
                if why == "changed" and _ptable.get(rel) == got:
                    _transitional.append(rel)

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
        print("  " + D + " THIS IS STILL A MISMATCH AGAINST THE ANCHORED PROTOCOL and is counted")
        print("  as one. A pending document explains a change; it cannot authorise one.")
        print()
    _selfinv = anchor_file_is_self_invalidating(PROTOCOL, bad) if bad else None
    if _selfinv:
        print()
        print("  " + D + " THE ONLY MISMATCH IS THE ANCHOR FILE, AND IT CHANGED BECAUSE THIS")
        print("  VERSION ANCHORED. %s attests to Bitcoin block(s) %s, and those blocks had to be"
              % (PROTOCOL, _selfinv))
        print("  added to %s for the attestation to be checkable -- which changes the file this"
              % ANCHOR_FILE)
        print("  version pins. A version can be STRUCTURAL with its blocks absent or GOVERNING")
        print("  AND RED with them present, and never green.")
        print()
        print("  " + W + " This is NOT a substitution and is not reported as one -- but it is")
        print("  unresolved, so this still exits non-zero. The fix is the adopted v10 design:")
        print("  report height and computed root as DATA, verdict unverified-here, and let a live")
        print("  re-fetch settle authority. No version can authenticate itself offline from a")
        print("  file its own anchoring rewrites.")
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
