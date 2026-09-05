# Pre-registration v12 — two rules that could not both be obeyed

*Amends v11. Everything not restated here is unchanged and still governs.*

## 1. What changed, and why it could not have been caught earlier

⛔ **On 5 September 2026 `check_commitments.py` refused on a clean checkout, and no edit to any
file could have satisfied it.** Three consecutive runs, identical output:

```
2 block(s) are pinned that NO PROOF NAMES: [964878, 964881]
```

Both heights are committed in **v11 §2d**, whose rule is *"Every line must remain present and
unchanged."* The gate required the pinned set to **EQUAL** the set the proofs currently name. So
§2d forbade removing the two lines and the gate refused because they were there.

⇒ **Neither rule was wrong. The pair was.** §2d exists because a byte pin over `ANCHORS.json` made
every version void the instant it became authoritative — a digest cannot express *"this file may
grow but never lie"*. The equality check exists because a round-7 reviewer added a fabricated block
with a chosen root and every block-by-block verification still passed: the file was protected
against damage and unprotected against extension.

**A superseded proof is what makes them incompatible**, and until one was superseded the tree
satisfied both by coincidence. That is why no earlier round found it: the condition did not exist
to be found, and every control that could have expressed it was passing truthfully.

### The resolution: containment against what an ANCHORED version committed

A height may be pinned with no current proof **only if some anchored version's §2d block commits it
as a fact**. Anything else is still refused.

This keeps the property the equality rule was defending. The round-7 attack still fails: getting a
height into an anchored document's fact table requires the signing key and a Bitcoin block, not a
text editor. And it stops the tree being punished for obeying §2d.

⚠️ **The parameter defaults to empty**, so a caller that forgets to pass it gets the strict old
behaviour. The failure direction is the safe one.

### Two further defects, fixed in the same amendment rather than in three

⛔ **A build output was an input to a gate.** `pin_anchors.heights()` globbed `HERE.rglob("*.ots")`
— recursive, and therefore including `package/`, which `build_package.py` regenerates. The set of
proofs deciding which heights the anchor file may pin depended on the contents of a generated,
git-ignored directory. The same command returned exit 0 in the morning and refused in the afternoon
on the same commit, with a package rebuild — step 1 of the measurement-4 runbook — the only change
outside version control. **The old bytes are gone, so the exact path cannot now be demonstrated;
that it could happen at all is the finding.** Generated directories are now excluded by name,
projected over path parts so a nested copy is excluded too.

⛔ **The package shipped the answer.** `build_package.py` writes `NO-TARGET.md`, which states that
an earlier package shipped the reference digest and *"defeated the ordering the protocol was
rewritten to establish"*. It still did: the reference weights digest is present in three shipped
protocol documents — v5, v8 and v9 — each quoting it correctly, each added to the package *after*
v3 made it target-free. The rule guarded **one filename**, `EXPECTED.json`, and never asked whether
the assembled package contained the answer. It now scans every shipped byte and fails closed.

> ⚠️ **This is disclosed, not repaired.** Those documents are signed, anchored and public in the
> repository, so the digest has been readable since v5 was published. The ordering §3 establishes —
> commitment first, target after — **is already defeated for anyone who reads the repository, and
> nothing in this or any later version restores it.** Any party filing after that date could in
> principle have known the target before starting. That limits what any matching result can
> support and must be reported with whatever the window produces.

## 2. ⛔ What is committed, by DIGEST — replacing v11 §2a and §2b

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
pin_anchors.py             53b72e25be1f3ce468bf487cf03a062c7ea9b74855645d58f05adb0c1494e844
reproduce_findings.py      d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
seed_sensitivity.py        1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
test_controls.py           4b69f2493beef6b1ec2190b07aaece748617026747d139561268e9e4733a1a97
verify_package.py          2f80ff99f8c92baef0a89e9f797e69611597f9698458e8653d91550d259ee748
```

⚠️ **Three digests moved and they are the subject of this version:**

```
build_package.py           7087ec4aeaf6b0bc -> a7f1bb3f6aa7d1c7
check_commitments.py       c93d86852537e2f9 -> 9c1dc325de483ea1
pin_anchors.py             86cdac895b60b74d -> 53b72e25be1f3ce4
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

Carried forward from v11 unchanged, and extended with the block v11's own anchoring reached.
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
```

## 3. ⚠️ Unchanged from v11

Everything not restated above. In particular §3 — a pin is still not a node — and the reproduction
rules of §2b of the original: we do not assist, we do not characterise independence, and no party
is approached in a way that is not equally available to everyone.

## 4. ⛔ What this version does NOT do

It does not make measurement 4 confirmatory. That needs a fresh pair on both machines under this
version, because the existing pair was taken under admissibility conditions strengthened after its
result was known, and under a `run.json` that bound itself to no pipeline or protocol digest.

It does not restore the target-free ordering. See the disclosure above.

It does not open the reproduction window. That is a separate act with a close date attached, and
`PUBLICATION-CHECKLIST.md` governs it.
