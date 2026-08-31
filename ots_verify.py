"""Parse an OpenTimestamps proof. Substring tests are not verification.

⛔ WHY THIS EXISTS. Every anchor check in this project decided whether a proof was a proof by
searching it for two byte strings: the document's SHA-256, and the eight-byte Bitcoin attestation
tag. Two round-5 reviewers independently built the same forgery --

    SHA256(document) || \\x05\\x88\\x96\\x0d\\x73\\xd7\\x19\\x01        = 40 bytes

-- and it passed `anchored()`, moved authority in `check_commitments.py`, and let a substituted
`train.py` through with exit 0. `ots info` on the same file says *"is not a timestamp file"*.

⚠️ ROUND 4'S ATTACK SURVIVED ITS OWN REPAIR. A reviewer then passed 35 bytes of junk containing the
tag; the fix added *binding* -- requiring the document's digest to appear -- and never added
*parsing*. So the next reviewer supplied 40 bytes containing both strings and was believed. Two
rounds, one defect, because the repair addressed the instance rather than the class: **a proof is a
structure, and looking for bytes inside it is not reading it.**

⇒ This walks the actual serialisation: magic header, version, the file-hash operation and its
digest, then the operation tree, collecting attestation records. It fails closed on any byte it
does not recognise, because an unparseable proof is not a passing proof.

⚠️ WHAT IT STILL DOES NOT DO, so nobody reads more into a pass. It does not contact a Bitcoin node
or a calendar, so it does not confirm that the named block exists or that its merkle root matches.
It establishes that the file IS an OpenTimestamps proof, that it commits to THESE bytes, and that
it carries a Bitcoin attestation naming a block height. Confirming the attestation path against a
chain is a network operation and belongs in the publication checklist.

⛔ AND ANCHORING ANSWERS *WHEN*, NEVER *WHO*. A reviewer put it exactly: stamping is free, public
and unilateral, so anyone with write access can stamp their own successor document and wait two
hours. What an anchor buys is a delay, not a refusal. Authorship needs a signature, which this
module deliberately does not pretend to provide.

    python ots_verify.py <file.ots> <document>
"""
import hashlib
import io
import pathlib
import sys

NL = chr(10)
D = chr(0x26D4)
W = chr(0x26A0)

MAGIC = (bytes([0x00]) + b"OpenTimestamps" + bytes([0x00, 0x00]) + b"Proof" + bytes([0x00])
         + bytes([0xbf, 0x89, 0xe2, 0xe8, 0x84, 0xe8, 0x92, 0x94]))
BITCOIN_TAG = bytes([0x05, 0x88, 0x96, 0x0d, 0x73, 0xd7, 0x19, 0x01])
PENDING_TAG = bytes([0x83, 0xdf, 0xe3, 0x0d, 0x2e, 0xf9, 0x0c, 0x8e])

ATTESTATION = 0x00
FORK = 0xff
# operations that consume a length-prefixed argument
OPS_WITH_ARG = {0xf0: "append", 0xf1: "prepend"}
# operations that consume nothing
OPS_PLAIN = {0xf2: "reverse", 0xf3: "hexlify", 0x02: "sha1", 0x03: "ripemd160",
             0x08: "sha256", 0x67: "keccak256"}
DIGEST_LEN = {0x02: 20, 0x03: 20, 0x08: 32, 0x67: 32}


class NotAProof(Exception):
    """The bytes are not an OpenTimestamps proof. Distinct from 'a proof that says nothing'."""


class _Reader:
    def __init__(self, b):
        self.b, self.i = b, 0

    def byte(self):
        if self.i >= len(self.b):
            raise NotAProof("ran off the end of the file")
        self.i += 1
        return self.b[self.i - 1]

    def varuint(self):
        """Base-128, little-endian, high bit as continuation -- the format's own integer."""
        val, shift = 0, 0
        while True:
            c = self.byte()
            val |= (c & 0x7f) << shift
            if not c & 0x80:
                return val
            shift += 7
            if shift > 63:
                raise NotAProof("varint longer than any real value")

    def take(self, n):
        if self.i + n > len(self.b):
            raise NotAProof("declared length %d runs past the end of the file" % n)
        self.i += n
        return self.b[self.i - n:self.i]

    def varbytes(self):
        return self.take(self.varuint())


def _apply(op, msg, arg):
    """One operation, evaluated. The path is COMPUTED, not skipped over."""
    if op == 0xf0:
        return msg + arg
    if op == 0xf1:
        return arg + msg
    if op == 0xf2:
        return msg[::-1]
    if op == 0xf3:
        return msg.hex().encode()
    if op == 0x02:
        return hashlib.sha1(msg).digest()
    if op == 0x03:
        try:
            return hashlib.new("ripemd160", msg).digest()
        except ValueError:
            raise NotAProof("ripemd160 unavailable in this build, so this path cannot be walked")
    if op == 0x08:
        return hashlib.sha256(msg).digest()
    raise NotAProof("operation 0x%02x cannot be evaluated" % op)


def _walk(r, found, msg, depth=0):
    """Consume one timestamp, EVALUATING each operation so the attestation's root is known.

    ⛔ AN EARLIER VERSION SKIPPED THE ARGUMENTS INSTEAD OF APPLYING THEM. It parsed the structure
    and never computed anything, so flipping one byte inside an append argument still passed --
    the shape was intact and the path led somewhere else entirely. Structure without evaluation is
    a shallower check than it looks, which is the same lesson as substring-instead-of-parse, one
    level in.

    ⚠ Computing the root does not verify it. Only the chain knows what root block N committed
    to. What this buys is that the root is REPORTED, so a reader can look it up -- and that a byte
    flipped anywhere in the path changes it.
    """
    if depth > 256:
        raise NotAProof("operation tree deeper than any real proof")
    while True:
        tag = r.byte()
        if tag == ATTESTATION:
            kind = r.take(8)
            payload = r.varbytes()
            if kind == BITCOIN_TAG:
                found.append(("bitcoin", _Reader(payload).varuint(), msg[::-1].hex()))
            elif kind == PENDING_TAG:
                found.append(("pending", payload[1:].decode("utf-8", "replace"), ""))
            else:
                found.append(("unknown:" + kind.hex(), len(payload), ""))
            return
        if tag == FORK:
            _walk(r, found, msg, depth + 1)
            continue
        if tag in OPS_WITH_ARG:
            msg = _apply(tag, msg, r.varbytes())
            continue
        if tag in OPS_PLAIN:
            msg = _apply(tag, msg, b"")
            continue
        raise NotAProof("unknown operation byte 0x%02x at offset %d" % (tag, r.i - 1))


def verify(proof_bytes, document_bytes):
    """(ok, why, attestations). ok means: a real proof, over THESE bytes, with a Bitcoin block."""
    try:
        r = _Reader(proof_bytes)
        if r.take(len(MAGIC)) != MAGIC:
            raise NotAProof("no OpenTimestamps magic header -- this is not a proof file at all")
        r.varuint()                                       # serialisation version
        op = r.byte()
        if op not in DIGEST_LEN:
            raise NotAProof("file-hash operation 0x%02x is not a digest operation" % op)
        digest = r.take(DIGEST_LEN[op])
        want = hashlib.new({0x02: "sha1", 0x03: "ripemd160", 0x08: "sha256",
                            0x67: "sha256"}[op], document_bytes).digest()
        if op == 0x67:
            return False, "keccak256 file hash is not supported here", []
        if digest != want:
            return False, ("the proof commits to %s and the document hashes to %s -- this proof "
                           "is over different bytes" % (digest.hex()[:16], want.hex()[:16])), []
        found = []
        _walk(r, found, digest)
        if r.i != len(proof_bytes):
            raise NotAProof("%d trailing byte(s) after the proof ended" % (len(proof_bytes) - r.i))
    except NotAProof as e:
        return False, "NOT A PROOF: %s" % e, []
    blocks = [(h, root) for k, h, root in found if k == "bitcoin"]
    if not blocks:
        pend = [v for k, v, _r in found if k == "pending"]
        return False, ("parsed, over the right bytes, and carries no Bitcoin attestation%s"
                       % (" (pending at %s)" % ", ".join(pend[:2]) if pend else "")), found
    return True, ("anchored in Bitcoin block(s) %s; merkle root(s) computed from these bytes: "
                  "%s" % (sorted({h for h, _r in blocks}),
                          ", ".join(sorted({r[:16] for _h, r in blocks})))), found


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if len(sys.argv) < 3:
        raise SystemExit("usage: python ots_verify.py <file.ots> <document>")
    proof, doc = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    ok, why, found = verify(proof.read_bytes(), doc.read_bytes())
    print("  %s  %s" % ("ok " if ok else D, why))
    for k, v, root in found:
        print("      attestation %-10s %s %s" % (k, v, ("root " + root[:32]) if root else ""))
    if ok:
        print()
        print("  " + W + " This says the file IS a proof, over THESE bytes, naming a block. It does")
        print("  not contact a node, so it does not confirm the block exists or that its merkle")
        print("  root matches. And an anchor answers WHEN, never WHO.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
