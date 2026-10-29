# Pre-registration v27 — confirming v26, counting every attack that does not run, and taking two inventories out of a signed version's way

**Status: this document governs nothing until it is signed, stamped, and confirmed by a later
version's anchor table.** That sentence is written to be true before and after signing.

## 1. ⛔ Why this version exists

**First, v26 is confirmed.** v26 was signed, and its proofs landed in Bitcoin blocks **970233**,
**970234** and **970258**. By this protocol's own rule a version's claim about its own anchor is not
evidence; only a later version's table settles it. §2d carries the three heights, and v26 is
PROVISIONAL until this document is in force.

**Second, v26 §2b claimed more than it repaired.** It said the verdict now carried its denominator, so
that *"a reader can now see that one did not"* run. That was true of the withdrawn-claims group and
false of the `prepare_anchor` group: on the first full run under v26, eight attacks there printed
`unmeasured` and reached no counter, so `attacks_declared: 68` counted the attacks that were scored,
not the attacks the suite holds. Writing the repair found three more sites of the same class, one of
which scored an unmeasured control as **refused**. §2a.

**Third, the operator adopted the two designs v26 §5 named and declined to adopt without them** (9
October 2026): the review packet's inventory leaves the pinned tool, and a superseded disposition-log
head is kept beside its proof. Both change what a signed version commits to, which is why §5 of v26
left them for the operator rather than calling them repairs. §2b and §2c.

## 2. ⛔ What was wrong, and is repaired under this version

### 2a. ⛔ every attack that does not run is counted, in every group, and none is scored as refused

`test_controls.py` now initialises one `unmeasured` counter before the first group, and every site that
cannot set an attack up increments it. The four sites:

- the `prepare_anchor` group caught `_Unmeasurable`, printed, and counted nothing (v26 §2b's gap);
- the same group scored its attacks as *refused* or *refused for the wrong reason* while its own
  baseline was refusing the tree. A refusal under a broken baseline is not a measurement; the
  withdrawn-claims group already applied that rule, and this group now does;
- the wrong-key `verify()` check caught `_Unmeasurable`, printed, and counted nothing;
- ⛔ **the round-14 subkey fixtures recorded an unmeasured control as `(label, True, True)`, and the
  scoring loop counts `got == want` as refused**, under a comment saying such a control *"scores
  nothing"*. It was latent: gpg could set the fixture up in every recorded run. It now carries a
  marker that cannot equal any measured value and is counted as unmeasured.

The verdict's identity is unchanged and now holds for every group: refused + refused for the wrong
reason + passed + not measured = declared.

### 2b. ⛔ the review packet's inventory is data, and the rule stays pinned

`build_review_packet.py` keeps the rule — *every file in this folder is shipped or excused by name, or
the build refuses* — and reads the names from `REVIEW-SHIP-LIST.json`, which ships with every packet and
is not pinned. Protocol versions and findings stay derived in code, as v25 made them. The one computed
entry inside the old static list (*every superseded artifact bound to `corpus/MANIFEST.json`*) is a
directive the loader expands at build time, and a second directive ships a pattern family (§2c). A
missing, malformed or self-omitting inventory refuses.

**Measured, not asserted:** the lists the v27 builder produces were compared with those the exact v26
builder produces (sha256 `c5349d52…`, taken from the last packet built under v26) over the same folder.
Every list is identical, and the shipped list gains exactly two entries: the inventory and
`build_review_packet.lists-until-v26.txt`, which keeps the old lists and their rationale comments
verbatim, since this folder has no version history.

### 2c. ⛔ a superseded disposition-log head stays beside its proof

Recording a reading rewrites `WITHDRAWN-DISPOSITIONS.head`, and an anchored proof over the previous
head then commits to bytes that are gone, so the pin file holds a block no proof names — which
`pin_anchors.py --verify` refuses, correctly. `withdrawn_claims.py` now keeps the pair, when and only
when the proof commits to the head's current bytes, as `WITHDRAWN-DISPOSITIONS.head-<16 hex>` and
`WITHDRAWN-DISPOSITIONS.head-<16 hex>.ots`. That name does not contain `.superseded-`, so the pin
file's projection reads it as it reads every proof beside the file it binds.

**Measured, with a control.** In a copy of this folder, recording one reading with the v26 tool left
block **967531** named by no proof (48 heights); with the v27 tool it stays named (49 heights).

**Applied.** `withdrawn_claims.py` changed, and it carries the withdrawn claim's phrasings in its hint
list, so its reading was recorded again (reading 18: *marked*, as reading 14 was; the phrasings are
unchanged). The previous head and its proof are kept as `WITHDRAWN-DISPOSITIONS.head-0a5e5b167ef49d29`
and its `.ots`, and block 967531 is still named by a proof. ⚠️ **The new head is not yet stamped**, so the
chain is tamper-evident only to a reader with an earlier copy until it is; and the packet builder
refuses until the head's proof exists, because the inventory promises it.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each listed height must still carry the listed merkle root; new heights are permitted, and later
anchoring adds rather than contradicts. **The rows for 970233, 970234 and 970258 make v26 CONFIRMED.**
Every height v26 carried is carried here.

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
```

The rows for **970631 and 970639** are the disposition-log head of §2c: `WITHDRAWN-DISPOSITIONS.head`,
stamped on 9 October 2026 and anchored by 12 October. Named here, they are CONFIRMED when this
version is; known only to `ANCHORS.json`, they would stay PROVISIONAL.

### 2e. ⚠️ two rows of this table still have no surviving proof behind them

Blocks **964878** and **964881** are carried, as v26 §2g carried them, and no proof in this folder names
either. Their roots are true facts about Bitcoin; what is gone is the evidence that a document of this
study was committed into those blocks. `pin_anchors.py --verify` refuses on them, and that is not
overridden here.

### 2f. ⛔ the eight state-dependent attacks, measured in this version's draft window

Measured on 9 October 2026, run completed 12:49 UTC, by `python test_controls.py` over this draft
before this subsection was written (a document cannot carry the digest of its own final bytes, so the
run is of the draft with this slot unfilled; nothing else changed between the run and this text).

```
CONTROL-SUITE-VERDICT.json   sha256 ef32903fc572a67ebe0fc6f8c044b61fe40779c77567f76e911a6778e846e327
  tree_digest                     dbb3f993e230fa6e
  attacks_declared                77
  attacks_refused                 77
  attacks_passed_that_should_not  0
  refused_for_the_wrong_reason    0
  attacks_not_measured            0
  hygiene_failed                  false
  security_ok                     true
  positive_control_failed         true     (liveness_ok false -- see below)
```

**The eight that v26 could not measure ran and were refused, each for the reason under test.** They are
the declaration checks on an unanchored draft's commitment table, the last eight of the
`prepare_anchor.py` group: a second, contradictory pin for one file; a digest in a commitment block that
no row consumes; a pinned file changed and its pin upper-cased; a pin whose name leaves the study
folder; a pin one hex character short; one non-hex character, so the row and the count leave; the
declared total deleted; a row added without updating the declared total. With §2a's global counter,
**77 declared is now the count of attacks the suite holds, and 0 unmeasured says every one ran.**

⚠️ **The positive control fails, and it is expected to in this window and nowhere else.**
`check_commitments.py` refuses the real tree for two reasons, both of which are the draft window itself:
the three repaired files (`test_controls.py`, `build_review_packet.py`, `withdrawn_claims.py`) no longer
match v26's commitments, and this document is present with no proof binding it. Both clear when this
version is signed and its proof is anchored. **A positive control that still fails after anchoring is a
finding against this version, not a window effect**, and the first post-anchor run is the check.

**Two later changes, and the run that covers them.** A second run on 9 October, over this document
with the slot filled, returned the same figures (tree `4c438acacd326a1b`). On 12 October the
disposition-log head's proof anchored, `pin_anchors.py --add` pinned blocks 970631 and 970639 in
`ANCHORS.json`, and §2d gained their two rows. The suite was run again over that tree before this
version was signed; its `CONTROL-SUITE-VERDICT.json` is the record of what was measured, and this
document is not edited after it.

## 3. ⛔ What is committed, by DIGEST

### 3a. The tools, the key, and every other path the composed history pins, at the bytes this version commits

Three rows are repairs: **`test_controls.py`** carries §2a, **`build_review_packet.py`** §2b, and
**`withdrawn_claims.py`** §2c. The other twenty-seven rows restate. `REVIEW-SHIP-LIST.json` is
deliberately not pinned (§2b).

**This version commits exactly 30 file pins, and the sorted pinned names hash to 968b5635c5e00e030a6f12da305fdae3b977327e5adfa484331cd48888f3926e.**

The membership digest is computed from the names this version INTENDS to commit -- v26's set,
unchanged, because this version moves three digests and no name.

Every digest below was written from the bytes on disk by `prepare_anchor.py --repin`, never typed.

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   886f615899d22181a0000223776c6ff3bbe33962e45dcd7e5471688fdd286d7c
build_review_packet.py             6ae679a3f70416029ee8050f42c162c0d076fd112a36910586cffbb70d28c620
check_commitments.py               c2532c98dbba0950fdc53b4fc4d289d0f70267e1c427ed617e5a7000aa20ea23
check_signature.py                 46bed0e0d35f1c192ad984f7be470a5acefe624e33d5f3ea5e11f2259728fff3
ots_verify.py                      2c5676b0518aca1b36af6899b71a326c73a5253e6593a7cc1f1ea266ea7290ee
pin_anchors.py                     ca5e9d207b77f87b6fef84ae322e03aab12bd1eea8b905fd62c9b5e107173d90
prepare_anchor.py                  687e0d5a03154697bfc14bb71d28a7910953546c01c46e2a771175a20ad51026
test_controls.py                   3363626196ca5b9b1f868e754f111f666bf821b8e9015c65cf85de240cf4b378
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

Everything v26 committed that is not named above is committed here at the same bytes. No claim v26
made is withdrawn except the one §1 corrects: v26 §2b's statement that a reader could now see every
attack that did not run.

## 5. ⛔ What this version does NOT do

It does not stamp the new disposition-log head; that is the operator's act, and until it is done the
head protects nothing and the packet does not build (§2c).

It does not resolve blocks 964878 and 964881 (§2e).

It does not re-pin the deposit, the manuscript, or anything outside this study folder.

It makes no claim about what any of these controls would find on a tree other than this one.
