# Pre-registration v28 — confirming v27, and one word for a version's state

**Status: until this document is signed and its proof anchors, it changes nothing. Once it is signed
and anchored, its §2d table makes v27 CONFIRMED and the digest check applies this version's pins; this
version is itself in force once a later version's §2d table names its blocks.** That sentence is written
to be true before and after signing.

## 1. ⛔ Why this version exists

**First, v27 is confirmed.** v27 was signed on 12 October 2026, and its proofs landed in Bitcoin blocks
**971101** and **971103**. By this protocol's own rule a version's claim about its own anchor is not
evidence; only a later version's table settles it. §2d carries the two heights, and v27 is PROVISIONAL
until this document is signed and anchored. This is the version the study needs before its window closes on
7 December 2026.

**Second, the tools described one state in words that read as a contradiction.** Two internal reviewers
of the round-23 packet (13 October 2026) ran the tools against the packet's own text, which called v27
*"signed, anchored and governing"*. `check_commitments.py` said v27 was the *authority*;
`prepare_anchor.py` and `anchor_status.py` said v27 was *not in force*. Both followed the design, and
the packet took the stronger word. The rule does not change; the word for each state is now decided in
one place. §2b.

**Third, three smaller repairs queued under v27** (`../queued-for-next-protocol-version/V28-QUEUE.md`,
at the bytes with sha256 fd634e4be74ce82fc725e11d03dedcb957ccc18afbef5b099ceb909cac4b61cb; its items 1,
3 and 5):
`pin_anchors.py --add` reported every pinned height as named by no proof (§2a); the verdict file's
headline could be quoted without its denominator (§2c); and signing adds a text file, so the
disposition record went stale at signing until the next suite run found it (§2g).

## 2. ⛔ What was wrong, and is repaired under this version

### 2a. ⛔ `pin_anchors.py --add` measures "kept" against every height the proofs name

In `pin_anchors.py`, `--add` narrows its working set to the heights it is about to fetch, and the set of pinned heights
*"kept that no current proof names"* was computed against that narrowed set, so on 12 October it
printed 51 heights where §2e expects two. The pins it wrote were right; the message was false. The
full projection now keeps its own name and "kept" is measured against it, once per run (the function
was called twice and printed twice). `--verify`, the act anything trusts, never narrowed its set and is
unchanged.

### 2b. ⛔ one word for a version's state, decided in one function

`prepare_anchor.status_word()` returns one of four words, and `check_commitments.py`,
`prepare_anchor.py` and `anchor_status.py` print it:

```
DRAFT        not signed
SIGNED       signed; its proof carries no Bitcoin attestation yet
PROVISIONAL  signed and anchored; no later version's section 2d table names its blocks
CONFIRMED    signed, and a later version's section 2d table names its blocks -- in force
```

`check_commitments.py` keeps its rule -- the newest signed and anchored version's pins are the ones the
digest check applies -- and now prints that version's word beside the word *authority*, and the latest
CONFIRMED version when they differ. `prepare_anchor.py`'s closing instruction no longer says the next
step *"will select vN as the authority"*; it says the check will apply vN's pins and that vN stays
PROVISIONAL until a later table names its blocks.

### 2c. ⛔ the verdict carries its headline with its denominator

`test_controls.py` writes `CONTROL-SUITE-VERDICT.json`, which gains `attacks_measured`, a `headline` that states measured of declared
before any other figure, and `security_ok_means`, which says that `security_ok` covers the measured
attacks and that the unmeasured ones are evidence neither way. A run outside `build_package.py` writes
`"none: run outside build_package.py"` in the nonce field instead of an empty string, which a reviewer
read as a value; `build_package.py` still refuses any verdict without the nonce it issued.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each listed height must still carry the listed merkle root; new heights are permitted, and later
anchoring adds rather than contradicts. **The rows for 971101 and 971103 make v27 CONFIRMED.**
Every height v27 carried is carried here.

```
964534  018d69dc7bf4e2e8a45fdf3a89855b9b7e03027227aa14e596a91dcf320e09b9
964535  ef17461955701f9c1d296245df4ab22a71a7e3e0fd3ceeb7213de12958ba69c5
964549  e863c303c5b515da7544652b29648659c66ff2fa6ffad9fe82ccc975042eb439
964747  8a9766909969f175693a1fd85a7236e3be4d33a95cd4a0bcab3fff2e76e16857
964761  23019c9499bd74096ae1d9c4015bc4f10176900d99cb805e7252011ed7415d37
964762  ff5f6043b9883f8e8830856a16dc52783c66d1185d6ffebab5dbe3598f42c543
964775  ed2dd86c5b3c983d859139542aeced248e1f18ec030ccd550e36286a59f54f5e
964785  8aac2039e614e1557aab7264848c8b0cb1152970f2d5e7fa76170ccdfbf2a587
964789  b73d9657064cb4a9842e18ec1a007bc4702308730257cc378dd56ed3443ec0dd
964812  9cd60bdc0fdc9ba7784f8a4705c22d11b82b081a41d69ff598729522834dbd4a
964815  ac3592ef064ea4e4c7db187954f057550018a38dfa02afc7a2c3d33ad2955b76
964848  5784c7dab006cedba2172ec6cce265b83b1f75c8a27a117f4b2df1165b151d9c
964856  a2c750b72ab68db7602962f230b1e8a236633d5cef8f132fed1547b3ac6aba9e
964878  b9fef3d8dd2fc6b2945cb580525f25beaf5612b7b71e3a1b78799e22f353dce0
964881  45cb82a2d9677e318826afb6fd6f3a6be84b5cf94780ee1487b49097d5293579
964920  7f5a7092d6b342430276b08b492f1f18e8a6fa8ddb55a6245f0d93f6e70e13d3
964922  d876c661233b2de9d92f1dabebf9c1a677570711dbec02b1e5317502b2610fe6
964923  92687073de11e6fd31a71c3f6aa0c75aa60a0950dffa30b80ad91155425f4986
965140  c836cd739ba5bddf491db621fcfe76154d6002cecfb10dd4a72eecd99e039ec6
965142  df6e4b4f68795f65252340e42467d77e8e8c2a44e1e5a4ff40730848aca56eb6
965152  46e025634022f51ac766cc16d8be33c04068c0eb7e7a2f66930e022ca4185ece
965332  c20da71633ebb813cd0f4f78f6059bab6b6b06912a2eb76cc48182acf66a9d35
965333  3d4a2b7fe40ea918d1496985dce09db8395a9559f99c80b7be61b9c259b32266
965458  f4cb09e6fc3350c3ddcf0b4d64d124d1504d94a8b148f92298cf0465fc1513c9
965750  6dde0e9afe57f11f8b833e405d736ae64820acc04ef97d4bfeaffb3d089b949c
965753  a0a8bb7589ecd091de601d52e66639b755285ad688f23b43bc161f8092937586
965767  1a000e0f8b386a3d7b9af7eea508041fc818776605e5be6e5eb3fa108ea5c750
965784  5d65ae5e5a55e51cf1477df815f41cdc3486dfe25e33999361e582bdde0e9c2c
965818  6e9b364e154b594ce72804c6be577f7fb7ae9bf49d941cb71fe9c8bb9d1b2ea8
965831  84f7aba8c1732f40a3b4a6fa6845d0f1e0272bf882760122ff257a23485a3b08
965832  fe0ed8292038251f49661bc2c2674520f23510114b49b7d0089caeb9d2c28855
965840  4a817365b47122ee011d2542c01e677c3dcca3abfa04f01715de02f38bdc7b84
965910  2a7d27ba92ece6f533426c684cc7ab0bbc57a51eed4dc2e332f921a71f3836ec
965912  4c456b1d277b5969250a57052ce30a0b70f4c41cd0659e8f780e4695e3fb2504
965922  e67fe31925653d81ff315c29d2364a5023ebec76de0fc0a6ce347202b3a4edea
966979  d154bdb8cfe1926a12a668599b409bc32fde8cb301ff670b9077587dcc4b294c
966981  febf47418ab2295a9531814e72e716a74ad1cdf853d90cb064be963b75676db0
967137  fbbe69eb9f9f39133822c0be9eae5fd2c6b16f93c4cbab0d1de3efb508d669d7
967140  58b46a7bd1b5813a1b30644c25815d37b298a3532ba893c6e3dc93eab7999088
967150  f099824f9d0fdece911e67d6380e08b6ffe2fe0b0952e398229f4b0cba5acbc6
967531  3abf092a1eafa76fde606ffffc5e62cf7c7fbcad944d1ec83eebed0aa38fe0dc
967728  57aff597b9004136ea9de160d284ba8cd1c59f8ac72aa400210c82a497c99d03
967736  a27c668a4d320942f8cb3906efbfefefaedda9d760d5d52bdb74f7a7e0f1a0d4
968668  62e24a1b11ad70b4aedc31f2eca6d15eec594db333f747ed994b2faa008f8688
968689  a78a98471004cbaadb5109722db134ac691eb9c9c8d504616626b33e74566c02
968848  453eebd038135e3b5fa26754b4d850dc1a8b9520d28ca0d4990c38d6bbe4b202
969166  13cb7c46534c94c5b5151e2a7c3f2e3ff3cefc5cdbf57ca59ea4699473314dbd
969170  29d3d4864b9ff96bc99cbbf59e76b9257546c8fa77843363216b388d779d2db2
970233  22fdcf846a0d9f7503e50288098af5326cf451a38353a98a9577de1efd875f1c
970234  660f2aafcba2ef023209d30f9bbd397c7b1e3541224d93f2f62dc7e0ecac89b2
970258  e0b96e5f938904b8eeae1aed86ffdeea9278b1cd080be8b886a0fb796dbbd298
970631  d7cb36e2ce7889c6be524c52dc3f9a5966f153a656da066b405ce65881f2652d
970639  c8494c9b9dbc02ea333ad90d463337517e3e0666c7fcb28df9225e8bbe741ea3
971101  8e8e46de7269fffc046e7cb83a2e873106c7d7a01aa2895a2cf9f8eeb25d4d15
971103  e3bf9edd4f776153565f0583105612564f682271d8768599dff175432eab5a49
```

### 2e. ⚠️ two rows of this table still have no surviving proof behind them

Blocks **964878** and **964881** are carried, as v27 §2e carried them, and no proof in this folder names
either. `pin_anchors.py --verify` refuses on them, and that is not overridden here.

### 2f. ⛔ the state-dependent attacks, measured in this version's draft window

Measured on 13 October 2026 by `python test_controls.py` over this draft before this subsection was
written (a document cannot carry the digest of its own final bytes, so the run is of the draft with this
slot unfilled; nothing else changed between the run and this text).

```
CONTROL-SUITE-VERDICT.json   sha256 af4c7fc825f725ecae2ec124537fd3cff8a33d76236bd9640774f47b62db9d50
  tree_digest                     9d848aed77dd244d
  headline                        77 of 77 declared attacks measured; 77 refused, 0 accepted that
                                  should not have been, 0 refused for the wrong reason; 0 not measured
  hygiene_failed                  false
  security_ok                     true
  positive_control_failed         true     (liveness_ok false -- see below)
```

**Every declared attack ran and was refused, including the nine draft-window attacks** (v27's eight
declaration checks and the forged restatement row), which need an unsigned version with a commitment
table in the folder and therefore ran here.

⚠️ **The first run of this draft measured 62 and left 15 unmeasured**, because the draft restated v27's
three repaired rows at v27's bytes while naming none of them as repairs, and v27 is not in force: the
`prepare_anchor.py` baseline refused, and every attack behind it measured nothing. §2h is the fix. A
draft that restates a PROVISIONAL predecessor's repairs has to name them, and the suite said so before a
signature did.

⚠️ **The positive control fails, and it is expected to in this window and nowhere else**, as in v27:
`check_commitments.py` refuses the real tree because the five repaired files no longer match v27's
commitments and this document is present with no proof binding it. Both clear when this version is
signed and its proof anchors. **A positive control that still fails after anchoring is a finding
against this version, not a window effect.**

**The run that covers this text.** The digest above is the run of the draft before this subsection
was filled. Filling it, and the repairs of 29 October 2026 to the messages of `check_commitments.py` and
`prepare_anchor.py`, changed the tree, so the suite is run again over the final draft before signing. A
document cannot carry the digest of the run over its own final bytes; that run's
`CONTROL-SUITE-VERDICT.json` digest and tree digest are recorded in `SIGNING-RECORD-v28.md` beside this
file at signing, and the next version's §2f names them. This document is not edited after that run.

**v27's post-anchor check.** v27 §2f made the first run after its anchoring the check of its positive
control. Every run since v27 anchored has had this draft in the folder, so its positive control has
failed for the draft's reason and has not yet been measured alone. It is measured by the first run after
this version anchors, which checks both.

### 2g. ⛔ signing regenerates the disposition record as part of the act

`prepare_anchor.py`'s printed operator steps now end with `python withdrawn_claims.py` after the
signature and the stamp. Signing adds the `.asc`, a text file the record counts; on 12 October the
record went stale at signing and the next suite run marked four attacks unmeasured and failed hygiene.

### 2h. ⛔ v27's three repairs are carried at v27's bytes

v27 repaired `test_controls.py`, `build_review_packet.py` and `withdrawn_claims.py` (v27 §2a-§2c) and
committed them at its own bytes. v27 is PROVISIONAL, so the versions in force (to v26) still give the
older bytes for those paths, and a row that merely restated v27's pin would not restate anything in
force. This version therefore names them here as rows it commits: `build_review_packet.py` and
`withdrawn_claims.py` at the bytes v27 committed, `test_controls.py` at the bytes §2c describes. Once
this version is signed and anchored, its §2d table makes v27 CONFIRMED and the two agree.

### 2i. ⚠️ queued, not done: a synthetic draft for the draft-window attacks

Nine `prepare_anchor.py` attacks (v27's eight declaration checks and the forged restatement row) run only while an unsigned version with a commitment table is in the
folder, a few hours per version; outside that window they are counted as not measured (§2c says so in
the headline). Building a synthetic draft inside the suite's sandbox would let them run on every
invocation. It is a change to how the suite constructs its fixtures and is left for a later version,
so that this one stays small enough to be signed inside the study window. This version's own draft
window measures them (§2f).

## 3. ⛔ What is committed, by DIGEST

### 3a. The tools, the key, and every other path the composed history pins, at the bytes this version commits

Five rows are repairs: **`pin_anchors.py`** carries §2a; **`prepare_anchor.py`**, **`check_commitments.py`**
and **`anchor_status.py`** §2b (and `prepare_anchor.py` §2g); **`test_controls.py`** §2c. Two more are
v27's repairs carried at v27's bytes (§2h): **`build_review_packet.py`** and **`withdrawn_claims.py`**. The
other twenty-three rows restate. `REVIEW-SHIP-LIST.json` stays unpinned (v27 §2b).

**This version commits exactly 30 file pins, and the sorted pinned names hash to 968b5635c5e00e030a6f12da305fdae3b977327e5adfa484331cd48888f3926e.**

The membership digest is computed from the names this version INTENDS to commit -- v27's set,
unchanged, because this version moves five digests and no name.

Every digest below was written from the bytes on disk by `prepare_anchor.py --repin`, never typed.

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   580ac38e95b4d41d215944e9f2cc7a0b5aaa95db821f055d4273d10cf706a736
build_review_packet.py             6ae679a3f70416029ee8050f42c162c0d076fd112a36910586cffbb70d28c620
check_commitments.py               9223d48bf77df1bd90c68d393873877f877b73cfaa128ba46c3b1083bf63c045
check_signature.py                 46bed0e0d35f1c192ad984f7be470a5acefe624e33d5f3ea5e11f2259728fff3
ots_verify.py                      2c5676b0518aca1b36af6899b71a326c73a5253e6593a7cc1f1ea266ea7290ee
pin_anchors.py                     1e1692b22a9f334b5d95504543782496d2c74ee95eff8e871d38493f30f54fdf
prepare_anchor.py                  77308afe5adfe36099bd4bf42413b53e809aa9b22ab7ff970049f6d739730f14
test_controls.py                   0796993a13156f24f59324f181a7fd3a32c0358f031bf60321c5d59d68fdf7c9
DISTRIBUTION-PLAN.md               6a1851278f20a89328cd5ffccb0359ee97d0ebbfc6e39147feea3b734fb2cb89
HOW-TO-RECHECK-THE-ANCHORS.md      403526de7aeaa22a73ddcc0df24350898a43a455beb97357c63e1f1d21d04233
REPRODUCTION-CALL.md               803e1047c9fcb186be4b4c5f8d16966db4ee4a9a00e252e42a8f01eb1d38ac83
attempts.py                        1edee542a8ecfa974694a8dbc807b706bb0b0aaf767cf3213f002ffed70f36ab
build_package.py                   0c50cc172500f62c0363f124fef3e9b494e8f8ef5b3532e9371c5ae927000f9c
capture_exposure.py                4a3cd9c235b499dff5430731c0fe867147ad799d7e6b3512febd9587feb1a90d
corpus/MANIFEST.json               fa67e35a7b7fb0c4b79f467cda6708226a4f0fab97e6116ed2ef69655b642c47
corpus/build_corpus.py             2d3ce23b80e9de7b25679e1a0eb81f4da62b058dc3dd15b466f2983306c87ec3
corpus/sources.json                7548856806ec771d973789c5e62d1cf8101976255ddbcae474d0f290e6d45b30
corpus/verify_shipped.py           943ebf0f6051a6b7c822378430a5e482b9e02b11de799a420b1bf9c838748749
exposure/exposure-2026-09-07.json  837fb43a3f9f5ddeddcd06372759c796d2df91ba958d12b269b0de2c7ccb2624
measure_cost.py                    4b8bdd95c6fcbc37fd557ff81041e0af28202bf4816ef34e5e458e9e8bdedba9
measure_divergence.py              d1dc9c7630e4b5c36231dd1a8ff7c044355463349ab6f674e390f2c63969711f
measure_hardware.py                9686200fc21b08e1ef0cfeb14f7ecda9733bc34296e0318b7e63c4f390b6effc
measure_storage.py                 1254e4049813bd28ef2064f2252bcc5983e6d2bbac22825bf445ff1f4e0895c5
reproduce_findings.py              d9c6be8882464a59e054d525b6e9970c02bb4f4b34be584cc403826cd0b39f25
runs/det-1/run.json                97a0318343b2fa60a072fd4339520b124c13e1b3fab62a5148dc5a8f60e2d816
seed_sensitivity.py                1012eb90d895146cac6d5f212ec18bc3012bc1e12176cb8918b83ea4563c24f5
train.py                           ebd61532782573a04aca8ab5d526ab6d233c450963ac111460f2d5d86f81d2fe
verify_package.py                  ed4d6d2a179169720fba28ef59769dc14e59cf9d207d617ad0c4aa75e32d0410
withdrawn_claims.py                105fcff6dfc9d44f7eacced14169b67396a5a9d0f1da01d097f13b78b777f4bd
```

## 4. ⚠️ Unchanged

Everything v27 committed that is not named above is committed here at the same bytes. No claim v27
made is withdrawn.

## 5. ⛔ What this version does NOT do

It does not change which version's pins the digest check applies, or when a version is in force; it
names those states in one vocabulary.

It does not build the synthetic draft of §2i.

It does not add the control the queue's item 1 asked for (`--add` on a tree with one new proof must report
exactly the §2e heights as kept); §2a's repair is checked by reading it, and the control is left for a
later version.

It does not reconcile the word `prepare_anchor.py` prints in its `in force:` list with `status_word()` for
v1, whose file (`PRE-REGISTRATION.md`) carries no version number in its name, so that list does not read
it; the list reports, and decides nothing.

It does not resolve blocks 964878 and 964881 (§2e).

It does not re-pin the deposit, the manuscript, or anything outside this study folder.

It makes no claim about what any of these controls would find on a tree other than this one.
