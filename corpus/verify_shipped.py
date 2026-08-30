"""Check the SHIPPED corpus against the anchored manifest, using only what the package contains.

⛔ WHY THIS IS A SEPARATE FILE. `build_corpus.py --verify` re-derives `clean/` from `raw/`, and
`raw/` is deliberately not shipped: the package carries the cleaned texts, the manifest and the
build script, not ten megabytes of Gutenberg downloads. So the only verification tool in the
package reported all ten texts *"absent and --verify fetches nothing"* the first time anyone ran it
there — a true message about a condition that is by design, printed as though the corpus were
broken.

⚠️ AND THE INSTRUCTION THAT SENT THEM THERE WAS TESTED IN THE WRONG TREE. It was run from the
source directory, where `raw/` exists, where it passed. Measuring one tree while exercising another
is an error this project has now made in three separate tools.

⛔ THE FIX IS NOT TO EDIT `build_corpus.py`. That file is pinned by digest in the pre-registration,
and adding a mode to it would move the digest — which is exactly the violation that
`check_commitments.py` was written to catch, committed inside the repair for a different one. A
verification helper is not part of the committed pipeline and does not belong inside it.

WHAT THIS CHECKS. Every clean file's SHA-256 against the manifest, and the Merkle root recomputed
from those digests. That establishes the corpus arrived intact and matches the anchored manifest.
It does NOT re-derive clean text from raw sources — that check needs `raw/` and belongs in the
source tree, and saying so is the point rather than an apology.

    python corpus/verify_shipped.py
"""
import hashlib
import io
import json
import pathlib
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent


def merkle(hexes):
    """The committed tree, IMPORTED rather than reimplemented.

    ⛔ THE FIRST VERSION OF THIS FUNCTION REIMPLEMENTED IT AND GOT IT WRONG THREE WAYS: leaves
    unsorted, hashed as hex strings instead of raw bytes, and concatenated as text. It reported a
    root of 888a40a8 against the committed 2006b732 -- a false alarm on an intact corpus, which a
    reproducer would reasonably have read as "the package is broken".

    It failed safe, and that is luck rather than design. Two implementations of one tree drift;
    the committed one is the definition, so this imports it. `build_corpus.py` is pinned by digest
    and guarded by `if __name__ == "__main__"`, so importing runs nothing.
    """
    sys.path.insert(0, str(HERE))
    import build_corpus
    return build_corpus.merkle(hexes)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    man_p = HERE / "MANIFEST.json"
    if not man_p.exists():
        raise SystemExit(D + " no MANIFEST.json beside this script; nothing to verify against.")
    man = json.loads(man_p.read_text(encoding="utf-8"))

    print("=" * 78)
    print("  SHIPPED CORPUS — every file against the anchored manifest")
    print("=" * 78)
    print()

    bad, leaves = [], []
    for rec in man["texts"]:
        rel = rec["file"].split("/")[-1]
        f = HERE / "clean" / rel
        if not f.exists():
            print("  " + D + " %-14s %s is missing from the package" % ("pg%s" % rec["id"], rel))
            bad.append(rel)
            continue
        got = hashlib.sha256(f.read_bytes()).hexdigest()
        ok = got == rec["clean_sha256"]
        print("  %s %-14s %-42s %s" % ("ok  " if ok else D, "pg%s" % rec["id"],
                                       rec["title"][:42], got[:16]))
        if not ok:
            print("       committed %s" % rec["clean_sha256"][:16])
            bad.append(rel)
        leaves.append(rec["clean_sha256"])

    print()
    if bad:
        print("  " + D + " %d file(s) do not match the manifest. STOP." % len(bad))
        print("  The two arms would not share an input, and any comparison between them")
        print("  measures nothing. Re-copy the package; do not proceed with a partial corpus.")
        return 1

    root = merkle(leaves)
    print("  %d texts, %s bytes" % (len(leaves), "{:,}".format(man["total_clean_bytes"])))
    print("  MERKLE ROOT %s" % root)
    if root != man["merkle_root"]:
        print("  " + D + " committed  %s" % man["merkle_root"])
        print()
        print("  " + D + " every file is individually correct and the ROOT is not. The manifest")
        print("  and the corpus disagree about WHICH texts belong — a disagreement no per-file")
        print("  check can see, which is why the root is recomputed rather than read.")
        return 1
    print("  matches the committed manifest: True")
    print()
    print("  " + W + " This verifies the SHIPPED corpus against the anchored manifest. It does")
    print("  not re-derive clean text from raw sources; that needs corpus/raw/, which the")
    print("  package deliberately does not carry. Run `build_corpus.py --verify` in the source")
    print("  tree for that.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
