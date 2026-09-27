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
# ⚠️ ONE QUESTION ONLY, NOW. This once meant both "how many pins make a table" and "how many
# loose digests make an empty parse suspicious", and round 9 found it answering a third: whether a
# complete parse of a SMALL table is a broken parser. It is not, and the completeness comparison in
# `governing()` replaced it there. What is left is the honest use.
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
# The distribution subset says what it is, in the one place a fence can carry a name that no
# heading owns and no example acquires by accident. See `distribution_subset`.
# _SUBSET_FENCE was a regex here until round 13; see `_fenced_blocks` for why a regex cannot
# read a fence. The name is kept so an importer fails loudly rather than silently on a None.
_SUBSET_FENCE = None
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

    ⛔⛔ AND THE FIX WAS DEFEATED BY A RENUMBERED HEADING. v15 called its tables 3a-3d instead of
    2a-2d, so this function did not find its heading, stripped NOTHING, and every one of v15's 30
    anchor heights was parsed as a committed FILE PATH. v15 is anchored, so `compose()` inherited
    all 30 permanently and `check_commitments` reported them MISSING forever.

    ⇒ THE STRIP IS NOW STRUCTURAL, NOT POSITIONAL. A fenced block whose every non-blank line is
    anchor-fact shaped IS an anchor-fact block, whatever heading sits above it or whether one does.
    That repairs every already-anchored version at parse time -- commitments are re-derived from
    each document on every run, never stored -- so no retirement list is needed and none is written.
    ⚠ Retiring the 30 names would have been an enumeration, and the next renumbering would have
    recreated them under different numbers.

    ⚠ A block must be non-empty to qualify: an empty fence is not an anchor-fact block, and treating
    it as one would strip a real table that happened to be blank.
    """
    out, pos = [], 0
    for start, end, _pairs in _anchor_fact_blocks(text):
        out.append(text[pos:start])
        pos = end
    out.append(text[pos:])
    return "".join(out)


def commitments(text):
    """(path, digest) for every file a protocol version pins. Read out, never retyped.

    ⛔ THE STRIP AND THE READER MUST AGREE, AND THIS REFUSES IF THEY EVER STOP. They were separate
    implementations and diverged: the strip removed blocks the reader could not find, so a document
    could have its facts deleted from the commitment table and contributed to no fact table either
    -- committed to nothing, silently, with every check green.

    ⇒ They now share `_anchor_fact_blocks`, which makes that unreachable. The assertion stays
    anyway: it costs nothing, and "unreachable by construction" is what was believed about the
    previous arrangement.
    """
    _blocks = _anchor_fact_blocks(text)
    if _blocks and not anchor_facts(text):
        raise SystemExit(
            D + " %d anchor-fact block(s) were stripped from the commitment table and the fact "
            "reader returned nothing. A document whose facts are removed from one side and absent "
            "from the other is committed to neither, and every check downstream would pass."
            % len(_blocks))
    return [(m.group(1), m.group(2).lower())
            for m in DIGEST_LINE.finditer(_without_anchor_facts(text))]


BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])


def _after_heading(text, heading):
    """Text following HEADING where it appears AS A HEADING -- at the start of a line.

    ⛔ THE LOOKUPS USED `text.split(heading, 1)`, WHICH MATCHES THE FIRST OCCURRENCE ANYWHERE. A
    document that DISCUSSES its own structure therefore rewrites it: v16's first draft quoted these
    constants with their values, so the marker appeared in prose ahead of the real heading.
    `anchor_facts` then parsed the explanation, and `distribution_subset` did not fail -- it
    returned the INSTRUMENTS table, eighteen entries of the wrong list, silently.

    ⇒ A heading is a line that STARTS with the marker. Prose that mentions it is prose. Returns
    None when absent, so a caller must decide rather than receive an empty string.

    ⛔ AND IT TOOK THE FIRST OF SEVERAL WITHOUT SAYING SO. Moving the match to line-start fixed
    prose-versus-heading and left the other half of the same defect: if the marker heads TWO lines,
    this returned the first and the second was read by nobody. v18 arrived with `## 2d.` narrating
    round 2 and `### 2d.` carrying the anchor facts -- two sections a reader calls "2d" -- which is
    the v15 renumbering hazard rebuilt by hand, and the only reason it was harmless is that the
    fact table stopped being found by heading at all.

    ⇒ AMBIGUITY IS A REFUSAL. A marker that names more than one place names none, and choosing
    silently is how a document quietly rewrites its own structure.
    """
    _all = list(re.finditer(r"^" + re.escape(heading), text, re.M))
    if len(_all) > 1:
        raise SystemExit(
            D + " the heading %r begins %d lines of this document. A marker that identifies more "
            "than one section identifies none, and taking the first silently is how v15's "
            "renumbering went unnoticed for two protocol versions." % (heading, len(_all)))
    return text[_all[0].end():] if _all else None


# ⚠ RESERVED, AND DELIBERATELY NOT USED TO FIND ANYTHING. `2a.`-`2d.` name the four commitment
# tables in every version since v15, and the strip became structural precisely so that no reader
# depends on them. The constant stays as the written record of the reservation -- a version that
# reuses these labels for narrative is the collision `_after_heading` now refuses -- and any code
# that starts locating facts by it has reintroduced the defect that cost v16 and v17.
ANCHOR_FACTS_HEADING = "### 2d."
# ⛔ THIS ENDED AT `\s*$` WHILE `DIGEST_LINE` PERMITTED A TRAILING `# comment`, AND THE STRIP
# REQUIRED *EVERY* LINE TO MATCH THIS ONE. So a single annotated height -- `965840  <root>  # the
# block that anchored v16`, which v17 §2d says in prose one line above its own table -- disqualified
# the whole block, and all 32 heights were parsed as committed FILE PATHS on a signed, anchored
# version. A reviewer ran it and reported the exact counts.
#
# ⚠ `_ROW`'s comment block above records this identical class -- "the two patterns disagreed about
# the line's tail, and the disagreement was fatal" -- fixed between the DETECTOR and the PARSER and
# left in place between the STRIP and the parser. Fixing one instance of a class and leaving its
# sibling is how this project keeps producing the same defect in a new place.
ANCHOR_FACT_LINE = re.compile(r"^\s*(\d{6,9})\s+([0-9a-fA-F]{64})\s*(?:#.*)?$", re.M)


# ⛔ THE TWO TOKENS, EACH DEFINED WITHOUT REFERENCE TO ITS SURROUNDINGS. These deliberately do NOT
# reuse ANCHOR_FACT_LINE: the whole purpose is to see what that pattern cannot, so sharing it would
# reproduce the defect this pair was written to end. Where a check and the thing it checks must
# differ, they differ here, on purpose and in one place.
_DIGEST_TOKEN = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64,}(?![0-9a-fA-F])")
_HEIGHT_TOKEN = re.compile(r"(?<![0-9])[0-9]{6,9}(?![0-9])")


# ⛔ A HEIGHT IS MADE OF HEX CHARACTERS TOO, so a height written HARD AGAINST its digest is one
# unbroken hex run and the digest token swallows the pair whole:
#
#     964534aaaaaaaa...aaaa      -> _anchor_shaped_lines []  -> anchor_facts {}
#
# A reviewer executed that against the real parser. The rule claimed to describe neither token in
# terms of what surrounds it, and a token with NOTHING around it defeated it.
#
# ⇒ A run of 70-73 hex characters is a 6-9 digit height followed by a 64-character digest, and
# nothing else this project writes looks like that. Split it and the pair is visible again.
_FUSED = re.compile(r"(?<![0-9a-fA-F])([0-9]{6,9})([0-9a-fA-F]{64})(?![0-9a-fA-F])")


def _anchor_shaped_lines(text):
    """[(offset, line)] for every line stating a height beside a digest, however it is decorated.

    The digests come out FIRST -- a digest contains digit runs of its own, and leaving them in
    would let the height be found inside the very token it is supposed to sit beside.
    """
    out, pos = [], 0
    for line in text.split(NL):
        probe = _FUSED.sub(lambda m: m.group(1) + " " + m.group(2), line)
        if _DIGEST_TOKEN.search(probe) and _HEIGHT_TOKEN.search(_DIGEST_TOKEN.sub(" ", probe)):
            out.append((pos, line))
        pos += len(line) + 1
    return out


# ⛔ AND A DIGEST ONE CHARACTER SHORT WAS SILENTLY IGNORED. `964534  <63 hex>` is not a fact this
# parser can read, and it was not a fact this parser complained about either -- it simply vanished,
# which is the whole failure class.
#
# ⚠ THE FIX IS CONTEXTUAL, BECAUSE A GLOBAL ONE WOULD BE WRONG. Lowering the digest threshold
# everywhere would make ordinary prose -- "965840 -> 8aac2039, the block that anchored v16" -- into
# a malformed fact, and these documents abbreviate digests beside heights on purpose. So: in PROSE
# a short hash beside a height stays prose; inside a FENCED BLOCK that otherwise presents itself as
# a fact table, a height beside a hash-shaped run that is not 64 characters is a MALFORMED FACT and
# is refused rather than dropped.
_NEARLY = re.compile(r"(?<![0-9a-fA-F])([0-9]{6,9})[^0-9a-fA-F]+([0-9a-fA-F]{16,63}|"
                     r"[0-9a-fA-F]{65,})(?![0-9a-fA-F])")


def _malformed_fact_rows(block):
    """Rows inside a fenced block that are ALMOST anchor facts. [(row, why)]."""
    bad = []
    for row in block.split(NL):
        if not row.strip() or ANCHOR_FACT_LINE.match(row):
            continue
        m = _NEARLY.search(row)
        if m:
            bad.append((row.strip(), "height %s beside a %d-character hex run"
                        % (m.group(1), len(m.group(2)))))
    return bad


def _anchor_fact_blocks(text):
    """Every fenced block that IS an anchor-fact table: [(start, end, [(height, root), ...])].

    ⛔ ONE FINDER, USED BY BOTH THE STRIP AND THE READER. They were separate: the strip was
    structural and removed every qualifying block; the reader located `### 2d.` and took the FIRST
    bare fence after it. Three consequences, all reported by a reviewer and all reproduced here:

      * a document with TWO fact blocks had both stripped and only the first read, so the second
        block's heights were silently committed to nothing;
      * a renumbered heading stripped correctly and declared ZERO facts, silently -- the reader
        failing quietly while the strip succeeded;
      * a fence tagged ```text was invisible to the strip (which required a bare fence) and visible
        to `_FENCE` everywhere else.

    ⇒ Sharing the finder makes those states unreachable rather than merely fixed.

    ⚠ THE ASSUMPTION, STATED RATHER THAN HIDDEN: a fenced block whose every row is a 6-9 digit
    token beside 64 hex characters is an anchor-fact table. An anchor fact and a commitment are
    genuinely indistinguishable by shape -- a file could legally be NAMED `964534`. This rule
    therefore misreads a commitment table all of whose paths are bare 6-9 digit numbers, and no
    such table exists or is ever likely to. The alternative -- trusting a heading -- is what cost
    three protocol versions.
    """
    out = []
    for m in _FENCE.finditer(text):
        rows = [l for l in m.group(1).split(NL) if l.strip()]
        if not rows or not all(ANCHOR_FACT_LINE.match(l) for l in rows):
            continue
        out.append((m.start(), m.end(),
                    [(int(x.group(1)), x.group(2).lower())
                     for x in ANCHOR_FACT_LINE.finditer(m.group(1))]))

    # ⛔ ELEVEN CONTROLS WERE ELEVEN SHAPES A REVIEWER HAD NAMED -- bare, trailing comment, tagged
    # fence, second block, renumbered heading -- which is ENUMERATION STANDING IN FOR PROJECTION,
    # inside the repair for the defect this project calls enumeration-for-projection. The next
    # unnamed shape wins, and a reviewer found two more in ten minutes:
    #
    #   a comment on its own LINE inside the fence   -> block disqualified, heights become PATHS
    #   an INDENTED fence (a list item)              -> no blocks at all; facts=0 AND commitments=0,
    #                                                   so the two halves "agree" on nothing and the
    #                                                   disagreement assertion cannot fire
    #
    # ⇒ THE PROJECTION, WHICH DOES NOT DEPEND ON KNOWING THE SHAPE. Every anchor-fact-shaped line in
    # the document must be accounted for by some block. A line the document commits and no reader
    # reads is the whole failure class, however the fence around it is written.
    # ⛔ THE PROJECTION PROJECTED OVER ITS OWN PREDICATE, AND A REVIEWER WALKED THROUGH IT. `_raw`
    # used ANCHOR_FACT_LINE -- the same pattern as the detector -- so any prefix the pattern does
    # not expect ('> ', '| ', '- ') hides a line from the CHECK and from the THING IT CHECKS alike,
    # and the two agree on having seen nothing. Real v18 with its fact table rewritten as a pipe
    # table reported 25 commitments and 0 facts, silently.
    #
    # ⇒ COUNT THE DIGESTS, NOT THE LINES. A 64-hex token beside a 6-9 digit number is an anchor
    # fact however the row around it is decorated, and **a digest cannot be reformatted away**.
    #
    # ⛔⛔ AND THAT REPAIR WAS DEFEATED BY THE SAME MOVE, A THIRD TIME. It read
    #     ^[^0-9a-fA-F]*?(\d{6,9})[^0-9a-fA-F]+([0-9a-fA-F]{64})\b
    # -- "the text before the height contains no hex character". But 0-9 and a-f ARE hex, so a
    # prefix containing a digit or any of a-f made the line invisible: `1. 964534 <root>`,
    # `Block 964534 <root>`, `height 964534: <root>`, `at height 964534 the root is <root>`, and
    # a row written digest-first. A reviewer listed five and there was no reason to think five was
    # the number. The rule was blind wherever the parser was blind and the two agreed on nothing,
    # which is the property the projection exists to make impossible.
    #
    # ⇒ THE PREDICATE NOW DESCRIBES NEITHER HALF IN TERMS OF WHAT SURROUNDS IT. Remove the digests
    # from the line first, then ask whether a height survives in what is left. No prefix, bullet,
    # quotation mark, pipe, cell, link or ordering can hide either token, because the rule never
    # looks at anything except the two tokens themselves.
    #
    # ⚠ THE ONE BOUND, STATED: a digest is a hex run of SIXTY-FOUR OR MORE. Sixty-four exactly is a
    # SHA-256; more is a malformed one, and it is included deliberately -- appending a character to
    # the only row of a one-row block would otherwise disqualify the block and leave nothing for
    # this rule to notice. Runs SHORTER than 64 are excluded because these documents legitimately
    # abbreviate digests in prose beside heights (38 such runs exist in this tree today), so a
    # lower threshold would fail on correct documents rather than on wrong ones.
    # ⇒ A BLOCK THAT LOOKS LIKE A FACT TABLE AND CONTAINS A MALFORMED ROW IS REFUSED, not
    # silently skipped. "Almost a fact" inside a fence is the one place a short or over-long digest
    # cannot be prose.
    for _m in _FENCE.finditer(text):
        _rows = [l for l in _m.group(1).split(NL) if l.strip()]
        if not _rows:
            continue
        _good = sum(1 for l in _rows if ANCHOR_FACT_LINE.match(l))
        _bad = _malformed_fact_rows(_m.group(1))
        if _bad and (_good or len(_bad) == len(_rows)):
            raise SystemExit(
                D + " a fenced block presents as an anchor-fact table and %d row(s) are malformed "
                "(%s: %s). A row that is almost a fact is a fact this parser would drop, and a "
                "dropped height is committed to nothing."
                % (len(_bad), _bad[0][1], _bad[0][0][:60]))

    _loose = [(_o, _l) for _o, _l in _anchor_shaped_lines(text)
              if not any(_s <= _o < _e for _s, _e, _p in out)]
    if _loose:
        # ⚠ POSITIONAL, NOT A COUNT. `raw > accounted` compares two totals, and two totals can
        # agree while naming different lines -- a disqualified block of n facts and n shaped lines
        # loose elsewhere cancel exactly. Each shaped line must lie INSIDE a block that was read.
        raise SystemExit(
            D + " %d anchor-fact-shaped line(s) in this document are accounted for by no block "
            "(%d fact(s) read). A height the document states and no reader parses is committed to "
            "nothing, and every check downstream would pass. First one:%s    %s"
            % (len(_loose), sum(len(p) for _s, _e, p in out), NL, _loose[0][1].strip()[:120]))
    return out


def anchor_facts(text):
    """(height -> merkle root) a version commits to, as FACTS rather than as file bytes.

    ⛔ WHY THIS SHAPE. ANCHORS.json was pinned by digest, and anchoring a new version rewrites it
    -- so every version was void the instant it became authoritative. The commitment being wrong
    was not carelessness; a byte pin cannot express "this file may grow but never lie".

    ⇒ A fact pin is MONOTONIC: each listed height must still carry the listed merkle root, and new
    heights are permitted. Later anchoring adds; it never contradicts. Anyone can re-derive every
    line from the chain, which is the property a digest of the file never had.
    """
    # ⛔ THIS LOCATED THE TABLE BY HEADING AND READ ONLY THE FIRST FENCE AFTER IT, while the strip
    # removed EVERY qualifying block. A document with two fact blocks therefore had both stripped
    # and one read, and a renumbered heading produced zero facts SILENTLY. Both halves now come
    # from `_anchor_fact_blocks`, so "stripped" and "read" cannot disagree.
    #
    # ⚠ ALL BLOCKS ARE MERGED, not just the first. A version may legitimately table its facts in
    # more than one fence -- and if it does, every one of them is a commitment.
    _blocks = _anchor_fact_blocks(text)
    if not _blocks:
        return {}
    # ⛔ THE MERGE TURNED A DOCUMENTATION EXAMPLE INTO A TREE-WIDE DENIAL OF SERVICE. Refusing a
    # repeated height ACROSS blocks meant a version that illustrates the format with a real height
    # -- which v17 warns about and v18 does in prose -- raised SystemExit inside anchor_facts ->
    # commitments -> governing, so every tool asking which document is authority died. It refused
    # even when both blocks stated the SAME root, reporting "commits height X TWICE", which is
    # false: two blocks each committed it once.
    #
    # ⇒ SCOPE THE RULE TO WHAT IS ACTUALLY A LIE. Within one block a repeat replaces the earlier
    # commitment when the block is read as a mapping -- that is the round-14 attack and it stays
    # refused. Across blocks, equal roots are consistent and only DISAGREEMENT is a violation.
    for _s, _e, _ps in _blocks:
        _within = {}
        for _h, _r in _ps:
            if _h in _within:
                raise SystemExit(
                    D + " one anchor-fact block commits height %d TWICE (%s then %s). A repeated "
                    "height silently replaces the earlier commitment when the block is read as a "
                    "mapping, which is how a fact pin lies while still looking monotonic."
                    % (_h, _within[_h][:16], _r[:16]))
            _within[_h] = _r
    _pairs = [p for _s, _e, ps in _blocks for p in ps]
    # ⛔ THE DICT COLLAPSE WAS THE LIE. A fact pin promises "every committed height keeps its
    # merkle root", and a comprehension keyed on height silently kept the LAST line for a
    # repeated height. So a document could commit 964534 twice -- once truthfully, once with a
    # fabricated root -- and the fabricated one would be the only fact ever checked. The older
    # commitment stops being checked without ever being contradicted: monotonic in shape, a lie
    # in substance. A round-14 reviewer built it and watched the real fact's failure vanish.
    #
    # ⇒ A repeated height is refused before any collapse, whatever the roots say. Two lines for
    # one height is never a legitimate document: the block is a set of commitments, and a set
    # cannot name the same thing twice. ⚠ Now enforced ACROSS blocks as well as within one, because
    # merging several fences is exactly where a duplicate could hide unnoticed.
    _seen = {}
    for _h, _r in _pairs:
        if _h in _seen and _seen[_h] != _r:
            raise SystemExit(
                D + " height %d is committed with TWO DIFFERENT roots (%s and %s). One of them is "
                "false, and reading the blocks as a mapping would silently keep whichever came "
                "last -- monotonic in shape, a lie in substance."
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
    # ⛔⛔ AND IT WAS FOUND BY A HAND-WRITTEN LABEL, WHICH v19 RENUMBERED. `DISTRIBUTION_HEADING`
    # is `### 2c.`; in v18 that is *What the reproducer package contains* and `### 2d.` is the
    # anchor facts, and in v19 -- signed, anchored, and the current authority -- **§2c IS the
    # anchor-fact table and there is no 2d**. So this returned 35 merkle roots as the declared
    # contents of the reproducer package:
    #
    #     subset: ['964534  018d69dc7bf4e2e8...', '964535  ef17461955701f9c...', ... 35 rows]
    #
    # The complement became the entire pinned set, and §2c's equality rule then required a
    # reproducer package to be missing every pinned file -- which is how *a genuine distribution*
    # and *everything absent* became the same input with opposite expectations, and why the suite
    # reports the collision as `⛔ WRONG everything absent`.
    #
    # ⚠️ v18 §3 NAMES THIS FAILURE SIX LINES ABOVE ITS OWN TABLES -- *a reader of this document
    # met two different sections called 2d* -- and reserved `2a.`-`2d.`. The reservation was read
    # as *narrative may not use these numbers* and not as *each number names one table*. v19
    # renumbered anyway, and this time the collision filled the subset with the wrong rows instead
    # of emptying it, which is quieter and worse.
    #
    # ⇒ FOUND BY SHAPE, LIKE THE ANCHOR FACTS ALREADY ARE. A distribution subset is a fenced
    # block whose every row is a bare path this tree resolves -- no digest, no height -- which is
    # what the block IS rather than what a heading calls it. `_anchor_fact_blocks` made exactly
    # this move for the same reason, and `_after_heading`'s own docstring records that trusting a
    # heading cost three protocol versions.
    #
    # ⚠️ TWO SUCH BLOCKS IS A REFUSAL, NOT A CHOICE. v10 carries a second one-row block naming
    # `ANCHORS.json`, so the rule cannot be *the first* or *the largest* without being a guess:
    # the subset is the block whose rows are all pins the document also commits, and if more than
    # one block qualifies this returns nothing rather than picking.
    # ⛔⛔ AND SHAPE ALONE CANNOT SAY WHAT A BLOCK IS FOR. The rule below -- a fence whose
    # rows are all bare paths the document pins -- fixed the heading collision and bought a new
    # ambiguity in its place. A round-12 reviewer appended an entirely ordinary code example to
    # v21 and read the result back out:
    #
    #     a fence containing the single line `anchor_status.py`
    #     distribution_subset() -> {'anchor_status.py'}
    #
    # There is nothing structural separating *these files constitute the reproducer distribution*
    # from *here is a path you might type*. The old rule read a heading and the new rule reads a
    # coincidence -- that the filenames in some block happen also to be pinned -- and a
    # coincidence is not a grammar. Enumerating more exceptions would be the same move a third
    # time.
    #
    # ⇒ THE DISCRIMINATOR IS PART OF THE BLOCK. A distribution subset is a fence whose INFO
    # STRING is `distribution-subset`. It is declared, not inferred; it is independent of every
    # heading, which is what the collision repair was for; and no example, quotation or listing
    # becomes one by accident, because writing it is a deliberate act. Two of them is a refusal
    # for the same reason two of anything is.
    #
    # ⚠️ A DECLARED BLOCK IS HELD TO MORE, NOT LESS. Under the shape rule a row naming a file
    # the document does not pin quietly disqualified the whole block; now it is an error, because
    # the block has said what it is. A subset may only name files the document commits -- the
    # equality this feeds is between the absences and the complement OF THE PINNED SET, and a row
    # outside that set makes the complement meaningless.
    # ⛔⛔ AND THE SENTINEL WAS READ BY A REGEX THAT IS NOT A MARKDOWN GRAMMAR, WITH THE OLD
    # SHAPE RULE UNDERNEATH IT. Two round-13 reviewers took it from both sides. One nested a
    # sentinel fence inside a four-backtick fence: CommonMark renders the inner three backticks
    # as LITERAL TEXT of the outer block, and the regex read them as a declaration -- a subset the
    # document's own structure does not contain. The other indented the sentinel two spaces
    # (natural under a list item): CommonMark still opens a fence, the regex saw nothing, and
    # the function FELL THROUGH to the coincidence rule it had replaced -- returning an example
    # elsewhere in the document as the declared subset. Author and tool held different subsets
    # of one anchored document, which is the heading collision one level down.
    #
    # ⇒ THE READER IS A FENCE SCANNER THAT WALKS THE DOCUMENT AS COMMONMARK DOES -- up to
    # three spaces of indent, backtick or tilde fences, a closing fence of the same character at
    # least as long, and everything between an opening and its closing fence is content in which
    # no fence opens. The shape fallback is GONE: a document declares a subset with the sentinel
    # or declares none (v22 carries the sentinel; v18's shape block is history, and history does
    # not govern). And a NEAR MISS IS A REFUSAL, not a silent demotion: a line that spells the
    # sentinel on a fence-shaped line the scanner did not accept as an opening fence -- inside
    # another fence, inside a blockquote, indented four spaces, with trailing text in the info
    # string -- is a declaration a renderer and this tool would read differently, and the only
    # safe reading of that is none.
    _pins = {n for n, _d in commitments(text)}
    _blocks = _fenced_blocks(text)
    _declared = [(ln, [l.strip() for l in body if l.strip()])
                 for info, body, ln in _blocks if info == "distribution-subset"]
    _accepted_open = {ln for ln, _rows in _declared}
    _near = []
    for _i, _line in enumerate(text.split(NL)):
        if "distribution-subset" not in _line or _i in _accepted_open:
            continue
        _bare = re.sub(r"^[ \t>]*", "", _line)
        if _bare.startswith((BT * 3, "~~~")):
            _near.append(_i + 1)
    if _near:
        raise SystemExit("%s line(s) %s spell a `distribution-subset` fence that a CommonMark "
                         "renderer would not open as one -- inside another fence, in a blockquote, "
                         "indented four or more spaces, or with text after the sentinel. A "
                         "declaration this tool and a reader would read differently is refused, "
                         "not guessed at." % (D, _near[:4]))
    if not _declared:
        return set()
    if len(_declared) > 1:
        raise SystemExit("%s this document declares %d `distribution-subset` blocks. What a "
                         "reproducer package contains is a single fact about a single "
                         "package, and this will not choose between two statements of it."
                         % (D, len(_declared)))
    _rows = _declared[0][1]
    _stray = sorted(r for r in _rows if r not in _pins)
    if _stray:
        raise SystemExit("%s the `distribution-subset` block names %d file(s) this document "
                         "does not pin: %s. The subset is checked as an equality against the "
                         "complement of the PINNED set, so a row outside that set makes the "
                         "rule state nothing." % (D, len(_stray), ", ".join(_stray)))
    return set(_rows)


BT = chr(96)
_FENCE_OPEN = re.compile(r"^( {0,3})(" + BT + r"{3,}|~{3,})[ \t]*([^\n]*?)[ \t]*$")


def _fenced_blocks(text):
    """[(info, body_lines, opening_line_index)] -- fenced code blocks as CommonMark reads them.

    A fence opens on a line indented at most three spaces that starts with three or more
    backticks or tildes; a backtick fence's info string may not contain a backtick. It closes
    on a line of the same character at least as long, indented at most three spaces, and
    nothing else on it; an unclosed fence runs to the end of the document. Lines between are
    content, and NO FENCE OPENS INSIDE CONTENT -- which is the whole reason a scanner is needed
    where a regex was: a regex has no notion of being inside something.
    """
    blocks, lines, i = [], text.split(NL), 0
    while i < len(lines):
        m = _FENCE_OPEN.match(lines[i])
        if m and not (m.group(2)[0] == BT and BT in m.group(3)):
            ch, n, info = m.group(2)[0], len(m.group(2)), m.group(3)
            close = re.compile(r"^ {0,3}" + re.escape(ch) + "{%d,}[ \t]*$" % n)
            body, j, closed = [], i + 1, False
            while j < len(lines):
                if close.match(lines[j]):
                    closed = True
                    break
                body.append(lines[j])
                j += 1
            blocks.append((info, body, i))
            i = j + 1 if closed else j
            continue
        i += 1
    return blocks


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
    # ⛔ ROUND 16: THIS WAS STILL A FILENAME TEST, one tool over from §2n's repair of `stamped()`.
    # A round-16 reader deleted v21's `.asc`, renamed its `.ots` under the retired-proof
    # convention, and this read DRAFT: the authority demoted to v20 with no refusal, and an
    # attacker holding pre-repair tool bytes rolls the tree back with rc=0. ⇒ The proof is found
    # by PROJECTION over every proof-shaped sibling (the OpenTimestamps magic, then a header that
    # commits to these bytes), whatever it is called; and a document whose proof is present while
    # its signature is absent is MISSING -- somebody's commitment with its signature gone -- not a
    # draft. A draft is the state with NEITHER.
    # ⛔⛔ ROUND 17: THE PROJECTION KEPT FIRST-MATCH-AND-BREAK SEMANTICS FOR A QUESTION THAT
    # NEEDS ANY-MATCH. A reviewer wrote a small, valid OpenTimestamps proof over v21's exact
    # bytes carrying only a calendar receipt, named it so it sorts before the real proof, and
    # this returned PENDING while the Bitcoin-attested proof sat unread one file along. PENDING
    # does not block, so authority rolled back a version in silence and the pre-signing gate
    # still printed READY. ⇒ Fixing instance N (a name decides nothing) built instance N+1 (the
    # FIRST thing found decides). THE STRONGEST COMMITMENT DECIDES, NOT THE FIRST ONE FOUND:
    # every proof-shaped sibling is read, ANCHORED wins if any of them verifies against the
    # pinned chain, and among the rest a file that is not a proof of these bytes outranks a
    # receipt -- because refusing is the safe direction and a receipt must not mask it.
    _proofs = _OTS.proofs_over(doc)
    proof = _proofs[0] if _proofs else None
    if proof is None:
        # ⛔⛔ AND A DRAFT HAS NO PROOF EITHER. `MISSING` above the selected authority is treated
        # as *someone removed the table that would have governed* -- correctly, for a document
        # somebody signed. An UNSIGNED draft is in exactly that shape and is the normal state of
        # this folder whenever anyone is writing the next version: drafting v21 made this tool
        # refuse outright, which is the same defect as a check that is switched off during every
        # drafting period, turned the other way round.
        #
        # ⇒ NO SIGNATURE AND NO PROOF IS A DRAFT. Nobody has claimed those bytes, so there is no
        # commitment to have been removed. A signature with no proof is still `MISSING` -- that is
        # a document somebody stood behind whose proof is gone, which is the attack.
        #
        # ⚠️ THE RESIDUAL, AND IT IS A PROPERTY OF THE DESIGN RATHER THAN OF THIS CHECK: an
        # attacker who deletes BOTH the signature and the proof of a signed higher version makes
        # it indistinguishable from a draft, and a weaker table then governs. Nothing local can
        # separate those two states -- a document newer than every anchored version cannot be
        # committed by one. What catches it is a reader noticing a version they signed is now a
        # draft, which is why every run prints the state of every document.
        if not (doc.parent / (doc.name + ".asc")).exists():
            return False, "an unsigned draft: no signature and no proof", "DRAFT"
        return False, "no proof beside it", "MISSING"
    # ⚠ PENDING AND TAMPERED ARE NOT THE SAME REJECTION, and §11 now turns on the difference,
    # so it is a VALUE and not a phrase in `why`. A proof that parses, commits to these bytes and
    # carries a calendar attestation is a document waiting for Bitcoin -- the normal state for
    # hours after stamping. Anything else is a proof that is not a proof.
    _doc_bytes = doc.read_bytes()
    _weakest = None
    for _p in _proofs:
        ok, why, found = _OTS.verify(_p.read_bytes(), _doc_bytes)
        if ok:
            return True, _named_proof(doc, _p, why), "ANCHORED"
        _state = "PENDING" if (found and all(k != "bitcoin" for k, _v, _r in found)
                               and any(k == "pending" for k, _v, _r in found)) else "TAMPERED"
        if _weakest is None or (_weakest[2] == "PENDING" and _state == "TAMPERED"):
            _weakest = (_p, why, _state)
    return False, _named_proof(doc, _weakest[0], _weakest[1]), _weakest[2]


def _named_proof(doc, proof, why):
    """`why`, and the proof it came from when that is not the conventional `<doc>.ots`.

    ⛔ THE DEMOTION WAS SILENT. `grep -c 0shadow` over the whole of this tool's output, while a
    planted file was deciding the verdict, returned 0: the reader could not learn WHICH file had
    answered. A verdict that depends on a file must name it.
    """
    if proof.name == doc.name + ".ots":
        return why
    return "%s [read from %s]" % (why, proof.name)


def witnessed_blocks(doc):
    """[(height, root)] that some proof in this folder verifies FOR THIS DOCUMENT, against the
    pinned chain -- over the document's own bytes, or over the bytes of its detached signature.

    The signature's proof is the second witness, and it is the one that matters here: a document
    whose own proof has been swapped for a calendar receipt still has, beside it, a proof of the
    SIGNATURE it was stamped with, and that proof names the blocks. See `pending_is_a_downgrade`.
    """
    out = []
    for _target in (doc, doc.parent / (doc.name + ".asc")):
        try:
            if not _target.is_file():
                continue
            _b = _target.read_bytes()
        except OSError:                                                   # pragma: no cover
            continue
        for _p in _OTS.proofs_over(_target):
            try:
                _ok, _why, _found = _OTS.verify(_p.read_bytes(), _b)
            except OSError:                                               # pragma: no cover
                continue
            if not _ok:
                continue
            for _k, _v, _r in (_found or ()):
                if _k == "bitcoin":
                    out.append((int(_v), str(_r).lower()))
    return sorted(set(out))


def pending_is_a_downgrade(doc, committed_facts):
    """(blocking, why) for a document that now reads PENDING. A Bitcoin attestation this tree can
    still see, for a document that no longer carries one, is one that was taken away.

    ⚠ PENDING MUST STAY NON-BLOCKING FOR THE STATE IT WAS EXCLUDED FOR: the hours between
    stamping a freshly signed successor and its block. In that state nothing in the folder
    witnesses a block for the document -- its signature's proof is a receipt too -- so this
    returns False and the tree stays green while it waits.

    ⇒ It blocks in the other state, which is the attack: the document reads PENDING and a proof
    of its own signature verifies in a Bitcoin block whose root a committed §2d anchor-fact table
    already confirms, or failing that which this tree's anchor file pins. The anchor file is not
    committed by any version and is not enough to ACCEPT anything; it is enough to REFUSE, which
    is the direction that cannot be used to promote a weaker table.
    """
    blocks = witnessed_blocks(doc)
    if not blocks:
        return False, ""
    _confirmed = sorted({h for h, r in blocks if committed_facts.get(h) == r})
    _heights = sorted({h for h, _r in blocks})
    return True, ("its proof names no Bitcoin block while a proof of its own signature is "
                  "anchored in block(s) %s, %s. An attestation this tree can still see has been "
                  "taken off the document"
                  % (_confirmed or _heights,
                     "confirmed by a committed anchor-fact table" if _confirmed
                     else "pinned by this tree's anchor file"))


_SIG_CACHE = {}


def signed_by_protocol_key(doc):
    """True, or the reason it is not. The protocol's signature, as `check_signature.verify` decides it.

    ⛔⛔ ROUND 14: `governing()` SELECTED EVERY ANCHORED DOCUMENT AND NEVER ASKED WHO SIGNED IT. A
    reviewer created a v23 with no signature, made only the selector's `anchored()` say True, and
    got `highest selected: (23, ...)`. Stamping is free -- anyone can obtain a calendar receipt and,
    in hours, a Bitcoin attestation over any bytes -- so an anchored unsigned successor is a draft
    with a timestamp, and the authority rule was letting a timestamp stand in for a signature.
    `in_force()` required `signed()`; the code that actually composes authority did not, and the
    two were not the same predicate.
    ⇒ ONE QUESTION, ANSWERED HERE FOR THE SELECTOR AND BY THE SAME VERIFIER `in_force()` USES: a
    version is eligible to govern only if the protocol's key stands behind it. Fails closed: a
    signature that cannot be attributed to that key is not one. Cached on the bytes of the
    document and its signature, because this is asked once per candidate per run.
    """
    sig = doc.parent / (doc.name + ".asc")
    try:
        key = (hashlib.sha256(doc.read_bytes()).hexdigest(),
               hashlib.sha256(sig.read_bytes()).hexdigest() if sig.is_file() else "")
    except OSError as e:
        return "the document or its signature could not be read (%s)" % e
    if key in _SIG_CACHE:
        return _SIG_CACHE[key]
    try:
        import check_signature as _CS
        state, detail, _f = _CS.verify(doc)
    except Exception as e:                                               # noqa: BLE001
        _SIG_CACHE[key] = "check_signature.verify could not run (%r)" % (e,)
        return _SIG_CACHE[key]
    _SIG_CACHE[key] = True if state == "ok" else "%s: %s" % (state, str(detail)[:90])
    return _SIG_CACHE[key]


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
    _t = _after_heading(text, RETIRES_HEADING)
    if _t is None:
        return []
    body = _t.split(NL + "## ", 1)[0]
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
        # ⛔⛔ `len(pinned) < MIN_EXPECTED` ASKED A QUESTION ABOUT THE FORMAT AND ANSWERED IT WITH
        # A QUESTION ABOUT THE SIZE, AND THE COMMENT TWENTY LINES ABOVE ALREADY SAYS WHY THAT IS
        # WRONG: *one integer cannot carry two questions*, and *a three-row table is a table*. The
        # structural detector was written for exactly this and then was not used here.
        #
        # Round 9 produced the document that proves it. v18 bundled a governance change with the
        # substantive withdrawal under review, so v19 was split out to carry the two tools alone
        # -- **two commitment rows**, correctly and completely parsed -- and this line filed it as
        # `UNPARSEABLE: the table's format has changed`. A version whose whole merit is being
        # small was refused for being small, by the threshold whose own comment forbids it.
        #
        # ⇒ THE FORMAT MOVED IF ROWS WENT MISSING, WHICH IS A COMPARISON, NOT A FLOOR. Every
        # version in this tree satisfies `presents_table == commitments + anchor facts` exactly,
        # because those are the only two kinds of row there are. When the structural count exceeds
        # what the two parsers read, rows exist that neither can see -- which is the real failure,
        # at any size. `MIN_EXPECTED` no longer decides anything here; it is kept only where it
        # answers its other, honest question.
        _rows = presents_table(_body)
        _read = len(pinned) + len(anchor_facts(_body))
        if _rows > _read:
            # ⛔ A THREE-TUPLE WHERE THE CONSUMER UNPACKS FOUR. This rejection path
            # raised ValueError instead of reporting, which is the same class as the eight
            # crashing error paths the sibling project found this round: a control that fires
            # and then destroys its own message. Found by adding a second rejection beside it.
            rejected.append(Rejection(version, f.name,
                             "lays out %d row(s) in table shape and the two parsers between them "
                             "read %d (%d commitment(s), %d anchor fact(s)). The rows neither can "
                             "see are commitments this document makes and nothing enforces."
                             % (_rows, _read, len(pinned), _read - len(pinned)), "UNPARSEABLE",
                             True))
            continue
        ok, why, state = anchored(f)
        if not ok:
            rejected.append(Rejection(version, f.name, why, state, bool(pinned)))
            continue
        # ⛔ ROUND 14: anchored is not authority; see `signed_by_protocol_key`. A proof says WHEN,
        # a signature says WHO, and a version eligible to govern needs both.
        _who = signed_by_protocol_key(f)
        if _who is not True:
            rejected.append(Rejection(version, f.name,
                                      "anchored and NOT signed by the protocol's key (%s). A timestamp "
                                      "over unsigned bytes is a draft somebody stamped, and a draft does "
                                      "not govern" % _who, "UNSIGNED", bool(pinned)))
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
        # UNSIGNED joins the blocking states: an anchored document above the authority that the
        # protocol's key does not stand behind is either a stripped signature or a stamp taken
        # before the signature the protocol requires first -- a tree to refuse, not to read past.
        blocking = [r for r in rejected
                    if r.version > top and r.state in ("TAMPERED", "MISSING", "UNSIGNED")]
        # ⛔ ROUND 17: AND PENDING WAS THE WAY PAST ALL THREE. A planted calendar-only proof over
        # the authority's own bytes demoted it a version with no refusal at all. PENDING blocks
        # when this tree can still witness the Bitcoin block the document has stopped naming --
        # see `pending_is_a_downgrade`, which leaves a genuinely fresh stamp alone.
        _facts = {}
        for _v, _n, _p in found:
            try:
                for _h, _r in anchor_facts((here / _n).read_text(encoding="utf-8")).items():
                    _facts.setdefault(int(_h), str(_r).lower())
            except (OSError, SystemExit, ValueError):                     # pragma: no cover
                continue
        for r in rejected:
            if r.version > top and r.state == "PENDING":
                _down, _why = pending_is_a_downgrade(here / r.name, _facts)
                if _down:
                    blocking.append(r._replace(why=_why, state="DOWNGRADED"))
        blocking.sort(key=lambda r: r.version)
        if blocking and _raise_on_blocking:
            # ⛔ THE REFUSAL HARDCODED ONE CAUSE FOR FOUR STATES. It said *its proof is not a
            # proof* for a document whose proof had just been read as ANCHORED and whose
            # SIGNATURE was the thing missing, and then cut the real reason off at sixty
            # characters, mid-word, leaving an unbalanced bracket. §2l added UNSIGNED to this set
            # and did not touch the sentence that reports it: the cause printer naming the wrong
            # cause, one tool over from §2e, for the third time in this archive. ⇒ The message
            # branches on the state, and the reason is clipped at a word or not at all.
            _worst = blocking[-1]
            _cause = {
                "TAMPERED": "the file beside it named as its proof is not a proof of these bytes",
                "MISSING": "its proof has been removed",
                "UNSIGNED": "nothing the protocol's key stands behind is holding it up",
                "DOWNGRADED": "its Bitcoin attestation has been taken off it",
            }.get(_worst.state, "its proof is not a proof")
            raise SystemExit(
                D + " %s is present, is a HIGHER version than the authority the next version "
                "down would select, and %s (%s). Falling back to an older document would enforce "
                "a SMALLER table -- v5 pins 4 files where v6 pins 16 -- so destroying a proof "
                "would make this check weaker and still pass. A protocol document whose proof "
                "has been destroyed is a tampered tree, not an older one."
                % (_worst.name, _cause, _clip(_worst.why)))
    return found, rejected


def _clip(text, limit=220):
    """`text`, cut at a WORD boundary if it must be cut at all.

    ⛔ `why[:60]` CUT THE ONE SENTENCE AN OPERATOR SEES IN THE MIDDLE OF A WORD -- `UNSIGNED: no `
    -- inside a parenthesis it then left unbalanced. A message that reports a rolled-back tree is
    not the place to save a hundred and sixty characters.
    """
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return (cut or text[:limit]) + " …"


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
