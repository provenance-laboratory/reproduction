# Pre-registration v11 — the parameter its only caller never passed

Supersedes v10 §2. Every digest below was measured when this document was written. This version
exists for one repair, and the repair is a good illustration of why the protocol requires a new
version rather than a re-pin.

## 1. What changed, and why it could not have been caught earlier

v10 moved `ANCHORS.json` from a byte pin to a monotonic **fact pin** (§2d), because anchoring a
version rewrites the file that version pins, so every version since v8 was void in that entry from
the moment it took effect.

The guard that permits that move asks whether the retiring document declares anchor facts in place
of the byte pin. It reads them from a `text` parameter — and that parameter's only caller passed
the empty string. Harmless while nothing read it; a **false refusal** the instant something did.
v10 declares 23 anchor facts and was refused for declaring none, and the failure appeared
only once v10 actually anchored, which is the first moment the retirement path had ever run.

That is the shape a round-13 reviewer found in `undefined_module_reads(where=)`: **a parameter with
one caller that never passes it is untested by construction**, and the test that would have caught
it is the one nobody writes for an argument that is always the same value.

So exactly one pinned file moved:

- `build_review_packet.py` — the composed authority records `800e79d9a4ea9351`, it now hashes to `db18eba091a22927`
- `check_commitments.py` — the composed authority records `61b8bfbfd9e447ed`, it now hashes to `c93d86852537e2f9`
- `pin_anchors.py` — the composed authority records `ba41da49785bba06`, it now hashes to `86cdac895b60b74d`
- `test_controls.py` — the composed authority records `6fa3341c5941cdad`, it now hashes to `4b69f2493beef6b1`

## 2. ⛔ What is committed, by DIGEST — replacing v10 §2a and §2b

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
build_review_packet.py     db18eba091a229271e3219950cc59650bb7c5a8c2e0efe0e9a11f39019098dde
check_commitments.py       c93d86852537e2f968898fc8d314a2a741eca5d481922df791b0df041234e601
check_signature.py         76923dcbcf0d6b4b36af0cc0057dacba39194baab5ff9babf05f350b24f49fe5
corpus/verify_shipped.py   943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
measure_cost.py            4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py      d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py        9686200fc21b08e1ef0cfeb14f7ecda9733bc34296e0318b7e63c4f390b6effc
measure_storage.py         1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
ots_verify.py              15ca911511c6c8aff0eee0c2821203cc201d689788f4687bee63e00c8a7c2ca9
pin_anchors.py             86cdac895b60b74d1ac7316097df7df306b66b30f3867bfef6732386d50ae162
reproduce_findings.py      d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
seed_sensitivity.py        1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
test_controls.py           4b69f2493beef6b1ec2190b07aaece748617026747d139561268e9e4733a1a97
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

### 2d. ⛔ ANCHOR FACTS — monotonic

Carried forward from v10 and extended with the blocks that anchored v10 itself. Each line is a
Bitcoin block height and the merkle root `ANCHORS.json` records for it. **Every line must remain
present and unchanged; new heights may be added and are not a violation.**

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
965332     c20da71633ebb813cd0f4f78f6059bab6b6b06912a2eb76cc48182acf66a9d35
965333     3d4a2b7fe40ea918d1496985dce09db8395a9559f99c80b7be61b9c259b32266
```

v10's own anchoring added two heights to this file and broke nothing — which is the property the
byte pin could never have, and the reason this section exists.

## 3. ⚠️ A pin is still not a node

`pin_anchors.py` requires agreement between at least two independent operators on both block hash
and merkle root, records which agreed, and refuses on disagreement rather than taking a majority.
All 23 heights above were confirmed by all three at the time of writing; two of the three run
the same Esplora software and one is a different codebase, and the record says so. None of this
substitutes for running a node.

## 4. Unchanged from v10

The experiment, the corpus, `train.py`, the outcome table, v3 §6's invalidating conditions, the
no-assistance rule, and §5's requirement that every control ship with a positive control that makes
it fail and a negative control one step outside its trigger. Nothing about what is measured has
moved.
