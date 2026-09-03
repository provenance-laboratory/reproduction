# Pre-registration v10 — the anchor file stops being a byte pin

Supersedes v9 §2. Every digest below was measured when this document was written, and every one is
re-derivable with `sha256sum`. This version exists because five gate files changed and because the
anchor file could never be pinned by digest in the first place.

## 1. Why v9 needed replacing

v9 pinned 22 paths. Eight of them no longer hash to what it recorded:

- `build_package.py` — v9 recorded `8f5f53139d4d3370`, it now hashes to `7087ec4aeaf6b0bc`
- `build_review_packet.py` — v9 recorded `6c056ecfbd4d048b`, it now hashes to `800e79d9a4ea9351`
- `check_commitments.py` — v9 recorded `a83088bdbe955597`, it now hashes to `61b8bfbfd9e447ed`
- `pin_anchors.py` — v9 recorded `027e068318393b96`, it now hashes to `ba41da49785bba06`
- `reproduce_findings.py` — v9 recorded `78d570f5df51245e`, it now hashes to `d9c6be8882464a59`
- `test_controls.py` — v9 recorded `ed6c0fe3fc747aae`, it now hashes to `6fa3341c5941cdad`
- `verify_package.py` — v9 recorded `bac029355505ad25`, it now hashes to `2f80ff99f8c92bae`

Five are gate and packaging scripts repaired across rounds 12 and 13 — the reviewer-found crash on
a pending successor, the NO-TABLE threshold that was wrong from both sides, the substring cache
exclusion in the tree digest, the accusatory wording on an undecidable dynamic-globals read, and
the multi-source rewrite of the anchor pinner. `reproduce_findings.py` gained progress output and
lost a runtime claim it had no business making. **The tool's own rule is that a changed gate file
is a new protocol version, stamped and anchored — not a re-pinned old one.** This is that version.

## 2. ⛔ What is committed, by DIGEST — replacing v9 §2a and §2b

### 2a. Experimental inputs

```
corpus/MANIFEST.json       fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py     2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json        7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30
train.py                   ebd61532782573a04aca8ab5d526ab6d233c450963ac111460f2d5d86f81d2fe
```

### 2b. Instruments and gates

```
PUBKEY.asc                 88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py           6a25887d9758fdc629c96b2e84f4380bb6fe7abf8581c7e63b7507cd3958206a
build_package.py           7087ec4aeaf6b0bcb7e96523f8f92b3ba47d8fa302f9db3940300dedc42d9519
build_review_packet.py     800e79d9a4ea93518d96f4bd121feb5859258cba708f8d565ec254d49569c7b6
check_commitments.py       61b8bfbfd9e447ed7d036e186a2f49dbfb3e94b71e5bcfa6d63905f46303da5a
check_signature.py         76923dcbcf0d6b4b36af0cc0057dacba39194baab5ff9babf05f350b24f49fe5
corpus/verify_shipped.py   943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
measure_cost.py            4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py      d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py        9686200fc21b08e1ef0cfeb14f7ecda9733bc34296e0318b7e63c4f390b6effc
measure_storage.py         1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
ots_verify.py              15ca911511c6c8aff0eee0c2821203cc201d689788f4687bee63e00c8a7c2ca9
pin_anchors.py             ba41da49785bba069a6bfbfe341d003547d661b79e5561c9a946352ca87da318
reproduce_findings.py      d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
seed_sensitivity.py        1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
test_controls.py           6fa3341c5941cdadfe3a64a9063d346e4a497b0360b73d4c0d368eba79e59991
verify_package.py          2f80ff99f8c92baef0a89e9f797e69611597f9698458e8653d91550d259ee748
```

### 2c. ⛔ What the reproducer package contains

```
check_commitments.py
check_signature.py
corpus/MANIFEST.json
corpus/build_corpus.py
corpus/sources.json
corpus/verify_shipped.py
ots_verify.py
test_controls.py
train.py
```

### RETIRES

```
ANCHORS.json
```

`ANCHORS.json` is retired **from the byte-pinned table only**, and is replaced by §2d below. It is
not removed from the protocol; it is committed in a shape that can survive its own use.

## 3. ⛔ Why the anchor file could never be pinned by digest

Anchoring a protocol version stamps it. Stamping produces new Bitcoin attestations. Recording
those attestations rewrites `ANCHORS.json`. So **the act of making version N authoritative
invalidates version N's own pin of the anchor file**, and every version since v8 has been void in
that one entry from the moment it took effect. That was not carelessness. A digest says "these
bytes never change", and the true commitment is "this file may grow but may never lie" — a
different shape, which a digest cannot express.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each line is a Bitcoin block height and the merkle root `ANCHORS.json` records for it. **Every
line must remain present and unchanged. New heights may be added and are not a violation.** A
later anchoring therefore adds to this commitment and can never contradict it.

```
964534     018d69dc7bf4e2e8a45fdf3a89855b9b7e03027227aa14e596a91dcf320e09b9
964535     ef17461955701f9c1d296245df4ab22a71a7e3e0fd3ceeb7213de12958ba69c5
964549     e863c303c5b515da7544652b29648659c66ff2fa6ffad9fe82ccc975042eb439
964747     8a9766909969f175693a1fd85a7236e3be4d33a95cd4a0bcab3fff2e76e16857
964761     23019c9499bd74096ae1d9c4015bc4f10176900d99cb805e7252011ed7415d37
964762     ff5f6043b9883f8e8830856a16dc52783c66d1185d6ffebab5dbe3598f42c543
964775     ed2dd86c5b3c983d859139542aeced248e1f18ec030ccd550e36286a59f54f5e
964785     8aac2039e614e1557aab7264848c8b0cb1152970f2d5e7fa76170ccdfbf2a587
964789     b73d9657064cb4a9842e18ec1a007bc4702308730257cc378dd56ed3443ec0dd
964812     9cd60bdc0fdc9ba7784f8a4705c22d11b82b081a41d69ff598729522834dbd4a
964815     ac3592ef064ea4e4c7db187954f057550018a38dfa02afc7a2c3d33ad2955b76
964848     5784c7dab006cedba2172ec6cce265b83b1f75c8a27a117f4b2df1165b151d9c
964856     a2c750b72ab68db7602962f230b1e8a236633d5cef8f132fed1547b3ac6aba9e
964878     b9fef3d8dd2fc6b2945cb580525f25beaf5612b7b71e3a1b78799e22f353dce0
964881     45cb82a2d9677e318826afb6fd6f3a6be84b5cf94780ee1487b49097d5293579
964920     7f5a7092d6b342430276b08b492f1f18e8a6fa8ddb55a6245f0d93f6e70e13d3
964922     d876c661233b2de9d92f1dabebf9c1a677570711dbec02b1e5317502b2610fe6
964923     92687073de11e6fd31a71c3f6aa0c75aa60a0950dffa30b80ad91155425f4986
965140     c836cd739ba5bddf491db621fcfe76154d6002cecfb10dd4a72eecd99e039ec6
965142     df6e4b4f68795f65252340e42467d77e8e8c2a44e1e5a4ff40730848aca56eb6
965152     46e025634022f51ac766cc16d8be33c04068c0eb7e7a2f66930e022ca4185ece
```

This is strictly stronger than the byte pin in the way that matters: reformatting the file cannot
launder a changed root, and adding a fabricated block cannot remove a real one. `check_commitments.py`
verifies every fact on every run, over every anchored version's facts rather than only this one.

## 4. ⚠️ A pin is still not a node — and now it is not one explorer either

A round-13 reviewer objected that settling authority by live re-fetch "moves the trust root from a
file you write to a block explorer you query", which replaces one single point of trust with
another. That objection is accepted. `pin_anchors.py` now requires **agreement between at least
two independent operators** on both the block hash and the merkle root, records which operators
agreed, and **refuses on disagreement rather than taking a majority**. Two of the three run the
same Esplora software and one is a different codebase; the record says so, because partial
independence reported as independence would be the same defect one level up.

Every one of the 21 blocks in §2d was confirmed by all three operators at the time of
writing. None of this is a substitute for running a node, and the record says that too.

## 5. Every new control ships with the controls that prove it works

Rounds 11, 12 and 13 each had the same headline: a control written to close the previous round's
hole, shipped without the control that would show it inert or over-broad, found by a reviewer
running it. Round 13's reviewer predicted round 14's finding would be in whatever was written to
close rounds 12 and 13, and was right twice within one day of work — the match-pattern captures
and the tuple-initialised accumulators both failed their first fixtures.

**From this version, a control is not finished until it ships with both:**

1. a **positive control** — an input that makes it FAIL, exercised in the suite, so "it passed" is
   distinguishable from "it cannot fire"; and
2. a **negative control one step outside its trigger** — the nearest legitimate input, so
   over-breadth is visible before a reviewer finds it.

Fixtures live in the tree and run in `test_controls.py`. A fixture kept outside the repository is
an assertion about work nobody can repeat, which is the thing this experiment is about.

## 6. What is unchanged from v9

The experiment, the corpus, `train.py`, the outcome table, the invalidating conditions of v3 §6,
and the no-assistance rule. Nothing about what is being measured has moved. This version changes
what the protocol commits to and how, and nothing about the science.
