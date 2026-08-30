"""Fetch the fixed source list, strip it to public-domain text, and commit a Merkle root.

⛔ THE ORDER IS THE POINT. sources.json was fixed before anything was fetched; the digests are
recorded on first retrieval and never edited; the Merkle root is computed over the CLEANED bytes
and OpenTimestamped BEFORE the first training step. A corpus commitment made after training is
not a commitment, it is a description.

WHAT "CLEANED" MEANS, EXACTLY, because a reproducer must be able to redo it:

  1. decode as UTF-8, dropping a byte-order mark if present
  2. normalise CRLF and CR to LF
  3. take only the text strictly between the Project Gutenberg START and END markers
  3b. drop any paragraph that still mentions Project Gutenberg (editorial notes)
  4. strip trailing whitespace from every line
  5. collapse three or more consecutive blank lines to two
  6. ensure exactly one trailing newline
  7. re-encode as UTF-8, and REFUSE if any reference survived

Every step is deterministic and order-dependent, so it is written here rather than described.
Project Gutenberg's terms make removing the licence AND ALL REFERENCES the condition for using the
underlying work freely, so steps 3 and 3b together are what leave the public-domain text -- and
step 7 ASSERTS it, because the first version of this file claimed the boilerplate removal was
sufficient and one clean text still said "Project Gutenberg's archives" in a transcriber's note.
An external reviewer found that, which is the correct outcome and an expensive one: the fix
changes the corpus bytes, so the Merkle root, its timestamp and every measurement downstream are
regenerated.

⚠️ SCOPE. Removing the licence and all references leaves the work unrestricted under US law by
Project Gutenberg's own terms. It does not adjudicate the underlying edition, translation or
typography in every jurisdiction, and this corpus does not claim it does.

⚠️ UPSTREAM DRIFT IS A FINDING. Project Gutenberg revises its files. If a raw digest recorded on
first fetch no longer matches, this refuses rather than absorbing the change, because the corpus
the model trained on must be the corpus the manifest describes.

    python build_corpus.py            fetch what is missing, clean, write the manifest
    python build_corpus.py --verify   re-verify everything; fetch nothing; write nothing
"""
import hashlib
import io
import json
import pathlib
import re
import subprocess
import sys

NL = chr(10)
HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "raw"
CLEAN = HERE / "clean"
SRC = HERE / "sources.json"
MANIFEST = HERE / "MANIFEST.json"
UA = "provenance-laboratory/reproduction research corpus (contact: parthms.id@gmail.com)"

START = re.compile(r"^\*\*\* ?START OF TH[EIS][^\n]*\*\*\* ?$", re.M)
END = re.compile(r"^\*\*\* ?END OF TH[EIS][^\n]*\*\*\* ?$", re.M)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fetch(pgid, dst):
    url = "https://www.gutenberg.org/cache/epub/%d/pg%d.txt" % (pgid, pgid)
    tmp = dst.with_suffix(".part")
    r = subprocess.run(["curl", "-sSL", "--max-time", "120", "-A", UA,
                        "-w", "%{http_code}", "-o", str(tmp), url],
                       capture_output=True, timeout=180)
    code = r.stdout.decode("ascii", "replace").strip()[-3:]
    if code != "200" or not tmp.exists() or tmp.stat().st_size < 10000:
        tmp.unlink(missing_ok=True)
        return None, "HTTP %s, %s bytes" % (code, tmp.stat().st_size if tmp.exists() else 0)
    body = tmp.read_bytes()
    # verify BEFORE moving into place: an error page must never take the name of a source text
    try:
        norm = decoded(body)
    except UnicodeDecodeError:
        tmp.unlink(missing_ok=True)
        return None, "not valid UTF-8"
    if not (START.search(norm) and END.search(norm)):
        tmp.unlink(missing_ok=True)
        return None, "no START/END markers -- not a Project Gutenberg text file"
    tmp.replace(dst)
    return body, None


def decoded(raw_bytes):
    """Decode and normalise line endings BEFORE anything looks for a marker.

    The first version searched for the START/END markers in the raw text, which still carries
    CRLF, so the marker pattern never matched and all ten sources were refused as "not a Project
    Gutenberg text file". The files were fine; the check was wrong. Normalising first makes the
    marker search and the cleaning agree about what a line is.
    """
    s = raw_bytes.decode("utf-8-sig", "strict")
    return s.replace(chr(13) + NL, NL).replace(chr(13), NL)


# ⛔ A REFERENCE CAN SURVIVE THE MARKERS. Project Gutenberg's terms make removal of the
# licence AND OF ALL REFERENCES the condition for redistributing the underlying work freely. The
# marker extraction removes the boilerplate; it does not remove a mention that sits INSIDE the
# extracted span. `pg2701.txt` carried one, in a transcriber's note describing where the etext
# came from -- so the corpus did not satisfy the condition the docstring claimed it satisfied,
# and an external reviewer found it, not us.
#
# ⚠️ The fix is a rule over the CLASS, not a patch for the one file that failed. A special case
# for pg2701 would leave the next text's note to be discovered by whoever redistributes it.
PG_REFERENCE = re.compile(r"project\s+gutenberg", re.I)


def _drop_referring_paragraphs(t):
    """Remove any blank-line-delimited paragraph that mentions Project Gutenberg.

    ⚠️ WHY PARAGRAPHS AND NOT LINES. A line-level deletion leaves the surrounding sentence
    fragmentary, which corrupts the work in a way that is harder to notice than a missing
    paragraph. These references occur in editorial notes -- transcriber's notes, production
    credits -- which are additions to the public-domain work rather than part of it, and a
    paragraph is the unit those come in.
    """
    kept, dropped = [], []
    for para in t.split(NL + NL):
        (dropped if PG_REFERENCE.search(para) else kept).append(para)
    return (NL + NL).join(kept), dropped


def clean(raw_bytes):
    t = decoded(raw_bytes)
    m1, m2 = START.search(t), END.search(t)
    if not (m1 and m2 and m1.end() < m2.start()):
        raise ValueError("markers missing or out of order")
    t = t[m1.end():m2.start()]
    t, dropped = _drop_referring_paragraphs(t)
    t = NL.join(line.rstrip() for line in t.split(NL))
    t = re.sub(NL + "{3,}", NL * 2, t)
    out = (t.strip() + NL).encode("utf-8")
    # ⛔ AND THE ASSERTION, because a cleaning rule nobody checks is a comment. If a
    # reference survives this, the file is not redistributable on the terms the manifest claims
    # and the build stops rather than writing a manifest that says otherwise.
    if PG_REFERENCE.search(out.decode("utf-8")):
        raise ValueError("a Project Gutenberg reference survived cleaning")
    return out, dropped


def merkle(leaves):
    """Binary Merkle root over sorted leaf digests; odd node is promoted, not duplicated.

    Duplicating an odd node is the classic CVE-2012-2459 shape. Promotion avoids it and is
    stated here so a reproducer implements the same tree rather than a plausible one.
    """
    layer = sorted(leaves)
    if not layer:
        return None
    layer = [bytes.fromhex(h) for h in layer]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer) - 1, 2):
            nxt.append(hashlib.sha256(layer[i] + layer[i + 1]).digest())
        if len(layer) % 2:
            nxt.append(layer[-1])
        layer = nxt
    return layer[0].hex()


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    verify = "--verify" in sys.argv
    src = json.loads(SRC.read_text(encoding="utf-8"))
    RAW.mkdir(exist_ok=True)
    CLEAN.mkdir(exist_ok=True)

    entries, problems, changed = [], [], False
    for t in src["texts"]:
        pid = t["id"]
        rawp = RAW / ("pg%d.txt" % pid)
        if not rawp.exists():
            if verify:
                problems.append("pg%d: absent and --verify fetches nothing" % pid)
                continue
            body, err = fetch(pid, rawp)
            if body is None:
                problems.append("pg%d: %s" % (pid, err))
                continue
        body = rawp.read_bytes()
        rs = sha(body)

        if t.get("raw_sha256") is None:
            if verify:
                problems.append("pg%d: no recorded digest yet" % pid)
                continue
            t["raw_sha256"] = rs
            changed = True
        elif t["raw_sha256"] != rs:
            problems.append("pg%d: UPSTREAM DRIFT -- recorded %s, now %s"
                            % (pid, t["raw_sha256"][:16], rs[:16]))
            continue

        cb, dropped = clean(body)
        cp = CLEAN / ("pg%d.txt" % pid)
        if not verify:
            cp.write_bytes(cb)
        entries.append({"id": pid, "title": t["title"], "author": t["author"],
                        "year": t["year"], "file": "clean/pg%d.txt" % pid,
                        "raw_sha256": rs, "clean_sha256": sha(cb), "clean_bytes": len(cb),
                        # What step 3b removed, recorded so the deletion is auditable rather
                        # than silent. A cleaning rule that removes text without saying what it
                        # removed is indistinguishable from a corpus that never had it.
                        "paragraphs_dropped_for_pg_reference": len(dropped),
                        "dropped_text": [d.strip()[:400] for d in dropped]})
        print("  pg%-5d %-38s raw %s  clean %s  %8d B"
              % (pid, t["title"][:38], rs[:8], sha(cb)[:8], len(cb)))

    if problems:
        print()
        for p in problems:
            print("  " + chr(0x26D4) + " %s" % p)
        print()
        print("  refusing to write a manifest over an incomplete or drifted corpus.")
        return 1

    root = merkle([e["clean_sha256"] for e in entries])
    total = sum(e["clean_bytes"] for e in entries)
    man = {
        "_readme": "The corpus this experiment trains on. merkle_root is over the sorted "
                   "clean_sha256 leaves, promoting an odd node rather than duplicating it. "
                   "The root is OpenTimestamped BEFORE the first training step.",
        "built": src["fixed_at"], "selection_rule": src["selection_rule"],
        "cleaning": ["decode utf-8, drop BOM", "CRLF and CR -> LF",
                     "take only the text strictly between the PG START and END markers",
                     "strip trailing whitespace per line",
                     "collapse 3+ blank lines to 2", "single trailing newline", "encode utf-8"],
        "texts": entries, "text_count": len(entries), "total_clean_bytes": total,
        "merkle_root": root,
    }
    print()
    print("  %d texts, %s bytes cleaned" % (len(entries), "{:,}".format(total)))
    print("  MERKLE ROOT %s" % root)
    if verify:
        old = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
        same = old.get("merkle_root") == root
        print("  matches the committed manifest: %s" % same)
        return 0 if same else 1

    if changed:
        SRC.write_text(json.dumps(src, indent=2) + NL, encoding="utf-8", newline=NL)
        print("  recorded raw digests into sources.json (first fetch only)")
    MANIFEST.write_text(json.dumps(man, indent=2) + NL, encoding="utf-8", newline=NL)
    print("  wrote MANIFEST.json")
    print()
    print("  " + chr(0x26A0) + " NEXT, AND BEFORE ANY TRAINING: OpenTimestamp MANIFEST.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
