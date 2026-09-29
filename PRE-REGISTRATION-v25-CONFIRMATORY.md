# Pre-registration v25 — confirming v24, and moving two rules out of the way of their own findings

**Status: DRAFT. Unsigned, unstamped, and it governs nothing.** It exists because v24 going in force
made a cost visible that three rounds had each paid without naming: shipping one new finding
required a signed, stamped, anchored protocol version, because the list of what the review packet
ships lives inside a file the protocol pins.

## 1. ⛔ Why this version exists

v24 was signed on 27 September 2026 and its proof landed in Bitcoin block **968848**. Three things
follow.

**First, v24 is confirmed.** §2d below carries that height, and by this protocol's own rule a
version's own claim about its own anchor is not evidence: only a later version's table settles it.
v24 is PROVISIONAL until this document is in force.

**Second, a cost that had been paid three times is removed rather than paid a fourth.**
`build_review_packet.py` listed the findings it ships. v23 pinned that file; v24 §2c re-pinned it to
ship the four findings of 26 September; and on 28 September a fifth finding could not be shipped for
the same reason. **The fix for a list that goes stale is not a longer list** — this tree's own words,
written one function above the list in question, about exactly this defect in the protocol-document
list. §2x applies it to findings.

**Third, two counters were conflated and a caller read the wrong one.** §2y.

## 2. ⛔ What was wrong, and is repaired under this version

### 2x. ⛔ the packet's finding list sat inside pinned scope

`build_review_packet.py` classified each `FINDING-*.md` by a hand-written entry. A finding with no
entry is a stray file and refuses the build — which is the fail-closed half working — but the only
way to add the entry was to edit a pinned file, and that costs a protocol version.

⇒ **The rule is pinned; the inventory is not.** `_findings_send()` collects every `FINDING-*.md` and
reads each one's description from the document's own first heading. A finding cannot ship with a
description that has drifted from what it says, and a new finding needs no version.

⚠️ **The fail-closed half is untouched.** A file that does not match the pattern is still a stray
file and still refuses. What changed is that a finding is classified by a rule rather than by
somebody remembering.

⚠️ This is the treatment `_protocol_send()` already had, for the same reason, after a list of
version names refused to build when v8 appeared.

### 2y. ⛔ a refusal for the wrong reason was counted as an attack that passed

On one run `test_controls.py` printed **"THE POSITIVE CONTROL FAILED, AND NO ATTACK PASSED"** while
its verdict file recorded `attacks_passed_that_should_not_have: 2` and `security_ok: false`. This
file states that a caller must read the verdict rather than the text, so the half that governs was
the half that was wrong.

`missed` was incremented whenever an attack was not `ok`, and `ok` requires both a refusal **and**
the expected reason. A case that refused for a *different* reason therefore landed in the counter
whose field name asserts the attack was accepted.

⇒ `wrong_reason` is counted and reported separately, `attacks_passed_that_should_not_have` means
what it says, and `security_ok` no longer goes false because the tree was red for an unrelated
reason.

⚠️ **It is still not good news.** A wrong-reason refusal means the attack measured nothing. It is
reported, and it keeps a run from being clean; it simply stops being reported as a breach.

⚠️ **Round 9 split security from liveness after a reviewer flagged that conflation three times.**
This is the same conflation one level in, and it survived because the two live in one counter.

### 2z. ⚠️ four attacks printed as refused under a baseline that said nothing below it was measured

The `withdrawn_claims.py` block printed `the baseline does not pass, so nothing below is measured`
and then four lines reading `refused`. Both cannot be load-bearing. The baseline's statement is:
a refusal observed while the baseline is broken says only that the tool refused, not that it refused
for the reason under test. Those four now print as `unmeasured` and are counted in neither total.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each listed height must still carry the listed merkle root; new heights are permitted, and later
anchoring adds rather than contradicts. **The last row is what makes v24 CONFIRMED.** Every height
v24 carried is carried here.

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
967728  57aff597b9004136ea9de160d284ba8cd1c59f8ac72aa400210c82a497c99d03
967736  a27c668a4d320942f8cb3906efbfefefaedda9d760d5d52bdb74f7a7e0f1a0d4
968668  62e24a1b11ad70b4aedc31f2eca6d15eec594db333f747ed994b2faa008f8688
968689  a78a98471004cbaadb5109722db134ac691eb9c9c8d504616626b33e74566c02
968848  453eebd038135e3b5fa26754b4d850dc1a8b9520d28ca0d4990c38d6bbe4b202
```

## 3. ⛔ What is committed, by DIGEST

### 2c. The tools, the key, and every other path the composed history pins, at the bytes this version commits

Two rows are repairs and are named here so the gate reads them as repairs rather than as
restatements that fail to restate. **`build_review_packet.py`** carries §2x's rule.
**`test_controls.py`** carries §2y's counter split and §2z's unmeasured reporting. The other
twenty-eight rows restate.

**This version commits exactly 30 file pins, and the sorted pinned names hash to 968b5635c5e00e030a6f12da305fdae3b977327e5adfa484331cd48888f3926e.**

The membership digest is computed from the names this version INTENDS to commit -- v24's set,
unchanged, because this version moves two digests and no name. It is stated because the count
alone cannot see a substitution: swapping one row for another holds the total exactly. The number is stated here, in prose and
outside the fence, because the only other answer to *how many* comes from the pattern that
reads the rows -- and a row that stops matching would take the total down with it, silently.

Every digest below was written from the bytes on disk, never typed.

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   886f615899d22181a0000223776c6ff3bbe33962e45dcd7e5471688fdd286d7c
build_review_packet.py             a333d3393a7f4ce9f4ea1bc9362735507e90d64b9a9714749d58bd5685a1397a
check_commitments.py               c2532c98dbba0950fdc53b4fc4d289d0f70267e1c427ed617e5a7000aa20ea23
check_signature.py                 46bed0e0d35f1c192ad984f7be470a5acefe624e33d5f3ea5e11f2259728fff3
ots_verify.py                      2c5676b0518aca1b36af6899b71a326c73a5253e6593a7cc1f1ea266ea7290ee
pin_anchors.py                     ca5e9d207b77f87b6fef84ae322e03aab12bd1eea8b905fd62c9b5e107173d90
prepare_anchor.py                  687e0d5a03154697bfc14bb71d28a7910953546c01c46e2a771175a20ad51026
test_controls.py                   6710862af7309a62a40e96ee484240f8dac2a5cdf52dff2499af69cd4d072d8c
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
withdrawn_claims.py                3d06a244f4dfbd2c6e87dacc6ff99d221bd201fb1997a8af9c784dd9b02c7e18
```

## 4. ⚠️ Unchanged

Everything v24 committed that is not named above is committed here at the same bytes. No claim v24
made is withdrawn.

## 5. ⛔ What this version does NOT do

It does not repair the hygiene finding of 28 September — the `withdrawn_claims.py` baseline that
failed inside the suite while passing standalone. §2z reports the consequence honestly rather than
hiding it, and that is not the same as understanding the cause.

It does not re-pin the deposit, the manuscript, or anything outside this study folder.

It makes no claim about what any of these controls would find on a tree other than this one.
