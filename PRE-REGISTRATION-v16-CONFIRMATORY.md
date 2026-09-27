# Pre-registration v16 — v15 renumbered the tables the instruments read by name

*Amends v15, which amends v14. Everything not restated here is unchanged and still governs.*

## 1. ⛔ Why this version exists, and it is not a new decision

**v15 decided nothing wrong. It renamed its committed tables from `2a`–`2d` to `3a`–`3d`**, for
readability, and those sub-headings are how the instruments FIND the tables:
`check_commitments.py` holds two constants, `ANCHOR_FACTS_HEADING` and `DISTRIBUTION_HEADING`
(lines 131 and 195), each naming the third-level heading that introduces its table — the `2d` and
`2c` ones respectively.

⇒ Under v15 the anchor-facts table and the distribution list **do not exist as far as any gate is
concerned**. `check_commitments.py` reported all 31 pinned heights as `MISSING`, because it was
comparing `ANCHORS.json` against an empty set of declared facts.

### ⛔ And the first draft of THIS document made it worse, which is why it is written this way

That paragraph originally quoted both constants with their exact string values. Those values
**are** heading text, so the document then contained the anchor-facts heading in its own prose,
before the real one. `anchor_facts` splits on the FIRST occurrence, so it parsed the explanation
instead of the table — and `distribution_subset` did not fail but returned the **instruments**
table, eighteen entries of the wrong list, silently.

⇒ **A document that quotes its own structural markers rewrites its own structure.** The constants
are therefore named here and never reproduced. Caught by running the real extractors over this file
before it was signed, which is the step v15 did not get.

⚠️ **The underlying fragility is in the parser, not only in the prose.** Splitting on the first
occurrence anywhere in the text means any future version that discusses headings breaks the same
way, and the distribution case fails SILENTLY rather than loudly. Matching at line start would fix
it. **Deliberately not fixed here** — that is a gate change, and widening a heading correction into
a gate change is how a small version becomes the risky one. Recorded for the next version.

**A section heading here is an interface, not formatting.** v16 restores `2a`–`2d` and changes
nothing else v15 settled.

### ⚠️ v15 is signed and Bitcoin-anchored, so it is not edited

Blocks **965831** and **965832**. Its bytes stand as part of the record, defect included — the same
rule this project applies to every sealed artifact. **A version is superseded by the next one, never
by a rewrite**, and pretending v15 said `2d` would be the substitution failure this corpus exists to
document.

### ⚠️ The gate caught it, and its message pointed at the wrong thing

`check_commitments.py` exited 1 rather than passing, which is the outcome that matters. But it said
`964534 MISSING` — a complaint about the DATA, when the fault was that the DOCUMENT declared no
table. **A governing version whose expected sections are absent should say so about the document.**
Recorded as a known weakness; not fixed here, because widening a heading-correction into a gate
change is how a small version becomes a risky one.

## 2. ⛔ What is committed, by DIGEST — headings restored

### 2a. Experimental inputs

```
corpus/MANIFEST.json       fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py     2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json        7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30
train.py                   ebd61532782573a04aca8ab5d526ab6d233c450963ac111460f2d5d86f81d2fe
```

### 2b. Instruments and gates

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

⚠️ **No digest moved between v15 and v16.** This version is a heading correction; the build asserts
that nothing changed and refuses otherwise.

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

⇒ Including `ANCHORS.json` and `HOW-TO-RECHECK-THE-ANCHORS.md`, per v15 §2 — the verifier ships
with its pins, and with the instructions for replacing our pins with the reader's own.

### 2d. ⛔ ANCHOR FACTS — monotonic

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
965831     84f7aba8c1732f40a3b4a6fa6845d0f1e0272bf882760122ff257a23485a3b08
965832     fe0ed8292038251f49661bc2c2674520f23510114b49b7d0089caeb9d2c28855
```

⇒ **2 height(s) added since v15**, being the blocks that anchored v15 itself.

## 3. ⚠️ Unchanged from v15 and v14

Everything not restated above: the withholding rule of v14 §1, the data-dependency projection and
the anchors-are-checkable-not-verified statement of v15, and the reproduction window's close date of
**7 December 2026**.

## 4. ⛔ What this version does NOT do

It does not revisit anything v15 decided. It does not make the reproduction blind. It does not make
measurement 4 confirmatory. It does not make the anchors independently verified — only
independently **checkable**, which stays the weaker claim v15 wrote down rather than glossed.
