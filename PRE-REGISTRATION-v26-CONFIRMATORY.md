# Pre-registration v26 — confirming v25, and repairing what round 22 found

**Status: this document governs nothing until it is signed, stamped, and confirmed by a later
version's anchor table.** That sentence is written to be true before and after signing, which the
status line of v25 was not: it read *"DRAFT. Unsigned, unstamped"* and was then signed with those
words in it.

## 1. ⛔ Why this version exists

**First, v25 is confirmed.** v25 was signed, and its proof landed in Bitcoin blocks **969166** and
**969170**. By this protocol's own rule a version's claim about its own anchor is not evidence; only
a later version's table settles it. §2d carries both heights, and v25 is PROVISIONAL until this
document is in force.

**Second, a review packet that could not be built was replaced by one that could, and the bundle
did not say so.** Three files appeared in this folder on 2 October — `AMENDMENT-CHRONOLOGY.md`,
`build_amendment_table.py` and `FRAMING-DECISION-2026-10-02.md`. No list classified them, so
`build_review_packet.py` refused from that day, correctly. **The round-22 bundle shipped a paper-B
packet anyway**: 235 members and none of the three, measured against the sealed bundle. The gate
failed closed and the pipeline used the last packet that had built. §2a.

**Third, three smaller defects found by an external reader of round 22** (§2b, §2c, §2f), and two
found while building this version: a proof anchored in no table (§2e), and two rows of the table
whose proofs no longer exist (§2g).

## 2. ⛔ What was wrong, and is repaired under this version

### 2a. ⛔ three files no list classified, and the stale packet that shipped in their place

`build_review_packet.py` now classifies the three files by name. ⚠️ **This is the same cost v25
removed for findings and did not remove for anything else**: the inventory lives inside a file this
protocol pins, so classifying a new file requires a new version. §5 names that and does not fix it.

⚠️ **The stale packet is recorded, not rewritten.** The round-22 bundle is sealed as sent. The next
packet carries the three files. A reader comparing the two should know that the round-22 reviewer did
not have them, so remarks made on the amendment chronology in that round were made without it.

### 2b. ⛔ the verdict carried its numerators and not its denominator

`test_controls.py` computed the number of attacks it could not measure, printed it, and dropped it.
`CONTROL-SUITE-VERDICT.json` reported `attacks_refused: 64` beside `security_ok: true` and nothing
that said four declared attacks had not run; an external reviewer reconciled 68 against 64 from the
console. ⇒ The verdict now carries `attacks_declared` and `attacks_not_measured`, so a run reconciles
in the file a caller is told to read: refused + refused-for-the-wrong-reason + not-measured =
declared. `security_ok` keeps its meaning — no attack was accepted — and is not weakened by an attack
that did not run; a reader can now see that one did not.

### 2c. ⛔ a finding with no heading shipped under a description the build invented

v25 §2x made the rule *every FINDING-* file is classified or the build refuses*, and classified a
finding by its own first heading. A finding with no heading was given the description *"a finding
record carrying no heading of its own"* and shipped. **A placeholder is not a classification.** And
since a filename now authorises publication, the placeholder is what would let a draft dropped into
this folder go out. ⇒ The build refuses.

### 2d. ⛔ ANCHOR FACTS — monotonic

Each listed height must still carry the listed merkle root; new heights are permitted, and later
anchoring adds rather than contradicts. **The rows for 969166 and 969170 make v25 CONFIRMED.**
Every height v25 carried is carried here, and every root below was checked against block headers
fetched from two independent explorers before this version was signed.

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
```

### 2e. ⛔ a proof anchored at block 967531 was in no anchor table

`WITHDRAWN-DISPOSITIONS.head.ots` is a proof this tree verifies, anchored in block **967531**, and it
is pinned in `ANCHORS.json`. It appears in no version's anchor-fact table — not v24's, not v25's.
The pin file projects over every proof; the protocol tables were built from the protocol documents'
own proofs, which is the narrower set. §2d now carries it. The height is older than v24's own
anchor, which is why it was worth chasing rather than adding: a disagreement between the pin file
and the tables is the thing to understand before signing, not to sign through.

### 2f. ⛔ the withdrawn-claims baseline refused for two reasons, and the record named one

v25 §5 left this open, and a finding of 28 September attributed it to the verdict file, which
`test_controls.py` deletes at the start of a run and writes at the end, so the folder's text-file
count was one lower inside the suite than outside it. On 6 October the baseline was measured
refusing **with the verdict file present as well as absent**: the folder had grown to 154 text files
and `WITHDRAWN-CLAIMS.md` described a smaller one.

⇒ **Both causes are repaired, and the first is repaired where it arises rather than where it was
noticed.** `test_controls.py` deleted the verdict at the start of a run, before the withdrawn-claims
group, so the tree that group measured was one file smaller than the tree the record described. It
now overwrites the verdict with a record that cannot be read as a pass — no nonce, so
`build_package.py` refuses it; no `security_ok`, so nothing else reads it as clean — which keeps the
protection the deletion gave against a crashed run leaving a stale green verdict, and keeps the count
stable. `WITHDRAWN-CLAIMS.md` is regenerated against the folder as it stands: a stale generated
record, cured by regenerating it, and not pinned.

⚠️ **The fix the 28 September finding proposed was tried first and withdrawn.** It excluded the verdict
inside `withdrawn_claims.py`. That file carries the withdrawn claim's wording, so changing it unbinds
its recorded reading; recording a new one appends to the disposition log and rewrites the log's head;
and the head's proof is the one anchored in block **967531**, which would then commit to bytes the
folder no longer has. `ots_verify.py` reports no attestation for a proof over other bytes, so the
pin file would hold block 967531 with no proof naming it — which `pin_anchors.py --verify` refuses,
correctly. `withdrawn_claims.py` is therefore committed here at v25's bytes. §5 names the general
problem.

⚠️ **The claim that "the security property those attacks guard was never in question" is withdrawn.**
It was in that finding and it was not measured: an attack that does not run produces no evidence
either way.

**Now measured.** On 7 October, with the tooling this version commits, the withdrawn-claims baseline
passes — *the unmutated record verifies and the file describes this folder* — and all four attacks
are refused for the reason under test. The verdict reconciles: 66 refused, 2 refused for another
reason, 0 not measured, 68 declared. The two wrong-reason refusals are in the `prepare_anchor` group,
whose baseline refused, and that run's red positive control is `check_commitments.py` refusing the
tree; both for one reason, that the two repaired tools were not yet pinned by any document — the
state this version exists to end.

### 2g. ⚠️ two rows of this table have no surviving proof behind them

Blocks **964878** and **964881** are carried by v24's and v25's tables and pinned in `ANCHORS.json`,
and no proof in this folder names either. Searched, not assumed: all 76 files here whose names
contain `.ots` — including 22 superseded proofs whose names do not end in `.ots`, which a first search
by suffix missed — and 91 proof files under the backup vault's copies of this folder. None attests
either height. Their place in the sequence, between v7's anchor at 964856 and v8's at 964920, says
which period they came from and not which document.

⇒ **What survives and what does not.** Both roots were checked against the chain on 7 October and
three independent explorers agreed with each — the rows are true facts about Bitcoin. What is gone is
the evidence that a document of this study was committed into those blocks. The rows are restated,
because this table is monotonic and a row removed is history rewritten; this paragraph says what they
now rest on.

⚠️ **One consequence is in force.** `pin_anchors.py --verify` refuses a block that is pinned and named
by no proof, so it refuses on these two. That is the gate describing the folder correctly, and it is
not overridden here: deleting the pins would make the gate pass by erasing the only record that the
anchors were taken.

## 3. ⛔ What is committed, by DIGEST

### 3a. The tools, the key, and every other path the composed history pins, at the bytes this version commits

Two rows are repairs. **`build_review_packet.py`** carries §2a and §2c. **`test_controls.py`**
carries §2b and §2f. The other twenty-eight rows restate, `withdrawn_claims.py` among them, for the
reason §2f gives.

**This version commits exactly 30 file pins, and the sorted pinned names hash to 968b5635c5e00e030a6f12da305fdae3b977327e5adfa484331cd48888f3926e.**

The membership digest is computed from the names this version INTENDS to commit -- v25's set, unchanged, because this version moves two digests and no name. It is stated because the count alone cannot see a substitution: swapping one row for another holds the total exactly.

Every digest below was written from the bytes on disk, never typed.

```
PUBKEY.asc                         88f9a69659c87a898c6a4408d28e69520306b6916744642f60519469cbb24273
anchor_status.py                   886f615899d22181a0000223776c6ff3bbe33962e45dcd7e5471688fdd286d7c
build_review_packet.py             c5349d522514ca96e3ed32510752dd062e62b3af35b5d04ce6032ac6697f453c
check_commitments.py               c2532c98dbba0950fdc53b4fc4d289d0f70267e1c427ed617e5a7000aa20ea23
check_signature.py                 46bed0e0d35f1c192ad984f7be470a5acefe624e33d5f3ea5e11f2259728fff3
ots_verify.py                      2c5676b0518aca1b36af6899b71a326c73a5253e6593a7cc1f1ea266ea7290ee
pin_anchors.py                     ca5e9d207b77f87b6fef84ae322e03aab12bd1eea8b905fd62c9b5e107173d90
prepare_anchor.py                  687e0d5a03154697bfc14bb71d28a7910953546c01c46e2a771175a20ad51026
test_controls.py                   3ef1cc70c38fde52f947a5ddf604298092464e81ea8fde07e0e97fbb9b1d2d3b
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

Everything v25 committed that is not named above is committed here at the same bytes. No claim v25
made is withdrawn. §2f withdraws one claim, which was made in a finding of 28 September and not in
any protocol version.

## 5. ⛔ What this version does NOT do

**It does not move the review packet's inventory out of pinned scope.** The rule deserves pinning —
*every file in this folder is shipped or excused by name, or the build refuses* — and the inventory
does not. As long as the inventory lives in `build_review_packet.py`, every new file costs a version,
and §1 records what that cost when it was not paid. A design that would end it: the rule stays in
the pinned tool, and the classification moves to a manifest the tool reads, shipped with every
packet so a reviewer sees it. It is not adopted here because it changes what a signed version
commits to, and that is a decision for the operator rather than a repair.

**It does not resolve the conflict between the disposition log and the anchor pins.** Every new
reading of a file that carries a withdrawn claim's wording rewrites
`WITHDRAWN-DISPOSITIONS.head`, and an anchored proof over the previous head then commits to bytes
that are gone. The pin file's rule that no block may be pinned without a proof naming it is right,
and so is the log's rule that a head protects nothing until a calendar has seen it; together they
mean the first reading recorded after the head is anchored orphans that anchor. The design that would
end it keeps each superseded head beside its proof, under a name the anchor projection reads, so an
old anchor stays evidence about the bytes it was taken over. It is not adopted here for the reason
the manifest above is not: it changes what this protocol commits to.

It does not re-pin the deposit, the manuscript, or anything outside this study folder.

It makes no claim about what any of these controls would find on a tree other than this one.
