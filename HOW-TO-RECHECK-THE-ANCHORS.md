# How to re-check the anchors, without taking our word for them

**`ANCHORS.json` is in this package so that `ots_verify.py` can do its job. It is also the one file
here that is our assertion rather than a derivation, so this document exists to tell you how to
replace it with your own.**

---

## What the pins are, and what they are not

An OpenTimestamps proof for a document ends in a **Bitcoin attestation**: a claim that a particular
merkle root was committed in a particular block. Verifying it needs two halves:

```
the proof     computes a merkle root from the document's bytes        <- shipped, self-contained
the chain     says what root block N actually has                     <- NOT in the proof
```

`ANCHORS.json` supplies the second half. Without it `ots_verify.py` can only report **STRUCTURAL**
— *"this parses and names block N, but naming a block is not being in it"* — which is what it does
if you delete the file. Try it; the refusal is the point.

⛔ **A pin is an explorer's word on a date, not a node.** The file says so itself, and it records
which operators agreed on each block; at least two must agree or nothing is pinned. But **agreement
between APIs is not the chain.** If the pins were wrong, every proof here would verify against a
wrong answer and look fine.

⇒ **So do not trust this file. Recompute it.**

## The strong version: your own node

If you run Bitcoin Core, this settles it completely and depends on nobody:

```bash
# for each height in ANCHORS.json
bitcoin-cli getblockhash 965818
bitcoin-cli getblockheader 00000000000000000000... | jq -r '.merkleroot'
```

Compare `merkleroot` against the `merkle_root` this file pins for that height. **They must be equal
for every block.** A single mismatch means the pin is wrong and nothing anchored by it is anchored.

## The weaker version: independent APIs

No node? Ask operators that do not share a codebase, and require them to agree with each other
rather than with us:

```bash
H=965818
curl -s https://blockstream.info/api/block-height/$H          # -> block hash
curl -s https://blockstream.info/api/block/<hash>   | jq -r .merkle_root
curl -s https://blockchain.info/rawblock/<hash>     | jq -r .mrkl_root
```

⚠️ `blockstream` and `mempool.space` are different operators running **the same Esplora software**.
Treating them as two independent confirmations overstates what you have. `blockchain.info` is a
different codebase, so a blockstream/blockchain.info agreement is worth more than a
blockstream/mempool one.

## What re-checking actually proves

```
pins recomputed and equal    the proofs' Bitcoin attestations are real, and the documents they
                             bind existed before those blocks were mined
pins recomputed and equal    ...says NOTHING about whether the documents are TRUE, or whether any
                             run obeyed the protocol they describe. An anchor answers WHEN
a pin disagrees              the anchor is void. Treat every claim resting on it as unsupported
```

## If you find a disagreement

**Please file it**, at `github.com/provenance-laboratory/reproduction/issues`. Include the height,
the root you obtained, and how you obtained it.

⚠️ A disagreement is a finding we want, exactly like a differing weights digest. It would mean
either that our pin is wrong — in which case the record needs correcting — or that something
between you and the chain is not what it claims to be. **Both are worth more than a quiet pass.**

---

*The anchors bind protocol documents to a point in time. They are not evidence about the model, the
corpus, or the reproduction. Those are settled by running `train.py` and comparing digests.*
