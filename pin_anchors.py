"""Pin the Bitcoin blocks our proofs name, so an offline check can mean something.

⛔ WHY THIS EXISTS. `ots_verify.py` parsed an OpenTimestamps proof, evaluated its operation tree,
and then reported "anchored in Bitcoin block(s) [N]" on the strength of having READ an attestation
record. Two round-6 reviewers minted a structurally valid attestation offline -- one naming block
999999 -- and moved authority with it. **Naming a Bitcoin attestation is not being anchored in
Bitcoin.** The parse was real; the conclusion drawn from it was not.

⇒ An OpenTimestamps Bitcoin attestation asserts: apply these operations to the document's digest
and you get the MERKLE ROOT OF BLOCK N. That is checkable offline against one number per block --
the block's real merkle root -- which this tool fetches from a public explorer and records here.
A forged attestation naming a block we have not pinned is STRUCTURAL, never authority; a forged
attestation naming a real block computes a root that will not match it.

⚠️ THIS IS A PIN, NOT A NODE. It moves the trust from "the proof says so" to "this explorer said
so on this date, and anyone may recompute it against the chain". That is weaker than running a
full node and stronger than believing the artifact about itself. The source and date are recorded
so the claim can be re-checked rather than taken.

    python pin_anchors.py            fetch and record every block our proofs name
    python pin_anchors.py --verify   re-fetch and refuse if any pin has moved
"""
import datetime
import io
import json
import pathlib
import sys
import time
import urllib.request

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "ANCHORS.json"
API = "https://blockstream.info/api"
UA = "pqbitcoin-reproduction-anchor-pin (mailto:parthms.id@gmail.com)"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace").strip()


def block(height):
    h = _get("%s/block-height/%d" % (API, height))
    time.sleep(1.0)
    d = json.loads(_get("%s/block/%s" % (API, h)))
    if d.get("height") != height:
        raise SystemExit(D + " the explorer returned height %s for %d" % (d.get("height"), height))
    return {"hash": h, "merkle_root": d["merkle_root"], "timestamp": d.get("timestamp")}


def heights():
    """Every Bitcoin height our own proofs attest to. Projected over the directory."""
    sys.path.insert(0, str(HERE))
    import ots_verify as OV
    # ⛔ THIS GLOBBED `PRE-REGISTRATION*.md` -- A FILENAME PATTERN STANDING IN FOR "every proof
    # this artifact requires". It pinned 15 blocks; the required proofs name 16. The missing one
    # is block 964747, `corpus/MANIFEST.json.ots` -- the only non-protocol document in the
    # required list, and the timestamp v3 section 2's non-retrofit argument rests on. Under the
    # new rule an unpinned block is STRUCTURAL, so my own repair made the corpus timestamp
    # indistinguishable from a fabrication. Both round-7 reviewers found it.
    #
    # ⚠ The projection is over EVERY .ots beside a file it binds, plus anchor_status.py's own
    # ALWAYS list, so a proof this project treats as required cannot fall outside the pin set by
    # not being named like a protocol document.
    import anchor_status as _AS
    docs = [d for d in sorted(HERE.glob("PRE-REGISTRATION*.md"))]
    for _rel in getattr(_AS, "ALWAYS", ()):
        _d = HERE / _rel
        if _d.exists() and _d not in docs:
            docs.append(_d)
    for _o in sorted(HERE.rglob("*.ots")):
        if ".superseded-" in _o.name:
            continue
        _d = _o.with_suffix("")
        if _d.exists() and _d not in docs:
            docs.append(_d)

    out = {}
    for doc in docs:
        p = pathlib.Path(str(doc) + ".ots")
        if not p.exists():
            continue
        try:
            ok, _why, found = OV.verify(p.read_bytes(), doc.read_bytes())
        except Exception:                                                    # noqa: BLE001
            continue
        for kind, h, root in found or []:
            if kind == "bitcoin":
                out.setdefault(int(h), set()).add(root)
    return out


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace",
                                  line_buffering=True)
    verify = "--verify" in sys.argv
    want = heights()
    print("=" * 78)
    print("  BITCOIN ANCHORS -- %d block(s) our proofs name" % len(want))
    print("=" * 78)
    print()
    old = {}
    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8")).get("blocks", {})
    rec, bad = {}, []
    for h in sorted(want):
        try:
            b = block(h)
        except Exception as e:                                               # noqa: BLE001
            print("  %s %-8d fetch failed: %s" % (D, h, str(e)[:50]))
            bad.append(h)
            continue
        rec[str(h)] = b
        computed = want[h]
        match = b["merkle_root"] in computed
        print("  %s %-8d merkle %s  %s"
              % ("ok  " if match else D + "   ", h, b["merkle_root"][:24],
                 "matches our proof" if match else "DOES NOT MATCH OUR PROOF"))
        if not match:
            bad.append(h)
        if verify and str(h) in old and old[str(h)] != b:
            print("     " + D + " the pin has MOVED since it was recorded")
            bad.append(h)
        time.sleep(1.0)

    # ⛔ A SUBSET TEST WHERE IT SHOULD BE AN EQUALITY. This walked the blocks OUR PROOFS NAME and
    # checked each one, so a block nobody names was simply never looked at: a round-7 reviewer
    # added a fabricated block with a chosen root and `--verify` exited 0. The file was protected
    # against DAMAGE -- rewriting a real root breaks a real proof and everything goes red -- and
    # unprotected against EXTENSION, which is the direction an attack uses, because every existing
    # verification still succeeds. It is the same equality-not-skip rule this project already
    # applies to distribution subsets, missing here.
    _recorded = set(old) if verify else set()
    if verify:
        _extra = sorted(_recorded - {str(h) for h in want})
        if _extra:
            print()
            print("  " + D + " %d block(s) are pinned that NO PROOF NAMES: %s"
                  % (len(_extra), _extra[:4]))
            print("  A pin nobody needs is a root somebody added. Additions are the direction an")
            print("  attack uses: every existing check still passes, so nothing else notices.")
            bad.extend(_extra)

    if bad:
        print()
        print("  " + D + " %d block(s) failed" % len(bad))
        return 1
    if verify:
        print()
        print("  ok  every pin re-fetches to the same block, matches our proofs, and NO PIN IS")
        print("  PRESENT THAT NO PROOF NAMES.")
        return 0
    OUT.write_text(json.dumps({
        "_readme": ("The Bitcoin blocks our OpenTimestamps proofs attest to, with the merkle root "
                    "each one really has. ots_verify.py grants ANCHORED only when a proof's "
                    "computed root equals the root pinned here; a proof naming a block absent "
                    "from this file is STRUCTURAL and is never authority."),
        "source": API,
        "fetched_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "caveat": (W + " A pin is an explorer's word on a date, not a node. It is recorded so a "
                   "reader can recompute it against the chain, which is the only thing that "
                   "settles it."),
        "blocks": rec,
    }, indent=1) + NL, encoding="utf-8")
    print()
    print("  wrote %s -- %d block(s)" % (OUT.name, len(rec)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
