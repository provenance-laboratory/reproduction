# Pre-registration v13 — the amendment that only changed one half

*Amends v12. Everything not restated here is unchanged and still governs.*

## 1. What changed, and why it could not have been caught earlier

⛔ **v12 changed a rule in the READER and left the WRITER enforcing the old one.** Within an hour of
v12 anchoring, `pin_anchors.py` ran and **deleted two anchor facts** — heights 964878 and 964881,
whose proofs had been superseded. It writes *"exactly the set our proofs name"*, which was correct
under the equality rule v12 replaced and became destructive the moment containment replaced it.
`check_commitments.py` then refused the tree for a §2d violation **the tooling had just
committed**.

⇒ That is what an incomplete amendment looks like: the rule moves in one place, the other place
  keeps enforcing the old one, and the disagreement is resolved by deleting data. **A fact pin may
  grow. It may never shrink, and it may never contradict.** `pin_anchors.py` now merges, reports
  every height it keeps that no current proof names, and refuses outright if a re-fetch would
  change a root already pinned.

### And the control suite had stopped testing what it names

⛔ **Five of eight commit-attacks were vacuous, and the suite reported them as SECURITY FAILURES.**
`_governing()` evicted only `check_commitments` from `sys.modules`; its dependencies stayed cached
against the first attack's temporary tree, which had already been deleted. From the second attack
onward every document failed verification, `found` came back empty, and a silent fallback returned
**v3** — so five attacks vandalised a long-superseded document's proof, `check_commitments`
correctly ignored it, and the suite called each correct pass an attack that got through.

**The defences were sound throughout.** This was reproduced by hand and by the suite's own
`_governing()`: deleting v12's real proof is refused, exit 1, every time.

⚠️ **The harness was wrong in both directions at once** — it under-reported what it tested and
over-reported what it found. Either alone is bad; together they make the number meaningless.

⇒ Two changes, and neither is a list. `_governing()` evicts **every locally-importable module**
  rather than one named by hand, prunes `sys.path` entries pointing at trees that no longer exist,
  and **raises instead of guessing**: a fallback that silently names a version is precisely how a
  control stops testing without saying so. All eight attacks now target the real authority and all
  eight are refused.

> ### ⚠️ WHY THIS KEEPS HAPPENING HERE
> Both defects are the same shape as the one this file's own docstring records from round 6: a
> control that names what it tests, and then quietly tests something else. It was hardcoding then
> and module caching now. **The lesson that generalises is not "do not hardcode" — it is that a
> control must fail closed when it cannot identify its own target.**

## 2. ⛔ What is committed, by DIGEST — replacing v12 §2a and §2b

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
build_package.py           a7f1bb3f6aa7d1c772c3ed537bf9973fd6f5213c529f5246ce9ebd9627771b9c
build_review_packet.py     db18eba091a229271e3219950cc59650bb7c5a8c2e0efe0e9a11f39019098dde
check_commitments.py       9c1dc325de483ea1dfec5982fba5fd6bb0079227440fffa5e2ddf6fecc48a452
check_signature.py         76923dcbcf0d6b4b36af0cc0057dacba39194baab5ff9babf05f350b24f49fe5
corpus/verify_shipped.py   943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
measure_cost.py            4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py      d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py        9686200fc21b08e1ef0cfeb14f7ecda9733bc34296e0318b7e63c4f390b6effc
measure_storage.py         1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
ots_verify.py              15ca911511c6c8aff0eee0c2821203cc201d689788f4687bee63e00c8a7c2ca9
pin_anchors.py             98ef5a2074803888da417bafc9ff6e9f01e16d5fde669acd5a54d651888ba705
reproduce_findings.py      d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
seed_sensitivity.py        1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
test_controls.py           0e38c72c43969cf7cf65fccd4a2339ed216f5ba1aade61f7adad61ed67bfb251
verify_package.py          2f80ff99f8c92baef0a89e9f797e69611597f9698458e8653d91550d259ee748
```

⚠️ **Two digests moved and they are the subject of this version:**

```
pin_anchors.py             53b72e25be1f3ce4 -> 98ef5a2074803888
test_controls.py           4b69f2493beef6b1 -> 0e38c72c43969cf7
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

Carried forward from v12 unchanged, and extended with the blocks v12's own anchoring reached.
**Every line must remain present and unchanged; new heights may be added and are not a violation.**

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
965458     f4cb09e6fc3350c3ddcf0b4d64d124d1504d94a8b148f92298cf0465fc1513c9
965750     6dde0e9afe57f11f8b833e405d736ae64820acc04ef97d4bfeaffb3d089b949c
965753     a0a8bb7589ecd091de601d52e66639b755285ad688f23b43bc161f8092937586
```

## 3. ⚠️ Unchanged from v12

Everything not restated above, including the containment rule for pinned heights, the exclusion of
generated directories from the proof projection, and the target-free projection over the assembled
package.

## 4. ⛔ What this version does NOT do

It does not make measurement 4 confirmatory; that still needs a fresh pair on both machines under
the governing version.

It does not restore the target-free ordering. The reference digest has been public in the
repository since v5 and no amendment can unpublish it.

It does not open the reproduction window.
