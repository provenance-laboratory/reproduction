# Pre-registration v15 — the package shipped a verifier with no pins

*Amends v14. Everything not restated here is unchanged and still governs.*

## 1. What changed, and why nothing caught it for six versions

⛔ **`ANCHORS.json` was never in the package.** `ots_verify.py` reads it to learn which Bitcoin
block roots a proof may be checked against. Without it every proof in the package degrades to
**STRUCTURAL only** — *"this parses and names block N, but naming a block is not being in it"* — so
`check_commitments.py` found no anchored protocol document and refused, and `test_controls.py` died
trying to mutate a file that was not there. **Two failing controls, one absent file.**

⇒ It shipped a verifier and withheld its data. A reproducer running the two scripts the call names
would have seen both fail on a package that was otherwise correct.

### ⚠️ Why the build did not notice

`_with_dependencies` closes the shipped set over **Python imports**. A data file opened at runtime
is not an import, so **that closure could never have reached `ANCHORS.json` however correct it
was**. The list was not wrong; the *relation* was.

⇒ Adding the filename to `CONTENTS` alone would have been instance N of the enumeration defect this
project keeps making. So the other relation is projected as well: **a filename a shipped script uses
as a value, which names a file that really exists, must either ship or be classified absent with a
reason.** Anything unclassified now fails the build.

Two refinements, both found by running it rather than reasoning about it — a string that is a
*statement* is prose rather than a filename, and a name that resolves to no real file is a
concatenation fragment. Requiring the file to exist makes the rule self-limiting.

### ⛔ And the excuse outlived its condition

The review-mode message said the failure was expected *"until v8 anchors and section 2c takes
effect"*. **v8 anchored in August and the failure stayed**, because that was never the cause. A
tolerated failure whose reason has expired is the reason nobody looks: it absorbed this defect for
six protocol versions, and it took the first genuine `--publishing` run to surface it.

## 2. ⚠️ What shipping our own pins does NOT establish

`ANCHORS.json` is our assertion, recorded from block explorers, not from a node we run. Shipping it
lets the verifier work; **it does not make the verification independent.** If the pins were wrong,
every proof would verify against a wrong answer and look correct.

⇒ `HOW-TO-RECHECK-THE-ANCHORS.md` ships beside it and says so plainly, with the commands to recompute
every root from a node or from operators that do not share a codebase. **A tool that looks like
verification and is not would be worse than shipping no tool at all**, so the two files ship
together or not at all.

## 3. ⛔ What is committed, by DIGEST — replacing v14 §2a and §2b

### 3a. Experimental inputs

```
corpus/MANIFEST.json       fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py     2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json        7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30
train.py                   ebd61532782573a04aca8ab5d526ab6d233c450963ac111460f2d5d86f81d2fe
```

### 3b. Instruments and gates

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   6a25887d9758fdc629c96b2e84f4380bb6fe7abf8581c7e63b7507cd3958206a
build_package.py                   ccbcd3b34a8be7bbbbc241514840ff37acb48a655188b307fff378c59b557750
build_review_packet.py             db18eba091a229271e3219950cc59650bb7c5a8c2e0efe0e9a11f39019098dde
check_commitments.py               9c1dc325de483ea1dfec5982fba5fd6bb0079227440fffa5e2ddf6fecc48a452
check_signature.py                 76923dcbcf0d6b4b36af0cc0057dacba39194baab5ff9babf05f350b24f49fe5
corpus/verify_shipped.py           943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
measure_cost.py                    4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py              d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py                9686200fc21b08e1ef0cfeb14f7ecda9733bc34296e0318b7e63c4f390b6effc
measure_storage.py                 1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
ots_verify.py                      15ca911511c6c8aff0eee0c2821203cc201d689788f4687bee63e00c8a7c2ca9
pin_anchors.py                     98ef5a2074803888da417bafc9ff6e9f01e16d5fde669acd5a54d651888ba705
reproduce_findings.py              d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
seed_sensitivity.py                1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
test_controls.py                   0e38c72c43969cf7cf65fccd4a2339ed216f5ba1aade61f7adad61ed67bfb251
verify_package.py                  2f80ff99f8c92baef0a89e9f797e69611597f9698458e8653d91550d259ee748
HOW-TO-RECHECK-THE-ANCHORS.md      403526de7aeaa22a73ddcc0df24350898a43a455beb97357c63e1f1d21d04233
```

⚠️ **One digest moved and one entry is new:**

```
build_package.py                   17f9b788b136b5d6 -> ccbcd3b34a8be7bb
HOW-TO-RECHECK-THE-ANCHORS.md      NEW, pinned from this version
```

### 3c. ⛔ What the reproducer package contains

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

⇒ **Plus `ANCHORS.json` and `HOW-TO-RECHECK-THE-ANCHORS.md`.** The protocol documents in the package
remain those that do not quote the target; that set is derived by the build, not fixed here, and
`NO-TARGET.md` records what a given package left out.

### 3d. ⛔ ANCHOR FACTS — monotonic

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
965767     1a000e0f8b386a3d7b9af7eea508041fc818776605e5be6e5eb3fa108ea5c750
965784     5d65ae5e5a55e51cf1477df815f41cdc3486dfe25e33999361e582bdde0e9c2c
965818     6e9b364e154b594ce72804c6be577f7fb7ae9bf49d941cb71fe9c8bb9d1b2ea8
```

## 4. ⚠️ Unchanged from v14

Everything not restated above, including the withholding rule of v14 §1 and the reproduction
window's close date of **7 December 2026**.

## 5. ⛔ What this version does NOT do

It does not make the reproduction blind — v14 §1 still governs and the target remains readable in
the project's public repository. It does not make measurement 4 confirmatory. It does not make the
anchors independently verified; it makes them independently **checkable**, which is a different and
weaker claim, and §2 is the reason that distinction is written down rather than glossed.
