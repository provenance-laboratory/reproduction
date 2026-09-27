"""Which documents still state a claim this study has withdrawn, and where to read the withdrawal.

⛔ WHY THIS EXISTS. `PRE-REGISTRATION.md` §2c states the ecosystem claim plainly, with no marker,
and it ships in the reproduction package. It is OpenTimestamped, so **it cannot be edited** -- an
anchored document whose bytes change is a broken proof, and not rewriting history is the point of
anchoring it. A round-6 reviewer found it and put it exactly: *the survivor is the one that
matters*. So the marker is additive and generated; nothing anchored is touched.

⛔⛔ AND THE FIRST VERSION PROJECTED OVER THE WRONG SET. It scanned for the claim's OWN WORDS --
`"finding about the ecosystem"` -- which is an OPEN set nobody can enumerate, so a withdrawal
restated in different language was invisible. Round 8 demonstrated it twice over:

    `PUBLICATION-CHECKLIST.md` argued from both sides of the withdrawal. Six lines after correctly
    recording that v18 §1 withdrew the inference, it wrote *the silence stops being a measurement
    and becomes a schedule* -- **"stops being a measurement" presupposes it is one**. Neither
    phrase appeared, so the file was not even a candidate.

And the marker predicate was worse than the scan. `marked = "withdraw" in text.lower()` was
UNSCOPED to any claim, over the whole document: a file that states the withdrawn claim and happens
to contain the word *withdrew* anywhere scored as already marked. It would have laundered the
contradiction above.

⇒ INVERT THE DIRECTION. Stop projecting over the claim's phrasings, which you must guess at.
**Project over the files, which you can walk.**

⛔⛔ AND ROUND 8'S WALK WAS CLOSED OVER A FILE EXTENSION -- the project's own recurring defect, in
the function whose docstring announces the cure. `rglob("*.md")` missed:

    PRE-REGISTRATION-v18-CONFIRMATORY.md.superseded-draft-...  20 KB of markdown, opens with the
                                                               claim, and SHIPS in the archive
    capture_exposure.py                                        carries the claim's phrasing, is
                                                               pinned, and is outside the walk

Two documents titled *Pre-registration v18* resolving the same question differently, one of them
invisible to the tool. That is `PUBKEY.asc`'s extension allowlist again, in a sibling tool written
the same day.

⇒ A FILE IS IN SCOPE IF IT IS TEXT. Not if it ends in `.md`. The walk decodes; what decodes is a
place the claim can be written, whatever it is called.

⛔⛔ AND THE RECORD ITSELF WAS UNPROTECTED, which made every label above beside the point. A
round-9 reviewer promoted all 35 machine seeds to `human`, flipped the one anchored carrier to
`clean`, and got `ok WITHDRAWN-CLAIMS.md describes this folder / EXIT=0`: the anchored document
this tool exists for, erased from the published record, and the doctored tree passing the step the
honest one fails. The per-entry digest binding defends against THE DOCUMENT changing. Nothing
defended against THE RECORD OF THE READING changing, and those are different threats.

⇒ THE SAME CONSTRUCTION `attempts.py` ALREADY USES IN THIS TREE. The dispositions are an
append-only hash-chained log: each entry carries `prev`, the SHA-256 of the previous entry's exact
bytes, so the digest of entry k fixes entries 1..k. A head file pins the count and the head, and is
stamped -- because a chain alone cannot see entries deleted from its end.

⛔ AND `seeded_from: phrase-scan` WAS WRITTEN BY NOTHING. The only writer of that field wrote
`"human"` unconditionally, so 35 records said a machine proposed them and no code path had ever
proposed anything: they arrived by an act with no code path, which is the exact fingerprint this
tree condemned in `package.incomplete`. A disposition IS an adjudication. The scan's guess is a
HINT, computed live and never stored, and only a reading goes in the log.

⚠️ SO WHAT THE SCAN COVERS IS STATED, NOT ASSUMED. Every text file is scanned; the ones carrying a
phrasing this tool knows MUST be read and recorded; the rest rest on the scan, and the report says
how many that is. A restatement in words nobody anticipated is still possible -- that residual is
printed rather than hidden, and the hint list is the thing to extend when one is found.

⚠️ WHAT THIS IS NOT. It does not withdraw anything; §1 of the governing version does that. It
makes the withdrawal findable from the document that carries the claim.

    python withdrawn_claims.py --review   # what is stale or unrecorded, with a scan hint
    python withdrawn_claims.py --record <file> <claim> <carrier|marked|clean> "note"
    python withdrawn_claims.py            # regenerate WITHDRAWN-CLAIMS.md from the log
    python withdrawn_claims.py --check    # verify it describes this folder, write nothing
"""
import datetime
import hashlib
import io
import json
import pathlib
import sys

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
D, W, OK, AR = chr(0x26D4), chr(0x26A0), "ok  ", chr(0x21D2)
NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "WITHDRAWN-CLAIMS.md"
LOG = HERE / "WITHDRAWN-DISPOSITIONS.jsonl"
HEAD = HERE / "WITHDRAWN-DISPOSITIONS.head"
GENESIS = "0" * 64
KEYS = ("claim", "disposition", "doc", "n", "note", "prev", "sha256", "utc")

# ⇒ THE FILES THIS TOOL WRITES, DERIVED FROM THE CONSTANTS THAT NAME THEM. These are the one
# principled exclusion from the walk, and the principle is not "they are ours": it is that a file
# this tool REWRITES cannot be bound by a digest this tool records. `WITHDRAWN-CLAIMS.md` is
# regenerated on every run and the log grows on every reading, so a disposition over either would
# be stale the instant after it was taken. Everything else in the tree is adjudicable, including
# this script -- which does state the claim, in the hint list, and is recorded like anything else.
WRITES = {OUT.name, LOG.name, HEAD.name, HEAD.name + ".ots"}

# ⛔ TWO PROJECTIONS OVER "THE TREE", DISAGREEING BY 14 FILES. This kept its own skip list while
# `build_review_packet.py` kept `EXCLUDED_DIRS`, so the walk here reached `package.incomplete/`
# and the walk there did not -- and the shipped `WITHDRAWN-CLAIMS.md` therefore published
# `package.incomplete/PRE-REGISTRATION.md` as *anchored -- cannot be edited*: a build-scratch path,
# labelled anchored, in a generated record of record. Step 2 of the review packet failed in the
# archive as shipped, and its refusal invited the reviewer to regenerate against the wrong walk.
#
# ⇒ ONE PROJECTION, IMPORTED. The packet builder decides what this tree contains, because it is
# the thing that hands the tree to a stranger. `.git` and `__pycache__` are added here because
# they are not files anybody writes.
try:
    from build_review_packet import EXCLUDED_DIRS as _PACKET_EXCLUDED
except ImportError:                                                      # pragma: no cover
    raise SystemExit(D + " build_review_packet.py must be importable: it owns the answer to what "
                         "this tree contains, and keeping a second answer here is what put a "
                         "build-scratch path into the published record.")
SKIP_DIRS = set(_PACKET_EXCLUDED) | {".git", "__pycache__"}

CARRIER, MARKED, CLEAN = "carrier", "marked", "clean"
DISPOSITIONS = (CARRIER, MARKED, CLEAN)

WITHDRAWN = [
    {
        "name": "the ecosystem claim",
        "claim": "that an unreproduced artifact published expressly to be reproduced would itself "
                 "be a finding about the ecosystem",
        # ⚠️ A HINT, NOT AN AUTHORITY, AND NEVER STORED. These say which files a human MUST read;
        # the recorded reading is what this tool reports. Round 8's carrier matched none of them.
        "hints": ["finding about the ecosystem",
                  "silence would be a finding",
                  "stops being a measurement",
                  "silence stops being"],
        "withdrawn_in": "PRE-REGISTRATION-v18-CONFIRMATORY.md",
        "section": "§1",
        "why": "the instrument could only measure that no issue was filed, and nothing fixed in "
               "advance how the call was distributed -- so minimum exposure was compliant and "
               "produced the preferred result. A protocol under which doing nothing is compliant "
               "and yields the flattering outcome can produce a dishonest paper without anyone "
               "lying.",
    },
]
CLAIMS = {spec["name"]: spec for spec in WITHDRAWN}


def _text(f):
    """The file's text, or None if it is not a place a sentence can be written."""
    try:
        s = f.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    return None if chr(0) in s else s


def documents():
    """Every TEXT file in the tree, as a path relative to here. Not every `.md` file.

    ⚠️ The classifier is *does this decode as UTF-8 without a NUL*, which is a property of the
    bytes rather than of the name. A `.superseded-draft-...` suffix, a `.py`, a `.json` and a
    `.md` are all places this claim has actually been written in this tree.
    """
    out = []
    for f in sorted(HERE.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(HERE)
        if set(rel.parts) & SKIP_DIRS or rel.as_posix() in WRITES:
            continue
        if _text(f) is None:
            continue
        out.append(rel.as_posix())
    return out


def sha(rel):
    return hashlib.sha256((HERE / rel).read_bytes()).hexdigest()


def hint(spec, rel):
    """Whether a scan this tool knows finds the claim here. Proposes; never decides, never stored."""
    text = _text(HERE / rel) or ""
    for h in spec["hints"]:
        if h in text:
            return True, "matches %r" % h
    return False, "no phrasing this scan knows"


# --------------------------------------------------------------------------------------------
# the log. One entry per reading, chained, append-only.
# --------------------------------------------------------------------------------------------
def canonical(entry):
    """The exact bytes of an entry's line. Sorted keys, no spaces: one entry, one spelling.

    ⚠ THE CHAIN IS OVER THESE BYTES, so the serialisation is part of the control. Two encodings of
    the same object would produce two heads and the difference would look like tampering.
    """
    return json.dumps({k: entry[k] for k in KEYS}, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def read_log():
    """[entry] with the chain verified, or SystemExit naming the first break."""
    if not LOG.exists():
        return []
    out, prev = [], GENESIS
    for i, raw in enumerate(LOG.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            e = json.loads(raw)
        except ValueError:
            raise SystemExit(D + " %s line %d is not JSON. The chain is over the entry's bytes, "
                                 "so an unreadable line is a break." % (LOG.name, i))
        missing = [k for k in KEYS if k not in e]
        if missing:
            raise SystemExit(D + " %s line %d is missing %s. The chain is over the entry's exact "
                                 "fields; one that is absent changes the bytes."
                             % (LOG.name, i, ", ".join(missing)))
        if e["n"] != i:
            raise SystemExit(D + " %s line %d is numbered %r. A gap or a repeat means entries were "
                                 "removed or inserted." % (LOG.name, i, e["n"]))
        if e["prev"] != prev:
            raise SystemExit(
                D + " %s entry %d records prev %s and entry %d hashes to %s. The record of the "
                "readings has been rewritten, which is what a chain over it is for."
                % (LOG.name, e["n"], str(e["prev"])[:16], e["n"] - 1, prev[:16]))
        # the bytes on disk must BE the canonical bytes, or the head a reader computes and the
        # head the log asserts are over two different documents
        if raw.encode("utf-8") != canonical(e):
            raise SystemExit(
                D + " %s entry %d is not in canonical form. Its stored bytes and its chain digest "
                "are over different spellings of the same object." % (LOG.name, e["n"]))
        prev = hashlib.sha256(canonical(e)).hexdigest()
        out.append(e)
    return out


def head_at(entries, n):
    return hashlib.sha256(canonical(entries[n - 1])).hexdigest() if n else GENESIS


def check_head(entries):
    """[problem]. The chain cannot see entries deleted from its END; the head file can.

    ⚠️ AND ONLY IF IT IS STAMPED. A head file written by the same tool, in the same directory, is
    rewritten by whoever rewrites the log. What makes it evidence is an OpenTimestamps proof over
    it, which is an outward act on a public calendar. Unstamped, it is reported as unstamped --
    the same way `attempts.py` reports its own heads -- because a control whose protection is
    absent must say so rather than look present.
    """
    bad = []
    if not HEAD.exists():
        if entries:
            bad.append("%s is absent, so nothing pins how many readings there are. Deleting "
                       "entries from the END of a chain leaves a valid chain." % HEAD.name)
        return bad
    try:
        rec = json.loads(HEAD.read_text(encoding="utf-8"))
        n, want = int(rec["n"]), str(rec["head"])
    except (OSError, ValueError, KeyError, TypeError):
        return ["%s does not state {n, head}." % HEAD.name]
    if n > len(entries):
        bad.append("%s pins %d reading(s) and the log has %d. Entries were deleted from the end, "
                   "which the chain alone cannot see." % (HEAD.name, n, len(entries)))
    elif head_at(entries, n) != want:
        bad.append("%s records head %s and reading %d now hashes to %s."
                   % (HEAD.name, want[:16], n, head_at(entries, n)[:16]))
    return bad


def write_head(entries):
    HEAD.write_text(json.dumps({"_what": "pins how many readings the log holds and what its head "
                                         "is. Stamp this file: a head the same tool rewrites "
                                         "protects nothing until a calendar has seen it.",
                                "head": head_at(entries, len(entries)),
                                "n": len(entries)}, indent=2, sort_keys=True) + NL,
                    encoding="utf-8", newline=NL)


def append(entries, claim, rel, disp, note):
    e = {"claim": claim, "disposition": disp, "doc": rel, "n": len(entries) + 1, "note": note,
         "prev": head_at(entries, len(entries)), "sha256": sha(rel),
         "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    with LOG.open("ab") as fh:
        fh.write(canonical(e) + NL.encode("utf-8"))
    entries.append(e)
    write_head(entries)
    return e


def latest(entries):
    """{(claim, doc): entry}. The last reading of a file for a claim is the one in force."""
    out = {}
    for e in entries:
        out[(e["claim"], e["doc"])] = e
    return out


# --------------------------------------------------------------------------------------------
def status(entries):
    """(spec, doc, disposition, state) for every file a reading is REQUIRED for.

    ⇒ WHICH FILES ARE REQUIRED IS ITSELF A PROJECTION, not a list. A file is required if the scan
    finds the claim in it, OR if somebody has already read it -- because an adjudication, once
    taken, stays bound to the bytes it was taken over. So a document that stops matching the scan
    does not quietly leave the record; its reading goes stale and this refuses.
    """
    cur = latest(entries)
    rows, scanned, scan_clean = [], 0, 0
    for spec in WITHDRAWN:
        for rel in documents():
            scanned += 1
            hit, _why = hint(spec, rel)
            entry = cur.get((spec["name"], rel))
            if entry is None:
                if hit:
                    rows.append((spec, rel, None, "UNREAD: the scan finds the claim here"))
                else:
                    scan_clean += 1
                continue
            if entry["sha256"] != sha(rel):
                rows.append((spec, rel, entry["disposition"], "STALE: the file changed"))
            elif entry["disposition"] not in DISPOSITIONS:
                rows.append((spec, rel, entry["disposition"], "INVALID disposition"))
            else:
                rows.append((spec, rel, entry["disposition"], "read"))
    return rows, scanned, scan_clean


def render(rows, scanned, scan_clean):
    out = ["# Withdrawn claims, and where each is still written down", "",
           "**Generated by `withdrawn_claims.py`. Do not edit.**", "",
           "This study has withdrawn claims that remain stated in OpenTimestamped documents. Those "
           "documents cannot be edited -- an anchored file whose bytes change is a broken proof, "
           "and not rewriting history is the point of anchoring them. So the withdrawal is "
           "recorded here instead, and this file travels with them.", "",
           "Each file below carries a RECORDED reading bound to its digest, in an append-only "
           "hash-chained log. If a file changes, its reading goes stale and the check refuses "
           "until somebody has read it again -- because a withdrawal restated in new words is "
           "exactly what a phrase scan cannot see.", ""]
    for spec in WITHDRAWN:
        mine = [r for r in rows if r[0] is spec]
        carriers = sorted(r[1] for r in mine if r[2] == CARRIER)
        marked = sorted(r[1] for r in mine if r[2] == MARKED)
        out += ["## %s" % spec["name"], "",
                "**The claim:** %s" % spec["claim"], "",
                "⛔ **Withdrawn in `%s` %s.**" % (spec["withdrawn_in"], spec["section"]), "",
                "**Why:** %s" % spec["why"], "",
                "**Still stated, with no marker of its own:**", ""]
        for rel in carriers:
            anchored = (HERE / (rel + ".ots")).is_file()
            out.append("- `%s`%s" % (rel, "  (anchored -- cannot be edited)" if anchored else ""))
        if not carriers:
            out.append("- none")
        out += ["", "**States the withdrawal itself:**", ""]
        for rel in marked:
            out.append("- `%s`" % rel)
        if not marked:
            out.append("- none")
        # ⚠️ THE BOUND IS PART OF THE RESULT. "N files examined" invited the reading that N files
        # were READ; most were scanned. Saying which is which is the difference between a measured
        # residual and an implied zero.
        out += ["", "%d text file(s) scanned; %d read and recorded; %d carry no phrasing this "
                    "scan knows and rest on the scan alone. %d carry the claim unmarked."
                % (scanned, len(mine), scan_clean, len(carriers)), ""]
    return NL.join(out) + NL


def main():
    argv = sys.argv[1:]
    entries = read_log()
    head_problems = check_head(entries)

    if argv[:1] == ["--record"]:
        # ⛔ ONE READING, ONE CLAIM. This used to loop over every entry in WITHDRAWN and write the
        # same disposition for all of them from a single human judgement -- so the record asserted
        # a per-claim adjudication it had never been given. This docstring gave that exact shape as
        # the reason the old marker predicate was fatal: *a document that withdraws claim 1 and
        # asserts claim 2 reads as marked for both*. The defect had moved from the reader to the
        # writer. It costs nothing with one claim and is unfixable in place the day there are two.
        if len(argv) < 4:
            raise SystemExit("%s usage: --record <file> <claim> <%s> [note]%s  claims: %s"
                             % (D, "|".join(DISPOSITIONS), NL, ", ".join(repr(c) for c in CLAIMS)))
        rel, claim, disp = argv[1].replace(chr(92), "/"), argv[2], argv[3]
        note = argv[4] if len(argv) > 4 else ""
        if claim not in CLAIMS:
            raise SystemExit("%s %r is not a withdrawn claim. One of: %s"
                             % (D, claim, ", ".join(repr(c) for c in CLAIMS)))
        if disp not in DISPOSITIONS:
            raise SystemExit("%s disposition must be one of %s" % (D, ", ".join(DISPOSITIONS)))
        if rel not in documents():
            raise SystemExit("%s %s is not a text file in this tree." % (D, rel))
        # ⚠ Complain about the record BEFORE adding to it. Appending onto a chain that already
        # fails is how a break gets buried under later entries.
        if head_problems:
            for p in head_problems:
                print("  %s %s" % (D, p))
            raise SystemExit(D + " the record of the readings does not verify; nothing is "
                                 "appended to it until that is resolved.")
        e = append(entries, claim, rel, disp, note)
        print("  %s reading %d recorded: %s is %s for %r" % (OK, e["n"], rel, disp, claim))
        print("      head %s -- stamp %s" % (head_at(entries, len(entries))[:16], HEAD.name))
        return 0

    rows, scanned, scan_clean = status(entries)
    unsettled = [r for r in rows if r[3] != "read"]

    if argv[:1] == ["--review"]:
        print("=" * 78)
        print("  FILES WITH NO CURRENT READING")
        print("=" * 78)
        for p in head_problems:
            print("  %s %s" % (D, p))
        if not unsettled and not head_problems:
            print("  %s every file the scan finds the claim in has a reading bound to its current "
                  "digest" % OK)
            return 0
        for spec, rel, disp, state in unsettled:
            h, why = hint(spec, rel)
            print("  %s %-62s %-34s %s" % (W, rel, state, why))
        print()
        print("  Read each, then: python withdrawn_claims.py --record <file> <claim> <%s> \"note\""
              % "|".join(DISPOSITIONS))
        return 1

    if head_problems:
        for p in head_problems:
            print("  %s %s" % (D, p))
        raise SystemExit(D + " the record of the readings does not verify. Every disposition below "
                             "it would rest on a record that has been rewritten.")

    if unsettled:
        for spec, rel, disp, state in unsettled[:8]:
            print("  %s %-62s %s" % (W, rel, state))
        raise SystemExit(
            "%s %d file(s) have no reading bound to their current digest. A withdrawal restated "
            "in words this tool does not know is exactly what that refusal is for -- run "
            "`--review`, read them, and record what each one does." % (D, len(unsettled)))

    body = render(rows, scanned, scan_clean)
    print("=" * 78)
    print("  WITHDRAWN CLAIMS STILL STATED IN THIS FOLDER")
    print("=" * 78)
    for spec, rel, disp, _st in rows:
        if disp == CLEAN:
            continue
        anchored = (HERE / (rel + ".ots")).is_file()
        print("  %s %-62s %-8s %s" % (OK if disp == MARKED else W, rel, disp,
                                      "anchored" if anchored else "not anchored"))
    print("  %s %d text file(s) scanned, %d read; %d rest on the scan alone"
          % (W, scanned, len(rows), scan_clean))
    # ⚠️ THE HEAD IS ONLY EVIDENCE ONCE A CALENDAR HAS SEEN IT. Until then the log and the file
    # that pins it are rewritten by the same hand, and saying so is the control.
    if not (HERE / (HEAD.name + ".ots")).is_file():
        print("  %s %s is NOT STAMPED, so the chain is tamper-EVIDENT only to a reader who "
              "already has an earlier copy of it." % (W, HEAD.name))

    if "--check" in argv:
        if not OUT.is_file():
            raise SystemExit("%s %s has not been generated." % (D, OUT.name))
        if OUT.read_text(encoding="utf-8") != body:
            raise SystemExit("%s %s does not describe this folder. Regenerate it." % (D, OUT.name))
        print("  %s %s describes this folder" % (OK, OUT.name))
        return 0
    OUT.write_text(body, encoding="utf-8", newline=NL)
    print("  %s wrote %s" % (OK, OUT.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
