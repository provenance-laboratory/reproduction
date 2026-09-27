#!/usr/bin/env python3
"""The append-only record of distribution attempts, and the control over it.

⛔ WHY THIS EXISTS, AND WHAT IT NO LONGER DOES. `DISTRIBUTION-PLAN.md` §3 required every named
venue to be attempted, permitted one attempt each, and put the record in `exposure/attempts.jsonl`
because the plan is pinned by digest and a file that must grow cannot be pinned by its bytes. The
log was moved out of the pinned document and then **protected by nothing** -- no file, no writer,
no reader, no control -- so a `removed` outcome could be deleted, a date moved back, or an attempt
invented after the fact, with every gate in this tree still green.

⛔ v18 §1 WITHDREW THE CLAIM THOSE OBLIGATIONS SERVED. Nothing infers anything from silence any
more, so nothing needs a venue list to have been exhausted, and this file **no longer requires any
venue to be attempted, permits any number of attempts, and gates nothing.** Distribution may or may
not happen; no result turns on the difference.

⇒ WHAT REMAINS IS TAMPER-EVIDENCE, AND ITS EXACT STRENGTH IS STATED BECAUSE THE FIRST
VERSION OVERSTATED IT. That version said a recorded attempt "cannot later be edited, backdated or
quietly removed". A reviewer disproved the last clause in four steps: write one attempt, write its
head, **delete the final entry AND its head**, run `--check` -- clean. The chain links entries to
each other, so it catches an edit in the middle; it cannot see a truncation that removes the end and
the record of the end together, because what is left is internally consistent.

⛔ SO THE HONEST CLAIM IS CONDITIONAL: **edits and deletions are detectable once a head has been
externally witnessed** -- OpenTimestamped, or counted by a stamped exposure capture. Until then the
log is ordinary evidence with an internal consistency check, which is worth having and is not
tamper-proof. `--check` now reports, per head, whether a proof exists, and refuses to describe an
unwitnessed log as tamper-evident.

⚠ This matters more since the captures became optional: they used to be the second witness on a
schedule, and a schedule nobody is obliged to keep is not a witness.

⇒ THE SAME MONOTONIC CONSTRUCTION THE ANCHOR FACTS USE. Each entry carries `prev`, the SHA-256 of
the previous entry's exact line bytes, so the digest of entry k fixes entries 1..k and nothing
appended later can change it. That digest is written to `exposure/attempts-<k>.head` and THAT is
what gets OpenTimestamped: a growing log cannot be stamped, a fixed digest can. Every exposure
capture also records the head and count it saw, and those captures are stamped too.

⇒ So a rewritten history has to contradict either a Bitcoin anchor or an earlier stamped capture,
and this file is what notices. Growth is permitted and expected; contradiction is the failure.

⚠️ IT PARSES THE PLAN, IT DOES NOT RESTATE IT. The venue identifiers and the permitted outcomes are
read out of `DISTRIBUTION-PLAN.md`, which is pinned by digest in the pre-registration. A hand-copied
list here would drift from the anchored document the moment either changed, and both copies would
look authoritative -- the defect `check_commitments.py` opens by describing.

    python attempts.py --record <venue> <url> <outcome>
    python attempts.py --check
"""
import datetime
import hashlib
import io
import json
import pathlib
import re
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
PLAN = HERE / "DISTRIBUTION-PLAN.md"
SERIES = HERE / "exposure"
LOG = SERIES / "attempts.jsonl"
GENESIS = "0" * 64
KEYS = ("n", "outcome", "prev", "url", "utc", "venue")

# The venue rows: an identifier, then whitespace, then prose. The plan states in the line above the
# block that the first token IS the identifier, so this reads a declaration rather than guessing
# where a human-readable name ends.
_VENUE_ROW = re.compile(r"^([a-z0-9][a-z0-9.-]*)\s\s+\S")
_OUTCOMES = re.compile(r'"outcome"\s*:\s*"([a-z|]+)"')
_FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S)


def plan_vocabulary():
    """(venues, outcomes) as the pinned plan declares them.

    ⛔ FAILS CLOSED ON AN EMPTY PARSE. If the plan's layout changes and either list comes back
    empty, that is a broken reader, not a plan with no venues. Recording an attempt against a
    vocabulary of nothing would accept any string at all, which is how a validator becomes a
    formality.
    """
    if not PLAN.exists():
        raise SystemExit(D + " %s is absent. The venues and outcomes are defined there and are "
                             "deliberately not defined here." % PLAN.name)
    text = PLAN.read_text(encoding="utf-8")
    venues = []
    for block in _FENCE.findall(text):
        rows = [l for l in block.split(NL) if l.strip()]
        hits = [m.group(1) for m in (_VENUE_ROW.match(l) for l in rows) if m]
        # A venue block is one where EVERY row is a venue row -- the same structural test the
        # anchor-fact block finder uses, for the same reason: a heading is not a commitment.
        if rows and len(hits) == len(rows):
            venues.extend(hits)
    outcomes = sorted({o for m in _OUTCOMES.findall(text) for o in m.split("|") if o})
    if not venues or not outcomes:
        raise SystemExit(
            D + " read %d venue(s) and %d outcome(s) out of %s. An empty vocabulary would accept "
            "any string, so this is a broken reader rather than a permissive one."
            % (len(venues), len(outcomes), PLAN.name))
    dupes = sorted({v for v in venues if venues.count(v) > 1})
    if dupes:
        raise SystemExit(D + " the plan names %s more than once; an identifier that means two "
                             "rows means neither." % ", ".join(dupes))
    return venues, outcomes


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
    for i, raw in enumerate(LOG.read_bytes().split(b"\n"), start=1):
        if not raw.strip():
            continue
        try:
            e = json.loads(raw.decode("utf-8"))
        except Exception as exc:                                                # noqa: BLE001
            raise SystemExit(D + " %s line %d does not parse (%s)." % (LOG.name, i, exc))
        missing = [k for k in KEYS if k not in e]
        extra = [k for k in e if k not in KEYS]
        if missing or extra:
            raise SystemExit(
                D + " %s line %d has fields %s and is missing %s. The chain is over the entry's "
                "exact bytes, so a field this reader does not know about is a field the digest "
                "covers and no rule checks." % (LOG.name, i, extra or "none", missing or "none"))
        if e["n"] != len(out) + 1:
            raise SystemExit(D + " %s line %d is numbered %r; entries are 1..N in order, and a gap "
                                 "is a deletion." % (LOG.name, i, e["n"]))
        if e["prev"] != prev:
            raise SystemExit(
                D + " %s entry %d links to %s but entry %d hashes to %s. An entry before it was "
                "changed or removed AFTER it was written -- which is the one thing an append-only "
                "log is for." % (LOG.name, e["n"], e["prev"][:16], e["n"] - 1, prev[:16]))
        # ⚠ The stored bytes and the canonical bytes must agree, or the head a stamp covers is not
        # the head this reader computes and the whole chain is over a different document.
        if canonical(e) != raw.strip():
            raise SystemExit(
                D + " %s entry %d is not in canonical form. Its stored bytes and its chain digest "
                "would differ, so a proof over the head would attest to something the reader never "
                "sees." % (LOG.name, e["n"]))
        prev = hashlib.sha256(canonical(e)).hexdigest()
        out.append(e)
    return out


def head_at(entries, n):
    return hashlib.sha256(canonical(entries[n - 1])).hexdigest() if n else GENESIS


def check(entries=None, verbose=True):
    """[complaint] -- empty when the record is intact. Never raises for a merely EMPTY log.

    ⚠ AN EMPTY LOG IS NOT A VIOLATION HERE. Nothing has been announced yet, and a control that
    fails before the work begins is a control nobody can keep green, which is a control that gets
    switched off. Whether the announcement is OWED is a publishing condition, and it is enforced
    in `build_package.py` where the decision to publish is actually taken.
    """
    venues, outcomes = plan_vocabulary()
    entries = read_log() if entries is None else entries
    bad = []
    seen, last_utc = {}, None
    for e in entries:
        # ⇒ NOT A DEFECT. The plan is superseded; a venue it never named is a venue nobody
        # forbade. Reported in the listing, not counted against the record's integrity.
        if not re.match(r"^[a-z0-9][a-z0-9.-]*$", str(e.get("venue") or "")):
            bad.append("entry %d names venue %r, which is not a well-formed identifier."
                       % (e["n"], e.get("venue")))
        if e["outcome"] not in outcomes:
            bad.append("entry %d records outcome %r; the plan permits %s."
                       % (e["n"], e["outcome"], "/".join(outcomes)))
        # ⚠ ONE ATTEMPT PER VENUE WAS A RULE HERE AND IS NOT ONE NOW. It existed because a study
        # that posts repeatedly until it clears its own exposure floor has replaced a measurement
        # with an effort. There is no floor and no exposure claim any more, so rationing posts
        # rations nothing -- it would only be this file having an opinion about conduct that no
        # result depends on. Repeats are RECORDED, and counted in the summary, because a reader of
        # the log should be able to see them; they are not refused.
        seen.setdefault(e["venue"], e["n"])
        try:
            t = datetime.datetime.fromisoformat(e["utc"].replace("Z", "+00:00"))
        except Exception:                                                       # noqa: BLE001
            bad.append("entry %d's utc %r does not parse." % (e["n"], e["utc"]))
            continue
        if last_utc and t < last_utc:
            bad.append("entry %d is dated %s, before entry %d at %s. An append-only log whose "
                       "dates run backwards was written out of order or edited."
                       % (e["n"], e["utc"], e["n"] - 1, last_utc.strftime("%Y-%m-%dT%H:%M:%SZ")))
        last_utc = t

    # ⛔ THE HEAD FILES ARE WHAT A BITCOIN PROOF ACTUALLY COVERS. Each is stamped when written, so
    # a head file that disagrees with the log is the log having been rewritten under an anchor.
    for hf in sorted(SERIES.glob("attempts-*.head")):
        try:
            k = int(hf.stem.split("-")[1])
        except ValueError:
            bad.append("%s is not named attempts-<n>.head, so nothing can say which entry it "
                       "pins." % hf.name)
            continue
        want = hf.read_text(encoding="utf-8").strip()
        if k > len(entries):
            bad.append("%s pins entry %d and the log has %d. A head for an entry that does not "
                       "exist means entries were DELETED from the end, which the chain alone "
                       "cannot see." % (hf.name, k, len(entries)))
        elif head_at(entries, k) != want:
            bad.append("%s records head %s and entry %d now hashes to %s. If that file is stamped, "
                       "the rewrite is contradicted by Bitcoin."
                       % (hf.name, want[:16], k, head_at(entries, k)[:16]))
        elif verbose:
            print("  ok  %-24s pins entry %d  %s%s"
                  % (hf.name, k, want[:16], "" if (SERIES / (hf.name + ".ots")).exists()
                     else "   " + W + " NOT STAMPED"))

    # ⛔ AND THE CAPTURES ARE THE SECOND WITNESS, because they are stamped on a schedule whether or
    # not anyone is thinking about the attempts log that week.
    for rec_path in sorted(SERIES.glob("exposure-*.json")):
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        att = rec.get("attempts")
        if not att:
            continue                    # captures written before this field existed
        k = att.get("count", 0)
        if k > len(entries):
            bad.append("%s saw %d attempt(s) and the log now holds %d."
                       % (rec_path.name, k, len(entries)))
        elif att.get("head") != head_at(entries, k):
            bad.append("%s recorded head %s at %d entries; the log now gives %s."
                       % (rec_path.name, str(att.get("head"))[:16], k, head_at(entries, k)[:16]))
    return bad


def record(venue, url, outcome):
    venues, outcomes = plan_vocabulary()
    # ⛔ THE SUPERSEDED PLAN WAS BOTH "NOTHING IN FORCE" AND THE THING THAT DECIDED WHAT COULD BE
    # RECORDED. A reviewer put it exactly: the banner says nothing in the document is in force, and
    # this function refused any venue the document did not name -- so an attempt at a venue outside
    # a withdrawn list could not be logged at all. A historical record cannot also be a gate.
    #
    # ⇒ NOTHING RATIONS VENUES ANY MORE, so nothing here should. Any well-formed identifier is
    # recordable, and the plan's list is reported as CONTEXT -- these are the venues it named --
    # rather than enforced as a vocabulary.
    if venue not in venues:
        print("  %s %r is not among the venues the superseded plan named (%s). Recording it; "
              "the plan is a historical record, not a permission list."
              % (W, venue, ", ".join(venues)))
    if not re.match(r"^[a-z0-9][a-z0-9.-]*$", venue or ""):
        raise SystemExit(
            D + " %r is not a well-formed venue identifier. The log is read back by machine, so "
            "the identifier has to be one: lower-case letters, digits, dots and hyphens."
            % venue)
    # ⚠ OUTCOMES STAY CLOSED. They are the vocabulary the log is READ with -- a reader has to
    # know what "removed" means -- and an open outcome set makes the record unaggregatable. That
    # is a property of the log, not an obligation on anybody.
    if outcome not in outcomes:
        raise SystemExit(D + " %r is not one of the recorded outcomes (%s). Unlike the venue list, "
                             "these are the vocabulary the log is read with; a free-text outcome "
                             "makes the record unreadable rather than unrestricted."
                         % (outcome, "/".join(outcomes)))
    entries = read_log()
    prior = [e for e in entries if e["venue"] == venue]
    if prior:
        # ⚠ THIS USED TO REFUSE. It does not any more -- see the one-per-venue note in `check` --
        # but a repeat is worth SAYING, because the commonest reason to record one twice is not
        # having noticed the first.
        print("  %s %s was already recorded (entry %d, %s, outcome %r). Recording another; "
              "nothing forbids it." % (W, venue, prior[0]["n"], prior[0]["utc"],
                                       prior[0]["outcome"]))
    # ⚠ Complain about the record BEFORE adding to it. Appending onto a chain that already fails
    # its own check buries the break under a new entry and makes the log harder to read back.
    broken = check(entries, verbose=False)
    if broken:
        print(D + " the existing record does not check out. Refusing to append to it:")
        for b in broken:
            print("     - " + b)
        return 1
    e = {"n": len(entries) + 1,
         "outcome": outcome,
         "prev": head_at(entries, len(entries)),
         "url": url,
         "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "venue": venue}
    SERIES.mkdir(exist_ok=True)
    with open(LOG, "ab") as fh:
        fh.write(canonical(e) + b"\n")
    h = hashlib.sha256(canonical(e)).hexdigest()
    hf = SERIES / ("attempts-%d.head" % e["n"])
    hf.write_text(h + NL, encoding="utf-8", newline="\n")
    print("  recorded entry %d: %s %s %s" % (e["n"], venue, outcome, e["utc"]))
    print("  head %s -> %s" % (h[:32], hf.name))
    # Both halves relative to the study directory -- see the note in capture_exposure.py.
    print("  %s NOW STAMP IT (from this directory): python ../../_ots_stamp.py %s"
          % (W, hf.relative_to(HERE).as_posix()))
    print("     An unstamped head is a file we wrote, and the whole point is that we cannot "
          "change it later.")
    return 0


def main():
    # ⛔ THIS LINE WAS AT MODULE SCOPE AND THE CONTROL SUITE DIED ON IT THE FIRST TIME IT IMPORTED
    # THIS FILE. Rebinding `sys.stdout` on import replaces the caller's stream and closes the
    # buffer the old wrapper owned, so `test_controls.py` -- the only thing that had ever imported
    # this module -- raised "I/O operation on closed file" in the middle of its own report.
    # ⇒ A module reconfigures the interpreter in `main()` or not at all. Anything it does on import
    # it does to every program that reads it, including the one checking whether it works.
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    if a[:1] == ["--record"]:
        if len(a) != 4:
            raise SystemExit("usage: attempts.py --record <venue> <url> <outcome>")
        return record(a[1], a[2], a[3])
    venues, outcomes = plan_vocabulary()
    entries = read_log()
    print("=" * 84)
    print(" DISTRIBUTION ATTEMPTS -- %d recorded across %d venue(s); the plan names %d"
          % (len(entries), len({e["venue"] for e in entries}), len(venues)))
    print("=" * 84)
    for e in entries:
        print("  %2d  %-20s %-9s %s  %s" % (e["n"], e["venue"], e["outcome"], e["utc"], e["url"]))
    missing = [v for v in venues if v not in {e["venue"] for e in entries}]
    if missing:
        # ⚠ "NOT YET ATTEMPTED ... an obligation, not an option" is what this said. The venues are
        # a list the superseded plan named; no version obliges any of them now, so they are printed
        # as what they are -- places nothing has been recorded for.
        print("  %s no attempt recorded for: %s" % (W, ", ".join(missing)))
        print("     These are the venues the superseded plan named. Nothing requires them.")
    bad = check(entries)
    print("-" * 84)
    if bad:
        for b in bad:
            print("  " + D + " " + b)
        print("  " + D + " the distribution record does not check out.")
        return 1
    # ⛔ "INTACT" WAS DOING TOO MUCH WORK. The chain and the heads agree -- that is what was
    # checked -- but a truncation that removes the last entry together with its head leaves a log
    # that agrees with itself. Only an external witness makes the end of the log checkable, so the
    # verdict now says which of the two it is.
    _heads = sorted(SERIES.glob("attempts-*.head"))
    _unwitnessed = [h.name for h in _heads if not (SERIES / (h.name + ".ots")).exists()]
    if not _heads:
        print("  ok  the record is internally consistent. %s NO HEAD IS WITNESSED: nothing here "
              "can detect a truncation that removes the last entry and its head together." % W)
    elif _unwitnessed:
        print("  ok  the record is internally consistent, and %d of %d head(s) carry no proof "
              "(%s)." % (len(_unwitnessed), len(_heads), ", ".join(_unwitnessed[:3])))
        print("      %s Deletion of the end is detectable only up to the last WITNESSED head." % W)
    else:
        print("  ok  the record is intact and every head is witnessed: an edit, a backdating or a "
              "truncation would have to contradict a Bitcoin anchor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
