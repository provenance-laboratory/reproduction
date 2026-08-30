"""What each OpenTimestamps proof actually attests — parsed, never inferred from prose.

⛔ THREE DOCUMENTS SAID "ANCHORED" WHILE NOTHING WAS. Both round-2 reviewers checked and both
reported the same thing: the corpus proof and the v2 pre-registration proof carry calendar
attestations only, and the sole Bitcoin attestations in this study belong to the SUPERSEDED corpus
proof and the RETIRED v1 pre-registration. **The pilot has the stronger guarantee than the
protocol that replaced it**, which is exactly backwards and was stated nowhere.

⚠️ A PENDING PROOF IS NOT A WEAK ANCHOR, IT IS NOT AN ANCHOR. A calendar attestation is a promise
by a server that it will include the digest in a future Merkle tree. Until a Bitcoin block confirms
it, the only thing standing behind the timestamp is the calendar operator -- which is precisely the
kind of trusted third party the timestamp exists to remove.

⇒ So the word "anchored" is reserved for a proof carrying the Bitcoin attestation tag, this script
decides which those are by reading the bytes, and the documents say "timestamped; Bitcoin anchoring
pending" until it says otherwise.

    python anchor_status.py
"""
import io
import pathlib
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)
HERE = pathlib.Path(__file__).resolve().parent
# The OpenTimestamps Bitcoin attestation tag. Presence of these eight bytes is the difference
# between "a calendar server said so" and "a block confirms it".
BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])


def status(p):
    b = p.read_bytes()
    return ("ANCHORED" if BITCOIN_TAG in b else "pending"), len(b)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    proofs = sorted(f for f in HERE.rglob("*.ots*")
                    if "package" not in f.parts and "review" not in f.parts)
    print("=" * 78)
    print("  OPENTIMESTAMPS STATUS — read from the proof bytes")
    print("=" * 78)
    print()
    active_pending = []
    for f in proofs:
        st, n = status(f)
        superseded = "superseded" in f.name
        tag = "  (superseded)" if superseded else ""
        print("  %-9s %6d B  %s%s" % (st, n, f.relative_to(HERE), tag))
        if st != "ANCHORED" and not superseded:
            active_pending.append(f.relative_to(HERE))
    print()
    if active_pending:
        print("  " + D + " %d ACTIVE proof(s) are NOT anchored:" % len(active_pending))
        for f in active_pending:
            print("      %s" % f)
        print()
        print("  Until these carry a Bitcoin attestation, no document may say the corpus or the")
        print("  protocol is ANCHORED. The honest phrase is 'timestamped; Bitcoin anchoring")
        print("  pending'. Run `python ../../_ots_upgrade.py` once a block has confirmed them.")
        print()
        print("  " + W + " AND DO NOT PUBLISH BEFORE THEY UPGRADE. The proofs are covered by the")
        print("  package's SHA256SUMS, so upgrading one after publication changes a file every")
        print("  reproducer has already checksummed -- `sha256sum -c` then fails for all of them,")
        print("  on a file that grew for the right reason. Publishing after anchoring costs a")
        print("  few hours and removes the choice between a broken checksum and a weak proof.")
        return 1
    print("  every active proof carries a Bitcoin attestation")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
