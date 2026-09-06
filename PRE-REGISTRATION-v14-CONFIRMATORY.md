# Pre-registration v14 — the package stops handing out the answer

*Amends v13. Everything not restated here is unchanged and still governs.*

## 1. What changed, and why it could not have been caught earlier

⛔ **The reproducer package shipped the target, in three signed protocol documents.** v5 quotes the
reference weights digest to show a pipeline edit was numerically inert; v8 and v9 quote it to show
a provenance change altered no result. Each quotation is correct and each document is anchored —
and all three were added to the package **after** v3 made it target-free. A reproducer opening the
package held the number they were supposed to arrive at.

⇒ `build_package.py` now reads the reference digest from our own run record and **withholds any
  protocol document that contains it**, naming the withheld versions in `NO-TARGET.md` together
  with where to read them. It also refuses outright if it cannot read the reference digest at all:
  *"is this package target-free"* is the package's central property, and a build that cannot
  answer the question must not ship.

### ⚠️ This does NOT restore the ordering, and the paper must not say it does

Those documents are public in the project's repository. The digest has been readable since the
first of them was published, and no packaging decision can unpublish it. **Withholding changes
"handed the answer" into "could go and look".** That is a materially better test and it is not a
blind one, and the difference is reported rather than smoothed over.

### How it was found

Not by a control. By running the published procedure as a stranger would: copying the package to a
clean directory and executing the three commands `REPRODUCTION-CALL.md` gives.

```
step 1  sha256sum -c SHA256SUMS   ->  7 files FAILED. The shipped package had gone stale
                                      against the tree it was built from
step 2  python train.py --out my-run  ->  ok, 300 steps in 5.5 s, and it reproduced the
                                      reference digest exactly
```

⇒ **The reproduction itself works; the packaging around it did not.** A reproducer following the
instructions would have stopped at the first command — the "three honest installs could file
nothing but *I could not run it*" outcome §2c would then have scored as an ecosystem finding about
our own packaging.

## 2. ⛔ What is committed, by DIGEST — replacing v13 §2a and §2b

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
build_package.py           17f9b788b136b5d610b65e726468270b662225c518e592a5db33ec2b2ad86117
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

⚠️ **One digest moved and it is the subject of this version:**

```
build_package.py           a7f1bb3f6aa7d1c7 -> 17f9b788b136b5d6
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

⚠️ **The protocol documents in the package are now those that do not quote the target.** The
excluded set is not fixed here by name, because naming it here would be a list to keep in step with
the documents themselves — the build derives it, and `NO-TARGET.md` records what a given package
left out.

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
```

## 3. ⚠️ Unchanged from v13

Everything not restated above.

## 4. ⛔ What this version does NOT do

It does not make the reproduction blind — see §1. It does not make measurement 4 confirmatory. It
does not open the reproduction window, which remains a separate act with a close date attached.
